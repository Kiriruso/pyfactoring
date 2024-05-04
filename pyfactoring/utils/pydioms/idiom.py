from dataclasses import dataclass, field

from pyfactoring.utils.pydioms.prefixtree import PrefixNode, SubtreeVariant


@dataclass
class Idiom:
    ids: set[int] = field(default_factory=set, repr=False)
    total_trees: int = field(default=0)
    efficiency: float = field(default=None)

    length: int = field(default=0, init=False)
    information: float = field(default=0, init=False)
    total_operators: int = field(default=0, init=False, repr=False)
    total_operands: int = field(default=0, init=False, repr=False)
    selected: int | None = field(default=None, init=False, repr=False)
    variant: SubtreeVariant | None = field(default=None, init=False, repr=False)


@dataclass
class IdiomState:
    idiom: Idiom
    edges: list[PrefixNode] = field(repr=False)
    is_idiom: bool = field(default=False, init=False)

    def __post_init__(self):
        self._ids = iter(self.idiom.ids)

    def __next__(self) -> int:
        try:
            return next(self._ids)
        except StopIteration:
            return -1

    @property
    def ids(self) -> set[int]:
        return self.idiom.ids

    @property
    def idiom_length(self) -> int:
        return self.idiom.length

    @property
    def efficiency(self) -> float:
        return self.idiom.efficiency

    @property
    def information(self) -> float:
        return self.idiom.information

    @property
    def total_trees(self) -> int:
        return self.idiom.total_trees

    @property
    def total_operands(self) -> int:
        return self.idiom.total_operands

    @property
    def total_operators(self) -> int:
        return self.idiom.total_operators


@dataclass
class IdiomInfo:
    state: IdiomState
    id: int
    primary_ids: set[int] = field(init=False)

    def __post_init__(self):
        self.primary_ids: set[int] = {self.id}

    @property
    def efficiency(self) -> float:
        return self.state.efficiency
