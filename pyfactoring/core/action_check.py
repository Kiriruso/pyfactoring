import shutil

from colorama import Fore, Style

from pyfactoring.core import analysis
from pyfactoring.utils.path import separate_filepaths
from pyfactoring.settings import common_settings, pyclones_settings


def display_analysis(title: str, data: list | dict, *, is_idiom: bool = False):
    if not data:
        return

    title = f" {Fore.LIGHTCYAN_EX}{title}{Style.RESET_ALL} "
    data_type = "idiom" if is_idiom else "clone"
    terminal_size = shutil.get_terminal_size().columns
    side_line = '=' * ((terminal_size - len(title)) // 2)
    full_line = '-' * terminal_size
    print(f"{side_line}{title}{side_line}")

    def _print(_templates: dict):
        nonlocal terminal_size, full_line, data_type

        for template, blocks in _templates.items():
            total_lines = 0

            for block in blocks:
                lines = block.end_lineno - block.lineno + 1
                total_lines += lines
                print(
                    f"{block.link}: {Fore.LIGHTWHITE_EX}{data_type} found{Style.RESET_ALL} "
                    f"[{Fore.MAGENTA}lines: {lines}{Style.RESET_ALL}]"
                )

            print(
                f"{Fore.GREEN}Total {data_type}s: "
                f"{Fore.LIGHTWHITE_EX}{len(blocks)}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.MAGENTA}Total lines: "
                f"{Fore.LIGHTWHITE_EX}{total_lines}{Style.RESET_ALL}"
            )

            match data_type:
                case "idiom":
                    print(
                        f"{Fore.YELLOW}With idiom: "
                        f"{Fore.LIGHTWHITE_EX}{template}{Style.RESET_ALL}"
                    )
                case "clone":
                    if pyclones_settings.template_view:
                        print(f"{Fore.YELLOW}With template:{Style.RESET_ALL}")
                        for i, line in enumerate(template.splitlines(), 1):
                            print(f"{Fore.LIGHTWHITE_EX}{i:3}{Style.RESET_ALL}{'|':^4}{line}")
            print(full_line)

    if isinstance(data, list):
        for data in data:
            _print(data)
    elif isinstance(data, dict):
        _print(data)


def action_check():
    single, chained = separate_filepaths(
        common_settings.paths, common_settings.chain, exclude=common_settings.exclude
    )
    sc, cc = analysis.clone(single), analysis.clone(chained, is_chained=True)
    si, ci = analysis.idiom(single), analysis.idiom(chained, is_chained=True)

    display_analysis("FINDING CLONES IN SINGLE FILES", sc)
    display_analysis("FINDING CLONES IN CHAINED FILES", cc)
    display_analysis("FINDING IDIOMS IN SINGLE FILES", si, is_idiom=True)
    display_analysis("FINDING IDIOMS IN CHAINED FILES", ci, is_idiom=True)