# todo: добавить __all__

import ast
import warnings

from pyfactoring.utils.pydioms.inspect.types import (
    CountingType,
    AST_NODES_INFO,
    AST_SPECIFIC_NODES,
    AST_REALIZE_SUBTREE_NODES,
    AST_PRESENTATION_LEAVES
)


class ASTInspectedLeaf:
    # todo: написать назначение класса
    """"""

    __slots__ = ["name", "count_as", "nodes", "total_operands", "total_operators", "ast"]

    def __init__(self, name: str = "None", count_as: CountingType = CountingType.NOT_COUNTED):
        self.name: str = name
        self.count_as: CountingType = count_as
        self.nodes: int = 1
        self.total_operands: int = int(self.count_as == CountingType.OPERAND)
        self.total_operators: int = int(self.count_as == CountingType.OPERATOR)
        self.ast: ast.AST | None = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name}, count_as={self.count_as.name})'

    def is_operand(self) -> bool:
        return self.count_as == CountingType.OPERAND


class ASTInspectedNode(ASTInspectedLeaf):
    # todo: написать назначение класса
    """"""

    __slots__ = ["realize_subtree", "children"]

    def __init__(self, name: str = "None", count_as: CountingType = CountingType.NOT_COUNTED):
        super().__init__(name, count_as)
        self.realize_subtree: bool = False
        self.children: list[ASTInspectedNode | ASTInspectedLeaf] = list()

    def __iter__(self):
        return iter(self.children)

    def append(self, inspect_node: ASTInspectedLeaf):
        self.children.append(inspect_node)
        self.nodes += inspect_node.nodes
        self.total_operators += inspect_node.total_operators
        self.total_operands += inspect_node.total_operands


