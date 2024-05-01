import shutil
import sys

from pyfactoring import extracting, inspect, collect_filepaths


def main():
    sys.setrecursionlimit(sys.getrecursionlimit() * 100)

    target = input("Path to dir or file[.txt | .py]: ")

    if target.endswith(".py"):
        exclude_dirs = None
        exclude_files = None
    else:
        exclude_dirs = input("Exclude dirs or skip: ")
        exclude_dirs = None if exclude_dirs.lower() in ("skip", "") else exclude_dirs.split()

        exclude_files = input("Exclude files or skip: ")
        exclude_files = None if exclude_files.lower() in ("skip", "") else exclude_files.split()

    print()

    filepaths = collect_filepaths(target, exclude_dirs=exclude_dirs, exclude_files=exclude_files)
    modules = [extracting.extract_ast(filepath) for filepath in filepaths]

    prefix_trees = inspect.make_prefix_trees(modules)
    prefix_trees = {filepath: tree for filepath, tree in zip(filepaths, prefix_trees)}

    terminal_size = shutil.get_terminal_size()
    print("=" * terminal_size.columns)

    for filepath, prefix_tree in prefix_trees.items():
        idioms = extracting.extract_idioms(prefix_tree)
        if not idioms:
            continue

        print(f"IDIOMS    |  {len(idioms)}")
        print(f"FILEPATH  |  {filepath}")

        for idiom, info in idioms.items():
            print("=" * terminal_size.columns)
            print(f"\n{info.state.idiom}\n")
            for i in info.primary_ids:
                inspected_tree = prefix_tree.inspected_trees[i]
                print(f"link: {filepath}:{inspected_tree.ast.lineno}:{inspected_tree.ast.col_offset}")
                for source in extracting.source_from_inspected_tree(filepath, inspected_tree):
                    print(source)
                print()

        print("=" * terminal_size.columns)
