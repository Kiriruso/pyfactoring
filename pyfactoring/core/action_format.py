import itertools
import pathlib
from collections import defaultdict
from colorama import Fore, Style

from pyfactoring.core import analysis, cache
from pyfactoring.core.templatedfunc import create_function
from pyfactoring.settings import common_settings
from pyfactoring.utils.path import separate_filepaths


def mainfile_from(blocks: list) -> pathlib.Path:
    return blocks[0].file


def format_chained(paths: list[pathlib.Path]):
    chained_clones = analysis.clone(paths, is_chained=True)

    if not chained_clones:
        print(f"{Fore.RED}[C] Nothing to format{Style.RESET_ALL}")
        return

    func_number = 0
    while chained_clones:
        template = max(chained_clones.keys(), key=len)
        blocks = chained_clones[template]

        main_file = mainfile_from(blocks)
        func = create_function(func_number, template, main_file)

        sources: dict[pathlib.Path, list[str]] = defaultdict(list)
        for block in blocks:
            if block.file not in sources:
                with open(block.file, "r", encoding="utf-8") as source_file:
                    sources[block.file].extend(source_file.readlines())

            params = itertools.chain(block.vars, block.consts)
            call = func.call(params)
            sources[block.file][block.lineno - 1] = f"{call}\n"

        prev_block_ends: dict[pathlib.Path, int] = defaultdict(int)
        replaced_sources: dict[pathlib.Path, list[str]] = defaultdict(list)

        for block in blocks:
            source = sources[block.file]
            replaced_sources[block.file].extend(source[prev_block_ends[block.file]:block.lineno])
            prev_block_ends[block.file] = block.end_lineno

        for path, source in sources.items():
            replaced_sources[path].extend(source[prev_block_ends[path]:])

        cleared_sources: dict[pathlib.Path, list[str]] = {}
        for block in blocks:
            if block.file in cleared_sources:
                continue

            after_imports = 0
            for line in replaced_sources[block.file]:
                if "import" not in line:
                    break
                after_imports += 1

            source = replaced_sources[block.file][:after_imports]
            if block.file == main_file:
                if after_imports != 0:
                    source.append("\n\n")
                source.append(f"{func.definition}\n\n")
            else:
                source.append(f"{func.import_from(main_file)}\n")
            source.extend(replaced_sources[block.file][after_imports:])

            cleared_sources[block.file] = source

        for path, source in cleared_sources.items():
            with open(path, "w", encoding="utf-8") as source_file:
                source_file.writelines(source)
            print(
                f"{path}:0: {Fore.GREEN}[C] Formatted: "
                f"{Style.RESET_ALL}add function {Fore.LIGHTWHITE_EX}{func.name}{Style.RESET_ALL}"
            )

        chained_clones = analysis.clone(paths, is_chained=True)
        func_number += 1


def format_single(paths: list[pathlib.Path]):
    single_clones = analysis.clone(paths)

    if not single_clones:
        print(f"{Fore.RED}[S] Nothing to format{Style.RESET_ALL}")
        return

    func_number = 0
    while single_clones:
        clones = single_clones.pop()
        template = max(clones.keys(), key=len)
        blocks = clones[template]

        main_file = mainfile_from(blocks)
        func = create_function(func_number, template, main_file)

        source: list[str]
        with open(main_file, "r", encoding="utf-8") as source_file:
            source = source_file.readlines()

        for block in blocks:
            params = itertools.chain(block.vars, block.consts)
            call = func.call(params)
            source[block.lineno - 1] = f"{call}\n"

        prev_block_end = 0
        replaced_source: list[str] = []
        for block in blocks:
            replaced_source.extend(source[prev_block_end:block.lineno])
            prev_block_end = block.end_lineno
        replaced_source.extend(source[prev_block_end:])

        after_imports = 0
        for line in replaced_source:
            if "import" not in line:
                break
            after_imports += 1

        cleared_source: list[str] = replaced_source[:after_imports]
        if after_imports != 0:
            cleared_source.append("\n\n")
        cleared_source.append(f"{func.definition}\n\n")
        cleared_source.extend(replaced_source[after_imports:])

        with open(main_file, "w", encoding="utf-8") as source_file:
            source_file.writelines(cleared_source)
        print(
            f"{main_file}:0: {Fore.GREEN}[S] Formatted: "
            f"{Style.RESET_ALL}add function {Fore.LIGHTWHITE_EX}{func.name}{Style.RESET_ALL}"
        )

        single_clones = analysis.clone(paths)
        func_number += 1


def action_format():
    single_paths, chained_paths = separate_filepaths(
        common_settings.paths,
        common_settings.chain,
        exclude=common_settings.exclude
    )

    cache.copy_files(single_paths, chained_paths)

    format_single(single_paths)
    format_chained(chained_paths)
