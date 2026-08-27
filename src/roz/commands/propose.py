"""Stage 1: generate SRPM, import SRPM, open dist-git PRs."""

import argparse

from roz import utils
from roz.packages import PACKAGES_MAP


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "propose",
        help="Stage 1: generate SRPM, import SRPM, open dist-git PRs.",
    )
    parser.add_argument(
        "--project",
        choices=list(PACKAGES_MAP.keys()),
        required=True,
        help="Project to release (e.g. goose).",
    )
    parser.add_argument(
        "--forge",
        choices=["pagure", "gitlab"],
        required=True,
        help="Forge to open PRs on.",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Upstream version to release.",
    )
    parser.add_argument(
        "--branch",
        action="append",
        dest="branches",
        metavar="BRANCH",
        help=(
            "Limit to specific branch(es). May be repeated. "
            "Defaults to all branches defined for the selected forge in the workflow."
        ),
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip tarball upload to lookaside cache (for testing).",
    )
    parser.add_argument(
        "--resolve",
        action="append",
        dest="resolves",
        metavar="TICKET",
        help=(
            "Bug or ticket to resolve (e.g. rhbz#12345 or RSPEED-678). "
            "May be repeated. Appended as 'Resolves: TICKET' trailers in the commit message."
        ),
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> None:
    project = PACKAGES_MAP[args.project]
    branches = utils.resolve_branches(project, args.forge, args.branches)

    project.propose(
        forge_name=args.forge,
        version=args.version,
        branches=branches,
        offline=args.offline,
        yes=args.yes,
        keep=args.keep,
        resolves=args.resolves,
    )
