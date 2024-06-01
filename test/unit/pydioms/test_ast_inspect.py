from collections import deque, defaultdict

import pytest

from pyfactoring import ast_inspect, ast_types, extract


@pytest.mark.parametrize(
    ("path", "nodes"),
    (
        (
            r"test\samples\file_containing_clone.py",
            {
                "If": 6,
            },
        ),
        (
            r"test\samples\class.py",
            {
                "FunctionDef": 4,
            },
        ),
        (
            r"test\samples\internal\internal_1.py",
            {
                "While": 2,
                "If": 2,
            },
        ),
        (
            r"test\samples\chained\chained_2.py",
            {
                "While": 9,
                "If": 6,
                "For": 2,
            },
        ),
        (
            r"test\samples\empty.py",
            {},
        ),
    ),
)
def test_make_inspected_tree_success(path: str, nodes: dict[str, int]):
    module = extract.module(path)
    tree = ast_inspect.make_inspected_tree(module, path)
    children = deque([tree])
    realize_subtree_nodes = defaultdict(int)

    assert tree

    while children:
        root = children.popleft()

        if isinstance(root, ast_inspect.ASTInspectedNode):
            assert root.name in ast_types.AST_NODES_INFO, root

        if not isinstance(root, ast_inspect.ASTInspectedNode):
            assert root.count_as in (
                ast_types.CountingType.OPERAND, ast_types.CountingType.NOT_COUNTED,
            ), root

        if root.file is not None:
            assert root.file == path, root

        if root.name in ast_types.AST_REALIZE_SUBTREE_NODES:
            assert root.realize_subtree, root
            assert root.count_as == ast_types.CountingType.OPERATOR, root
            assert root.ast_node, root
            realize_subtree_nodes[root.name] += 1

        if isinstance(root, ast_inspect.ASTInspectedNode) and root.children:
            children.extend(root.children)

    assert realize_subtree_nodes == nodes, realize_subtree_nodes
