import os.path
import sys

from pathlib import Path
from typing import List, Union, Tuple


def strip_whitespace_and_return_instructions(path: Path) -> List[str]:
    instructions = []
    with open(path, 'r') as asm_file:
        line = asm_file.readline()
        while line:
            line = line.replace(" ", "")
            line = line.replace("\n", "")
            line = line.split("//")[0]
            if line:
                instructions.append(line)
            line = asm_file.readline()

    return instructions


class SymbolTable:

    def __init__(self):
        self.table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,
        }
        self.next_variable_address = 16

    def add_label(self, symbol, address):
        if not self.contains(symbol):
            self.table[symbol] = address

    def add_variable(self, symbol):
        if not self.contains(symbol):
            self.table[symbol] = self.next_variable_address
            self.next_variable_address = self.next_variable_address + 1

    def contains(self, symbol) -> bool:
        return symbol in self.table

    def get_address(self, symbol) -> int:
        return self.table[symbol]


def is_label(instruction) -> bool:
    return instruction[0] == "(" and instruction[-1:] == ")"


class AInstruction:

    def __init__(self, value: int):
        self.value = value

    def as_binary(self) -> str:
        return "{0:b}".format(self.value).zfill(16)


COMP_TABLE = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

DEST_TABLE = {
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

JUMP_TABLE = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


class CIntruction:

    def __init__(self, comp, dest, jump):
        self.comp = comp
        self.dest = dest
        self.jump = jump

    def as_binary(self) -> str:
        return f"111{self._comp_to_binary_form(self.comp)}{self._dest_to_binary_form(self.dest)}{self._jump_to_binary_form(self.jump)}"

    def _comp_to_binary_form(self, comp):
        return COMP_TABLE[comp]

    def _dest_to_binary_form(self, dest):
        if dest in DEST_TABLE:
            return DEST_TABLE[dest]
        else:
            return "000"

    def _jump_to_binary_form(self, jump):
        if jump in JUMP_TABLE:
            return JUMP_TABLE[jump]
        else:
            return "000"


def main():
    filepath: str = sys.argv[1]
    path: Path = Path(filepath)

    if not os.path.isfile(path) or path.suffix != ".asm":
        print("Please pass absolute path to a file with .asm extension")
        return

    instructions_with_labels: List[str] = strip_whitespace_and_return_instructions(path)
    print(instructions_with_labels)

    if not instructions_with_labels:
        print("no valid instructions in file")
        return

    symbol_table: SymbolTable = SymbolTable()

    labels: List[Tuple[int, str]] = [(index + 1, instruction[1:-1]) for index, instruction in
                                     enumerate(instructions_with_labels) if is_label(instruction)]

    for address, symbol in labels:
        symbol_table.add_label(symbol, address)

    with open(filepath.replace(".asm", ".hack"), "w") as hack_file:
        for instruction in instructions_with_labels:
            if is_label(instruction):
                continue

            binary = None
            if instruction[0] == "@":
                value = instruction[1:]
                if value.isnumeric():
                    binary = AInstruction(int(value)).as_binary()
                else:
                    if symbol_table.contains(value):
                        binary = AInstruction(symbol_table.get_address(value)).as_binary()
                    else:
                        symbol_table.add_variable(value)
                        binary = AInstruction(symbol_table.get_address(value)).as_binary()
            else:
                dest = None
                jump = None
                if "=" in instruction and ";" in instruction:
                    dest = instruction.split("=")[0]
                    jump = instruction.split(";")[1]
                    comp = instruction.split("=")[1].split(";")[0]
                elif "=" in instruction:
                    dest = instruction.split("=")[0]
                    comp = instruction.split("=")[1]
                else:
                    jump = instruction.split(";")[1]
                    comp = instruction.split(";")[0]

                binary = CIntruction(comp, dest, jump).as_binary()

            hack_file.write(binary+"\n")

if __name__ == "__main__":
    main()
