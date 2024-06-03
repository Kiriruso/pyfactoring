import ast
from collections.abc import Generator
from dataclasses import dataclass, field
from pathlib import Path

from pyfactoring.utils.pydioms.ast_types import (
    AST_NODES_INFO,
    AST_PRESENTATION_LEAVES,
    AST_REALIZE_SUBTREE_NODES,
    AST_SPECIFIC_NODES,
    CountingType,
)


@dataclass
class ASTInspectedLeaf:
    name: str = field(default="None")
    count_as: CountingType = field(default=CountingType.NOT_COUNTED)

    nodes: int = field(default=1, init=False, repr=False)
    total_operands: int = field(default=0, init=False, repr=False)
    total_operators: int = field(default=0, init=False, repr=False)
    ast_node: ast.AST = field(default=None, init=False, repr=False)
    file: str = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.total_operands = int(self.count_as == CountingType.OPERAND)
        self.total_operators = int(self.count_as == CountingType.OPERATOR)

    def is_operand(self) -> bool:
        return self.count_as == CountingType.OPERAND


@dataclass
class ASTInspectedNode(ASTInspectedLeaf):
    """"""

    realize_subtree: bool = field(default=False, init=False, repr=False)
    children: list["ASTInspectedNode | ASTInspectedLeaf"] = field(
        default_factory=list, init=False, repr=False,
    )

    def __iter__(self):
        return iter(self.children)

    def append(self, inspect_node: ASTInspectedLeaf):
        self.children.append(inspect_node)
        self.nodes += inspect_node.nodes
        self.total_operators += inspect_node.total_operators
        self.total_operands += inspect_node.total_operands


