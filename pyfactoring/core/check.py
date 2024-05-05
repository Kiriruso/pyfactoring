import pathlib

from pyfactoring import collect_filepaths, CloneFinder, prefixtree, extract_idioms
from pyfactoring.settings import common_settings, pyclones_settings


def is_chained(target) -> bool:
    return any(map(lambda chained: str(pathlib.Path(chained)) in str(target), common_settings.chain))


def check():
    single_paths = []
    chained_paths = []

    for target in common_settings.paths:
        filepaths = collect_filepaths(target, exclude=common_settings.exclude)
        chained_paths.extend(filepath for filepath in filepaths if is_chained(filepath))
        single_paths.extend(filepath for filepath in filepaths if filepath not in chained_paths)

    clone_finder = CloneFinder()

    for path in single_paths:
        clones = clone_finder.find_all(path)
        for template, blocks in clones.items():
            if pyclones_settings.template_view:
                print("TEMPLATE:")
                print(template)
                print()
            print("CLONES FOUND IN:")
            for block in blocks:
                print(block.link)
            print()

    clones = clone_finder.chained_find_all(chained_paths)
    for template, blocks in clones.items():
        if pyclones_settings.template_view:
            print("TEMPLATE:")
            print(template)
            print()
        print("CLONES FOUND IN:")
        for block in blocks:
            print(block.link)
        print()
