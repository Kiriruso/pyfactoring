import ast

from pathlib import Path


def load_tests(folder: str) -> list[tuple[ast.AST, ast.AST]]:
    path = Path(__file__).parent / "templater" / folder / "tests.py"

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tests = []
    module = ast.parse(source)
    children = ast.iter_child_nodes(module)

    while True:
        try:
            pair = next(children), next(children)
            tests.append(pair)
        except StopIteration:
            if len(tests[-1]) % 2 == 1:
                raise ValueError(f"Incorrect amount of test data: {len(tests)}")
            return tests
