__all__ = ["extract_idioms", "Idiom", "IdiomInfo", "IdiomState"]

import math

from pyfactoring.config import config
from pyfactoring.utils.pydioms.inspect.prefix import PrefixLeaf, PrefixNode, PrefixTree, SubtreeVariant
from pyfactoring.utils.pydioms.inspect.types import AST_TOTAL_UNIQUE_OPERATORS, CountingType

min_idiom_count = config.get("pydioms").get("idiom_count", 5)
min_idiom_length = config.get("pydioms").get("idiom_length", 10)


class Idiom:
    __slots__ = [
        "ids",
        "length",
        "total_operators",
        "total_operands",
        "total_trees",
        "information",
        "efficiency",
        "variant",
        "selected",
    ]

    def __init__(self, ids: set[int] = None, total_trees: int = 0, efficiency: float = None):
        self.ids: set[int] = set() if ids is None else ids

        self.length: int = 0
        self.total_operators: int = 0
        self.total_operands: int = 0
        self.information: float = 0

        self.total_trees: int = total_trees
        self.efficiency: float | None = efficiency

        self.selected: int | None = None
        self.variant: SubtreeVariant | None = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"length={self.length}, "
            f"trees={self.total_trees}, "
            f"information={self.information}, "
            f"efficiency={self.efficiency}, "
            f"ids={self.ids}"
            f")"
        )


class IdiomState:
    __slots__ = ["idiom", "edges", "is_idiom", "_ids"]

    def __init__(self, idiom: Idiom, edges: list[PrefixNode]):
        self.idiom: Idiom = idiom
        self.edges: list[PrefixNode | PrefixLeaf] = edges
        self.is_idiom = False

        self._ids = iter(self.idiom.ids)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(is_idiom={self.is_idiom}, idiom={self.idiom})"

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


class IdiomInfo:
    __slots__ = ["state", "id", "primary_ids"]

    def __init__(self, state: IdiomState, id_: int):
        self.state: IdiomState = state
        self.id: int = id_
        self.primary_ids: set[int] = {id_}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(state={self.state}, id={self.id}, primaries={self.primary_ids})"
        )

    @property
    def efficiency(self) -> float:
        return self.state.efficiency


def extract_idioms(tree: PrefixTree, *, debug: bool = False) -> dict[frozenset[int], IdiomInfo]:
    global min_idiom_count
    global min_idiom_length

    if not tree.id_to_freq:
        return {}

    min_idiom_count = math.log2(sum(freq for i, freq in tree.id_to_freq.items()))

    idioms: dict[frozenset[int], IdiomInfo] = {}
    rejected_idioms: set[frozenset[int]] = set()
    processed_variants: list[bool] = [False] * len(tree.id_to_freq)
    efficiencies: list[tuple[float | None, frozenset[int]]] = (
            [(None, frozenset())] * len(tree.id_to_freq)
    )
    states: list[IdiomState] = []

    ids = {i for i, _ in enumerate(tree.id_to_freq)}
    total_trees = tree.trees_by_ids(ids)
    efficiency = (
        _information_from_tree(tree)
        - (tree.total_operators + total_trees + 1) * math.log2(AST_TOTAL_UNIQUE_OPERATORS)
        - (tree.total_operands + total_trees + 1) * math.log2(len(tree.operand_names) + 1)
    )
    static_state = IdiomState(Idiom(ids, tree.trees_by_ids(ids), efficiency), [tree.root])

    for variant_id, _ in enumerate(tree.id_to_freq):
        if processed_variants[variant_id]:
            continue

        possible_idiom, _ = _expand_tree(tree, static_state, 0, variant_id)
        state = IdiomState(possible_idiom, tree.root.variant_by_id(variant_id).children.copy())
        states.append(state)

        while True:
            unprocessed_idiom_id, state = _find_unprocessed_state(state, states, processed_variants)

            if not states:
                break

            idiom_id = _find_idiom_in_tree(tree, unprocessed_idiom_id, state, states, processed_variants)
            processed_variants[idiom_id] = True
            state = max(states, key=lambda st: st.efficiency)

            if not (state.idiom_length < min_idiom_length or state.efficiency < 0):
                _process_idiom(idiom_id, idioms, state, states, rejected_idioms, efficiencies)

    filtered_idioms: dict[frozenset[int], IdiomInfo] = {}
    for _, idiom_state in efficiencies:
        if idiom_state in idioms:
            filtered_idioms[idiom_state] = idioms[idiom_state]

    # todo: изменить реализацию флага debug
    if debug:
        print(f"rejected: {len(rejected_idioms):>3}")
        print(f"unfiltered: {len(idioms)}")
        print(f"filtered: {len(filtered_idioms):>3}")
        print()

    # todo: разобраться с доп. фильтрацией
    sorted_idioms = sorted(filtered_idioms.items(), key=lambda p: -1 * p[1].efficiency)
    i = 0
    while i < len(sorted_idioms) - 1:
        for j in range(len(sorted_idioms) - 1, i, -1):
            i_ids = sorted_idioms[i][0]
            j_ids = sorted_idioms[j][0]
            if i_ids.issuperset(j_ids) or j_ids.issuperset(i_ids):
                del sorted_idioms[j]
        i += 1

    filtered_idioms: dict = {}
    for si in sorted_idioms:
        filtered_idioms[si[0]] = si[1]

    return filtered_idioms


