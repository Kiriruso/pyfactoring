__all__ = ["collect_filepaths"]

import re

from os import walk
from os.path import isdir, isfile
from pathlib import Path
from platform import system
from typing import Iterable

from pyfactoring.exceptions import FileOrDirNotFoundError


_SYSTEM = system()

match _SYSTEM:
    case "Linux" | "Darwin":
        _DIR_PATTERN = r"(?<=\/){}(?=\/)"
        _FILE_PATTERN = r"(?<=\/){}\.py"
    case "Windows":
        _DIR_PATTERN = r"(?<=\\){}(?=\\)"
        _FILE_PATTERN = r"(?<=\\){}\.py"
    case _:
        _DIR_PATTERN = r"(?(?<=\\)|(?<=\/)){}(?=\\|\/)"
        _FILE_PATTERN = r"(?(?<=\\)|(?<=\/)){}\.py"


def collect_filepaths(
    path: str, *, exclude_dirs: Iterable[str] | None = None, exclude_files: Iterable[str] | None = None
) -> list[Path]:
    if isfile(path) and path.endswith(".py"):
        return [Path(path)]
    if isdir(path):
        return _collect_from_dir(path, exclude_dirs, exclude_files)
    if isfile(path) and path.endswith(".txt"):
        return _collect_from_file(path, exclude_dirs, exclude_files)

    raise FileOrDirNotFoundError(f"Path does not lead to any dirs or file[.txt | .py]: '{path}'")


def _filter_filepaths(
    filepaths: Iterable[Path], exclude_dirs: Iterable[str] | None, exclude_files: Iterable[str] | None
) -> list[Path]:
    if not exclude_dirs and not exclude_files:
        return list(filepaths)

    patterns: list[str] = []
    if exclude_dirs:
        for exclude_dir in exclude_dirs:
            pattern = _DIR_PATTERN.format(exclude_dir)
            patterns.append(pattern)
    if exclude_files:
        for exclude_file in exclude_files:
            pattern = _FILE_PATTERN.format(exclude_file.rstrip(".py"))
            patterns.append(pattern)

    return [
        filepath
        for filepath in filepaths
        if all(map(lambda p: re.search(p, str(filepath)) is None, patterns))
    ]


def _collect_from_dir(
    dirpath: str, exclude_dirs: Iterable[str] | None, exclude_files: Iterable[str] | None
) -> list[Path]:
    filepaths: list[Path] = []
    for current_path, dirs, files in walk(dirpath):
        current_path = Path(current_path)
        current_filepaths = [current_path / file for file in files if file.endswith(".py")]
        filepaths.extend(current_filepaths)
    return _filter_filepaths(filepaths, exclude_dirs, exclude_files)


def _collect_from_file(
    filepath: str, exclude_dirs: Iterable[str] | None, exclude_files: Iterable[str] | None
) -> list[Path]:
    relative_path = Path(filepath).parent
    with open(filepath, "r") as f:
        filepaths = [
            relative_path / file.rstrip()
            for file in f.readlines()
            if not file.startswith("#") and file != "\n" and file.rstrip().endswith(".py")
        ]
    return _filter_filepaths(filepaths, exclude_dirs, exclude_files)