# todo: подумать над тем, чтобы разбить класс на отдельные функции
class ASTInspector:
    # todo: написать назначение класса
    """"""

    @classmethod
    def make_inspected_tree(cls, root: ast.AST | ast.expr | str) -> ASTInspectedNode | ASTInspectedLeaf:
        if not root:
            return ASTInspectedNode()

        if not isinstance(root, ast.AST):
            leaf_name = root
            return ASTInspectedLeaf(leaf_name, CountingType.OPERAND)

        if type(root) in AST_SPECIFIC_NODES:
            return cls._make_specific(root)

        ast_name, ast_body = cls._info_from_ast(root)

        # todo: удалить, когда будет реализована корректная обработка match case
        if ast_name == "Match":
            warnings.warn("Match Case пока не поддерживается.")
            return ASTInspectedNode()

        ast_info = AST_NODES_INFO.get(ast_name)

        inspected_node = ASTInspectedNode(ast_info.name, ast_info.count_as)
        inspected_node.realize_subtree = ast_info.name in AST_REALIZE_SUBTREE_NODES
        inspected_node.ast = root

        for ast_child_name in ast_info.children_names:
            ast_child_children = ast_body.get(ast_child_name)

            if isinstance(ast_child_children, list):
                child_realize_subtree = inspected_node.realize_subtree
                child_realize_subtree &= ast_child_name in ("body", "orelse", "finalbody")

                inspected_list = []
                for ast_child_child in ast_child_children:
                    inspected_child_child = cls.make_inspected_tree(ast_child_child)
                    inspected_child_child.realize_subtree |= child_realize_subtree
                    inspected_child_child.ast = ast_child_child

                    inspected_list.append(inspected_child_child)
                inspected_list = cls._make_list(inspected_list)

                inspected_node.append(inspected_list)
                continue

            if ast_child_children is None and AST_PRESENTATION_LEAVES.get(inspected_node.name) == ast_child_name:
                inspected_node.append(ASTInspectedLeaf())
                continue

            inspected_node.append(cls.make_inspected_tree(ast_child_children))

        return inspected_node

    @classmethod
    def _info_from_ast(cls, root: ast.AST) -> tuple[str, dict]:
        return root.__class__.__name__, root.__dict__

    @classmethod
    def _make_list(cls, inspected_nodes: list[ASTInspectedNode]) -> ASTInspectedNode:
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

    @classmethod
    def _make_specific(cls, root) -> ASTInspectedNode:
        match type(root):
            case ast.Dict | ast.Compare:
                return cls._make_dict_or_compare(root)
            case ast.Global | ast.Nonlocal:
                return cls._make_global_or_nonlocal(root)
            case ast.Constant:
                return cls._make_constant(root)
            case ast.comprehension:
                return cls._make_comprehension(root)
            case ast.arguments:
                return cls._make_arguments(root)

    @classmethod
    def _make_dict_or_compare(cls, root: ast.Dict | ast.Compare) -> ASTInspectedNode:
        is_dict = isinstance(root, ast.Dict)
        node_name, pair_name = ("Dict", "DICT_PAIR") if is_dict else ("Compare", "COMP_PAIR")
        keys_or_ops, values_or_comparators = (root.keys, root.values) if is_dict else (root.ops, root.comparators)
        count_as = CountingType.OPERATOR if is_dict else CountingType.NOT_COUNTED

        inspected = ASTInspectedNode(node_name, count_as)
        if not is_dict:
            inspected.append(cls.make_inspected_tree(root.left))

        inspected_pairs = []
        for key, value in zip(keys_or_ops, values_or_comparators):
            inspected_pair = ASTInspectedNode(pair_name)
            inspected_pair.append(cls.make_inspected_tree(key))
            inspected_pair.append(cls.make_inspected_tree(value))
            inspected_pairs.append(inspected_pair)

        inspected.append(cls._make_list(inspected_pairs))
        return inspected

    @classmethod
    def _make_global_or_nonlocal(cls, root: ast.Global | ast.Nonlocal) -> ASTInspectedNode:
        node_name = 'Global' if isinstance(root, ast.Global) else 'Nonlocal'
        inspected = ASTInspectedNode(node_name, CountingType.OPERATOR)

        inspected_names = []
        for name in root.names:
            inspected_name = ASTInspectedNode("NAME")
            inspected_name.append(ASTInspectedLeaf(name, CountingType.OPERAND))
            inspected_names.append(inspected_name)

        inspected.append(cls._make_list(inspected_names))
        return inspected

    @classmethod
    def _make_constant(cls, root: ast.Constant) -> ASTInspectedNode:
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

    @classmethod
    def _make_comprehension(cls, root: ast.comprehension) -> ASTInspectedNode:
        name = "AsyncComprehension" if root.is_async else "comprehension"
        inspected = ASTInspectedNode(name, CountingType.OPERATOR)
        inspected.append(cls.make_inspected_tree(root.target))
        inspected.append(cls.make_inspected_tree(root.iter))

        inspected_ifs = ASTInspectedNode()
        if len(root.ifs) == 1:
            inspected_ifs = cls.make_inspected_tree(root.ifs[0])
        inspected.append(inspected_ifs)

        return inspected

    @classmethod
    def _make_args(
            cls,
            posonly: list[ast.arg],
            other: list[ast.arg],
            defaults: list[ast.expr]
    ) -> tuple[list[ASTInspectedNode], list[ASTInspectedNode]]:
        it = len(defaults) - len(posonly) - len(other)

        def internal_make(arguments: list[ast.arg]) -> list[ASTInspectedNode]:
            nonlocal cls, it, defaults
            inspected_args = []
            for arg in arguments:
                inspected_arg = ASTInspectedNode("arg")
                inspected_arg.append(cls.make_inspected_tree(arg.arg))
                inspected_arg.append(cls.make_inspected_tree(arg.annotation))

                if it < 0:
                    inspected_arg.append(ASTInspectedNode())
                else:
                    inspected_arg.append(cls.make_inspected_tree(defaults[it]))

                inspected_args.append(inspected_arg)
                it += 1
            return inspected_args

        return internal_make(posonly), internal_make(other)

    @classmethod
    def _make_kwargs(cls, vararg: ast.arg, kwarg: ast.arg) -> tuple[ASTInspectedNode, ASTInspectedNode]:
        def internal_make(arg: ast.arg) -> ASTInspectedNode:
            nonlocal cls
            if arg is None:
                return ASTInspectedNode()
            inspected_arg = ASTInspectedNode("sarg")
            inspected_arg.append(cls.make_inspected_tree(arg.arg))
            inspected_arg.append(cls.make_inspected_tree(arg.annotation))
            return inspected_arg

        return internal_make(vararg), internal_make(kwarg)

    @classmethod
    def _make_arguments(cls, root: ast.arguments) -> ASTInspectedNode:
        inspected_arguments = ASTInspectedNode("arguments")

        posonlyargs, args = cls._make_args(root.posonlyargs, root.args, root.defaults)
        kwonlyargs = []
        for i, kwonlyarg in enumerate(root.kwonlyargs):
            inspected_arg = ASTInspectedNode("arg")
            inspected_arg.append(cls.make_inspected_tree(kwonlyarg.arg))
            inspected_arg.append(cls.make_inspected_tree(kwonlyarg.annotation))
            inspected_arg.append(cls.make_inspected_tree(root.kw_defaults[i]))
            kwonlyargs.append(inspected_arg)
        vararg, kwarg = cls._make_kwargs(root.vararg, root.kwarg)

        inspected_arguments.append(cls._make_list(posonlyargs))
        inspected_arguments.append(cls._make_list(args))
        inspected_arguments.append(vararg)
        inspected_arguments.append(cls._make_list(kwonlyargs))
        inspected_arguments.append(kwarg)

        return inspected_arguments
