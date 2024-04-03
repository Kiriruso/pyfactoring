import ast

from pathlib import Path
from typing import Generator

from pyfactoring.utils.pydioms.inspect.inspector import ASTInspectedNode, ASTInspectedLeaf


def extract_ast(filepath: Path, *, return_source: bool = False) -> ast.Module | tuple[ast.Module, str]:
    # todo: назначение функции
    """

    :param filepath:
    :param return_source:
    :return:
    """

    with open(filepath, 'r', encoding='utf-8') as f:
        source: str = f.read()

    if return_source:
        return ast.parse(source), source
    else:
        return ast.parse(source)


def dump_inspected_tree(
        root: ASTInspectedNode | ASTInspectedLeaf,
        *,
        indent: int = 0,
        subindent: int = 0
) -> Generator[str, None, None]:
    """ Построчное получение строкового представления проинспектированного AST

    :param root: узел с которого начинается обход
    :param indent: базовый отступ слева
    :param subindent: дополнительный отступ слева, который добавляется к дочерним узлам
    :return: узел дерева представленный в виде строки с отступом
    """

    yield f"{" " * indent}{root}"

    while True:
        if not isinstance(root, ASTInspectedNode):
            return

        for node in root:
            yield from dump_inspected_tree(node, indent=indent + subindent, subindent=subindent)

        return


def source_from_inspected_tree(filepath: str, root: ASTInspectedNode) -> Generator[str, None, None]:
    """ Поиск частей исходного кода, соответствующих узлам проинспектированного AST,
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
