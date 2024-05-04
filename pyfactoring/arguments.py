import argparse


class _SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=80)

    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


parser = argparse.ArgumentParser(
    prog="pyfactoring",
    description="Pyfactoring: A linter that will help you find and refactor copy-paste",
    usage="%(prog)s [OPTIONS] <ACTION> [<path>, ...]",
    formatter_class=_SubcommandHelpFormatter,
)

# === ACTION === #
action_parser = parser.add_subparsers(title="actions", dest="action")

check_parser = action_parser.add_parser(
    name="check",
    prog="pyfactoring",
    usage="%(prog)s [OPTIONS] check [<path>, ...] [OPTIONS]",
    help="run check on the given files or directories",
    formatter_class=_SubcommandHelpFormatter,
)
check_parser.add_argument(
    "paths",
    nargs="*",
    default=".",
    help="list of files or directories [default: .]"
)
check_parser.add_argument(
    "--exclude-dirs",
    nargs="*",
    metavar="<dir name>,",
    help="excludes added directories",
)
check_parser.add_argument(
    "--exclude-files",
    nargs="*",
    metavar="<file name>,",
    help="excludes added files"
)

format_parser = action_parser.add_parser(
    name="format",
    prog="pyfactoring",
    usage="%(prog)s [OPTIONS] format [<path>, ...] [OPTIONS]",
    help="run format on the given files or directories",
    formatter_class = _SubcommandHelpFormatter,
)
format_parser.add_argument(
    "paths",
    nargs="*",
    default=".",
    help="list of files or directories [default: .]"
)
format_parser.add_argument(
    "--exclude-dirs",
    nargs="*",
    metavar="<dir name>,",
    help="excludes added directories"
)
format_parser.add_argument(
    "--exclude-files",
    nargs="*",
    metavar="<file name>,",
    help="excludes added files"
)

# === COMMON OPTIONS === #
general_options = parser.add_argument_group("general options")
general_options.add_argument(
    "--color",
    action="store_true",
    help="displays colors when outputting information"
)
general_options.add_argument(
    "--diff",
    action="store_true",
    help="displays the differences between the changes made and the source"
)
general_options.add_argument(
    "--workers",
    type=int,
    default=1,
    metavar="<count>",
    help="changes the number of workers processing files [default: 1]"
)

# === SPECIFIC OPTIONS === #
pydioms_group = parser.add_argument_group("pydioms options")
pydioms_group.add_argument(
    "--verbose",
    action="store_true",
    help="displays additional information"
)
pydioms_group.add_argument(
    "--pd-count",
    type=int,
    metavar="<count>",
    help="minimum number of trees considered an idiom [default: 5]"
)
pydioms_group.add_argument(
    "--pd-length",
    type=int,
    metavar="<length>",
    help="minimum length of each tree to be processed [default: 10]"
)

pyclones_group = parser.add_argument_group("pyclones options")
pyclones_group.add_argument(
    "--template-mode",
    choices=["code", "tree"],
    metavar="<mode>",
    help="selecting the mode for saving templates [default: code]"
)
pyclones_group.add_argument(
    "--pc-count",
    type=int,
    metavar="<count>",
    help="minimum number of templates considered a clone [default: 2]"
)
pyclones_group.add_argument(
    "--pc-length",
    type=int,
    metavar="<length>",
    help="minimum code fragment length [default: 3]",
)

args = parser.parse_args()
