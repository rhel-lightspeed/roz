"""Stage 2: kick off Koji builds for merged PRs."""

import argparse
import logging

from roz import koji
from roz import utils
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
        "--forge",
        choices=["pagure", "gitlab"],
        required=True,
        help="Forge whose dist-git to clone and build from.",
    )
    parser.add_argument(
        "--branch",
        action="append",
        dest="branches",
        metavar="BRANCH",
        help="Limit to specific branch(es). May be repeated. Default: all.",
    )
    parser.add_argument(
        "--scratch-build",
        action="store_true",
        dest="scratch_build",
        help="Run fedpkg scratch-build before the real build.",
    )
    parser.add_argument(
        "--arches",
        nargs="+",
        choices=["x86_64", "aarch64", "ppc64le", "s390x"],
        metavar="ARCH",
        help=(
            "Architectures to target for scratch-build. "
            "May be repeated or space-separated (e.g. --arches x86_64 aarch64). "
            "Only used with --scratch-build. Default: all."
        ),
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> None:
    """Entry point for the ``roz build`` subcommand.

    Resolves the target branches, then delegates to the project workflow to
    clone the dist-git repository and submit Koji builds for each branch.
    Optionally runs a scratch build first when ``--scratch-build`` is set.

    Authentication and build submission failures are caught here, logged at
    DEBUG level with full fedpkg output, and re-raised as a clean
    :exc:`SystemExit` with a user-facing message.

    Args:
        args: Parsed CLI arguments. Expected attributes: ``project``, ``forge``,
            ``branches``, ``scratch_build``, ``arches``, ``keep``.
    """
    project = PACKAGES_MAP[args.project]
    branches = utils.resolve_branches(args.project, project, args.forge, args.branches)
    arches = " ".join(args.arches) if args.arches else None

    try:
        project.build(
            forge_name=args.forge,
            branches=branches,
            scratch_build=args.scratch_build,
            arches=arches,
            keep=args.keep,
        )
    except (koji.AuthenticationError, koji.BuildSubmissionError) as exc:
        logging.debug("fedpkg error details: %s", exc.details)
        raise SystemExit(str(exc)) from None
