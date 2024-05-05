__all__ = ["collect_filepaths"]

import re
import os
import os.path
import sys
from pathlib import Path
from platform import system
from collections.abc import Collection
from itertools import chain

from pyfactoring.exceptions import FileOrDirNotFoundError

match system():
    case "Linux" | "Darwin":
        _DIR_PATTERN = r"(?<=\/){}(?=\/)"
        _FILE_PATTERN = r"(?<=\/){}\.py"
    case "Windows":
        _DIR_PATTERN = r"(?<=\\){}(?=\\)"
        _FILE_PATTERN = r"(?<=\\){}\.py"
    case _:
        _DIR_PATTERN = r"(?(?<=\\)|(?<=\/)){}(?=\\|\/)"
        _FILE_PATTERN = r"(?(?<=\\)|(?<=\/)){}\.py"


def _get_venv_name() -> str:
    python_dir = os.path.dirname(sys.executable)
    venv_name = os.path.basename(os.path.dirname(python_dir))
    return venv_name


_DEFAULT_EXCLUDE = (
    _get_venv_name(),
    ".idea",
    ".vscode"
)


def collect_filepaths(path: str, *, exclude: Collection[str] | None = None) -> list[Path]:
    if os.path.isfile(path) and path.endswith(".py"):
        return [Path(path)]
    if os.path.isdir(path):
        return _collect_from_dir(path, exclude)
    if os.path.isfile(path) and path.endswith(".txt"):
        return _collect_from_file(path, exclude)

    raise FileOrDirNotFoundError(f"Path does not lead to any dirs or file[.txt | .py]: '{path}'")


def _collect_from_dir(dirpath: str, exclude: Collection[str] | None) -> list[Path]:
    filepaths: list[Path] = []
    for current_path, dirs, files in os.walk(dirpath):
        current_path = Path(current_path)
        current_filepaths = [current_path / file for file in files if file.endswith(".py")]
        filepaths.extend(current_filepaths)
    return _filter_filepaths(filepaths, exclude)


def _collect_from_file(filepath: str, exclude: Collection[str] | None) -> list[Path]:
    relative_path = Path(filepath).parent
    with open(filepath, "r") as f:
        filepaths = [
            relative_path / file.rstrip()
            for file in f.readlines()
            if not file.startswith("#") and file != "\n" and file.rstrip().endswith(".py")
        ]
    return _filter_filepaths(filepaths, exclude)


def _filter_filepaths(filepaths: Collection[Path], exclude: Collection[str] | None) -> list[Path]:
    global _DIR_PATTERN, _FILE_PATTERN, _DEFAULT_EXCLUDE

    patterns: list[str] = []
    for file_or_dir in chain(_DEFAULT_EXCLUDE, exclude):
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
