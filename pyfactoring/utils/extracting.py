import ast
from pathlib import Path


def extract_source(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        source: str = f.read()
    return source


def extract_ast(filepath: Path) -> ast.Module:
    return ast.parse(extract_source(filepath))
