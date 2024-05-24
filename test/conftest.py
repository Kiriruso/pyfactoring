import ast

from pathlib import Path
from typing import Generator


def mock_factory():
    def _load_tests() -> Generator[tuple[ast.AST, ast.AST], None, None]:
        path = yield
        path = Path(__file__).parent / "unit" / path / "mocks.py"

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        _if_iter = ast.iter_child_nodes(ast.parse(source))

        while True:
            try:
                yield next(_if_iter), next(_if_iter)
            except StopIteration:
                return

    tests = _load_tests()
    next(tests)
    return tests