def dump_inspected_tree(
    root: ASTInspectedNode | ASTInspectedLeaf, *, indent: int = 0, subindent: int = 0,
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


def source_from_inspected_tree(
        filepath: str | Path, root: ASTInspectedNode,
) -> Generator[str, None, None]:
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
                yield ast.get_source_segment(source, root_.ast_node)
                return
            if isinstance(root_, ASTInspectedNode):
                for node in root_:
                    yield from source_from_(node)
            return

    yield from source_from_(root)


def make_inspected_tree(root, filepath) -> ASTInspectedNode | ASTInspectedLeaf:
    """
    :param root:
    :param filepath
    :return:
    """

    if not root:
        return ASTInspectedNode()

    if not isinstance(root, ast.AST):
        leaf_name = root
        return ASTInspectedLeaf(leaf_name, CountingType.OPERAND)

    if type(root) in AST_SPECIFIC_NODES:
        return _make_specific(root, filepath)

    ast_name, ast_body = _info_from_ast(root)
    ast_info = AST_NODES_INFO.get(ast_name)

    if ast_info is None:
        return ASTInspectedNode()

    inspected_node = ASTInspectedNode(ast_info.name, ast_info.count_as)
    inspected_node.realize_subtree = ast_info.name in AST_REALIZE_SUBTREE_NODES
    inspected_node.ast_node = root
    inspected_node.file = filepath

    for ast_child_name in ast_info.children_names:
        ast_child_children = ast_body.get(ast_child_name)

        if isinstance(ast_child_children, list):
            child_realize_subtree = inspected_node.realize_subtree
            child_realize_subtree &= ast_child_name in ("body", "orelse", "finalbody")

            inspected_list = []
            for ast_child_child in ast_child_children:
                inspected_child_child = make_inspected_tree(ast_child_child, filepath)
                inspected_child_child.realize_subtree |= child_realize_subtree
                inspected_child_child.ast_node = ast_child_child

                inspected_list.append(inspected_child_child)
            inspected_list = _make_list(inspected_list)

            inspected_node.append(inspected_list)
            continue

        if (
            ast_child_children is None
            and AST_PRESENTATION_LEAVES.get(inspected_node.name) == ast_child_name
        ):
            inspected_node.append(ASTInspectedLeaf())
            continue

        inspected_node.append(make_inspected_tree(ast_child_children, filepath))

    return inspected_node


def _info_from_ast(root: ast.AST) -> tuple[str, dict]:
    return root.__class__.__name__, root.__dict__


def _make_list(inspected_nodes: list[ASTInspectedNode]) -> ASTInspectedNode:
    if len(inspected_nodes) == 0:
        return ASTInspectedNode()

    if len(inspected_nodes) == 1:
        return inspected_nodes[0]

    sublist = ASTInspectedNode("LIST")
    sublist.append(inspected_nodes[-2])
    sublist.append(inspected_nodes[-1])

    index_of_end = len(inspected_nodes) + 1
    for i in range(-3, -index_of_end, -1):
        toplist = ASTInspectedNode("LIST")
        toplist.append(inspected_nodes[i])
        toplist.append(sublist)
        sublist = toplist
    return sublist


def _make_specific(root, filepath) -> ASTInspectedNode:
    match type(root):
        case ast.Dict | ast.Compare:
            return _make_dict_or_compare(root, filepath)
        case ast.Global | ast.Nonlocal:
            return _make_global_or_nonlocal(root)
        case ast.Constant:
            return _make_constant(root)
        case ast.comprehension:
            return _make_comprehension(root, filepath)
        case ast.arguments:
            return _make_arguments(root, filepath)


def _make_dict_or_compare(root: ast.Dict | ast.Compare, filepath: str) -> ASTInspectedNode:
    is_dict = isinstance(root, ast.Dict)
    node_name, pair_name = ("Dict", "DICT_PAIR") if is_dict else ("Compare", "COMP_PAIR")
    keys_or_ops, values_or_comparators = (
        (root.keys, root.values) if is_dict else (root.ops, root.comparators)
    )
    count_as = CountingType.OPERATOR if is_dict else CountingType.NOT_COUNTED

    inspected = ASTInspectedNode(node_name, count_as)
    if not is_dict:
        inspected.append(make_inspected_tree(root.left, filepath))

    inspected_pairs = []
    for key, value in zip(keys_or_ops, values_or_comparators):
        inspected_pair = ASTInspectedNode(pair_name)
        inspected_pair.append(make_inspected_tree(key, filepath))
        inspected_pair.append(make_inspected_tree(value, filepath))
        inspected_pairs.append(inspected_pair)

    inspected.append(_make_list(inspected_pairs))
    return inspected


def _make_global_or_nonlocal(root: ast.Global | ast.Nonlocal) -> ASTInspectedNode:
    node_name = "Global" if isinstance(root, ast.Global) else "Nonlocal"
    inspected = ASTInspectedNode(node_name, CountingType.OPERATOR)

    inspected_names = []
    for name in root.names:
        inspected_name = ASTInspectedNode("NAME")
        inspected_name.append(ASTInspectedLeaf(name, CountingType.OPERAND))
        inspected_names.append(inspected_name)

    inspected.append(_make_list(inspected_names))
    return inspected


def _make_constant(root: ast.Constant) -> ASTInspectedNode:
    type_ = type(root.value).__name__

    if type_ == "ellipsis":
        return ASTInspectedNode("Ellipsis", CountingType.OPERATOR)

    if type_ == "NoneType":
        return ASTInspectedNode("NoneConst", CountingType.OPERAND)

    type_formatting_functions = {
        "str": lambda t: str(t).capitalize(),
        "bool": lambda t: str(t).capitalize(),
        "bytes": lambda t: str(t).capitalize(),
        "int": lambda t: "Num",
        "float": lambda t: "Num",
        "complex": lambda t: "Num",
    }

    format_ = type_formatting_functions.get(type_)
    inspected = ASTInspectedNode(format_(type_))
    inspected.append(ASTInspectedLeaf(root.value, CountingType.OPERAND))

    return inspected


def _make_comprehension(root: ast.comprehension, filepath: str) -> ASTInspectedNode:
    name = "AsyncComprehension" if root.is_async else "comprehension"
    inspected = ASTInspectedNode(name, CountingType.OPERATOR)
    inspected.append(make_inspected_tree(root.target, filepath))
    inspected.append(make_inspected_tree(root.iter, filepath))

    inspected_ifs = ASTInspectedNode()
    if len(root.ifs) == 1:
        inspected_ifs = make_inspected_tree(root.ifs[0], filepath)
    inspected.append(inspected_ifs)

    return inspected


def _make_args(
    posonly: list[ast.arg], other: list[ast.arg], defaults: list[ast.expr], filepath: str,
) -> tuple[list[ASTInspectedNode], list[ASTInspectedNode]]:
    it = len(defaults) - len(posonly) - len(other)

    def internal_make(arguments: list[ast.arg]) -> list[ASTInspectedNode]:
        nonlocal it, defaults, filepath
        inspected_args = []
        for arg in arguments:
            inspected_arg = ASTInspectedNode("arg")
            inspected_arg.append(make_inspected_tree(arg.arg, filepath))
            inspected_arg.append(make_inspected_tree(arg.annotation, filepath))

            if it < 0:
                inspected_arg.append(ASTInspectedNode())
            else:
                inspected_arg.append(make_inspected_tree(defaults[it], filepath))

            inspected_args.append(inspected_arg)
            it += 1
        return inspected_args

    return internal_make(posonly), internal_make(other)


def _make_kwargs(
        vararg: ast.arg, kwarg: ast.arg, filepath: str,
) -> tuple[ASTInspectedNode, ASTInspectedNode]:
    def internal_make(arg: ast.arg) -> ASTInspectedNode:
        if arg is None:
            return ASTInspectedNode()
        inspected_arg = ASTInspectedNode("sarg")
        inspected_arg.append(make_inspected_tree(arg.arg, filepath))
        inspected_arg.append(make_inspected_tree(arg.annotation, filepath))
        return inspected_arg

    return internal_make(vararg), internal_make(kwarg)


def _make_arguments(root: ast.arguments, filepath: str) -> ASTInspectedNode:
    inspected_arguments = ASTInspectedNode("arguments")

    posonlyargs, args = _make_args(root.posonlyargs, root.args, root.defaults, filepath)
    kwonlyargs = []
    for i, kwonlyarg in enumerate(root.kwonlyargs):
        inspected_arg = ASTInspectedNode("arg")
        inspected_arg.append(make_inspected_tree(kwonlyarg.arg, filepath))
        inspected_arg.append(make_inspected_tree(kwonlyarg.annotation, filepath))
        inspected_arg.append(make_inspected_tree(root.kw_defaults[i], filepath))
        kwonlyargs.append(inspected_arg)
    vararg, kwarg = _make_kwargs(root.vararg, root.kwarg, filepath)

    inspected_arguments.append(_make_list(posonlyargs))
    inspected_arguments.append(_make_list(args))
    inspected_arguments.append(vararg)
    inspected_arguments.append(_make_list(kwonlyargs))
    inspected_arguments.append(kwarg)

    return inspected_arguments
