from pathlib import Path


class TemplatedFunc:
    CONST_FOR_CLASS = 0

    def __init__(self):
        self.name: str = None
        self.definition: str = None
        self.is_async: bool = None
        self.in_func: bool = None

    def call(self, params: list[str]) -> str:
        print("temp")
        awaitable = "await " if self.is_async else ""
        params = ", ".join(params)
        return f"{awaitable}{self.name}({params})"

    def import_from(self, path: Path) -> str:
        module = ".".join(path.parts)
        module = module.rstrip(".py")
        return f"from {module} import {self.name}"

    def call_clone(cls, params: list[str]) -> str:
        print("temp")
        awaitable = "await " if cls.is_async else ""
        params = ", ".join(params)
        return f"{awaitable}{cls.name}({params})"
