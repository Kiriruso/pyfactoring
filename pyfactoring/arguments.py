import argparse


class _SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=80)

    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


def _create_base_action_parser(subparser, action: str, is_default: bool = False):
    _default = "[default]" if is_default else ""
    _help = f"run {action} on the given files or directories {_default}"

    _action_parser: argparse.ArgumentParser = subparser.add_parser(
        name=action,
        prog="pyfactoring",
        usage=f"%(prog)s [OPTIONS] {action} [<path>, ...] [OPTIONS]",
        help=_help,
        formatter_class=_SubcommandHelpFormatter,
    )
    _action_parser.add_argument(
        "paths",
        nargs="*",
        default=".",
        help="list of files or directories [default: .]",
    )
    _action_parser.add_argument(
        "--chain",
        nargs="*",
        metavar="<dir/file name>,",
        help="combines on the given files or directories for analysis",
    )
    _action_parser.add_argument(
        "--chain-all",
        action="store_true",
        help="combines all files or directories for analysis",
    )
    _action_parser.add_argument(
        "--exclude",
        nargs="*",
        metavar="<dir/file name>,",
        help="excludes on the given files or directories",
    )

    return _action_parser


parser = argparse.ArgumentParser(
    prog="pyfactoring",
    description="Pyfactoring: A linter that will help you find and refactor copy-paste",
    usage="%(prog)s [OPTIONS] <ACTION> [<path>, ...] [OPTIONS]",
    formatter_class=_SubcommandHelpFormatter,
)

# === ACTION === #
action_subparser = parser.add_subparsers(title="actions", dest="action")
check_parser = _create_base_action_parser(action_subparser, "check", True)
format_parser = _create_base_action_parser(action_subparser, "format")
format_parser.add_argument(
    "--pack-consts",
    action="store_true",
    help="when generating a function, all constants are packed into '*consts'",
)
format_parser.add_argument(
    "--diff",
    action="store_true",
    help="displays the differences between the changes made and the source",
)
restore_parser = action_subparser.add_parser(
    name="restore",
    prog="pyfactoring",
    usage=f"%(prog)s restore",  # noqa
    help="restore previous version of files",
    formatter_class=_SubcommandHelpFormatter,
)

# === COMMON OPTIONS === #
general_options = parser.add_argument_group("general options")
general_options.add_argument(
    "--workers",
    type=int,
    default=1,
    metavar="<count>",
    help="changes the number of workers processing files [default: 1]",
)

# === SPECIFIC OPTIONS === #
pydioms_group = parser.add_argument_group("pydioms options")
pydioms_group.add_argument(
    "--pd-verbose",
    action="store_true",
    help="displays additional information",
)
pydioms_group.add_argument(
    "--pd-count",
    type=int,
    metavar="<count>",
    help="minimum number of trees considered an idiom [default: 5]",
)
pydioms_group.add_argument(
    "--pd-length",
    type=int,
    metavar="<length>",
    help="minimum length of each tree to be processed [default: 10]",
)

pyclones_group = parser.add_argument_group("pyclones options")
pyclones_group.add_argument(
    "--template-view",
    action="store_true",
    help="display template for clone set",
)
pyclones_group.add_argument(
    "--template-mode",
    choices=["code", "tree"],
    metavar="<mode>",
    help="selecting the mode for saving templates [default: code]",
)
pyclones_group.add_argument(
    "--pc-count",
    type=int,
    metavar="<count>",
    help="minimum number of templates considered a clone [default: 2]",
)
pyclones_group.add_argument(
    "--pc-length",
    type=int,
    metavar="<length>",
    help="minimum code fragment length [default: 5]",
)

args = parser.parse_args()
