import sys
from pathlib import Path

from pyfactoring.utils.pyclones import CloneFinder, CodeBlockClone
from pyfactoring.utils.pydioms import IdiomFinder, prefixtree
from pyfactoring.utils.pydioms.possibleidiom import CodeBlockIdiom, Idiom


def clone_analysis(
        paths: list[Path], *, is_chained: bool = False,
) -> list[dict[str, list[CodeBlockClone]]] | dict[str, list[CodeBlockClone]]:
    finder = CloneFinder()
    if is_chained:
        return finder.chained_find_all(paths)
    single = [finder.find_all(path) for path in paths]
    return [clones for clones in single if clones]


def idiom_analysis(
        paths: list[Path], *, is_chained: bool = False,
) -> list[dict[Idiom, list[CodeBlockIdiom]]] | dict[Idiom, list[CodeBlockIdiom]]:
    recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(sys.getrecursionlimit() * 100)

    if is_chained:
        tree = prefixtree.PrefixTree()
        for path in paths:
            tree.add_tree(path)
        idioms = IdiomFinder.find_all(tree)
    else:
        prefix_trees = prefixtree.make_prefix_trees(paths)
        single = [IdiomFinder.find_all(tree) for tree in prefix_trees]
        idioms = [idioms for idioms in single if idioms]

    sys.setrecursionlimit(recursion_limit)
    return idioms


def paths_with_clones(
        clones: list[dict[str, list[CodeBlockClone]]] | dict[str, list[CodeBlockClone]],
        *,
        is_chained: bool = False,
) -> list[Path]:
    if is_chained:
        return list({
            block.file
            for blocks in clones.values()
            for block in blocks
        })

    return list({
        blocks[0].file
        for clone in clones
        for blocks in clone.values()
    })
