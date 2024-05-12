import ast
from pathlib import Path

from colorama import Fore, Style


def source(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    return src


def module(filepath: Path) -> ast.Module:
    try:
        return ast.parse(source(filepath))
    except (SyntaxError, AttributeError):
        print(f"{filepath}:0: {Fore.RED}The file with the error was skipped{Style.RESET_ALL}")
        return ast.parse("# Nothing")

