"""Stage 1: generate SRPM, import SRPM, open dist-git PRs."""

import argparse

from downstream_release.workflows import WORKFLOW_MAP


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "propose",
        help="Stage 1: generate SRPM, import SRPM, open dist-git PRs.",
    )
    parser.add_argument(
        "--project",
        choices=list(WORKFLOW_MAP),
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
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> None:
    WORKFLOW_MAP[args.project].propose(
        forge_name=args.forge,
        version=args.version,
        branches=args.branches,
        dry_run=args.dry_run,
        offline=args.offline,
        yes=args.yes,
        keep=args.keep,
    )
