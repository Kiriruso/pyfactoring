import pytest

from pyfactoring.utils.pydioms import idiomfinder
from pyfactoring.utils.pydioms.prefixtree import PrefixTree


@pytest.mark.parametrize(
    ("path", "count"),
    (
        (
            r"test\samples\empty.py",
            0,
        ),
        (
            r"test\unit\pydioms\idiom_1.py",
            3,
        ),
        (
            r"test\unit\pydioms\idiom_2.py",
            5,
        ),
    )
)
def test_find_idioms_success(path: str, count: int):
    tree = PrefixTree()
    tree.add_tree(path)

    idiom_finder = idiomfinder.IdiomFinder()
    idioms = idiom_finder.find_all(tree)

    for blocks in idioms.values():
        for block in blocks:
            assert str(block.file) == path

    assert len(idioms) == count, (len(idioms), idioms)
