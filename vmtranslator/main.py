from pathlib import Path
from sys import argv
from typing import TextIO

from codewriter import CodeWriter
from commands import CommandNameEnum
from parser import Parser


def main():
    try:
        input_path: str = argv[1]
    except IndexError:
        print("Please provide an input path as a command line argument.")
        return

    path: Path = Path(input_path)
    if path.is_file() and path.suffix != ".vm":
        with open(path, "r") as input_file:
            output_path: str = input_path.replace(".vm", ".asm")
            print(f"writing to {output_path}")
            write_file: TextIO = open(output_path, "w+")
            code_writer: CodeWriter = CodeWriter(write_file)

            parser: Parser = Parser(input_file)
            parser.advance()

            while parser.has_more_commands():
                match parser.command_type():
                    case CommandNameEnum.C_ARITHMETIC:
                        code_writer.write_arithmetic(parser.arg1())
                    case CommandNameEnum.C_PUSH | CommandNameEnum.C_POP:
                        code_writer.write_push_pop(parser.command_type(), parser.arg1(), parser.arg2())
                    case _:
                        raise Exception
                parser.advance()
        code_writer.close()
    elif path.is_dir():
        output_path: str = input_path + f"{path.name}/sys.asm"
        write_file: TextIO = open(output_path, "w+")
        code_writer: CodeWriter = CodeWriter(write_file)
        print(f"writing to {output_path}")

        vm_files = list(path.glob('**/*.vm'))
        for vm_file in vm_files:
            with open(vm_file, "r") as input_file:
                code_writer.set_file_name(input_file.name)
                parser: Parser = Parser(input_file)
                parser.advance()

                while parser.has_more_commands():
                    match parser.command_type():
                        case CommandNameEnum.C_ARITHMETIC:
                            code_writer.write_arithmetic(parser.arg1())
                        case CommandNameEnum.C_PUSH | CommandNameEnum.C_POP:
                            code_writer.write_push_pop(parser.command_type(), parser.arg1(), parser.arg2())
                        case CommandNameEnum.C_RETURN:
                            code_writer.write_return()
                        case CommandNameEnum.C_FUNCTION:
                            code_writer.write_function(parser.arg1(), parser.arg2())
                        case CommandNameEnum.C_CALL:
                            code_writer.write_call(parser.arg1(), parser.arg2())
                        case CommandNameEnum.C_LABEL:
                            code_writer.write_label(parser.arg1())
                        case CommandNameEnum.C_IF:
                            code_writer.write_if(parser.arg1())
                        case CommandNameEnum.C_GOTO:
                            code_writer.write_goto(parser.arg1())
                        case _:
                            raise Exception
                    parser.advance()
        code_writer.close()


if __name__ == "__main__":
    main()
