"""Bodhi update submission via fedpkg."""

from pathlib import Path

from roz.fedpkg import run_fedpkg


# Updates to rawhide are done automatically after builds to that target are successful.
BODHI_SKIP_BRANCHES: set[str] = {"rawhide"}


class UpdateSubmissionError(Exception):
    """Raised when fedpkg fails to submit a Bodhi update for a non-auth reason."""

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__("Failed to submit Bodhi update. Check your Kerberos ticket and dist-git branch state.")


def update(
    repo_dir: Path,
    update_type: str,
    severity: str,
    bugs: list[str] | None = None,
    stable_karma: int = 1,
) -> None:
    """Submit a Bodhi update via ``fedpkg update --notes-file changelog``.

    The ``changelog`` file at the root of the dist-git checkout is used as the
    update notes, so the caller must ensure the checkout is on the correct branch
    before invoking this function.

    Args:
        repo_dir: Path to the dist-git repository checkout (on the target branch).
        update_type: Bodhi update type (e.g. ``"enhancement"``, ``"bugfix"``,
            ``"security"``).
        severity: Bodhi severity level (e.g. ``"unspecified"``, ``"low"``,
            ``"medium"``, ``"high"``, ``"urgent"``).
        bugs: Optional list of bug IDs to associate with the update
            (e.g. ``["1234567", "7654321"]``).
        stable_karma: Stable karma threshold. Must be at least 1 (default: 1).

    Raises:
        AuthenticationError: If the failure looks like an auth/connectivity issue.
        UpdateSubmissionError: For any other update submission failure.
    """
    args = [
        "update",
        "--type",
        update_type,
        "--severity",
        severity,
        "--notes-file",
        "changelog",
        "--stable-karma",
        str(stable_karma),
    ]
    if bugs:
        args.extend(["--bugs"] + bugs)

    run_fedpkg(args, repo_dir, error_cls=UpdateSubmissionError)
