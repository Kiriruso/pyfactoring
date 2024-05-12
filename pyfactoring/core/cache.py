import itertools
import os
import pathlib
import shutil
import time

from colorama import Fore, Style


_CACHE_DIR = pathlib.Path("./.pyfactoring_cache")


def copy_files(single_paths: list[pathlib.Path], chained_paths: list[pathlib.Path]):
    head_path = _CACHE_DIR / "head"
    paths_path = head_path / ".paths"
    recovery_path = _CACHE_DIR / "RECOVERY"

    if os.path.exists(head_path):
        recovery_dir = _CACHE_DIR / str(hex(int(time.time())))
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
            paths = [pathlib.Path(line.rstrip()) for line in paths_file.readlines()]

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
