import shutil
import sys

from pyfactoring import (
    collect_filepaths,
    extract_ast, extract_idioms,
    ast_inspect, prefixtree
)
from pyfactoring.core.check import check


def idiom_check():
    sys.setrecursionlimit(sys.getrecursionlimit() * 100)

    target = input("Path to dir or file[.txt | .py]: ")

    filepaths = collect_filepaths(target)
    modules = [extract_ast(filepath) for filepath in filepaths]

    prefix_trees = prefixtree.make_prefix_trees(modules)
    prefix_trees = {filepath: tree for filepath, tree in zip(filepaths, prefix_trees)}

    terminal_size = shutil.get_terminal_size()
    print("=" * terminal_size.columns)

    for filepath, prefix_tree in prefix_trees.items():
        idioms = extract_idioms(prefix_tree)

        print(f"IDIOMS    |  {len(idioms)}")
        print(f"FILEPATH  |  {filepath}")

        for idiom, info in idioms.items():
            print("=" * terminal_size.columns)
            print(f"\n{info.state.idiom}\n")
            for i in info.primary_ids:
                inspected_tree = prefix_tree.inspected_trees[i]
                print(
                    f"{filepath}:{inspected_tree.ast_node.lineno}:{inspected_tree.ast_node.col_offset}")
                for source in ast_inspect.source_from_inspected_tree(filepath, inspected_tree):
                    print(source)
                print()

        print("=" * terminal_size.columns)


if __name__ == '__main__':
    check()
