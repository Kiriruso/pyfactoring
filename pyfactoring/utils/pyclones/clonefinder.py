import ast
import copy
import pathlib

from dataclasses import dataclass, field

from pyfactoring.settings import pyclones_settings
from pyfactoring.exceptions import UndefinedModeError
from pyfactoring.utils.pydioms import extracting
from pyfactoring.utils.pyclones.templater import Templater

MIN_CLONE_COUNT = pyclones_settings.count
MIN_CLONE_LENGTH = pyclones_settings.length
DEBUG_MODE = pyclones_settings.debug_mode

ALLOWED_NODES = (
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


@dataclass(frozen=True)
class CodeBlockClone:
    source: str = field(repr=False)
    lineno: int
    end_lineno: int
    colno: int
    end_colno: int


class CloneFinder:
    def __init__(self):
        self._templater: Templater = Templater()

    def find_all(self, root: ast.AST) -> dict[str, list[CodeBlockClone]]:
        global MIN_CLONE_LENGTH, MIN_CLONE_COUNT
        clones: dict[str, list[CodeBlockClone]] = {}

        for node in ast.walk(root):
            if isinstance(node, ast.Module):
                self._templater.find_all_imports(node)
                continue

            if not self._is_allowed_node(node):
                continue

            if node.end_lineno - node.lineno < MIN_CLONE_LENGTH:
                continue

            clone = CodeBlockClone(
                self._get_source(node),
                node.lineno, node.end_lineno,
                node.col_offset, node.end_col_offset
            )

            to_template = copy.deepcopy(node)
            template = self._get_source(self._templater.visit(to_template))
            del to_template

            if template not in clones:
                clones.setdefault(template, [])
            clones[template].append(clone)

        return {t: cs for t, cs in clones.items() if len(cs) >= MIN_CLONE_COUNT}

    @staticmethod
    def _get_source(node: ast.AST) -> str:
        global DEBUG_MODE

        match DEBUG_MODE:
            case "code":
                return ast.unparse(node)
            case "tree":
                return ast.dump(node, indent=4)
            case _:
                raise UndefinedModeError(
                    f"Режим извлечения шаблона не задан или некорректен: {DEBUG_MODE}"
                )

    @staticmethod
    def _is_allowed_node(node: ast.AST):
        global ALLOWED_NODES
        return type(node).__name__ in ALLOWED_NODES


def main():
    target = pathlib.Path(__file__).parents[3] / "test" / "common" / "test_all.py"
    module = extracting.extract_ast(target)
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
