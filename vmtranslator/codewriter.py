from typing import TextIO

from vmtranslator.commands import CommandNameEnum


class CodeWriter:
    output_file: TextIO

    def __init__(self, output_file: TextIO):
        self.output_file = output_file
        self.label_number = 0

    def write_arithmetic(self, command: str) -> None:
        """
        Writes to the output file the assembly code that implements the given arithmetic command.
        :param command: str
        :return: None
        """
        self.output_file.write(f'// {command}')
        match command:
            case "add":
                self._arith_multi_param("M+D")
            case "sub":
                self._arith_multi_param("M-D")
            case "neg":
                self._arith_single_param("-M")
            case "eq":
                self._arith_jump_logic("JEQ")
            case "gt":
                self._arith_jump_logic("JGT")
            case "lt":
                self._arith_jump_logic("JLT")
            case "and":
                self._arith_multi_param("D&M")
            case "or":
                self._arith_multi_param("D|M")
            case "not":
                self._arith_single_param("!M")
            case _:
                pass

    def write_push_pop(self, command: CommandNameEnum, segment: str, index: int) -> None:
        """
        Writes to the output file the assembly code that implements the given command
        :param command: C_PUSH or C_POP
        :param segment: str
        :param index: int
        :return:
        """
        self._write(f'// {command} {segment} {index}')
        match command:
            case CommandNameEnum.C_POP:
                match segment:
                    case "local":
                        self._pop_common_pattern("LCL", index)
                    case "argument":
                        self._pop_common_pattern("ARG", index)
                    case "this":
                        self._pop_common_pattern("THIS", index)
                    case "that":
                        self._pop_common_pattern("THAT", index)
                    case "static":
                        self._decrement_stack_pointer_and_get_value_in_d_register()
                        self._write(f"@{self.output_file.name}.{index}")
                        self._write("M=D")
                    case "temp":
                        #addr = 5 + i, SP - -, *addr = *SP
                        self._decrement_stack_pointer_and_get_value_in_d_register()
                        self._write(f"@{index+5}")
                        self._write("M=D")
                    case "pointer":
                        #SP--, THIS/THAT = *SP
                        self._decrement_stack_pointer_and_get_value_in_d_register()
                        match index:
                            case 0:
                                self._write("@THIS")
                                self._write("M=D")
                            case 1:
                                self._write("@THAT")
                                self._write("M=D")
                            case _:
                                raise Exception
                    case _:
                        raise Exception
            case CommandNameEnum.C_PUSH:
                match segment:
                    case "local":
                        self._push_common_pattern("LCL", index)
                    case "argument":
                        self._push_common_pattern("ARG", index)
                    case "this":
                        self._push_common_pattern("THIS", index)
                    case "that":
                        self._push_common_pattern("THAT", index)
                    case "constant":
                        #*SP = i, SP++
                        self._write(f"@{index}")
                        self._write("D=A")
                        self._write_to_stack_and_increment_stack_pointer()
                    case "static":
                        """                
                        static
                        // D = stack.pop (code omitted)
                            @Foo.5
                            M=D
                        """
                        self._write(f"@{self.output_file.name}.{index}")
                        self._write("D=M")
                        self._write_to_stack_and_increment_stack_pointer()
                    case "pointer":
                        match index:
                            case 0:
                                assembly_pointer: str = "THIS"
                            case 1:
                                assembly_pointer: str = "THAT"
                            case _:
                                raise Exception
                        self._write(f"@{assembly_pointer}.{index}")
                        self._write("D=M")
                        self._write_to_stack_and_increment_stack_pointer()
                    case "temp":
                        """
                        temp (address 5 through 12)
                        addr = 5 + i, *SP = *addr, SP++
                        """
                        self._write(f"@{5+index}")
                        self._write("D=M")
                        self._write_to_stack_and_increment_stack_pointer()
                    case _:
                        raise Exception
            case _:
                raise Exception

    def close(self) -> None:
        """
        CLoses the output file.
        :return:
        """
        self.output_file.close()

    def _push_common_pattern(self, assembly_pointer: str, index: int) -> None:
        """
        addr = segmentPointer + i, *SP = *addr, SP++

        :param pointer: assembly pointer recognized by assembler
        :param index: int
        :return: None
        """
        self._write(f"@{assembly_pointer}")
        self._write(f"D=M")
        self._write(f"@{index}")
        self._write(f"A=A+D")
        self._write("D=M")
        self._write_to_stack_and_increment_stack_pointer()

    def _pop_common_pattern(self, assembly_pointer: str, index: int) -> None:
        # addr = segmentPointer + i, SP - -, *addr = *SP
        self._write(f"@{assembly_pointer}")
        self._write("D=M")
        self._write(f"@{index}")
        self._write("D=D+A")
        self._write("@R13")
        self._write("M=D") #addr to write to stored in R13

        self._decrement_stack_pointer_and_get_value_in_d_register()

        self._write("@R13")
        self._write("A=M")
        self._write("M=D")

    def _write_to_stack_and_increment_stack_pointer(self):
        self._write("@SP")
        self._write("A=M")
        self._write("M=D")
        self._write("@SP")
        self._write("M=M+1")

    def _decrement_stack_pointer_and_get_value_in_d_register(self):
        self._write("@SP")
        self._write("M=M-1")  # SP - -
        self._write("A=M")
        self._write("D=M")

    def _write(self, text: str):
        self.output_file.write(text+"\n")

    def _create_label(self):
        self.label_number += 1
        return f"LABEL{self.label_number}"

    def _decrement_segment_pointer_and_go_to_memory_address_one_below_sp(self):
        self._write("@SP")
        self._write("M=M-1")  # set stack pointer to one lower
        self._write("A=M")
        self._write("D=M")  # get latest value in stack to D register
        self._write("A=A-1")  # A register to second latest value in stack

    def _arith_multi_param(self, return_value: str):
        self._decrement_segment_pointer_and_go_to_memory_address_one_below_sp()
        self._write(f"M={return_value}")  # do calculation

    def _arith_jump_logic(self, jump_condition: str):
        jump_label: str = self._create_label()
        end_label: str = self._create_label()
        self._decrement_segment_pointer_and_go_to_memory_address_one_below_sp()
        self._write("D=M-D")  # do calculation
        self._write(f"@{jump_label}")
        self._write(f"D;{jump_condition}")
        self._write(f"@{end_label}")
        self._write("0;JMP")
        self._write(f"({jump_label})")
        self._write("@SP")
        self._write("A=M")
        self._write("A=A-1")
        self._write("M=1")
        self._write(f"({end_label})")

    def _arith_single_param(self, return_value: str):
        self._write("@SP")
        self._write("A=M")
        self._write("A=A-1")
        self._write(f"M={return_value}")