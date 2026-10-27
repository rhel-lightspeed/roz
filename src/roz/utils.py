"""Shared helpers for roz."""

from __future__ import annotations

import itertools

from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from roz.packages.protocol import PackageProtocol


_BODHI_NOTES_MAX = 10_000


def truncate_changelog(path: Path) -> None:
    """Overwrite *path* with only the most recent RPM changelog entry.

    No-op when the file is already within Bodhi's character limit.
    """

    text = path.read_text(encoding="utf-8")

    # early return if there's no reason to truncate
    if len(text) <= _BODHI_NOTES_MAX:
        return

    lines = iter(text.splitlines(keepends=True))
    first_header = next((line for line in lines if line.startswith("* ")), None)

    if first_header is None:
        path.write_text(text[:_BODHI_NOTES_MAX], encoding="utf-8")
        return

    body = itertools.takewhile(lambda line: not line.startswith("* "), lines)
    path.write_text((first_header + "".join(body))[:_BODHI_NOTES_MAX], encoding="utf-8")


def resolve_branches(
    project: PackageProtocol,
    forge_name: str,
    requested: list[str] | None,
) -> list[str]:
    """Resolve and validate a branch list against the workflow's known branches.

    Returns the effective branch list — either *requested* (if provided) or all
    branches defined for *forge_name* in the workflow.

    Args:
        project: Workflow instance whose ``DIST_GIT_BRANCHES`` mapping is consulted.
        forge_name: Forge key (e.g. ``'pagure'`` or ``'gitlab'``).
        requested: Branch names supplied by the user via ``--branch``, or ``None``
            to use all valid branches for the forge.

    Raises:
        SystemExit: If any requested branch is not in the workflow's valid set.
    """
    forge_branches = project.DIST_GIT_BRANCHES[forge_name]
    valid: list[str] = list(forge_branches.keys()) if isinstance(forge_branches, dict) else forge_branches
    branches = requested or valid

    unknown = sorted(set(branches) - set(valid))
    if unknown:
        raise SystemExit(
            f"Unknown branch(es) for {project.NAME!r} on {forge_name!r}: "
            f"{', '.join(unknown)}\n"
            f"Valid branches: {', '.join(valid)}"
        )

    return branches
