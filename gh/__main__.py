import argparse
import logging

from rich.logging import RichHandler
from rich.traceback import install

import gh.analytics
import gh.commands

install()
logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def setup_args() -> argparse.ArgumentParser:
    """geocode(
    Configures CLI arg parser
    :return: Configured arg parser
    """
    main_parser = argparse.ArgumentParser(prog="gh")
    subparsers = main_parser.add_subparsers(dest="subparser")
    command_parser = subparsers.add_parser("commands", help="Runs a command")
    command_parser.add_argument(
        "choice",
        help="The chosen command to run",
        choices=gh.commands.OPTIONS.keys(),
    )
    analytics_parser = subparsers.add_parser("analytics", help="Runs an analysis")
    analytics_parser.add_argument(
        "choice",
        help="The chosen analysis to run",
        choices=gh.analytics.OPTIONS.keys(),
    )
    return main_parser


if __name__ == "__main__":
    parser = setup_args()
    args = parser.parse_args()

    module_name = args.subparser
    if module_name == "commands":
        option = gh.commands.OPTIONS[args.choice]
    else:
        option = gh.analytics.OPTIONS[args.choice]
    option(**vars(args))
