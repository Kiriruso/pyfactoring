import hashlib
import itertools
import os
import pickle
import shutil
from dataclasses import dataclass
from pathlib import Path
from time import time

from colorama import Fore, Style

from pyfactoring.utils.pyclones import CodeBlockClone
from pyfactoring.utils.pydioms.possibleidiom import CodeBlockIdiom, Idiom


_CACHE_DIR = Path("./.pyfactoring_cache")


@dataclass
class FileCache:
    path: Path
    hash: bytes
    data: bytes

    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path)


def hash_file(path: Path) -> bytes:
    with open(path, "rb") as source_file:
        source_hash = hashlib.md5()
        while chunk := source_file.read(8192):
            source_hash.update(chunk)
    return source_hash.digest()


def format_retrieve(paths: list[Path], *, is_chained: bool = False) -> list[Path]:
    suffix = "chained" if is_chained else "single"
    cache_path = _CACHE_DIR / f".format.{suffix}"

    if not os.path.exists(cache_path):
        return paths

    with open(cache_path, "rb") as cache_file:
        caches: dict[Path, bytes] = pickle.load(cache_file)

    if is_chained:
        for path in paths:
            if hash_file(path) != caches.get(path):
                return paths
        return []
    else:
        return [
            path
            for path in paths
            if hash_file(path) != caches.get(path)
        ]


def format_cache(paths: list[Path], *, is_chained: bool = False):
    suffix = "chained" if is_chained else "single"
    cache_path = _CACHE_DIR / f".format.{suffix}"
    caches: dict[Path, bytes] = {}

    if os.path.exists(cache_path):
        with open(cache_path, "rb") as cache_file:
            caches = pickle.load(cache_file)

    for path in paths:
        caches[path] = hash_file(path)

    with open(cache_path, "wb") as cache_file:
        pickle.dump(caches, cache_file)


def check_retrieve(
    paths: list[Path],
    *,
    is_idiom: bool = False,
) -> tuple[list[dict[str | Idiom, list[CodeBlockClone | CodeBlockIdiom]]], list[Path]]:
    suffix = "idioms" if is_idiom else "clones"
    cache_path = _CACHE_DIR / f".check.{suffix}"

    if not os.path.exists(cache_path):
        return [], paths

    with open(cache_path, "rb") as cache_file:
        caches: list[FileCache] = pickle.load(cache_file)

    caches_dumps = {cache.path: (cache.hash, cache.data) for cache in caches}
    cached_clones = []
    uncached_paths = []

    for path in paths:
        if path in caches_dumps and hash_file(path) == caches_dumps[path][0]:
            clone: dict[str, list[CodeBlockClone]] = caches_dumps[path][1]
            cached_clones.append(clone)
        else:
            uncached_paths.append(path)

    return cached_clones, uncached_paths


def check_cache(
    paths: list[Path],
    clones: list[dict[str, list[CodeBlockClone]]],
    *,
    is_idiom: bool = False,
):
    suffix = "idioms" if is_idiom else "clones"
    cache_path = _CACHE_DIR / f".check.{suffix}"
    caches_dumps = {}

    if os.path.exists(cache_path):
        with open(cache_path, "rb") as cache_file:
            caches = pickle.load(cache_file)
        caches_dumps = {cache.path: (cache.hash, cache.data) for cache in caches}

    for clone in clones:
        for _, blocks in clone.items():
            filepath = blocks[0].file
            filehash = hash_file(filepath)
            if filehash != caches_dumps.get(filepath):
                caches_dumps[filepath] = (filehash, clone)
            break

    for path in paths:
        if path not in caches_dumps:
            caches_dumps[path] = (hash_file(path), {})

    caches = [
        FileCache(path, filehash, data)
        for path, (filehash, data) in caches_dumps.items()
    ]

    with open(cache_path, "wb") as cache_file:
        pickle.dump(caches, cache_file)


def copy_files(single_paths: list[Path], chained_paths: list[Path]):
    head_path = _CACHE_DIR / "head"
    paths_path = head_path / ".paths"
    recovery_path = _CACHE_DIR / "RECOVERY"

    if os.path.exists(head_path):
        recovery_dir = _CACHE_DIR / hex(int(time()))
        os.rename(head_path, recovery_dir)

        with open(recovery_path, "r") as recovery_file:
            recoveries = [line.rstrip() for line in recovery_file.readlines()]

        recoveries[0] = recovery_dir.name

        with open(recovery_path, "w") as recovery_file:
            recovery_file.write("head\n")
            for recovery in recoveries:
                recovery_file.write(f"{recovery}\n")
    else:
        with open(recovery_path, "w") as recovery_file:
            recovery_file.write("head\n")

    os.makedirs(head_path, exist_ok=True)
    for path in itertools.chain(single_paths, chained_paths):
        shutil.copyfile(path, head_path / path.name)

    with open(paths_path, "w") as paths_file:
        for path in itertools.chain(single_paths, chained_paths):
            paths_file.write(f"{path}\n")


def restore():
    head_path = _CACHE_DIR / "head"
    paths_path = head_path / ".paths"
    recovery_path = _CACHE_DIR / "RECOVERY"

    with open(recovery_path, "r") as recovery_file:
        recoveries = [line.rstrip() for line in recovery_file.readlines()]

    if recoveries:
        recoveries.pop(0)

        with open(paths_path, "r") as paths_file:
            paths = [Path(line.rstrip()) for line in paths_file.readlines()]

        for path in paths:
            print(f"{path}:0: {Fore.GREEN}Restored{Style.RESET_ALL}")
            shutil.copyfile(head_path / path.name, path)

        shutil.rmtree(head_path)
    else:
        print(f"{Fore.RED}Nothing to restore{Style.RESET_ALL}")

    if recoveries:
        os.rename(_CACHE_DIR / recoveries[0], _CACHE_DIR / "head")
        recoveries[0] = "head"

    with open(recovery_path, "w") as recovery_file:
        for recovery in recoveries:
            recovery_file.write(f"{recovery}\n")


def create_dir():
    os.makedirs(_CACHE_DIR, exist_ok=True)

    gitignore_path = _CACHE_DIR / ".gitignore"
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as gitignore:
            gitignore.write("# Automatically created by pyfactoring.\n")
            gitignore.write("*")

    recovery_path = _CACHE_DIR / "RECOVERY"
    if not os.path.exists(recovery_path):
        with open(recovery_path, "w"):
            pass


create_dir()
