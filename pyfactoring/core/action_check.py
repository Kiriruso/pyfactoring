import shutil

from colorama import Fore, Style

from pyfactoring.core import analysis
from pyfactoring.settings import common_settings, pyclones_settings
from pyfactoring.utils.path import separate_filepaths


def display_analysis(title: str, data: list | dict, *, is_idiom: bool = False):
    if not data:
        return

    data_type = "idiom" if is_idiom else "clone"
    terminal_size = shutil.get_terminal_size().columns
    full_line = '-' * terminal_size

    title = f" {title} "
    print(Fore.CYAN, title.center(terminal_size, "="), Style.RESET_ALL, sep='')

    def _print(_templates: dict):
        nonlocal terminal_size, full_line, data_type

        for template, blocks in _templates.items():
            total_lines = 0

            for block in blocks:
                lines = block.end_lineno - block.lineno + 1
                total_lines += lines
                print(
                    f"{block.link}: {data_type} found "
                    f"[{Fore.MAGENTA}lines: {lines}{Style.RESET_ALL}]",
                )

            print(
                f"{Fore.GREEN}Total {data_type}s: "
                f"{Style.RESET_ALL}{len(blocks)}",
            )
            print(
                f"{Fore.MAGENTA}Total lines: "
                f"{Style.RESET_ALL}{total_lines}",
            )

            match data_type:
                case "idiom":
                    print(
                        f"{Fore.CYAN}With idiom: "
                        f"{Style.RESET_ALL}{template}",
                    )
                case "clone":
                    if pyclones_settings.template_view:
                        print(f"{Fore.CYAN}With template:{Style.RESET_ALL}")
                        for i, line in enumerate(template.splitlines(), 1):
                            print(f"{i:3}{'|':^4}{line}")
            print(full_line)

    if isinstance(data, list):
        for data in data:
            _print(data)
    elif isinstance(data, dict):
        _print(data)


def action_check():
    single, chained = separate_filepaths(
        common_settings.paths, common_settings.chain, exclude=common_settings.exclude,
    )
    sc, cc = analysis.clone(single), analysis.clone(chained, is_chained=True)
    si, ci = analysis.idiom(single), analysis.idiom(chained, is_chained=True)

    display_analysis("FINDING CLONES IN SINGLE FILES", sc)
    display_analysis("FINDING CLONES IN CHAINED FILES", cc)
    display_analysis("FINDING IDIOMS IN SINGLE FILES", si, is_idiom=True)
    display_analysis("FINDING IDIOMS IN CHAINED FILES", ci, is_idiom=True)
