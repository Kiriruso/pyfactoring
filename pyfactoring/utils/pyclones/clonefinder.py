import ast
import copy
from collections import defaultdict
from collections.abc import Collection
from dataclasses import dataclass, field
from pathlib import Path

from pyfactoring.settings import pyclones_settings
from pyfactoring.utils import extract
from pyfactoring.utils.pyclones.templater import Templater


@dataclass
class CodeBlockClone:
    file: Path
    lineno: int
    end_lineno: int
    colno: int
    end_colno: int
    source: str = field(repr=False, kw_only=True)
    class_name: str = field(default=None, kw_only=True)
    vars: list[str] = field(default_factory=list, kw_only=True)
    consts: list[str] = field(default_factory=list, kw_only=True)

    @property
    def link(self) -> str:
        return f"{self.file}:{self.lineno}:{self.colno}"


@dataclass
class CloneFinder:
    allowed_nodes: Collection[str] = field(default=None)
    templater: Templater = field(default_factory=Templater)

    def __post_init__(self):
        if self.allowed_nodes is None:
            self.allowed_nodes: tuple[str] = (
                "If",
                "While",
                "For",
                "AsyncFor",
                "With",
                "AsyncWith",
                "FunctionDef",
                "AsyncFunctionDef",
                "Try",
                "TryStar",
                "Match",
                "ClassDef",
            )
        else:
            self.allowed_nodes: tuple[str] = tuple(self.allowed_nodes)

    def find_all(
            self, path: Path, *, unfiltered: bool = False,
    ) -> dict[str, list[CodeBlockClone]]:
        clones: dict[str, list[CodeBlockClone]] = defaultdict(list)
        module = extract.module(path)
        self.templater.update_globals(module)

        for node in ast.walk(module):
            if not self._is_allowed_node(node):
                continue

            if isinstance(node, ast.ClassDef):
                for stmt in node.body:
                    stmt.class_name = node.name
                continue

            if node.end_lineno - node.lineno < pyclones_settings.length:
                continue

            to_template = copy.deepcopy(node)
            to_template = self.templater.visit(to_template)

            class_name = to_template.in_class if hasattr(to_template, "class_name") else None
            variables, consts = self.templater.pop_unique_operands()

            template = extract.stmt_source(to_template)
            clone = CodeBlockClone(
                path, node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                source=extract.stmt_source(node),
                class_name=class_name,
                vars=variables,
                consts=consts,
            )
            clones[template].append(clone)

            del to_template

        if unfiltered:
            return clones

        return {
            t: cs
            for t, cs in clones.items()
            if len(cs) >= pyclones_settings.count
        }

    def chained_find_all(
            self, path: Collection[Path],
    ) -> dict[str, list[CodeBlockClone]]:
        clones: dict[str, list[CodeBlockClone]] = {}
        for filepath in path:
            current_clones = self.find_all(filepath, unfiltered=True)
            for template, blocks in current_clones.items():
                if template not in clones.keys():
                    clones[template] = blocks
                else:
                    clones[template].extend(blocks)

        return {
            t: cs
            for t, cs in clones.items()
            if len(cs) >= pyclones_settings.count
        }

    def _is_allowed_node(self, node: ast.AST):
        return type(node).__name__ in self.allowed_nodes
