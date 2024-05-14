import ast
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from pyfactoring.utils import extract
from pyfactoring.utils.pydioms.ast_inspect import (
    ASTInspectedLeaf,
    ASTInspectedNode,
    make_inspected_tree,
)
from pyfactoring.utils.pydioms.ast_types import CountingType


def make_prefix_trees(filepaths: Iterable[str | Path]) -> list["PrefixTree"]:
    prefix_trees = []
    for filepath in filepaths:
        prefix_tree = PrefixTree()
        prefix_tree.add_tree(filepath)
        prefix_trees.append(prefix_tree)
    return prefix_trees


@dataclass
class SubtreeVariant:
    ast_variants: set[ast.AST] = field(default_factory=set)
    count_as: CountingType = field(default=CountingType.NOT_COUNTED)
    ids: set[int] = field(default_factory=set, init=False, repr=False)
    children: list["PrefixNode | PrefixLeaf"] = field(default_factory=list, init=False, repr=False)

    def add_id(self, subtree_id: int):
        self.ids.add(subtree_id)

    def add_node(self, prefix_node_or_leaf: "PrefixNode | PrefixLeaf"):
        self.children.append(prefix_node_or_leaf)


@dataclass
class PrefixLeaf:
    value_to_ids: dict[str, set[int]] = field(default_factory=dict, init=False, repr=False)
    id_to_values: dict[int, tuple[str, CountingType]] = field(
        default_factory=dict, init=False, repr=False,
    )

    def add_subtree(self, inspected_leaf: ASTInspectedLeaf, subtree_id: int):
        self.value_to_ids.setdefault(inspected_leaf.name, set())
        self.value_to_ids[inspected_leaf.name].add(subtree_id)
        self.id_to_values[subtree_id] = (inspected_leaf.name, inspected_leaf.count_as)

    def variant(
        self, id_: int | None, name_: str | None,
    ) -> tuple[SubtreeVariant | None, set[int], CountingType]:
        if id_ is not None:
            name = self.id_to_values.get(id_)[0]
            ids = self.value_to_ids.get(name)
        elif name_ is not None:
            ids = self.value_to_ids.get(name_)
        else:
            raise ValueError(f"Expected value: id_ or name_. Received: {id_=}, {name_=}")
        return None, ids, CountingType.OPERAND


@dataclass
class PrefixNode:
    name_to_variants: dict[str, SubtreeVariant] = field(default_factory=dict, init=False, repr=False)
    id_to_node_name: dict[int, str] = field(default_factory=dict, init=False, repr=False)

    def add_subtree(self, subtree_root: ASTInspectedNode, subtree_id: int):
        variant = self.variant_by_name(subtree_root.name)

        if variant is None:
            variant = self._returning_variant_insert(subtree_root)
            for inspected_node_or_leaf in subtree_root.children:
                if isinstance(inspected_node_or_leaf, ASTInspectedNode):
                    variant.add_node(PrefixNode())
                else:
                    variant.add_node(PrefixLeaf())

        variant.add_id(subtree_id)
        self.id_to_node_name[subtree_id] = subtree_root.name

        for prefix_node_or_leaf, inspected_node_or_leaf in zip(variant.children, subtree_root.children):
            prefix_node_or_leaf.add_subtree(inspected_node_or_leaf, subtree_id)

    def variant(
        self, id_: int | None, name_: str | None,
    ) -> tuple[SubtreeVariant | None, set[int], CountingType]:
        if id_ is not None:
            variant = self.variant_by_id(id_)
        elif name_ is not None:
            variant = self.variant_by_name(name_)
        else:
            raise ValueError(f"Expected value: id_ or name_. Received: {id_=}, {name_=}")
        return variant, variant.ids, variant.count_as

    def variant_by_id(self, id_: int) -> SubtreeVariant:
        if id_ not in self.id_to_node_name:
            return SubtreeVariant()
        name = self.id_to_node_name.get(id_)
        return self.name_to_variants.get(name)

    def variant_by_name(self, name_: str) -> SubtreeVariant | None:
        return self.name_to_variants.get(name_)

    def _returning_variant_insert(
        self, subtree_root: ASTInspectedNode | ASTInspectedLeaf,
    ) -> SubtreeVariant:
        variant = SubtreeVariant(subtree_root.ast_node, subtree_root.count_as)
        self.name_to_variants[subtree_root.name] = variant
        return variant


