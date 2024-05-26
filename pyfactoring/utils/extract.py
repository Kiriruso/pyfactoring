import ast
from pathlib import Path

from colorama import Fore, Style

from pyfactoring.exceptions import UndefinedModeError
from pyfactoring.settings import pyclones_settings


def file_source(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    return src


def stmt_source(stmt: ast.AST) -> str:
    match pyclones_settings.template_mode:
        case "code":
            return ast.unparse(stmt)
        case "tree":
            return ast.dump(stmt, indent=4)
        case _:
            raise UndefinedModeError(
                f"Template extraction mode is not specified or is incorrect: "
                f"{pyclones_settings.template_mode}",
            )


def module(filepath: Path) -> ast.Module:
    try:
        return ast.parse(file_source(filepath))
    except (SyntaxError, AttributeError):
        print(f"{filepath}:0: {Fore.RED}The file with the error was skipped{Style.RESET_ALL}")
    finally:
        return ast.parse("# Nothing")
