"""Shared helpers for roz."""

from roz.packages.protocol import PackageProtocol


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
    valid: list[str] = project.DIST_GIT_BRANCHES[forge_name]
    branches = requested or valid

    unknown = sorted(set(branches) - set(valid))
    if unknown:
        raise SystemExit(
            f"Unknown branch(es) for {project.NAME!r} on {forge_name!r}: "
            f"{', '.join(unknown)}\n"
            f"Valid branches: {', '.join(valid)}"
        )

    return branches
