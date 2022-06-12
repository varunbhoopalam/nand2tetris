from enum import Enum
from typing import TextIO, List, Callable
import re


class EOFReached(Exception):
    pass


class TokenType(Enum):
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    IDENTIFIER = "IDENTIFIER"
    INT_CONST = "INT_CONST"
    STRING_CONST = "STRING_CONST"


KEYWORDS: List[str] = [
    "class",
    "method",
    "function",
    "constructor",
    "int",
    "boolean",
    "char",
    "void",
    "var",
    "static",
    "field",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return",
    "true",
    "false",
    "null",
    "this",
]

SYMBOLS = [
    '{',
    '}',
    '(',
    ')',
    '[',
    ']',
    '.',
    ',',
    '; ',
    '+',
    '-',
    '*',
    '/',
    '&',
    '|',
    '<',
    '>',
    '=',
    '~',
]


class JackTokenizer:
    input_file: TextIO
    _eof: bool = False
    _current_token: str
    _current_token_type: TokenType
    _current_line: str
    _current_line_index: int

    def __init__(self, input_file: TextIO):
        self.input_file = input_file

    def has_more_tokens(self) -> bool:
        return not self._eof

    def advance(self) -> None:
        if self._eof:
            return
        try:
            starting_character: str = self._get_starting_character()
        except EOFReached:
            self._eof = True
            return

        if starting_character in SYMBOLS:
            self._set_current_token(starting_character, TokenType.SYMBOL)
            self._current_line_index += 1
        elif starting_character.isnumeric():
            matcher: Callable = lambda x: x.isnumeric()
            token: str = self._builds_token_and_sets_index(starting_character, matcher)
            self._set_current_token(token, TokenType.INT_CONST)
        elif starting_character == '"':
            matcher: Callable = lambda x: x != '"'
            token: str = self._builds_token_and_sets_index(starting_character, matcher)
            self._set_current_token(token, TokenType.STRING_CONST)
        elif starting_character.isalpha():
            matcher: Callable = lambda x: re.match("^[a-zA-Z0-9_]*$", x)
            token: str = self._builds_token_and_sets_index(starting_character, matcher)
            if token in KEYWORDS:
                self._set_current_token(token, TokenType.KEYWORD)
            else:
                self._set_current_token(token, TokenType.IDENTIFIER)

    def token_type(self) -> TokenType:
        return self._current_token_type

    def key_word(self) -> str:
        return self._current_token

    def symbol(self) -> str:
        return self._current_token

    def identifier(self) -> str:
        return self._current_token

    def int_val(self) -> int:
        return int(self._current_token)

    def string_val(self) -> str:
        return self._current_token

    def _set_current_token(self, token: str, token_type: TokenType):
        self._current_token = token
        self._current_token_type = token_type

    def _builds_token_and_sets_index(self, starting_character: str, matcher: Callable):
        token: str = starting_character
        index: int = self._current_line_index + 1
        next_character: str = self._current_line[index]

        while matcher(next_character):
            starting_character += next_character
            index += 1
            next_character = self._current_line[index]

        self._current_line_index = index - 1
        return token

    def _get_starting_character(self):
        try:
            char: str = self._current_line[self._current_line_index]
        except IndexError:
            raise EOFReached

        if char.isspace():
            self._current_line_index += 1
            return self._get_starting_character()
        elif char == "\\":
            self._current_line = self.input_file.readline()
            self._current_line_index = 0
            return self._get_starting_character()
        elif char == "/":
            if self._current_line[self._current_line_index + 1] == "/":
                self._current_line = self.input_file.readline()
                self._current_line_index = 0
                return self._get_starting_character()
            else:
                next_index_location = self._current_line[self._current_line_index:].index("*/") + 2
                self._current_line_index = next_index_location
                return self._get_starting_character()
        else:
            return char
