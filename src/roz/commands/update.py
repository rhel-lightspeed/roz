"""Stage 3: create Bodhi updates (skips rawhide)."""

import argparse

from roz import bodhi
from roz import utils
from roz.packages import PACKAGES_MAP


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "update",
        help="Stage 3: create Bodhi updates (skips rawhide).",
    )
    parser.add_argument(
        "--project",
        choices=list(PACKAGES_MAP.keys()),
        required=True,
        help="Project to update (e.g. goose).",
    )
    parser.add_argument(
        "--type",
        choices=["enhancement", "bugfix", "security"],
        default="enhancement",
        dest="update_type",
        help="Bodhi update type (default: enhancement).",
    )
    parser.add_argument(
        "--forge",
        choices=["pagure", "gitlab"],
        required=True,
        help="Forge to open PRs on.",
    )
    parser.add_argument(
        "--resolve",
        action="append",
        dest="bugs",
        metavar="BUG_ID",
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
        action="append",
        dest="branches",
        metavar="BRANCH",
        help="Limit to specific branch(es). May be repeated. Default: all.",
    )
    parser.add_argument(
        "--build",
        action="append",
        dest="builds",
        metavar="NVR",
        required=True,
        help="Koji build NVR to submit to Bodhi (e.g. goose-1.45.0-1.fc45). May be repeated.",
    )
    parser.add_argument(
        "--stable-karma",
        type=int,
        default=1,
        metavar="KARMA",
        help="Stable karma threshold (default: 1, minimum: 1).",
    )
    parser.add_argument(
        "--unstable-karma",
        type=int,
        default=-3,
        metavar="KARMA",
        help="Unstable karma threshold (default: -3).",
    )
    parser.add_argument(
        "--stable-days",
        type=int,
        default=7,
        metavar="DAYS",
        help="Days in testing before auto-promotion (default: 7).",
    )
    parser.add_argument(
        "--notes",
        default=None,
        help="Update notes. Overrides the changelog file when provided.",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> None:
    # Early check to stop the program if stable karma is less than 1
    if args.stable_karma < 1:
        raise SystemExit("--stable-karma must be at least 1.")

    set_of_branches = set(args.branches)
    if set_of_branches.intersection(bodhi.BODHI_SKIP_BRANCHES):
        raise SystemExit("rawhide do not need a Bodhi update (auto-composed). Remove them from --branch and try again.")

    valid_branches = set_of_branches - bodhi.BODHI_SKIP_BRANCHES

    project = PACKAGES_MAP[args.project]
    branches = utils.resolve_branches(project, args.forge, list(valid_branches))

    project.update(
        update_type=args.update_type,
        severity=args.severity,
        bugs=args.bugs,
        branches=branches,
        builds=args.builds,
        notes=args.notes,
        stable_karma=args.stable_karma,
        unstable_karma=args.unstable_karma,
        stable_days=args.stable_days,
    )
