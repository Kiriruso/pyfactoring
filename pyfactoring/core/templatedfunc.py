import re
import itertools
from dataclasses import dataclass, field
from pathlib import Path

from pyfactoring.settings import common_settings


@dataclass(frozen=True)
class TemplatedFunc:
    name: str
    definition: str = field(repr=False)
    is_async: bool

    def call(self, params: list[str]) -> str:
        awaitable = "await " if self.is_async else ""
        params = ", ".join(params)
        return f"{awaitable}{self.name}({params})"

    def import_from(self, path: Path) -> str:
        module = ".".join(path.parts)
        module = module.rstrip(".py")
        return f"from {module} import {self.name}"


def create_function(idx: int, template: str, filepath: Path) -> TemplatedFunc:
    filename = filepath.name.rstrip(".py")

    is_async = bool(re.search(r"async|await", template))
    func_template = "# Pyfactoring: rename this!\ndef {}({}):\n{}"
    if is_async:
        func_template = f"async {func_template}"

    variables = sorted(set(re.findall(r"(__var_\d+__)", template)))
    if common_settings.pack_consts:
        params = ", ".join(variables)
        params = f"{params}, *consts"
    else:
        constants = sorted(set(re.findall(r"(__const_\d+__)", template)))
        params = ", ".join(itertools.chain(variables, constants))

    name = f"{filename}_func_{idx}"
    if common_settings.pack_consts:
        body = re.sub(r"'__const_(\d+)__'", r"consts[\1]", template)
    else:
        body = re.sub(r"'(__const_\d+__)'", r"\1", template)
    body = "\n    ".join(f"    {body}".splitlines())

    definition = func_template.format(
        name,
        params,
        body
    )

    return TemplatedFunc(name, definition, is_async)
