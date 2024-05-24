from pathlib import Path


class TemplatedFunc:
    CONST_FOR_CLASS = 0

    def __init__(self):
        self.name: str = None
        self.definition: str = None
        self.is_async: bool = None
        self.in_func: bool = None

    def call(self, params: list[str]) -> str:
        awaitable = "await " if self.is_async else ""
        params = ", ".join(params)
        return f"{awaitable}{self.name}({params})"

    def import_from(self, path: Path) -> str:
        module = ".".join(path.parts)
        module = module.rstrip(".py")
        return f"from {module} import {self.name}"

    def call_clone(self, params: list[str]) -> str:
        awaitable = "await " if self.is_async else ""
        params = ", ".join(params)
        return f"{awaitable}{self.name}({params})"


def clone_function_1(x, y):
    z = 0
    for i in range(10):
        z += i * 2
    return x + y + z
