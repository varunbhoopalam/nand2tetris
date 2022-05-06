from typing import TextIO, Optional, List

from vmtranslator.commands import CommandNameEnum


class Parser:
    input_file: TextIO
    _current_command: Optional[str] = None
    _eof: bool = False

    def __init__(self, input_file: TextIO):
        self.input_file = input_file

    def has_more_commands(self) -> bool:
        """
        Are there more commands in the input?
        """
        return self._eof

    def advance(self) -> None:
        """
        Reads the next command from the input and makes it the current command.
        Should only be called if has_more_commands is true.
        Initially, there is no current command
        """
        if self._eof:
            return

        line: str = self.input_file.readline(1)

        if not line:
            self._eof = True
            return
        else:
            command: str = self._parse_command(line)
            if not command:
                self.advance()
            else:
                self._current_command = command

    def command_type(self) -> CommandNameEnum:
        """
        Returns a constant representing the type of the current command.
        C_ARITHMETIC is returned for all the arithmetic/logical commands.
        :return: CommandNameEnum
        """
        match self._current_command.split(" ")[0]:
            case "push":
                return CommandNameEnum.C_PUSH
            case "pop":
                return CommandNameEnum.C_POP
            case ("add" | "eq" | "gt" | "lt" | "not"):
                return CommandNameEnum.C_ARITHMETIC
            case _:
                raise Exception("unimplemented")

    def arg1(self) -> str:
        """
        Returns the first argument of the current command.
        In the case of C_ARITHMETIC, the command itself (add, sub, etc.) is returned.
        Shoudl not be called if the current command is C_RETURN
        :return: str
        """
        if self.command_type() == CommandNameEnum.C_RETURN:
            raise Exception("arg1 should not be called if the current command is C_RETURN")
        return self._current_command.split(" ")[0]

    def arg2(self) -> int:
        """
        Returns the second argument of the current command.
        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        :return: int
        """
        if not self.command_type() in [CommandNameEnum.C_PUSH, CommandNameEnum.C_POP, CommandNameEnum.C_FUNCTION,
                                       CommandNameEnum.C_CALL]:
            raise Exception("arg2 should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or C_CALL")
        return int(self._current_command.split(" ")[1])

    @staticmethod
    def _parse_command(command: str) -> str:
        if "//" in command:
            command = command.split("//")[0]
        return command.strip().strip("\n")
