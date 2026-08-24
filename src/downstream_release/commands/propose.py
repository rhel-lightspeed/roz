"""Stage 1: generate SRPM, import SRPM, open dist-git PRs."""

import argparse

from downstream_release.const import BRANCHES


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "propose",
        help="Stage 1: generate SRPM, import SRPM, open dist-git PRs.",
    )
    parser.add_argument(
        "--version",
        help="Upstream version to release (auto-detected if omitted).",
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
    branches = args.branches
    print("command: propose")
    print(f"dry_run: {args.dry_run}")
    print(f"version: {args.version}")
    print(f"branches: {branches}")
