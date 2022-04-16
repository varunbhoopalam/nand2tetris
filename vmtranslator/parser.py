from io import TextIOWrapper

from vmtranslator.commands import CommandNameEnum


class Parser:
    input_file: TextIOWrapper
    current_command: str

    def __init__(self, input_file: TextIOWrapper):
        self.input_file = input_file

    def has_more_commands(self) -> bool:
        """
        Are there more commands in the input?
        """
        pass

    def advance(self) -> None:
        """
        Reads the next command from the input and makes it the current command.
        Should only be called if has_more_commands is true.
        Initially, there is no current command
        """
        pass

    def command_type(self) -> CommandNameEnum:
        """
        Returns a constant representing the type of the current command.
        C_ARITHMETIC is returned for all the arithmetic/logical commands.
        :return: CommandNameEnum
        """
        pass

    def arg1(self) -> str:
        """
        Returns the first argument of the current command.
        In the case of C_ARITHMETIC, the command itself (add, sub, etc.) is returned.
        Shoudl not be called if the current command is C_RETURN
        :return: str
        """
        pass

    def arg2(self) -> int:
        """
        Returns the second argument of the current command.
        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        :return: int
        """



