import ast
import copy
import pathlib
from collections.abc import Collection
from dataclasses import dataclass, field

from pyfactoring.exceptions import UndefinedModeError
from pyfactoring.settings import pyclones_settings
from pyfactoring.utils.pyclones.templater import Templater
from pyfactoring.utils.extracting import extract_ast


@dataclass(frozen=True)
class CodeBlockClone:
    source: str = field(repr=False)
    lineno: int
    end_lineno: int
    colno: int
    end_colno: int


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

    def find_all(self, root: ast.AST) -> dict[str, list[CodeBlockClone]]:
        clones: dict[str, list[CodeBlockClone]] = {}

        for node in ast.walk(root):
            if isinstance(node, ast.Module):
                self.templater.find_all_imports(node)
                continue

            if not self._is_allowed_node(node):
                continue

            if node.end_lineno - node.lineno < pyclones_settings.length:
                continue

            clone = CodeBlockClone(
                self._get_source(node),
                node.lineno, node.end_lineno,
                node.col_offset, node.end_col_offset
            )

            to_template = copy.deepcopy(node)
            template = self._get_source(self.templater.visit(to_template))
            del to_template

            if template not in clones:
                clones.setdefault(template, [])
            clones[template].append(clone)

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


def main():
    target = pathlib.Path(__file__).parents[3] / "test" / "common" / "test_all.py"
    module = extract_ast(target)
    finder = CloneFinder()

    for template, clones in finder.find_all(module).items():
        print(template, end='\n\n')
        for clone in clones:
            print(clone.source, end='\n\n')
        print()


if __name__ == "__main__":
    main()

# Задачи:
# 1. Реализовать алгоритм упрощения блока кода, для его анализа и поиска клонов всех типов
    # 1.1. Добавить настройку для поиска всех типов клонов или только конкретных
# 2. Определить параметры фильтрации
# 3. Создать алгоритм фильтрации по заданным параметрам
# 4. Реализовать алгоритм фильтрации входящих друг в друга блоков кода
# 5. Поиск исходных блоков, для их дальнейшей замены
