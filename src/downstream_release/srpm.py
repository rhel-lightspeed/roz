"""SRPM build operations for downstream-release."""

import subprocess

from pathlib import Path

from downstream_release.const import FEDPKG


def build(repo_dir: Path) -> Path:
    """Run fedpkg srpm in an already-cloned repo and return the SRPM path."""
    subprocess.run(  # noqa: S603
        [FEDPKG, "srpm"],
        cwd=repo_dir,
        check=True,
    )

    srpms = list(repo_dir.glob("*.src.rpm"))
    if not srpms:
        msg = f"No .src.rpm found in {repo_dir} after fedpkg srpm"
        raise FileNotFoundError(msg)

    return srpms[0]
