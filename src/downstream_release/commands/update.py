"""Stage 3: create Bodhi updates (skips rawhide)."""

import argparse

from downstream_release.const import BRANCHES


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "update",
        help="Stage 3: create Bodhi updates (skips rawhide).",
    )
    parser.add_argument(
        "--type",
        choices=["enhancement", "bugfix", "security"],
        default="enhancement",
        dest="update_type",
        help="Bodhi update type (default: enhancement).",
    )
    parser.add_argument(
        "--bugs",
        action="append",
        help="Related bug IDs. May be repeated.",
    )
    parser.add_argument(
        "--severity",
        choices=["unspecified", "low", "medium", "high", "urgent"],
        default="unspecified",
        help="Bodhi severity (default: unspecified).",
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
    print("command: update")
    print(f"dry_run: {args.dry_run}")
    print(f"update_type: {args.update_type}")
    print(f"bugs: {args.bugs}")
    print(f"severity: {args.severity}")
    print(f"branches: {branches}")
