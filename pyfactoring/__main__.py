import shutil
import sys

from pyfactoring import collect_filepaths, extract_ast, extract_idioms, ast_inspect, prefixtree

if __name__ == '__main__':
    sys.setrecursionlimit(sys.getrecursionlimit() * 100)

    target = input("Path to dir or file[.txt | .py]: ")
    exclude_dirs = []
    exclude_files = []

    if not target.endswith(".py"):
        exclude_dirs = input("Exclude dirs or skip: ")
        if exclude_dirs.lower() not in ("skip", "s", ""):
            exclude_dirs = exclude_dirs.split()

        exclude_files = input("Exclude files or skip: ")
        if exclude_files.lower() not in ("skip", "s", ""):
            exclude_files = exclude_files.split()

    print()

    filepaths = collect_filepaths(target, exclude_dirs=exclude_dirs, exclude_files=exclude_files)
    modules = [extract_ast(filepath) for filepath in filepaths]

    prefix_trees = prefixtree.make_prefix_trees(modules)
    prefix_trees = {filepath: tree for filepath, tree in zip(filepaths, prefix_trees)}

    terminal_size = shutil.get_terminal_size()
    print("=" * terminal_size.columns)

    for filepath, prefix_tree in prefix_trees.items():
        idioms = extract_idioms(prefix_tree)
        if not idioms:
            continue

        print(f"IDIOMS    |  {len(idioms)}")
        print(f"FILEPATH  |  {filepath}")

        for idiom, info in idioms.items():
            print("=" * terminal_size.columns)
            print(f"\n{info.state.idiom}\n")
            for i in info.primary_ids:
                inspected_tree = prefix_tree.inspected_trees[i]
                print(f"{filepath}:{inspected_tree.ast_node.lineno}:{inspected_tree.ast_node.col_offset}")
                for source in ast_inspect.source_from_inspected_tree(filepath, inspected_tree):
                    print(source)
                print()

        print("=" * terminal_size.columns)
