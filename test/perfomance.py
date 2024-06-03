import os
from pathlib import Path
from time import perf_counter

from colorama import Fore, Style

from pyfactoring.core import analysis, cache
from pyfactoring.core.action_format import format_files
from pyfactoring.settings import common_settings, pydioms_settings
from pyfactoring.utils.path import separate_filepaths


def performance_check():
    total_time = perf_counter()
    start = perf_counter()

    single_paths, chained_paths = separate_filepaths(
        common_settings.paths, common_settings.chain, exclude=common_settings.exclude,
    )

    print(f"collecting all paths: {perf_counter() - start:4.4f}s")

    if common_settings.no_cache:
        start = perf_counter()

        single_clones = analysis.clone_analysis(single_paths)

        print(f"single {Fore.GREEN}syntax{Style.RESET_ALL} analysis: {perf_counter() - start:4.4f}s {Fore.YELLOW}[NO CACHE]{Style.RESET_ALL}")
    else:
        start = perf_counter()

        single_clones, uncached_clones = cache.check_retrieve(single_paths)
        single_clones.extend(analysis.clone_analysis(uncached_clones))
        cache.check_cache(single_paths, single_clones)

        print(f"single {Fore.GREEN}syntax{Style.RESET_ALL} analysis: {perf_counter() - start:4.4f}s {Fore.YELLOW}[CACHE]{Style.RESET_ALL}")

    if pydioms_settings.enable:
        if common_settings.no_cache:
            start = perf_counter()

            single_idioms = analysis.idiom_analysis(single_paths)

            print(f"single {Fore.BLUE}metric{Style.RESET_ALL} analysis: {perf_counter() - start:4.4f}s {Fore.YELLOW}[NO CACHE]{Style.RESET_ALL}")
        else:
            start = perf_counter()

            single_idioms, uncached_idioms = cache.check_retrieve(single_paths, is_idiom=True)
            single_idioms.extend(analysis.idiom_analysis(uncached_idioms))
            cache.check_cache(single_paths, single_idioms, is_idiom=True)

            print(f"single {Fore.BLUE}metric{Style.RESET_ALL} analysis: {perf_counter() - start:4.4f}s {Fore.YELLOW}[CACHE]{Style.RESET_ALL}")

    total_time = perf_counter() - total_time

    total_lines = 0

    for path in single_paths:
        with open(path, "r", encoding="utf-8") as f:
            total_lines += len(f.readlines())

    for path in chained_paths:
        with open(path, "r", encoding="utf-8") as f:
            total_lines += len(f.readlines())

    print()

    print(f"total time: {total_time:4.4f}s")
    total_files = len(single_paths) + len(chained_paths)
    print(f"total files: {total_files}")
    print(f"total lines: {total_lines}")

    if total_files:
        average_lines = total_lines / total_files
        print(f"time for one file: {total_time / average_lines:4.4f}s {Fore.YELLOW}[{int(average_lines)} lines]{Style.RESET_ALL}")

    if not common_settings.no_cache:
        print()

        cache_path = Path(".pyfactoring_cache/")
        check_clones = cache_path / ".check.clones"
        check_idioms = cache_path / ".check.idioms"

        total_size = 0

        if os.path.exists(check_clones):
            size = os.path.getsize(check_clones) // 1024  # KB
            total_size += size
            print(f"{Fore.GREEN}syntax{Style.RESET_ALL} cache size: {size} KB")

        if os.path.exists(check_idioms):
            size = os.path.getsize(check_idioms) // 1024  # KB
            total_size += size
            print(f"{Fore.BLUE}metric{Style.RESET_ALL} cache size: {size} KB")

        if total_size:
            print(f"total cache size: {total_size} KB")


