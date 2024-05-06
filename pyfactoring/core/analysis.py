import sys

from pyfactoring.utils.pyclones import CloneFinder, CodeBlockClone
from pyfactoring.utils.pydioms import prefixtree, IdiomFinder
from pyfactoring.utils.pydioms.possibleidiom import Idiom, CodeBlockIdiom


def clone(
        single_paths: list[str], chained_paths: list[str]
) -> tuple[
    list[dict[str, list[CodeBlockClone]]],
    dict[str, list[CodeBlockClone]]
]:
    finder = CloneFinder()
    single = [finder.find_all(path) for path in single_paths]
    single = [clones for clones in single if clones]
    chained = finder.chained_find_all(chained_paths)
    return single, chained


def idiom(
        single_paths: list[str], chained_paths: list[str]
) -> tuple[
    list[dict[Idiom, list[CodeBlockIdiom]]],
    dict[Idiom, list[CodeBlockIdiom]]
]:
    recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(sys.getrecursionlimit() * 100)

    prefix_trees = prefixtree.make_prefix_trees(single_paths)
    single = [IdiomFinder.find_all(tree) for tree in prefix_trees]
    single = [idioms for idioms in single if idioms]

    tree = prefixtree.PrefixTree()
    for path in chained_paths:
        tree.add_tree(path)
    chained = IdiomFinder.find_all(tree)

    sys.setrecursionlimit(recursion_limit)
    return single, chained
