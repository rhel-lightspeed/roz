import re

from pathlib import Path

from roz.fedpkg import run_fedpkg


_TASK_URL_RE = re.compile(r"https?://\S+taskinfo\S+")


class BuildSubmissionError(Exception):
    """Raised when fedpkg fails to submit a build for a non-auth reason."""

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__("Failed to submit build to Koji. Check your spec file and dist-git branch state.")


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
    args = []
    if scratch_build:
        args.append("scratch-build")
    else:
        args.append("build")

    # When we perform regular builds, we want to do it for all arches.
    # Only scratch-builds should be triggered with specific arches.
    if arches and scratch_build:
        args.extend(["--arches", arches])

    # We don't want the process to be hanging.
    args.append("--nowait")

    output = run_fedpkg(args, repo_dir, error_cls=BuildSubmissionError)
    match = _TASK_URL_RE.search(output)
    return match.group(0) if match else None
