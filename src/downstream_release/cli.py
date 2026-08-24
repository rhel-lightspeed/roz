"""CLI entry point for downstream-release."""

import argparse

from downstream_release.commands import build
from downstream_release.commands import propose
from downstream_release.commands import update


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="downstream-release",
        description="Fedora/EPEL release automation for goose.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without making real changes.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    propose.register(sub)
    build.register(sub)
    update.register(sub)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.handler(args)
