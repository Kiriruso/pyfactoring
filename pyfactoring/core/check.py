import colorama
import shutil

from pyfactoring.core.analysis import clone_analysis, idiom_analysis
from pyfactoring.utils.path import separate_filepaths
from pyfactoring.settings import common_settings, pyclones_settings


def display_analysis(title: str, data: list | dict, data_type: str):
    if not data:
        return

    title = f" {title} "
    terminal_size = shutil.get_terminal_size().columns
    side_size = (terminal_size - len(title)) // 2
    print(f"{'=' * side_size}{title}{'=' * side_size}")

    def _print(_templates: dict):
        nonlocal terminal_size

        for template, blocks in _templates.items():
            total_lines = 0

            for block in blocks:
                lines = block.end_lineno - block.lineno + 1
                total_lines += lines
                print(
                    f"{block.link}: {data_type} found [lines: {lines}]"
                )

            print(f"Total {data_type}s: {len(blocks)}")
            print(f"Total lines in {data_type}s: {total_lines}")

            match data_type:
                case "idiom":
                    print(f"With idiom: {template}")
                case "clone":
                    if pyclones_settings.template_view:
                        print(f"With template:")
                        for i, line in enumerate(template.splitlines(), 1):
                            print(f"{i:2}{'|':^4}{line}")
            print("-" * terminal_size)

    if isinstance(data, list):
        for data in data:
            _print(data)
    elif isinstance(data, dict):
        _print(data)


def check():
    paths = separate_filepaths(
        common_settings.paths, common_settings.chain, exclude=common_settings.exclude
    )
    sc, cc = clone_analysis(*paths)
    si, ci = idiom_analysis(*paths)

    display_analysis("FINDING CLONES IN SINGLE FILES", sc, "clone")
    display_analysis("FINDING CLONES IN CHAINED FILES", cc, "clone")
    display_analysis("FINDING IDIOMS IN SINGLE FILES", si, "idiom")
    display_analysis("FINDING IDIOMS IN CHAINED FILES", ci, "idiom")
