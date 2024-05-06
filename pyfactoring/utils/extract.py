import ast
from pathlib import Path


def source(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()
    return src


def module(filepath: Path) -> ast.Module:
    return ast.parse(source(filepath))
