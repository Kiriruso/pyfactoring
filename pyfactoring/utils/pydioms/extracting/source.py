import ast

from pathlib import Path
from typing import Generator

from pyfactoring.utils.pydioms.inspect.inspector import ASTInspectedNode, ASTInspectedLeaf


def extract_source(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        source: str = f.read()
    return source


def extract_ast(filepath: Path) -> ast.Module:
    return ast.parse(extract_source(filepath))


def dump_inspected_tree(
    root: ASTInspectedNode | ASTInspectedLeaf, *, indent: int = 0, subindent: int = 0
) -> Generator[str, None, None]:
    """Построчное получение строкового представления проинспектированного AST

    :param root: узел с которого начинается обход
    :param indent: базовый отступ слева
    :param subindent: дополнительный отступ слева, который добавляется к дочерним узлам
    :return: узел дерева представленный в виде строки с отступом
    """

    yield f"{' ' * indent}{root}"

    while True:
        if not isinstance(root, ASTInspectedNode):
            return
        for node in root:
            yield from dump_inspected_tree(node, indent=indent + subindent, subindent=subindent)
        return


def source_from_inspected_tree(filepath: str, root: ASTInspectedNode) -> Generator[str, None, None]:
    """Поиск частей исходного кода, соответствующих узлам проинспектированного AST,
    реализующего поддеревья, например: For, ...

    :param filepath: путь к файлу с исходным кодом
    :param root: узел с которого начинается поиск
    :return: часть исходного кода соответствующая узлу, реализующему поддеревья
    """
    with open(filepath, "r", encoding="utf-8") as code:
        source = code.read()

    def source_from_(root_: ASTInspectedNode | ASTInspectedLeaf) -> Generator[str, None, None]:
        nonlocal source

        while True:
            if isinstance(root_, ASTInspectedNode) and root_.realize_subtree:
                yield ast.get_source_segment(source, root_.ast)
                return
            if isinstance(root_, ASTInspectedNode):
                for node in root_:
                    yield from source_from_(node)
            return

    yield from source_from_(root)


# todo: реализовать или удалить функции
def walk_prefix_tree():
    raise NotImplementedError


def source_from_prefix_tree():
    raise NotImplementedError
