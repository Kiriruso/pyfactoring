from collections import defaultdict
from pathlib import Path

from colorama import Fore, Style

from pyfactoring.core import analysis, cache
from pyfactoring.core.templatedfunc import TemplatedFunc
from pyfactoring.exceptions import FileOrDirNotFoundError
from pyfactoring.settings import common_settings
from pyfactoring.utils.path import separate_filepaths
from pyfactoring.utils.pyclones import CodeBlockClone


def _read_sources(blocks: list[CodeBlockClone]) -> dict[Path, list[str]]:
    sources: dict[Path, list[str]] = defaultdict(list)
    for block in blocks:
        if block.file not in sources:
            with open(block.file, "r", encoding="utf-8") as source_file:
                sources[block.file] = source_file.readlines()
    return sources


def _write_sources(sources: dict[Path, list[str]]):
    for path, source in sources.items():
        with open(path, "w", encoding="utf-8") as source_file:
            source_file.writelines(source)


def _insert_function_call(sources: dict[Path, list[str]], block: CodeBlockClone, func: TemplatedFunc):
    shift = int(not func.in_func)
    call = func.call(block)
    line = sources[block.file][block.lineno - shift]
    indent = " " * (len(line) - len(line.lstrip()))
    sources[block.file][block.lineno - shift] = f"{indent}{call}\n"
    print(f"{block.file}:0: {Fore.GREEN}Formatted:{Style.RESET_ALL} clone replaced by call {call}")


def _remove_remaining_clone_parts(
        sources: dict[Path, list[str]], blocks: list[CodeBlockClone], in_func: bool,
) -> dict[Path, list[str]]:
    shift = int(in_func)
    ends: dict[Path, int] = defaultdict(int)
    cleared_sources: dict[Path, list[str]] = defaultdict(list)

    for block in blocks:
        source = sources[block.file]
        cleared_sources[block.file].extend(
            source[ends[block.file]:block.lineno + shift],
        )
        ends[block.file] = block.end_lineno

    for path, source in sources.items():
        cleared_sources[path].extend(source[ends[path]:])

    return cleared_sources


def _replace_clones_with_calls(
        sources: dict[Path, list[str]], blocks: list[CodeBlockClone], func: TemplatedFunc,
) -> dict[Path, list[str]]:
    for block in blocks:
        _insert_function_call(sources, block, func)
    return _remove_remaining_clone_parts(sources, blocks, func.in_func)


def _find_lineno_after_class_name(name: str, lines: list[str]) -> int:
    lineno_after_name = 0
    for lineno, line in enumerate(lines):
        if name in line:
            lineno_after_name = lineno + 1
            break
    return lineno_after_name


def _find_lineno_after_imports(lines: list[str]) -> int:
    lineno_after_imports = 0
    for lineno, line in enumerate(lines):
        if "import" not in line:
            lineno_after_imports = lineno
            break
    return lineno_after_imports


def _insert_func_def_or_import(
    sources: dict[Path, list[str]],
    blocks: list[CodeBlockClone],
    func: TemplatedFunc,
    main_file: Path,
):
    changed_sources: dict[Path, list[str]] = {}
    for block in blocks:
        if block.file in changed_sources:
            continue

        end_lineno = (
            _find_lineno_after_class_name(block.class_name, sources[block.file])
            if block.class_name else
            _find_lineno_after_imports(sources[block.file])
        )
        source = sources[block.file][:end_lineno]

        print(f"{block.file}:{len(source)}: {Fore.GREEN}Formatted: {Style.RESET_ALL}", end='')

        if block.class_name:
            line = source[-1]
            indent = " " * (len(line) - len(line.lstrip()) + 4)
            definition = indent.join(func.definition.splitlines(keepends=True))
            source.append(f"{indent}{definition}\n\n")
            print(f"define {func.name} in class {block.class_name}")
        elif block.file == main_file:
            if end_lineno > 0:
                source.append("\n\n")
            source.append(f"{func.definition}\n\n")
            print(f"define {func.name}")
        else:
            source.append(f"{func.import_from(main_file)}\n")
            print(f"import {func.name}")

        source.extend(sources[block.file][end_lineno:])
        changed_sources[block.file] = source

    return changed_sources


def _max_len_clone(clones: dict):
    template = max(clones.keys(), key=len)
    return template, clones[template]


def format_files(paths: list[Path], *, is_chained: bool = False):
    clones_from_files = analysis.clone_analysis(paths, is_chained=is_chained)
    paths_with_clones = analysis.paths_with_clones(clones_from_files, is_chained=is_chained)

    func_id = 0
    while clones_from_files:
        if not is_chained:
            clones_from_files = clones_from_files[0]

        template, blocks = _max_len_clone(clones_from_files)
        sources = _read_sources(blocks)

        target: Path = blocks[0].file
        func = TemplatedFunc.make(func_id, target, template)

        sources = _replace_clones_with_calls(sources, blocks, func)
        sources = _insert_func_def_or_import(sources, blocks, func, target)

        _write_sources(sources)

        clones_from_files = analysis.clone_analysis(paths_with_clones, is_chained=is_chained)
        paths_with_clones = analysis.paths_with_clones(clones_from_files, is_chained=is_chained)
        func_id += 1


def action_format():
    try:
        single_paths, chained_paths = separate_filepaths(
            common_settings.paths, common_settings.chain, exclude=common_settings.exclude,
        )
    except FileOrDirNotFoundError as e:
        print(e.text)
        return

    if not common_settings.no_cache:
        single_paths = cache.format_retrieve(single_paths)
        chained_paths = cache.format_retrieve(chained_paths, is_chained=True)

    if not (single_paths or chained_paths):
        print(f"{Fore.RED}Nothing to format{Style.RESET_ALL}")
        return

    cache.store(single_paths, chained_paths)

    if single_paths:
        format_files(single_paths)
        cache.format_cache(single_paths)

    if chained_paths:
        format_files(chained_paths, is_chained=True)
        cache.format_cache(chained_paths, is_chained=True)
