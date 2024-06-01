import pytest

from pyfactoring.utils.path import collect_filepaths, separate_filepaths


@pytest.mark.parametrize(
    ("path", "expected", "count"),
    (
        (
            r"D:\Projects\Pet\Python\pyfactoring\test\samples\chained",
            {
                r"D:\Projects\Pet\Python\pyfactoring\test\samples\chained\chained_1.py",
                r"D:\Projects\Pet\Python\pyfactoring\test\samples\chained\chained_2.py",
                r"D:\Projects\Pet\Python\pyfactoring\test\samples\chained\chained_3.py",
            },
            3,
        ),
        (
            r"test\samples\chained",
            {
                r"test\samples\chained\chained_1.py",
                r"test\samples\chained\chained_2.py",
                r"test\samples\chained\chained_3.py",
            },
            3,
        ),
        (
            r"test\samples\file_containing_clone.py",
            {
                r"test\samples\file_containing_clone.py"
            },
            1,
        ),
        (
            r"test\samples",
            {
                r"test\samples\chained\chained_1.py",
                r"test\samples\chained\chained_2.py",
                r"test\samples\chained\chained_3.py",
                r"test\samples\function\function_1.py",
                r"test\samples\function\function_2.py",
                r"test\samples\function\function_3.py",
                r"test\samples\internal\internal_1.py",
                r"test\samples\internal\internal_2.py",
                r"test\samples\internal\internal_3.py",
                r"test\samples\all_nodes.py",
                r"test\samples\class.py",
                r"test\samples\file_containing_clone.py",
                r"test\samples\empty.py"
            },
            13,
        ),
        (
            r"test\samples\example.txt",
            {
                r"test\samples\chained\chained_1.py",
                r"test\samples\chained\chained_2.py",
                r"test\samples\chained\chained_3.py",
                r"test\samples\class.py",
                r"test\samples\file_containing_clone.py",
            },
            5,
        )
    ),
)
def test_collect_filepaths_success(path: str, expected: set[str], count: int):
    collected = collect_filepaths(path)
    collected = {str(path) for path in collected}

    assert len(collected) == count, collected
    assert collected == expected, collected


@pytest.mark.parametrize(
    "path",
    (
        r"undefined",
        r"test\undefined",
        r"data.py",
    )
)
def test_collect_filepaths_fail(path: str):
    with pytest.raises(FileNotFoundError):
        collect_filepaths(path)


@pytest.mark.parametrize(
    ("path", "exclude", "expected", "count"),
    (
        (
            r"test\samples",
            ("test",),
            set(),
            0,
        ),
        (
            r"test\samples\file_containing_clone.py",  # files not filter
            ("chained", "function", "file_containing_clone.py"),
            {r"test\samples\file_containing_clone.py"},
            1,
        ),
        (
            r"test\samples",
            ("chained", "function", "all_nodes.py", "class.py"),
            {
                r"test\samples\internal\internal_1.py",
                r"test\samples\internal\internal_2.py",
                r"test\samples\internal\internal_3.py",
                r"test\samples\file_containing_clone.py",
                r"test\samples\empty.py",
            },
            5,
        ),
        (
            r"test\samples\file_containing_clone.py",
            ("chained", "function"),
            {r"test\samples\file_containing_clone.py"},
            1,
        ),
    )
)
def test_collect_filepaths_with_exclude_success(
        path: str, exclude: tuple[str], expected: set[str], count: int
):
    collected = collect_filepaths(path, exclude=exclude)
    collected = {str(path) for path in collected}

    assert len(collected) == count, collected
    assert collected == expected, collected


@pytest.mark.parametrize(
    ("paths", "chain", "expected_single", "expected_chained", "s_count", "c_count"),
    (
        (
            [r"test\samples\chained"],
            [r"chained"],
            set(),
            {
                r"test\samples\chained\chained_1.py",
                r"test\samples\chained\chained_2.py",
                r"test\samples\chained\chained_3.py"
            },
            0,
            3,
        ),
        (
            [r"test\samples\chained"],
            [r"chained_1.py", r"chained_2.py"],
            {
                r"test\samples\chained\chained_3.py",
            },
            {
                r"test\samples\chained\chained_1.py",
                r"test\samples\chained\chained_2.py",
            },
            1,
            2,
        ),
        (
            [r"test\samples\chained"],
            [],
            {
                r"test\samples\chained\chained_1.py",
                r"test\samples\chained\chained_2.py",
                r"test\samples\chained\chained_3.py",
            },
            set(),
            3,
            0,
        ),
        (
            [r"test\samples"],
            [
                "function",
                "internal"
            ],
            {
                r"test\samples\chained\chained_1.py",
                r"test\samples\chained\chained_2.py",
                r"test\samples\chained\chained_3.py",
                r"test\samples\all_nodes.py",
                r"test\samples\class.py",
                r"test\samples\file_containing_clone.py",
                r"test\samples\empty.py",
            },
            {
                r"test\samples\function\function_1.py",
                r"test\samples\function\function_2.py",
                r"test\samples\function\function_3.py",
                r"test\samples\internal\internal_1.py",
                r"test\samples\internal\internal_2.py",
                r"test\samples\internal\internal_3.py",
            },
            7,
            6,
        ),
        (
            [
                r"test\samples\class.py",
                r"test\samples\all_nodes.py",
                r"test\samples\file_containing_clone.py"
            ],
            [
                "test"
            ],
            set(),
            {
                r"test\samples\class.py",
                r"test\samples\all_nodes.py",
                r"test\samples\file_containing_clone.py"
            },
            0,
            3,
        ),
        (
            [
                r"test\samples\class.py",
                r"test\samples\all_nodes.py",
                r"test\samples\file_containing_clone.py"
            ],
            [
                "class.py",
                "file_containing_clone.py",
            ],
            {
                r"test\samples\all_nodes.py",
            },
            {
                r"test\samples\class.py",
                r"test\samples\file_containing_clone.py"
            },
            1,
            2,
        ),
    )
)
def test_separate_filepaths_success(
        paths: list[str],
        chain: list[str],
        expected_single: set[str],
        expected_chained: set[str],
        s_count: int,
        c_count: int,
):
    single, chained = separate_filepaths(paths, chain)
    single = {str(path) for path in single}
    chained = {str(path) for path in chained}

    assert len(single) == s_count, single
    assert single == expected_single, single

    assert len(chained) == c_count, chained
    assert chained == expected_chained, chained
