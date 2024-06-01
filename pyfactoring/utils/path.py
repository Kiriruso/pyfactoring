import os
import os.path
import re
import sys
from collections.abc import Collection
from pathlib import Path


def _get_venv_name() -> str:
    python_dir = os.path.dirname(sys.executable)
    venv_name = os.path.basename(os.path.dirname(python_dir))
    return venv_name


_DEFAULT_EXCLUDE = (
    _get_venv_name(),
    "venv",
    ".venv",
    "build",
    "_build",
    "__pycache__",
    "__pypackages__",
    "dist",
    "site-packages",
    ".pyfactoring_cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    ".git",
    ".git-rewrite",
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

    raise FileNotFoundError(f"Path does not lead to any dirs or file[.txt | .py]: '{path}'")


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
    filepaths = []
    relative_path = Path(filepath).parent
    with open(filepath, "r") as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue

            path = line.rstrip()
            if os.path.isdir(path):
                filepaths.extend(_collect_from_dir(path, exclude))
            elif path.endswith(".py"):
                filepaths.append(relative_path / path)

    return _filter_filepaths(filepaths, exclude)


def _filter_filepaths(filepaths: Collection[Path], exclude: Collection[str]) -> list[Path]:
    patterns = [re.escape(str(Path(path))) for path in exclude]
    return [
        filepath
        for filepath in filepaths
        if all(map(lambda p: re.search(p, str(filepath)) is None, patterns))
    ]
