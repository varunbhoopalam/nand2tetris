from typing import TextIO, List, Optional

from jackanalyzer.jacktokenizer import TokenType


class Token:
    type: TokenType
    content: str

    def match(self, type: TokenType, content: Optional[str]) -> bool:
        return self.type == type and self.content == content




class CompilationEngine:

    def __init__(self, input_file: TextIO, output_file: TextIO, token_list: List[Token]):
        self.input_file = input_file
        self.output_file = output_file
        self.token_list = token_list
        self.token_index = 0

    def compile_class(self):
        """
        Top level call
        Grammar should conform to
            class className { classVarDec* subroutineDec* }
        :return:
        """
        self._consume(TokenType.KEYWORD, "class")
        self._consume(TokenType.IDENTIFIER)
        self._consume(TokenType.SYMBOL, "{")

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
        self._consume(TokenType.KEYWORD, ['static', 'field'])
        self.compile_type()
        self._consume(TokenType.IDENTIFIER)

        next_token = self._peek()
        while next_token.match(TokenType.SYMBOL, ','):
            self._consume(TokenType.SYMBOL, ',')
            self._consume(TokenType.IDENTIFIER)
            next_token = self._peek()

        self._consume(TokenType.SYMBOL, ";")

    def compile_subroutine_dec(self):
        """
        Jack Grammar
            (constructor | function | method) (void | type) subroutineName ( parameterList ) subroutineBody
        :return:
        """
        self._consume(TokenType.KEYWORD, ['constructor', 'function', 'method'])
        next_token: Token = self._peek()
        if next_token.match(TokenType.KEYWORD, 'void'):
            self._consume(TokenType.KEYWORD, 'void')
        else:
            self.compile_type()
        self._consume(TokenType.IDENTIFIER)
        self._consume(TokenType.SYMBOL, '(')
        self.compile_parameter_list()
        self._consume(TokenType.SYMBOL, ')')
        self.compile_subroutine_body()

    def compile_parameter_list(self):
        """
        Jack Grammar
            ( (type varName) (',' type varName)*)*
        :return:
        """
        next_token: Token = self._peek()
        # If next token is a right parenthesis, tbere are no parameters
        if next_token.match(TokenType.SYMBOL, ')'):
            return

        self.compile_type()
        self._consume(TokenType.IDENTIFIER)

        next_token: Token = self._peek()
        while next_token.match(TokenType.SYMBOL, ','):
            self._consume(TokenType.SYMBOL, ',')
            self._consume(TokenType.IDENTIFIER)
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
        self.compile_type()
        self._consume(TokenType.IDENTIFIER)
        while self._peek().match(TokenType.SYMBOL, ','):
            self._consume(TokenType.SYMBOL, ',')
            self._consume(TokenType.IDENTIFIER)
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
        self._consume(TokenType.IDENTIFIER)
        if self._peek().match(TokenType.SYMBOL, '['):
            self._consume(TokenType.SYMBOL, '[')
            self.compile_expression()
            self._consume(TokenType.SYMBOL, ']')
        self._consume(TokenType.SYMBOL, '=')
        self.compile_expression()
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
        if self._peek().content in OP_SYMBOLS:
            self._consume(TokenType.SYMBOL, OP_SYMBOLS)
            self.compile_term()

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
        match self._peek().type:
            case TokenType.INT_CONST:
                self._consume(TokenType.INT_CONST)
            case TokenType.STRING_CONST:
                self._consume(TokenType.STRING_CONST)
            case TokenType.KEYWORD:
                self._consume(TokenType.KEYWORD, ['true', 'false', 'null', 'this'])
            case TokenType.SYMBOL:
                if self._peek().content == '(':
                    #compile parenth expression
                    self._consume(TokenType.SYMBOL, '(')
                    self.compile_expression()
                    self._consume(TokenType.SYMBOL, ')')
                else:
                    #compile unaryOp term
                    self._consume(TokenType.SYMBOL, ['-', '~'])
            case TokenType.IDENTIFIER:
                self._consume(TokenType.IDENTIFIER)
                if self._peek().content in ['(', '.']:
                    self.compile_subroutine_call()
                elif self._peek().match(TokenType.SYMBOL, '['):
                    self._consume(TokenType.SYMBOL, '[')
                    self.compile_expression()
                    self._consume(TokenType.SYMBOL, ']')

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
