"""Git operations for downstream-release."""

import subprocess
import tempfile

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from downstream_release.const import GIT


@contextmanager
def clone(repo_url: str, branch: str = "main") -> Generator[Path]:
    """Clone a repo into a temporary directory and yield its path.

    The temporary directory — and everything in it — is cleaned up
    when the context manager exits.
    """
    with tempfile.TemporaryDirectory(prefix="downstream-release-") as tmpdir:
        repo_dir = Path(tmpdir) / "repo"

        subprocess.run(  # noqa: S603
            [GIT, "clone", "--branch", branch, "--depth", "1", repo_url, str(repo_dir)],
            cwd=repo_dir.parent,
            check=True,
        )

        yield repo_dir
