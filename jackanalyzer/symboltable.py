from enum import Enum
from typing import Optional, Literal, TypedDict, Dict


class Kind(Enum, str):
    STATIC = 'static',
    FIELD = 'this',
    ARG = 'arg',
    VAR = 'local',


KIND = Literal[
    Kind.STATIC,
    Kind.FIELD,
    Kind.ARG,
    Kind.VAR,
]


class Symbol(TypedDict):
    type: str
    kind: str
    index: int


class SymbolTable:
    table: Dict[str, Symbol]

    def __init__(self):
        self.table = {}

    def define(self, name: str, type_: str, kind: KIND) -> None:
        """
        Defines a new identifier of the given name, type, kind and assigns it a running index.

        STATIC and FIELD identifiers have class scope,
        while ARG and VAR identfiers have a subroutine scope.

        :param name:
        :param type_:
        :param kind:
        :return: None
        """
        index: int = len([x for x in self.table.values() if x['kind'] == kind and x['type'] == type_])
        self.table[name] = {'type': type_, 'kind': kind, 'index': index}

    def var_count(self, kind: KIND) -> int:
        """
        Returns the number of variables of the given kind already defined in the current scope
        :param kind:
        :return: int
        """
        return len([x for x in self.table.values() if x['kind'] == kind])

    def kind_of(self, name: str) -> Optional[str]:
        """
        Returns the kind of the named identifier in the current scope.
        If the identfier is unknown in the current scope, returns None
        :param name:
        :return:
        """
        symbol: Optional[Symbol] = self.table.get(name, None)
        if not symbol:
            return None

        return symbol['kind']

    def type_of(self, name: str) -> Optional[str]:
        """
        Returns the type of the named identifier in the current scope
        :param name:
        :return:
        """
        symbol: Optional[Symbol] = self.table.get(name, None)
        if not symbol:
            return None

        return symbol['type']

    def index_of(self, name: str) -> Optional[int]:
        """
        Returns the index assigned to the named identifier
        :param name:
        :return:
        """
        symbol: Optional[Symbol] = self.table.get(name, None)
        if not symbol:
            return None

        return symbol['index']

    def reset_subroutine_vars(self):
        pass