@dataclass
class PrefixTree:
    filepaths: Iterable[str | Path] = field(default_factory=list)

    total_operands: int = field(default=0, init=False)
    total_operators: int = field(default=0, init=False)

    root: PrefixNode = field(default_factory=PrefixNode, init=False, repr=False)
    total_leafs: int = field(default=0, init=False, repr=False)
    id_to_freq: dict[int, int] = field(default_factory=dict, init=False, repr=False)
    operand_names: set[str] = field(default_factory=set, init=False, repr=False)
    inspected_trees: dict[int, ASTInspectedNode] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        for filepath in self.filepaths:
            self.add_tree(filepath)

    def add_tree(self, filepath: str | Path):
        module = extract.module(filepath)
        if isinstance(filepath, str):
            self.add_ast_obj(module, Path(filepath))
        else:
            self.add_ast_obj(module, filepath)

    def add_inspected_tree(self, root: ASTInspectedNode):
        self.total_operands += root.total_operands
        self.total_operators += root.total_operators
        self._add_tree(root)

    def add_ast_obj(self, root: ast.AST, filepath: Path):
        inspected_tree = make_inspected_tree(root, filepath)
        self.add_inspected_tree(inspected_tree)

    def _add_name(self, operand_name: str):
        self.operand_names.add(operand_name)

    def _add_subtree(self, subtree: ASTInspectedNode | ASTInspectedLeaf, subtree_id: int):
        self.root.add_subtree(subtree, subtree_id)

    def _add_tree(self, inspected_root: ASTInspectedNode | ASTInspectedLeaf):
        if not isinstance(inspected_root, ASTInspectedNode):
            if inspected_root.is_operand():
                self._add_name(inspected_root.name)
            return

        if inspected_root.realize_subtree:
            subtree_id = self._contains(inspected_root)

            if subtree_id is not None:
                self.id_to_freq[subtree_id] += 1
            else:
                new_subtree_id = len(self.id_to_freq)
                self._add_subtree(inspected_root, new_subtree_id)
                self.inspected_trees[new_subtree_id] = inspected_root
                self.id_to_freq[new_subtree_id] = 1

        for child in inspected_root.children:
            self._add_tree(child)

        self.total_leafs += 1

    def _contains(self, inspected_root: ASTInspectedNode | ASTInspectedLeaf) -> int | None:
        ids = self._contains_inspected_tree(self.root, inspected_root)
        return None if not ids else list(ids)[0]

    @classmethod
    def _contains_node(
        cls, prefix_root: PrefixNode, inspected_node: ASTInspectedNode, rset: set | None,
    ) -> set:
        if inspected_node.name not in prefix_root.name_to_variants:
            return set()

        variant = prefix_root.name_to_variants[inspected_node.name]
        rset = variant.ids if rset is None else rset & variant.ids
        if not rset:
            return set()

        for v, i in zip(variant.children, inspected_node.children):
            rset = cls._contains_inspected_tree(v, i, rset)
            if not rset:
                return set()

        return rset

    @classmethod
    def _contains_leaf(cls, value_to_ids: dict, leaf_name: str, rset: set | None) -> set:
        if leaf_name not in value_to_ids:
            return set()

        ids = value_to_ids[leaf_name]
        if rset is None:
            return ids

        return ids & rset

    @classmethod
    def _contains_inspected_tree(
        cls,
        prefix_root: PrefixNode | PrefixLeaf,
        inspected_root: ASTInspectedNode | ASTInspectedLeaf,
        rset: set | None = None,
    ) -> set:
        is_prefix_node = isinstance(prefix_root, PrefixNode)
        is_inspected_node = isinstance(inspected_root, ASTInspectedNode)

        # leaf and node
        if not is_prefix_node and is_inspected_node:
            return set()

        # node and leaf
        if is_prefix_node and not is_inspected_node:
            return set()

        # (node and node) or (leaf and leaf)
        if is_prefix_node and is_inspected_node:
            return cls._contains_node(prefix_root, inspected_root, rset)
        else:
            return cls._contains_leaf(prefix_root.value_to_ids, inspected_root.name, rset)

    def trees_by_ids(self, ids: set[int]) -> int:
        return sum(self.id_to_freq[i] for i in ids)