def performance_format():
    total_time = perf_counter()
    start = perf_counter()

    single_paths, chained_paths = separate_filepaths(
        common_settings.paths, common_settings.chain, exclude=common_settings.exclude,
    )

    collect_time = perf_counter() - start
    retrieve_time = 0

    if not common_settings.no_cache:
        start = perf_counter()

        single_paths = cache.format_retrieve(single_paths)
        chained_paths = cache.format_retrieve(chained_paths, is_chained=True)

        retrieve_time = perf_counter() - start

    if not (single_paths or chained_paths):
        print(f"{Fore.RED}Nothing to format{Style.RESET_ALL}")

        print()

        print(f"collecting all paths: {collect_time:4.4f}s")
        if retrieve_time:
            print(f"retrieve time: {retrieve_time:4.4f}s")

        total_time = perf_counter() - total_time
        print(f"total time: {total_time:4.4f}s")

        print()

        cache_path = Path(".pyfactoring_cache/")
        format_single = cache_path / ".format.single"
        format_chained = cache_path / ".format.chained"

        total_size = 0

        if os.path.exists(format_single):
            size = os.path.getsize(format_single)  # Bytes
            total_size += size

            if size:
                print(f"{Fore.GREEN}single{Style.RESET_ALL} cache size: {size} B")

        if os.path.exists(format_chained):
            size = os.path.getsize(format_chained)  # Bytes
            total_size += size

            if size:
                print(f"{Fore.BLUE}chained{Style.RESET_ALL} cache size: {size} B")

        if total_size:
            print(f"total cache size: {total_size} B")

        return

    lines_time = perf_counter()

    total_lines = 0

    for path in single_paths:
        with open(path, "r", encoding="utf-8") as f:
            total_lines += len(f.readlines())

    for path in chained_paths:
        with open(path, "r", encoding="utf-8") as f:
            total_lines += len(f.readlines())

    lines_time = perf_counter() - lines_time

    start = perf_counter()

    cache.store(single_paths, chained_paths)  # update RECOVERY file

    store_time = perf_counter() - start

    single_time = 0
    if single_paths:
        start = perf_counter()

        format_files(single_paths)
        if not common_settings.no_cache:
            cache.format_cache(single_paths)

        single_time = perf_counter() - start

    chained_time = 0
    if chained_paths:
        start = perf_counter()

        format_files(chained_paths, is_chained=True)
        if not common_settings.no_cache:
            cache.format_cache(chained_paths, is_chained=True)

        chained_time = perf_counter() - start

    total_time = perf_counter() - total_time - lines_time

    print()

    print(f"collecting all paths: {collect_time:4.4f}s")

    if retrieve_time:
        print(f"retrieve time: {perf_counter() - start:4.4f}s")

    print(f"store time: {store_time:4.4f}s")

    if single_time:
        print(f"{Fore.GREEN}single{Style.RESET_ALL} format: {single_time:4.4f}s")

    if chained_time:
        print(f"{Fore.BLUE}chained{Style.RESET_ALL} format: {chained_time:4.4f}s")

    print()

    print(f"total time: {total_time:4.4f}s")

    total_files = len(single_paths) + len(chained_paths)
    print(f"total files: {total_files}")
    print(f"total lines: {total_lines}")

    if total_files:
        average_lines = total_lines / total_files
        print(f"time for one file: {total_time / average_lines:4.4f}s {Fore.YELLOW}[{int(average_lines)} lines]{Style.RESET_ALL}")

    if not common_settings.no_cache:
        print()

        cache_path = Path(".pyfactoring_cache/")
        format_single = cache_path / ".format.single"
        format_chained = cache_path / ".format.chained"

        total_size = 0

        if os.path.exists(format_single):
            size = os.path.getsize(format_single)  # Bytes
            total_size += size

            if size:
                print(f"{Fore.GREEN}single{Style.RESET_ALL} cache size: {size} B")

        if os.path.exists(format_chained):
            size = os.path.getsize(format_chained)  # Bytes
            total_size += size

            if size:
                print(f"{Fore.BLUE}chained{Style.RESET_ALL} cache size: {size} B")

        if total_size:
            print(f"total cache size: {total_size} B")


if __name__ == '__main__':
    print(f"{__file__}:255:5: add call")
