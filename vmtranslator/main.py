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
    if not path.is_file() or path.suffix != ".vm":
        print(f"Please provide an input path with file extension '.vm'. Provided: {input_path}")
        return

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

if __name__ == "__main__":
    main()