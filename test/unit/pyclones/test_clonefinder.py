from pathlib import Path

import pytest

from pyfactoring import CloneFinder


@pytest.mark.parametrize(
    ("path", "count", "total", "linenos"),
    (
        (
            Path("test/samples/empty.py"),
            0,
            0,
            set(),
        ),
        (
            Path("test/samples/file_containing_clone.py"),
            2,
            4,
            {6, 8, 18, 20},
        ),
        (
            Path("test/samples/class.py"),
            1,
            2,
            {13, 24},
        ),
        (
            Path("test/samples/chained/chained_1.py"),
            1,
            2,
            {8, 31},
        ),
        (
            Path("test/samples/chained/chained_2.py"),
            3,
            8,
            {7, 11, 22, 30, 34, 45, 53, 57},
        ),
    ),
)
def test_find_clones_in_single_files_success(path: Path, count: int, total: int, linenos: set[int]):
    finder = CloneFinder()
    clones = finder.find_all(path)  # with default settings: length = 4, count = 2

    assert len(clones) == count

    t = 0

    for template, blocks in clones.items():
        for block in blocks:
            assert block.file == path
            assert block.lineno in linenos

            t += 1

    assert t == total
    assert t == len(linenos)


@pytest.mark.parametrize(
    ("paths", "count", "total", "positions"),
    (
        (
            (
                Path("test/samples/chained/chained_1.py"),
                Path("test/samples/chained/chained_2.py"),
            ),
            3,
            12,
            {
                Path("test/samples/chained/chained_1.py"): {8, 19, 27, 31},
                Path("test/samples/chained/chained_2.py"): {7, 11, 22, 30, 34, 45, 53, 57},
            }
        ),
        (
            (
                Path("test/samples/chained/chained_1.py"),
                Path("test/samples/chained/chained_3.py"),
            ),
            2,
            5,
            {
                Path("test/samples/chained/chained_1.py"): {8, 19, 31},
                Path("test/samples/chained/chained_3.py"): {7, 15},
            }
        ),
        (
            (
                Path("test/samples/chained/chained_1.py"),
                Path("test/samples/chained/chained_2.py"),
                Path("test/samples/chained/chained_3.py"),
            ),
            3,
            14,
            {
                Path("test/samples/chained/chained_1.py"): {8, 19, 27, 31},
                Path("test/samples/chained/chained_2.py"): {7, 11, 22, 30, 34, 45, 53, 57},
                Path("test/samples/chained/chained_3.py"): {7, 15},
            }
        ),
        (
            (
                Path("test/samples/function/function_1.py"),
                Path("test/samples/function/function_2.py"),
                Path("test/samples/function/function_3.py"),
            ),
            1,
            4,
            {
                Path("test/samples/function/function_1.py"): {1},
                Path("test/samples/function/function_2.py"): {8, 18},
                Path("test/samples/function/function_3.py"): {6},
            }
        ),
        (
            (
                    Path("test/samples/function/function_1.py"),
                    Path("test/samples/function/function_2.py"),
                    Path("test/samples/function/function_3.py"),
                    Path("test/samples/chained/chained_3.py"),
            ),
            2,
            6,
            {
                Path("test/samples/function/function_1.py"): {1},
                Path("test/samples/function/function_2.py"): {8, 18},
                Path("test/samples/function/function_3.py"): {6},
                Path("test/samples/chained/chained_3.py"): {7, 15},
            }
        ),
    )
)
def test_find_clones_in_chained_files_success(
    paths: tuple[Path], count: int, total: int, positions: dict[Path, set[int]],
):
    finder = CloneFinder()
    clones = finder.chained_find_all(paths)  # with default settings: length = 4, count = 2

    assert len(clones) == count

    t = 0

    for template, blocks in clones.items():
        for block in blocks:
            assert block.file in paths
            assert block.lineno in positions[block.file]

            t += 1

    assert t == total
