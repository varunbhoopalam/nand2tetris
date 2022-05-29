from typing import TextIO

from commands import CommandNameEnum


class CodeWriter:
    output_file: TextIO

    def __init__(self, output_file: TextIO):
        self.output_file = output_file
        self.label_number = 0
        self.filename = self.output_file.name
        self.assembly_command = ""

    def write_arithmetic(self, command: str) -> None:
        """
        Writes to the output file the assembly code that implements the given arithmetic command.
        :param command: str
        :return: None
        """
        self._add_to_write(f'// {command}')
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
        self._write()

    def write_push_pop(self, command: CommandNameEnum, segment: str, index: int) -> None:
        """
        Writes to the output file the assembly code that implements the given command
        :param command: C_PUSH or C_POP
        :param segment: str
        :param index: int
        :return:
        """
        self._add_to_write(f'// {command} {segment} {index}')
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
                        self._add_to_write(f"@{self.filename}.{index}")
                        self._add_to_write("M=D")
                    case "temp":
                        #addr = 5 + i, SP - -, *addr = *SP
                        self._decrement_stack_pointer_and_get_value_in_d_register()
                        self._add_to_write(f"@{index + 5}")
                        self._add_to_write("M=D")
                    case "pointer":
                        #SP--, THIS/THAT = *SP
                        self._decrement_stack_pointer_and_get_value_in_d_register()
                        match index:
                            case 0:
                                self._add_to_write("@THIS")
                                self._add_to_write("M=D")
                            case 1:
                                self._add_to_write("@THAT")
                                self._add_to_write("M=D")
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
                        self._add_to_write(f"@{index}")
                        self._add_to_write("D=A")
                        self._write_to_stack_and_increment_stack_pointer()
                    case "static":
                        """                
                        static
                        // D = stack.pop (code omitted)
                            @Foo.5
                            M=D
                        """
                        self._add_to_write(f"@{self.filename}.{index}")
                        self._add_to_write("D=M")
                        self._write_to_stack_and_increment_stack_pointer()
                    case "pointer":
                        match index:
                            case 0:
                                assembly_pointer: str = "THIS"
                            case 1:
                                assembly_pointer: str = "THAT"
                            case _:
                                raise Exception
                        self._add_to_write(f"@{assembly_pointer}.{index}")
                        self._add_to_write("D=M")
                        self._write_to_stack_and_increment_stack_pointer()
                    case "temp":
                        """
                        temp (address 5 through 12)
                        addr = 5 + i, *SP = *addr, SP++
                        """
                        self._add_to_write(f"@{5 + index}")
                        self._add_to_write("D=M")
                        self._write_to_stack_and_increment_stack_pointer()
                    case _:
                        raise Exception
            case _:
                raise Exception
        self._write()

    def close(self) -> None:
        """
        CLoses the output file.
        :return:
        """
        self.output_file.close()

    def set_file_name(self, filename: str) -> None:
        """
        Informs the codewriter that the parsing of a new file has started
        :param filename: str
        :return: None
        """
        self.filename = filename

    def write_init(self) -> None:
        """
        Writes the assembly instructions that effect the bootstrap code that initializes the VM.
        This code must be places at the beginnning of the generated *.asm file.
        :return: None
        """
        self._add_to_write("// init")
        self._add_to_write("@256")
        self._add_to_write("D=A")
        self._add_to_write("@SP")
        self._add_to_write("M=D")
        self.write_call("Sys.init", 0)

    def write_label(self, label: str) -> None:
        """
        Writes assembly code that effects the label command
        :return: None
        """
        self._add_to_write(f'// label {label}')
        self._add_to_write(f"({label})")
        self._write()

    def write_goto(self, label: str) -> None:
        """
        Writes assembly code that effects the goto command
        :return:
        """
        self._add_to_write(f'// goto {label}')
        self._add_to_write(f"@({label})")
        self._add_to_write("0;JMP")
        self._write()

    def write_if(self, label: str) -> None:
        """
        Writes assembly code that effects the if command
        :param label:
        :return:
        """
        self._add_to_write(f'// if-goto {label}')
        self._decrement_stack_pointer_and_get_value_in_d_register()
        self._add_to_write(f"@({label})")
        self._add_to_write("D;JGT")
        self._write()

    def write_function(self, function_name: str, num_vars: int) -> None:
        """
        Responsibilities:
        1. Sets up the local segment of the called function
          > push n_vars zero on to stack and set stack pointer to LCL
        :param function_name:
        :param num_vars:
        :return:
        """
        self._add_to_write(f"// function {function_name} {num_vars}")
        self._add_to_write(f'// function {function_name} {num_vars}')
        self._add_to_write(f"({self.filename}.{function_name})")
        self._add_to_write("@SP")
        self._add_to_write("D=M")
        self._add_to_write("@LCL")
        self._add_to_write("M=D")
        for x in range(num_vars):
            self.write_push_pop(CommandNameEnum.C_PUSH, "constant", 0)
        self._write()

    def write_call(self, function_name: str, num_vars: int) -> None:
        """
        Responsiblities:
        1. sets arg pointer @ argument 0 memory address
        2. saves the callers frame
          > (return address | saved LCL | saved ARG | saved THIS | saved THAT)
        3. jump to execute function_name
        :param function_name:
        :param num_vars:
        :return:
        """
        self._add_to_write(f"// call {function_name} {num_vars}")
        #SP is at x, arg should be set at x - nArgs - store in temp
        self._add_to_write("@SP")
        self._add_to_write("D=M")
        self._add_to_write(f"@{num_vars}")
        self._add_to_write("D=D-A")
        self._add_to_write("@R13")
        self._add_to_write("M=D") #Stores arg pointer in R13 temporarily
        # save return address by writing label and pushing label register onto stack
        label: str = self._create_label(f"Return_{function_name}")
        self._add_to_write(f"@{label}")
        self._add_to_write("D=A")
        self._write_to_stack_and_increment_stack_pointer()
        # save LCL bump SP
        self._add_to_write("@LCL")
        self._add_to_write("D=M")
        self._write_to_stack_and_increment_stack_pointer()
        # save ARG bump SP
        self._add_to_write("@ARG")
        self._add_to_write("D=M")
        self._write_to_stack_and_increment_stack_pointer()
        # save THIS bump SP
        self._add_to_write("@THIS")
        self._add_to_write("D=M")
        self._write_to_stack_and_increment_stack_pointer()
        # save THAT bump SP
        self._add_to_write("@THAT")
        self._add_to_write("D=M")
        self._write_to_stack_and_increment_stack_pointer()
        # jump to execute function name
        self.write_goto(function_name)
        # write return value
        self.write_label(label)
        self._write()

    def write_return(self) -> None:
        """
        Responsibilities:
        1. Copy top most value of stack to arg 0
        2. Restore segment pointers of the callers
        3. Clear the stack
        4. Sets SP for the caller (one above arg0)
        5. Jumps to the return address within the code
        :return:
        """
        self._add_to_write("// return")
        self.write_push_pop(CommandNameEnum.C_POP, "argument", 0)
        # Save address for SP to clear stack
        self._add_to_write("@ARG")
        self._add_to_write("D=M")
        self._add_to_write("@R13")
        self._add_to_write("M=D+1")
        # Navigate to saved Frame
        self._add_to_write("@LCL")
        self._add_to_write("A=M")
        # Restore THAT
        self._add_to_write("A=A-1")
        self._add_to_write("D=M")
        self._add_to_write("@THAT")
        self._add_to_write("M=D")
        # Restore THIS
        self._add_to_write("D=D-1")
        self._add_to_write("@THIS")
        self._add_to_write("M=D")
        # Restore ARG
        self._add_to_write("D=D-1")
        self._add_to_write("@ARG")
        self._add_to_write("M=D")
        # Restore LCL
        self._add_to_write("D=D-1")
        self._add_to_write("@LCL")
        self._add_to_write("M=D")
        # Save return address
        self._add_to_write("A=D")
        self._add_to_write("A=A-1")
        self._add_to_write("D=M") #return address in d register
        self._add_to_write("@R14")
        self._add_to_write("M=D")
        # Set SP
        self._add_to_write("@R13")
        self._add_to_write("D=M")
        self._add_to_write("@SP")
        self._add_to_write("M=D")
        # Jump to return address
        self._add_to_write("@R14")
        self._add_to_write("A=M")
        self._add_to_write("0;JMP")
        self._write()

    def _push_common_pattern(self, assembly_pointer: str, index: int) -> None:
        """
        addr = segmentPointer + i, *SP = *addr, SP++

        :param pointer: assembly pointer recognized by assembler
        :param index: int
        :return: None
        """
        self._add_to_write(f"@{assembly_pointer}")
        self._add_to_write(f"D=M")
        self._add_to_write(f"@{index}")
        self._add_to_write(f"A=A+D")
        self._add_to_write("D=M")
        self._write_to_stack_and_increment_stack_pointer()

    def _pop_common_pattern(self, assembly_pointer: str, index: int) -> None:
        # addr = segmentPointer + i, SP - -, *addr = *SP
        self._add_to_write(f"@{assembly_pointer}")
        self._add_to_write("D=M")
        self._add_to_write(f"@{index}")
        self._add_to_write("D=D+A")
        self._add_to_write("@R13")
        self._add_to_write("M=D") #addr to write to stored in R13

        self._decrement_stack_pointer_and_get_value_in_d_register()

        self._add_to_write("@R13")
        self._add_to_write("A=M")
        self._add_to_write("M=D")

    def _write_to_stack_and_increment_stack_pointer(self):
        self._add_to_write("@SP")
        self._add_to_write("A=M")
        self._add_to_write("M=D")
        self._add_to_write("@SP")
        self._add_to_write("M=M+1")

    def _decrement_stack_pointer_and_get_value_in_d_register(self):
        self._add_to_write("@SP")
        self._add_to_write("M=M-1")  # SP - -
        self._add_to_write("A=M")
        self._add_to_write("D=M")

    def _add_to_write(self, text: str):
        self.assembly_command.append(text+"\n")

    def _write(self):
        self.output_file.write(self.assembly_command+"\n")
        self.assembly_command = ""

    def _create_label(self):
        self.label_number += 1
        return f"LABEL{self.label_number}"

    def _decrement_segment_pointer_and_go_to_memory_address_one_below_sp(self):
        self._add_to_write("@SP")
        self._add_to_write("M=M-1")  # set stack pointer to one lower
        self._add_to_write("A=M")
        self._add_to_write("D=M")  # get latest value in stack to D register
        self._add_to_write("A=A-1")  # A register to second latest value in stack

    def _arith_multi_param(self, return_value: str):
        self._decrement_segment_pointer_and_go_to_memory_address_one_below_sp()
        self._add_to_write(f"M={return_value}")  # do calculation

    def _arith_jump_logic(self, jump_condition: str):
        jump_label: str = self._create_label()
        end_label: str = self._create_label()
        self._decrement_segment_pointer_and_go_to_memory_address_one_below_sp()
        self._add_to_write("D=M-D")  # do calculation
        self._add_to_write(f"@{jump_label}")
        self._add_to_write(f"D;{jump_condition}")
        self._add_to_write(f"@{end_label}")
        self._add_to_write("0;JMP")
        self._add_to_write(f"({jump_label})")
        self._add_to_write("@SP")
        self._add_to_write("A=M")
        self._add_to_write("A=A-1")
        self._add_to_write("M=1")
        self._add_to_write(f"({end_label})")

    def _arith_single_param(self, return_value: str):
        self._add_to_write("@SP")
        self._add_to_write("A=M")
        self._add_to_write("A=A-1")
        self._add_to_write(f"M={return_value}")