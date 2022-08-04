from typing import TextIO, List, Optional

from jackanalyzer.jacktokenizer import TokenType
from jackanalyzer.symboltable import SymbolTable, Kind
from jackanalyzer.vmwriter import VMWriter, Segment


class Token:
    type: TokenType
    content: str

    def match(self, type: TokenType, content: Optional[str]) -> bool:
        return self.type == type and self.content == content


class CompilationEngine:
    symbol_table: SymbolTable
    class_name: str
    vmwriter: VMWriter

    def __init__(self, input_file: TextIO, output_file: TextIO, token_list: List[Token]):
        self.input_file = input_file
        self.output_file = output_file
        self.token_list = token_list
        self.token_index = 0
        self.vmwriter = VMWriter()

    def compile_class(self):
        """
        Top level call
        Grammar should conform to
            class className { classVarDec* subroutineDec* }
        :return:
        """
        self._consume(TokenType.KEYWORD, "class")
        self.class_name: str = self._peek().content
        self._consume(TokenType.IDENTIFIER)
        self._consume(TokenType.SYMBOL, "{")

        self.symbol_table = SymbolTable()

        finished_compiling_class_var_dec = False
        current_token: Token = self._peek()
        while current_token.type == TokenType.KEYWORD:
            if finished_compiling_class_var_dec and current_token.content in ('static', 'field'):
                raise Exception("Class variables must be declared before subroutines to conform to Jack grammar")
            elif current_token.content in ('static', 'field'):
                self.compile_class_var_dec()
                current_token = self._peek()
            elif current_token.content in ('constructor', 'function', 'method'):
                self.compile_subroutine_dec()
                finished_compiling_class_var_dec = True
                current_token = self._peek()
            else:
                raise Exception(f"Unknown keyword in class declaration | {current_token.content}")

        self._consume(TokenType.SYMBOL, "}")

    def compile_class_var_dec(self):
        """
        Grammar should conform to
            (static | field ) type varName (, varName)* ;
        :return:
        """
        symbol_kind: str = self._peek().content  # Should be static or field
        self._consume(TokenType.KEYWORD, ['static', 'field'])
        symbol_type: str = self._peek().content
        self.compile_type()
        symbol_name: str = self._peek().content
        self._consume(TokenType.IDENTIFIER)
        self.symbol_table.define(symbol_name, symbol_type, symbol_kind)

        next_token = self._peek()
        while next_token.match(TokenType.SYMBOL, ','):
            self._consume(TokenType.SYMBOL, ',')
            symbol_name: str = self._peek().content
            self._consume(TokenType.IDENTIFIER)
            self.symbol_table.define(symbol_name, symbol_type, symbol_kind)
            next_token = self._peek()

        self._consume(TokenType.SYMBOL, ";")

    def compile_subroutine_dec(self):
        """
        Jack Grammar
            (constructor | function | method) (void | type) subroutineName ( parameterList ) subroutineBody
        :return:
        """
        self.symbol_table.reset_subroutine_vars()
        subroutine_type: str = self._peek().content
        if subroutine_type == 'method':
            self.symbol_table.define('this', self.class_name, Kind.ARG)
        self._consume(TokenType.KEYWORD, ['constructor', 'function', 'method'])
        next_token: Token = self._peek()
        subroutine_return_type: str = self._peek().content
        if next_token.match(TokenType.KEYWORD, 'void'):
            self._consume(TokenType.KEYWORD, 'void')
        else:
            self.compile_type()
        subroutine_name: str = self._peek().content
        self._consume(TokenType.IDENTIFIER)
        self._consume(TokenType.SYMBOL, '(')
        self.compile_parameter_list()
        self._consume(TokenType.SYMBOL, ')')

        if subroutine_type == 'constructor':
            n_field_args: int = self.symbol_table.var_count(Kind.FIELD)
            self.vmwriter.write_push(Segment.CONST, n_field_args)
            self.vmwriter.write_call("Memory.alloc", 1)
            self.vmwriter.write_pop(Segment.POINTER, 0)

        self.compile_subroutine_body()

    def compile_parameter_list(self):
        """
        Jack Grammar
            ( (type varName) (',' type varName)*)*
        :return:
        """
        next_token: Token = self._peek()
        # If next token is a right parenthesis, there are no parameters
        if next_token.match(TokenType.SYMBOL, ')'):
            return

        arg_type: str = self._peek().content
        self.compile_type()
        arg_name: str = self._peek().content
        self._consume(TokenType.IDENTIFIER)
        self.symbol_table.define(arg_name, arg_type, Kind.ARG)

        next_token: Token = self._peek()
        while next_token.match(TokenType.SYMBOL, ','):
            self._consume(TokenType.SYMBOL, ',')
            arg_type: str = self._peek().content
            self.compile_type()
            arg_name: str = self._peek().content
            self._consume(TokenType.IDENTIFIER)
            self.symbol_table.define(arg_name, arg_type, Kind.ARG)
            next_token = self._peek()

    def compile_subroutine_body(self):
        """
        Jack grammar
            '{' varDec* statements '}'
        :return:
        """
        self._consume(TokenType.SYMBOL, '{')
        next_token: Token = self._peek()
        while next_token.match(TokenType.KEYWORD, 'var'):
            self.compile_var_dec()
            next_token = self._peek()
        self.compile_statements()
        self._consume(TokenType.SYMBOL, '}')

    def compile_var_dec(self):
        """
        Jack Grammar
            'var' type varName (',' varName)* ';'
        :return:
        """
        self._consume(TokenType.KEYWORD, 'var')
        var_type: str = self._peek().content
        self.compile_type()
        var_name: str = self._peek().content
        self._consume(TokenType.IDENTIFIER)
        self.symbol_table.define(var_name, var_type, Kind.VAR)
        while self._peek().match(TokenType.SYMBOL, ','):
            self._consume(TokenType.SYMBOL, ',')
            var_name: str = self._peek().content
            self._consume(TokenType.IDENTIFIER)
            self.symbol_table.define(var_name, var_type, Kind.VAR)
        self._consume(TokenType.SYMBOL, ';')

    def compile_statements(self):
        """
        Jack Grammar
            statment*

        statement jack grammar
            letStatement | ifStatment | whileStatment | doStatement | returnStatment
        :return:
        """
        while True:
            match self._peek().content:
                case 'let':
                    self.compile_let()
                case 'if':
                    self.compile_if()
                case 'while':
                    self.compile_while()
                case 'do':
                    self.compile_do()
                case 'return':
                    self.compile_return()
                case _:
                    break

    def compile_let(self):
        """
        Jack Grammar
            'let' varName ('[' expression ']')? '=' expression ';'
        :return:
        """
        self._consume(TokenType.KEYWORD, 'let')
        var_name: str = self._peek().content
        var_type: str = self.symbol_table.type_of(var_name)
        var_index: int = self.symbol_table.index_of(var_name)
        self.vmwriter.write_push(var_type, var_index)
        self._consume(TokenType.IDENTIFIER)
        if self._peek().match(TokenType.SYMBOL, '['):
            self._consume(TokenType.SYMBOL, '[')
            self.compile_expression()
            self._consume(TokenType.SYMBOL, ']')
            self.vmwriter.write_arithmetic('add')
            self.vmwriter.write_pop(Segment.TEMP, 0)
            self.vmwriter.write_pop(Segment.POINTER, 1)
            self.vmwriter.write_push(Segment.TEMP, 0)
            self.vmwriter.write_pop(Segment.THAT, 0)
        self._consume(TokenType.SYMBOL, '=')
        self.compile_expression()
        self.vmwriter.write_pop(Segment.POINTER, 1)
        self._consume(TokenType.SYMBOL, ';')

    def compile_if(self):
        """
        Jack grammar
            'if' '(' expression ')' '{' statements '}' (else '{' statements '}' )?
        :return:
        """
        self._consume(TokenType.KEYWORD, 'if')
        self._consume(TokenType.SYMBOL, '(')
        self.compile_expression()
        self._consume(TokenType.SYMBOL, ')')
        self._consume(TokenType.SYMBOL, '{')
        self.compile_statements()
        self._consume(TokenType.SYMBOL, '}')
        if self._peek().match(TokenType.KEYWORD, 'else'):
            self._consume(TokenType.KEYWORD, 'else')
            self._consume(TokenType.SYMBOL, '{')
            self.compile_statements()
            self._consume(TokenType.SYMBOL, '}')

    def compile_while(self):
        """
        Jack Grammar
            while '(' expression ')' '{' statements '}'
        :return:
        """
        self._consume(TokenType.KEYWORD, 'while')
        self._consume(TokenType.SYMBOL, '(')
        self.compile_expression()
        self._consume(TokenType.SYMBOL, ')')
        self._consume(TokenType.SYMBOL, '{')
        self.compile_statements()
        self._consume(TokenType.SYMBOL, '}')

    def compile_do(self):
        """
        jack grammar
            'do' subroutineCall
        :return:
        """
        self._consume(TokenType.KEYWORD, 'do')
        self.compile_subroutine_call()

    def compile_return(self):
        """
        jack grammar
            return expression? ;
        :return:
        """
        self._consume(TokenType.KEYWORD, 'return')
        if not self._peek().match(TokenType.SYMBOL, ';'):
            self.compile_expression()
        self._consume(TokenType.SYMBOL, ';')

    def compile_expression(self):
        """
        Jack Grammar
            term (op term)*
        :return:
        """
        OP_SYMBOLS = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        self.compile_term()
        op_symbol: Token = self._peek()
        if op_symbol.content in OP_SYMBOLS:
            self._consume(TokenType.SYMBOL, OP_SYMBOLS)
            self.compile_term()
            match op_symbol.content:
                case '+':
                    self.vmwriter.write_arithmetic('add')
                case '-':
                    self.vmwriter.write_arithmetic('sub')
                case '*':
                    self.vmwriter.write_call('Math.multiply', 2)
                case '/':
                    self.vmwriter.write_call('Math.divide', 2)
                case '&':
                    self.vmwriter.write_arithmetic('and')
                case '|':
                    self.vmwriter.write_arithmetic('or')
                case '<':
                    self.vmwriter.write_arithmetic('lt')
                case '>':
                    self.vmwriter.write_arithmetic('gt')
                case '=':
                    self.vmwriter.write_arithmetic('eq')

    def compile_term(self):
        """
        Jack Grammar
            integerConstant
            stringConstant
            keywordConstant
            varName
            varName'[' expression ']'
            subroutineCall
            '(' expression ')'
            unaryOp term
        :return:
        """
        token: Token = self._peek()
        match token.type:
            case TokenType.INT_CONST:
                self._consume(TokenType.INT_CONST)
                self.vmwriter.write_push(Segment.CONST, int(token.content))
            case TokenType.STRING_CONST:
                self._consume(TokenType.STRING_CONST)
                self.vmwriter.write_push(Segment.CONST, len(token.content))
                self.vmwriter.write_call('String.new')
                for char in token.content:
                    self.vmwriter.write_push(Segment.CONST, ord(char))
                    self.vmwriter.write_call('String.appendChar', 2)

            case TokenType.KEYWORD:
                self._consume(TokenType.KEYWORD, ['true', 'false', 'null', 'this'])
                match token.content:
                    case 'true':
                        self.vmwriter.write_push(Segment.CONST, 1)
                        self.vmwriter.write_call('neg', 1)
                    case 'false':
                        self.vmwriter.write_push(Segment.CONST, 0)
                    case 'null':
                        self.vmwriter.write_push(Segment.CONST, 0)
                    case 'this':
                        self.vmwriter.write_push(Segment.POINTER, 0)
                    case _:
                        raise Exception

            case TokenType.SYMBOL:
                if self._peek().content == '(':
                    #compile parenth expression
                    self._consume(TokenType.SYMBOL, '(')
                    self.compile_expression()
                    self._consume(TokenType.SYMBOL, ')')
                else:
                    #compile unaryOp term
                    self._consume(TokenType.SYMBOL, ['-', '~'])
                    self.vmwriter.write_call('neg', -1)
            case TokenType.IDENTIFIER:
                self._consume(TokenType.IDENTIFIER)
                var_kind = self.symbol_table.kind_of(token.content)
                if not var_kind:
                    raise Exception("Variable referenced before declaration")
                var_index = self.symbol_table.index_of(token.content)
                self.vmwriter.write_push(var_kind, var_index)

                if self._peek().content in ['(', '.']:
                    self.compile_subroutine_call()
                elif self._peek().match(TokenType.SYMBOL, '['):
                    self._consume(TokenType.SYMBOL, '[')
                    self.compile_expression()
                    self._consume(TokenType.SYMBOL, ']')
                    self.vmwriter.write_arithmetic('add')
                    self.vmwriter.write_pop(Segment.TEMP, 0)
                    self.vmwriter.write_pop(Segment.POINTER, 1)
                    self.vmwriter.write_push(Segment.TEMP, 0)
                    self.vmwriter.write_pop(Segment.THAT, 0)

    def compile_expression_list(self):
        """
        Jack Grammar
            (expression (',' expression)* )?
        :return:
        """
        if self._peek().match(TokenType.SYMBOL, ')'):
            return
        self.compile_expression()
        while self._peek().match(TokenType.SYMBOL, ','):
            self._consume(TokenType.SYMBOL, ',')
            self.compile_expression()


    def compile_type(self):
        """
        Jack grammar of type
            int | char | boolean | className
        :return:
        """
        if self._peek().type == TokenType.KEYWORD:
            self._consume(TokenType.KEYWORD, ['int', 'char', 'boolean'])
        else:
            self._consume(TokenType.IDENTIFIER)

    def compile_subroutine_call(self):
        """
        Jack grammar
            subroutineName '(' expressionList ')' |
            (className | varName) '.' subroutineName '(' expressionList ')'
        :return:
        """
        self._consume(TokenType.IDENTIFIER)
        if self._peek().match(TokenType.SYMBOL, '.'):
            self._consume(TokenType.SYMBOL, '.')
            self._consume(TokenType.IDENTIFIER)
        self._consume(TokenType.SYMBOL, '(')
        self.compile_expression_list()
        self._consume(TokenType.SYMBOL, ')')

    def _consume(self, type: TokenType, content: Optional = None) -> None:
        """
        Consumes the next token expecting it to be of type with content.

        content accepted as a list or string

        Raises the token index if successfully conforms to grammar
        Raises Exception if token is not as expected
        """
        token: Token = self.token_list[self.token_index]
        if isinstance(content, str):
            is_expected_token: bool = token.match(type, content)
        elif isinstance(content, list):
            is_expected_token: bool = token.type == type and token.content in content
        else:
            is_expected_token: bool = token.type == type

        if not is_expected_token:
            raise Exception("Does not conform to Jack grammar")

        self.token_index += 1

    def _peek(self) -> Token:
        """
        Returns the current token without advancing the index of current token
        :return: Token
        """
        return self.token_list[self.token_index]
