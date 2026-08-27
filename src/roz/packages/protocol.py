"""Protocol module for any package"""

from typing import Protocol


class PackageProtocol(Protocol):
    """Interface that every workflow module must satisfy.

    Each workflow encapsulates all project-specific logic for the three
    release stages. The commands layer dispatches into these methods;
    shared utilities (forge, srpm, git) are called from within.
    """

    NAME: str
    DIST_GIT_BRANCHES: dict[str, list[str]] = {}
    DIST_GIT_URL: dict[str, str] = {}
    UPSTREAM_REPO_URL: str
    BODHI_SKIP_BRANCHES: set[str] = set()

    def propose(
        self,
        forge_name: str,
        offline: bool,
        yes: bool,
        keep: bool,
        branches: list[str],
        resolves: list[str] | None,
    ) -> None:
        """Stage 1: generate SRPM, import SRPM, open dist-git PRs."""

    def build(
        self,
        forge_name: str,
        branches: list[str],
        scratch_build: bool,
        arches: str | None,
        keep: bool,
    ) -> None:
        """Stage 2: kick off Koji builds for merged PRs."""

    def update(
        self,
        update_type: str,
        severity: str,
        bugs: list[str] | None,
        branches: list[str],
        stable_karma: int,
    ) -> None:
        """Stage 3: create Bodhi updates."""
