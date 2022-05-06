from pathlib import Path
from sys import argv
from typing import TextIO

from vmtranslator.codewriter import CodeWriter
from vmtranslator.commands import CommandNameEnum
from vmtranslator.parser import Parser


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
        path.suffix = ".hack"
        write_file: TextIO = open(path)
        code_writer: CodeWriter = CodeWriter(write_file)

        parser: Parser = Parser(input_file)
        parser.advance()

        while parser.has_more_commands():
            match parser.command_type():
                case CommandNameEnum.C_ARITHMETIC:
                    pass
                case CommandNameEnum.C_PUSH:
                    pass
                case CommandNameEnum.C_POP:
                    pass
                case _:
                    pass
            parser.advance()

    code_writer.close()


#get input file from command line arg

#construct parser to handle input file

#construct codewriter to handle output file

#march through input file, parse each line generating code from it