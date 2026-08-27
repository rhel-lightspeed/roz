"""Stage 2: kick off Koji builds for merged PRs."""

import argparse

from roz.packages import PACKAGES_MAP


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "build",
        help="Stage 2: kick off Koji builds for merged PRs.",
    )
    parser.add_argument(
        "--project",
        choices=list(PACKAGES_MAP.keys()),
        required=True,
        help="Project to build (e.g. goose).",
    )
    parser.add_argument(
        "--branch",
        action="append",
        dest="branches",
        metavar="BRANCH",
        help="Limit to specific branch(es). May be repeated. Default: all.",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> None:
    project = PACKAGES_MAP[args.project](dry_run=args.dry_run)
    project.build(
        branches=args.branches,
    )
