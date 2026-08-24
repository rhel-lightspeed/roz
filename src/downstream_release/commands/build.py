"""Stage 2: kick off Koji builds for merged PRs."""

import argparse

from downstream_release.const import BRANCHES


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "build",
        help="Stage 2: kick off Koji builds for merged PRs.",
    )
    parser.add_argument(
        "--branch",
        choices=BRANCHES,
        action="append",
        dest="branches",
        help="Limit to specific branch(es). May be repeated. Default: all.",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> None:
    branches = args.branches or BRANCHES
    print("command: build")
    print(f"dry_run: {args.dry_run}")
    print(f"branches: {branches}")
