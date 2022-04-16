from io import TextIOWrapper

from vmtranslator.commands import CommandNameEnum


class CodeWriter:
    output_file: TextIOWrapper

    def __init__(self, output_file: TextIOWrapper):
        self.output_file = output_file

    def write_arithmetic(self, command: str) -> None:
        """
        Writes to the output file the assembly code that implements the given arithmetic command.
        :param command: str
        :return: None
        """
        pass

    def write_push_pop(self, command: CommandNameEnum, segment: str, index: int) -> None:
        """
        Writes to the output file the assembly code that implements the given command
        :param command: C_PUSH or C_POP
        :param segment: str
        :param index: int
        :return:
        """
        pass

    def close(self):
        """
        CLoses the output file.
        :return:
        """
