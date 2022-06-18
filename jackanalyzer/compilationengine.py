from typing import TextIO, List, Optional

from jackanalyzer.jacktokenizer import TokenType


class Token:
    type: TokenType
    content: str


class CompilationEngine:

    def __init__(self, input_file: TextIO, output_file: TextIO, token_list: List[Token]):
        self.input_file = input_file
        self.output_file = output_file
        self.token_list = token_list
        self.token_index = 0

    def compile_class(self):
        """
        Top level call
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
        pass

    def compile_subroutine_dec(self):
        pass

    def compile_parameter_list(self):
        pass

    def compile_subroutine_body(self):
        pass

    def compile_var_dec(self):
        pass

    def compile_statements(self):
        pass

    def compile_let(self):
        pass

    def compile_if(self):
        pass

    def compile_while(self):
        pass

    def compile_do(self):
        pass

    def compile_return(self):
        pass

    def compile_expression(self):
        pass

    def compile_term(self):
        pass

    def compile_expression_list(self):
        pass

    def _consume(self, type: TokenType, content: Optional[str] = None) -> None:
        """
        Consumes the next token expecting it to be of type with content.
        Raises the token index if successfully conforms to grammar
        Raises Exception if token is not as expected
        """
        token: Token = self.token_list[self.token_index]
        if content:
            is_expected_token: bool = token.type == type and token.content == content
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
