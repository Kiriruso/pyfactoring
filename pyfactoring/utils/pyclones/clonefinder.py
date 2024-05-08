import ast
import copy
import pathlib
from collections import defaultdict
from collections.abc import Collection
from dataclasses import dataclass, field

from pyfactoring.exceptions import UndefinedModeError
from pyfactoring.settings import pyclones_settings
from pyfactoring.utils.pyclones.templater import Templater
from pyfactoring.utils import extract


@dataclass
class CodeBlockClone:
    source: str = field(repr=False)
    file: pathlib.Path
    lineno: int
    end_lineno: int
    colno: int
    end_colno: int
    vars: list[str] = field(init=False, default_factory=list)
    consts: list[str] = field(init=False, default_factory=list)

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
            )
        else:
            self.allowed_nodes: tuple[str] = tuple(self.allowed_nodes)

    def find_all(
            self, filepath: pathlib.Path, *, unfiltered: bool = False
    ) -> dict[str, list[CodeBlockClone]]:
        clones: dict[str, list[CodeBlockClone]] = defaultdict(list)
        module = extract.module(filepath)
        self.templater.update_globals(module)

        for node in ast.walk(module):
            if not self._is_allowed_node(node):
                continue

            if node.end_lineno - node.lineno < pyclones_settings.length:
                continue

            clone = CodeBlockClone(
                self._get_source(node),
                filepath,
                node.lineno, node.end_lineno,
                node.col_offset, node.end_col_offset
            )

            to_template = copy.deepcopy(node)
            template = self._get_source(self.templater.visit(to_template))
            del to_template

            clone.vars, clone.consts = self.templater.pop_unique_operands()
            clones[template].append(clone)

        if unfiltered:
            return clones

        return {
            t: cs
            for t, cs in clones.items()
            if len(cs) >= pyclones_settings.count
        }

    def chained_find_all(
            self, filepaths: Collection[pathlib.Path]
    ) -> dict[str, list[CodeBlockClone]]:
        clones: dict[str, list[CodeBlockClone]] = {}
        for filepath in filepaths:
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

    @staticmethod
    def _get_source(node: ast.AST) -> str:
        match pyclones_settings.template_mode:
            case "code":
                return ast.unparse(node)
            case "tree":
                return ast.dump(node, indent=4)
            case _:
                raise UndefinedModeError(
                    f"Template extraction mode is not specified or is incorrect: "
                    f"{pyclones_settings.template_mode}"
                )
