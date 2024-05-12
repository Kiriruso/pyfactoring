import os
import os.path
import re
import sys
from collections.abc import Collection
from pathlib import Path
from platform import system

from pyfactoring.exceptions import FileOrDirNotFoundError


match system():
    case "Linux" | "Darwin":
        _DIR_PATTERN = r"(?:(?<=\/))?{}(?=\/)"
        _FILE_PATTERN = r"(?:(?<=\/))?{}\.py"
    case "Windows":
        _DIR_PATTERN = r"(?:(?<=\\))?{}(?=\\)"
        _FILE_PATTERN = r"(?:(?<=\\))?{}\.py"
    case _:
        _DIR_PATTERN = r"(?:(?<=\\)|(?<=\/))?{}(?=\\|\/)"
        _FILE_PATTERN = r"(?:(?<=\\)|(?<=\/))?{}\.py"


def _get_venv_name() -> str:
    python_dir = os.path.dirname(sys.executable)
    venv_name = os.path.basename(os.path.dirname(python_dir))
    return venv_name


_DEFAULT_EXCLUDE = (
    _get_venv_name(),
    ".pyfactoring_cache",
    ".idea",
    ".vscode",
    ".git",
)


def collect_filepaths(path: str, *, exclude: Collection[str] = None) -> list[Path]:
    if exclude is None:
        exclude = []

    if os.path.isfile(path) and path.endswith(".py"):
        return [Path(path)]
    if os.path.isdir(path):
        return _collect_from_dir(path, exclude)
    if os.path.isfile(path) and path.endswith(".txt"):
        return _collect_from_file(path, exclude)

    raise FileOrDirNotFoundError(f"Path does not lead to any dirs or file[.txt | .py]: '{path}'")


def separate_filepaths(
        paths: list[Path], chain: list[str], *, exclude: Collection[str] = None,
) -> tuple[list[Path], list[Path]]:
    single = []
    chained = []

    for path in paths:
        filepaths = collect_filepaths(path, exclude=exclude)
        chained.extend(
            filepath
            for filepath in filepaths
            # checking that the path is chained
            if any(map(lambda ch: str(Path(ch)) in str(filepath), chain))
        )
        single.extend(filepath for filepath in filepaths if filepath not in chained)

    return single, chained


def _collect_from_dir(dirpath: str, exclude: Collection[str]) -> list[Path]:
    files_or_dirs = [
        os.path.join(dirpath, fd)
        for fd in os.listdir(dirpath)
        if fd not in _DEFAULT_EXCLUDE and not fd.startswith(".")
    ]

    filepaths: list[Path] = []
    for file_or_dir in files_or_dirs:
        if os.path.isfile(file_or_dir) and file_or_dir.endswith(".py"):
            filepaths.append(Path(file_or_dir))
            continue

        for current_path, dirs, files in os.walk(file_or_dir):
            current_filepaths = [Path(current_path) / file for file in files if file.endswith(".py")]
            filepaths.extend(current_filepaths)

    return _filter_filepaths(filepaths, exclude)


def _collect_from_file(filepath: str, exclude: Collection[str]) -> list[Path]:
    relative_path = Path(filepath).parent
    with open(filepath, "r") as f:
        filepaths = [
            relative_path / file.rstrip()
            for file in f.readlines()
            if not file.startswith("#") and file != "\n" and file.rstrip().endswith(".py")
        ]
    return _filter_filepaths(filepaths, exclude)


def _filter_filepaths(filepaths: Collection[Path], exclude: Collection[str]) -> list[Path]:
    if not exclude:
        return filepaths

    patterns: list[str] = []
    for file_or_dir in exclude:
        if file_or_dir.endswith('.py'):
            pattern = _FILE_PATTERN.format(file_or_dir.replace(".py", ""))
        else:
            pattern = _DIR_PATTERN.format(file_or_dir)
        patterns.append(pattern)

    return [
        filepath
        for filepath in filepaths
        if all(map(lambda p: re.search(p, str(filepath)) is None, patterns))
    ]