def _information_from_tree(tree: PrefixTree) -> float:
    return (
        tree.total_operators * math.log2(AST_TOTAL_UNIQUE_OPERATORS)
        + tree.total_operands * math.log2(len(tree.operand_names))
    )


def _efficiency_from_tree(tree: PrefixTree, idiom: Idiom) -> float:
    total_operators = (
        tree.total_operators
        - idiom.total_trees * idiom.total_operators
        + idiom.total_trees
        + idiom.total_operators
        + 1
    )

    total_operands = (
        tree.total_operands
        - idiom.total_trees * idiom.total_operands
        + idiom.total_trees
        + idiom.total_operands
        + 1
    )

    return _information_from_tree(tree) - (
        total_operators * math.log2(AST_TOTAL_UNIQUE_OPERATORS)
        + total_operands * math.log2(len(tree.operand_names) + 1)
    )


def _expand_tree(
    tree: PrefixTree,
    state: IdiomState,
    selected_id: int,
    variant_id: int = None,
    variant_name: str = None,
) -> tuple[Idiom, CountingType]:
    edge: PrefixNode | PrefixLeaf = state.edges[selected_id]
    possible: Idiom = Idiom()
    possible.selected = selected_id

    variant, ids, count_as = edge.variant(variant_id, variant_name)

    possible.ids = state.ids & ids
    possible.length = state.idiom_length + 1
    possible.variant = variant

    possible.total_operands = state.total_operands + int(count_as == CountingType.OPERAND)
    possible.total_operators = state.total_operators + int(count_as == CountingType.OPERATOR)
    possible.total_trees = tree.trees_by_ids(possible.ids)

    possible.efficiency = _efficiency_from_tree(tree, possible)
    possible.information = state.information - math.log2(possible.total_trees / state.total_trees)

    return possible, count_as


def _process_state(tree: PrefixTree, state: IdiomState, idiom_id: int) -> Idiom:
    global min_idiom_count

    selected = Idiom()
    selected_no_len = Idiom()

    for i, _ in enumerate(state.edges):
        possible, count_as = _expand_tree(tree, state, i, idiom_id)

        if possible.total_trees < min_idiom_count or possible.total_trees == 1:
            continue

        if possible.total_trees == state.total_trees:
            selected = possible
            break

        if selected.efficiency is None or possible.efficiency >= selected.efficiency:
            selected = possible

        if count_as == CountingType.NOT_COUNTED:
            if selected_no_len.efficiency is None or possible.efficiency >= selected_no_len.efficiency:
                selected_no_len = possible

    if selected.efficiency is None:
        return Idiom()

    if selected.efficiency >= state.efficiency:
        return selected

    if selected_no_len is not None:
        return selected_no_len

    return Idiom()


def _find_unprocessed_state(
    state: IdiomState, states: list[IdiomState], processed_variants: list[bool]
) -> tuple[int, IdiomState]:
    while True:
        idiom_id = next(state)
        if idiom_id != -1:
            if not processed_variants[idiom_id]:
                return idiom_id, state
        else:
            states.pop()
            if not states:
                return idiom_id, state
            state = states[-1]


def _find_idiom_in_tree(
    tree: PrefixTree,
    idiom_id: int,
    state: IdiomState,
    states: list[IdiomState],
    processed_variants: list[bool],
) -> int:
    while True:
        hypothesis = _process_state(tree, state, idiom_id)
        if hypothesis.selected is None:
            return idiom_id

        edges = state.edges.copy()
        edges.pop(hypothesis.selected)
        if isinstance(hypothesis.variant, SubtreeVariant):
            edges.extend(hypothesis.variant.children)

        states.append(IdiomState(hypothesis, edges))
        state = states[-1]

        idiom_id = next(state)
        while processed_variants[idiom_id]:
            idiom_id = next(state)


def _process_idiom(
    idiom_id: int,
    idioms: dict[frozenset[int], IdiomInfo],
    state: IdiomState,
    states: list[IdiomState],
    rejected_idioms: set[frozenset[int]],
    efficiencies: list[tuple[float | None, frozenset[int]]],
):
    global min_idiom_count

    idiom_state = frozenset(state.ids)

    if idiom_state in rejected_idioms:
        return

    if idiom_state in idioms:
        idioms[idiom_state].primary_ids.add(idiom_id)
        rejected_idioms.update(_reject(state, states, idioms, efficiencies))
        return

    if state.total_trees < min_idiom_count:
        rejected_idioms.update(_reject(state, states, idioms, efficiencies))
        return

    idioms[idiom_state] = IdiomInfo(state, idiom_id)
    state.is_idiom = True

    for i in idiom_state:
        efficiency, _ = efficiencies[i]
        if efficiency is None or efficiency < state.efficiency:
            efficiencies[i] = (state.efficiency, idiom_state)


def _reject(
    state: IdiomState,
    states: list[IdiomState],
    idioms: dict[frozenset[int], IdiomInfo],
    efficiencies: list[tuple[float | None, frozenset[int]]],
) -> set[frozenset[int]]:
    rejected: set[frozenset[int]] = set()
    for s in states:
        if s is state:
            break
        if s.is_idiom:
            s.is_idiom = False
            s_idiom_state = frozenset(s.ids)

            if s_idiom_state in idioms:
                idioms.pop(s_idiom_state)

            rejected.add(s_idiom_state)
            for i in s_idiom_state:
                if efficiencies[i][1] == s_idiom_state:
                    efficiencies[i] = (None, frozenset())
    return rejected
