import itertools
import re
from dataclasses import dataclass, field
from pathlib import Path

from pyfactoring.settings import common_settings


@dataclass(frozen=True)
class TemplatedFunc:
    name: str
    definition: str = field(repr=False)
    is_async: bool
    in_func: bool

    def call(self, params: list[str]) -> str:
        awaitable = "await " if self.is_async else ""
        params = ", ".join(params)
        return f"{awaitable}{self.name}({params})"

    def import_from(self, path: Path) -> str:
        module = ".".join(path.parts)
        module = module.rstrip(".py")
        return f"from {module} import {self.name}"

    @staticmethod
    def make(idx: int, filepath: Path, template: str) -> "TemplatedFunc":
        filename = filepath.name.rstrip(".py")
        func_template = "# Pyfactoring: rename this!\n{} {}({}):\n{}"

        is_func = "__function__" in template
        is_async = "async" in template or "await" in template
        prefix_def = "async def" if is_async else "def"

        variables = sorted(set(re.findall(r"__var_\d+__", template)))

        if common_settings.pack_consts:
            params = ", ".join(variables)
            params = f"{params}, *consts"
        else:
            constants = sorted(set(re.findall(r"__const_\d+__", template)))
            params = ", ".join(itertools.chain(variables, constants))

        name = f"{filename}_func_{idx}"
        if common_settings.pack_consts:
            body = re.sub(r"'__const_(\d+)__'", r"consts[\1]", template)
        else:
            body = re.sub(r"'(__const_\d+__)'", r"\1", template)

        if is_func:
            body = "\n".join(f"    {body}".splitlines()[1:])
        else:
            body = "\n    ".join(f"    {body}".splitlines())

        definition = func_template.format(
            prefix_def,
            name,
            params,
            body,
        )

        return TemplatedFunc(name, definition, is_async, is_func)
