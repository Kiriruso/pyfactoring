import ast
import copy
import pathlib

from pyfactoring import extracting
from pyfactoring.config import pyclones_settings
from pyfactoring.utils.pyclones.templater import Templater

MIN_CLONE_COUNT = pyclones_settings.count
MIN_CLONE_LENGTH = pyclones_settings.length
DEBUG_MODE = pyclones_settings.debug_mode

HANDLE_ASTS = (
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


class Clone:
    def __init__(self, node: ast.AST = None):
        self.count: int = 1
        self.instances: list[ast.AST] = []

        if node is not None:
            self.instances.append(node)


def is_handle_node(node: ast.AST) -> bool:
    return type(node).__name__ in HANDLE_ASTS


if __name__ == "__main__":
    target = pathlib.Path(__file__).parents[3] / "test" / "common" / "simple.py"
    module = extracting.extract_ast(target)
    templater = Templater()

    # поиск импортов
    imports: list[str] = []
    for ast_node in ast.walk(module):
        if isinstance(ast_node, ast.alias):
            imports.append(ast_node.asname if ast_node.asname else ast_node.name)

    templater.add_imports(imports)

    # поиск клонов
    clones: dict[str, Clone] = {}
    for ast_node in ast.walk(module):
        if is_handle_node(ast_node):
            if ast_node.end_lineno - ast_node.lineno < MIN_CLONE_LENGTH:
                continue

            dump = ast.unparse(templater.visit(copy.deepcopy(ast_node)))

            if dump in clones:
                clones[dump].count += 1
                clones[dump].instances.append(ast_node)
            else:
                clones.setdefault(dump, Clone(ast_node))

    for dump, info in clones.items():
        if info.count <= MIN_CLONE_COUNT:
            continue

        print(dump)
        print()
        for instance in info.instances:
            print(ast.unparse(instance))
            print()
        print()

# Задачи:
# 1. Реализовать алгоритм упрощения блока кода, для его анализа и поиска клонов всех типов
    # 1.1. Добавить настройку для поиска всех типов клонов или только конкретных
# 2. Определить параметры фильтрации
# 3. Создать алгоритм фильтрации по заданным параметрам
# 4. Реализовать алгоритм фильтрации входящих друг в друга блоков кода
# 5. Поиск исходных блоков, для их дальнейшей замены
