from enum import Enum
from typing import Literal


class Segment(Enum, str):
    CONST = 'const'
    ARG = 'arg'
    LOCAL = 'local'
    STATIC = 'static'
    THIS = 'this'
    THAT = 'that'
    POINTER = 'pointer'
    TEMP = 'temp'


SEGMENT = Literal[
    Segment.CONST,
    Segment.ARG,
    Segment.LOCAL,
    Segment.STATIC,
    Segment.THIS,
    Segment.THAT,
    Segment.POINTER,
    Segment.TEMP,
]


class VMWriter:

    def __init__(self):
        """
        Creates a new output .vm file and prepares it for writing
        """
        pass

    def write_push(self, segment: Segment, index: int):
        """
        Writes a VM push command
        :param segment: (CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)
        :param index:
        :return:
        """
        pass

    def write_pop(self, segment: Segment, index: int):
        """
        Writes a VM pop command
        :param segment: (CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)
        :param index:
        :return:
        """
        pass

    def write_arithmetic(self, command: str):
        """
        Writes a VM arithmetic-logical command
        :param command: (ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT)
        :return:
        """
        pass

    def write_label(self, label: str):
        pass

    def write_goto(self, label: str):
        pass

    def write_if(self, label: str):
        pass

    def write_call(self, name: str, n_args: int):
        pass

    def write_function(self, name: str, n_locals: int):
        pass

    def write_return(self):
        pass

    def close(self):
        pass
