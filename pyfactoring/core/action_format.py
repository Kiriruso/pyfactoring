import itertools
import pathlib
import re

from dataclasses import dataclass, field

from pyfactoring.core import analysis, cache
from pyfactoring.settings import common_settings
from pyfactoring.utils.path import separate_filepaths


@dataclass(frozen=True)
class TemplatedFunc:
    name: str
    definition: str = field(repr=False)
    is_async: bool

    def call(self, params: list[str]) -> str:
        awaitable = "await " if self.is_async else ""
        params = ", ".join(params)
        return f"{awaitable}{self.name}({params})"


def get_filepath(blocks: list) -> pathlib.Path:
    return blocks[0].file


def create_function(idx: int, template: str, filepath: pathlib.Path) -> TemplatedFunc:
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


def action_format():
    single_paths, chained_paths = separate_filepaths(
        common_settings.paths,
        common_settings.chain,
        exclude=common_settings.exclude
    )
    cache.copy_files(single_paths, chained_paths)

    single_clones = analysis.clone(single_paths)
    # chained_clones = analysis.clone(chained_paths, is_chained=True)

    func_number = 0
    while single_clones:
        clones = single_clones.pop()
        template = max(clones.keys(), key=len)
        blocks = clones[template]

        path = get_filepath(blocks)
        func = create_function(func_number, template, path)

        source: list[str] = [f"{func.definition}\n\n\n"]
        with open(path, "r", encoding="utf-8") as source_file:
            source.extend(source_file.readlines())

        for block in blocks:
            params = itertools.chain(block.vars, block.consts)
            call = func.call(params)
            source[block.lineno] = f"{call}\n"

        prev_block_end = 0
        filtered_source: list[str] = []
        for block in blocks:
            filtered_source.extend(source[prev_block_end:block.lineno + 1])
            prev_block_end = block.end_lineno + 1
        filtered_source.extend(source[prev_block_end:])

        if filtered_source:
            with open(path, "w", encoding="utf-8") as source_file:
                source_file.writelines(filtered_source)
            print(f"{path}: Formatted: add function '{func.name}'")

        single_clones = analysis.clone(single_paths)
        func_number += 1
