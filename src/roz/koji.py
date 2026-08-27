import re
import subprocess

from pathlib import Path


_AUTH_SIGNALS = ("kinit", "kerberos", "401", "403", "authentication", "unauthorized")
_TASK_URL_RE = re.compile(r"https?://\S+taskinfo\S+")


class AuthenticationError(Exception):
    """Raised when fedpkg fails due to an authentication or connectivity issue."""

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(
            "Authentication failure. Run `fkinit -u <your-user>` to get a valid Kerberos ticket and try again."
        )


class BuildSubmissionError(Exception):
    """Raised when fedpkg fails to submit a build for a non-auth reason."""

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__("Failed to submit build to Koji. Check your spec file and dist-git branch state.")


def _run_fedpkg(cmd: list[str], cwd: Path) -> str:
    """Run a fedpkg command and return its stdout.

    Args:
        cmd: Full command list including the fedpkg binary.
        cwd: Directory to run the command in (dist-git checkout).

    Raises:
        AuthenticationError: If stderr contains authentication-related signals.
        BuildSubmissionError: For any other non-zero exit.
    """
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        stderr_lower = result.stderr.lower()
        if any(signal in stderr_lower for signal in _AUTH_SIGNALS):
            raise AuthenticationError(result.stderr.strip())
        raise BuildSubmissionError(result.stderr.strip())
    return result.stdout


def build(repo_dir: Path, arches: str | None = None, scratch_build: bool = False) -> str | None:
    """Submit a build to Koji via ``fedpkg (scratch-)build --nowait``.

    Args:
        repo_dir: Path to the dist-git repository checkout (on the target branch).
        scratch_build: When ``True``, runs ``fedpkg scratch-build`` instead of ``fedpkg build``.
        arches: Optional space-separated architecture string passed to ``--arches``
            (e.g. ``"x86_64 aarch64"``), already joined by the caller. When ``None``,
            fedpkg uses the default architectures for the build target.

    Returns:
        The Koji task URL parsed from fedpkg output, or ``None`` if it could
        not be found in the output.

    Raises:
        AuthenticationError: If the failure looks like an auth/connectivity issue.
        BuildSubmissionError: For any other submission failure.
    """
    build_cmd = ["/usr/bin/fedpkg"]
    if scratch_build:
        build_cmd.append("scratch-build")
    else:
        build_cmd.append("build")

    # When we perform regular builds, we want to do it for all arches.
    # Only scratch-builds should be triggered with specific arches.
    if arches and scratch_build:
        build_cmd.extend(["--arches", arches])

    # We don't want the process to be hanging.
    build_cmd.append("--nowait")

    output = _run_fedpkg(build_cmd, repo_dir)
    match = _TASK_URL_RE.search(output)
    return match.group(0) if match else None
