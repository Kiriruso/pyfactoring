import colorama
import shutil
import sys

from pathlib import Path
from collections.abc import Collection

from pyfactoring import collect_filepaths, CloneFinder, CodeBlockClone, prefixtree, IdiomFinder
from pyfactoring.settings import common_settings, pyclones_settings


def clone_analyze(
        single_paths: list[str], chained_paths: list[str]
) -> tuple[list[dict[str, list[CodeBlockClone]]], dict[str, list[CodeBlockClone]]]:
    finder = CloneFinder()
    single = [finder.find_all(path) for path in single_paths]
    chained = finder.chained_find_all(chained_paths)
    return single, chained


def idiom_analyze(
        single_paths: list[str], chained_paths: list[str]
) -> tuple:  # tuple[dict[Idiom, list[CodeBlockIdiom]], dict[Idiom, list[CodeBlockIdiom]]]
    recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(sys.getrecursionlimit() * 100)

    prefix_trees = prefixtree.make_prefix_trees(single_paths)
    single = [IdiomFinder.find_all(tree) for tree in prefix_trees]

    tree = prefixtree.PrefixTree()
    for path in chained_paths:
        tree.add_tree(path)
    chained = IdiomFinder.find_all(tree)

    sys.setrecursionlimit(recursion_limit)
    return single, chained


def separate_paths(
        paths: list[Path], *, exclude: Collection[str] = None
) -> tuple[list[Path], list[Path]]:
    single = []
    chained = []

    for path in paths:
        filepaths = collect_filepaths(path, exclude=exclude)
        chained.extend(
            filepath
            for filepath in filepaths
            # checking that the path is chained
            if any(map(lambda ch: str(Path(ch)) in str(filepath), common_settings.chain))
        )
        single.extend(filepath for filepath in filepaths if filepath not in chained)

    return single, chained


def check():
    # print("=" * terminal_size.columns)
    # print("=" * terminal_size.columns)

    single_paths, chained_paths = separate_paths(common_settings.paths, exclude=common_settings.exclude)
    single_clones, chained_clones = clone_analyze(single_paths, chained_paths)
    # single_idioms, chained_idioms = idiom_analyze(single_paths, chained_paths)

    terminal_size = shutil.get_terminal_size().columns

    if single_clones:
        title = " FINDING CLONES IN SINGLE FILES "
        side_size = (terminal_size - len(title)) // 2
        print(f"{'='*side_size}{title}{'='*side_size}")

        for clone in single_clones:
            for template, blocks in clone.items():
                total_lines = 0

                for block in blocks:
                    lines = block.end_lineno - block.lineno + 1
                    total_lines += lines
                    print(
                        f"{block.link}: clone found [lines: {lines}]"
                    )

                print(f"Total clones: {len(blocks)}")
                print(f"Total lines in clones: {total_lines}")

                if pyclones_settings.template_view:
                    print(f"With template:")
                    for i, line in enumerate(template.splitlines(), 1):
                        print(f"{i:2} {'|':<2}{line}")
                print()
                print("-" * terminal_size)
                print()

    if chained_clones:
        title = " FINDING CLONES IN CHAINED FILES "
        side_size = (terminal_size - len(title)) // 2
        print(f"{'=' * side_size}{title}{'=' * side_size}")

        for template, blocks in chained_clones.items():
            total_lines = 0

            for block in blocks:
                lines = block.end_lineno - block.lineno + 1
                total_lines += lines
                print(
                    f"{block.link}: clone found [lines: {lines}]"
                )

            print(f"Total clones: {len(blocks)}")
            print(f"Total lines in clones: {total_lines}")

            if pyclones_settings.template_view:
                print(f"With template:")
                for i, line in enumerate(template.splitlines(), 1):
                    print(f"{i:2}{'|':^4}{line}")
            print()
            print("-" * terminal_size)
            print()
