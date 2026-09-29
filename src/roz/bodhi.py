"""Bodhi update submission via bodhi-client."""

import subprocess

from pathlib import Path

from roz.fedpkg import AuthenticationError


BODHI_BIN: list[str] = ["/usr/bin/bodhi"]

# Updates to rawhide are done automatically after builds to that target are successful.
BODHI_SKIP_BRANCHES: set[str] = {"rawhide"}


class UpdateSubmissionError(Exception):
    """Raised when bodhi-client fails to submit an update for a non-auth reason."""

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(
            f"Failed to submit Bodhi update. "
            f"Check your Kerberos ticket and dist-git branch state.\n{details}"
        )


def run_bodhi(args: list[str], cwd: Path, error_cls: type[Exception]) -> None:
    cmd = BODHI_BIN + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)  # noqa: S603
    if result.stderr:
        stderr_lower = result.stderr.lower()
        if any(s in stderr_lower for s in ("kinit", "kerberos", "401", "403", "authentication", "unauthorized")):
            raise AuthenticationError(result.stderr.strip())
        raise error_cls(result.stderr.strip())
    if result.stdout:
        print(result.stdout.strip())


def update(
    cwd: Path,
    update_type: str,
    severity: str,
    koji_build: str,
    notes: str,
    bugs: list[str] | None = None,
    stable_karma: int = 1,
    unstable_karma: int = -3,
    stable_days: int = 7,
) -> None:
    """Submit a Bodhi update via ``bodhi updates new``.

    Args:
        cwd: Working directory for the bodhi subprocess.
        update_type: Bodhi update type (e.g. ``"enhancement"``, ``"bugfix"``,
            ``"security"``).
        severity: Bodhi severity level (e.g. ``"unspecified"``, ``"low"``,
            ``"medium"``, ``"high"``, ``"urgent"``).
        koji_build: Koji build NVR to submit (e.g. ``goose-1.45.0-1.fc45``).
        notes: Update notes shown in Bodhi.
        bugs: Optional list of bug IDs to associate with the update.
        stable_karma: Stable karma threshold (default: 1).
        unstable_karma: Unstable karma threshold (default: -3).
        stable_days: Days in testing before auto-promotion (default: 7).

    Raises:
        AuthenticationError: If the failure looks like an auth/connectivity issue.
        UpdateSubmissionError: For any other update submission failure.
    """
    args = [
        "updates", "new",
        "--type", update_type,
        "--severity", severity,
        "--notes", notes,
        "--request", "testing",
        "--autotime",
        "--stable-days", str(stable_days),
        "--autokarma",
        "--stable-karma", str(stable_karma),
        "--unstable-karma", str(unstable_karma),
        *(["--bugs"] + bugs if bugs else []),
        koji_build,
    ]

    run_bodhi(args, cwd, error_cls=UpdateSubmissionError)
