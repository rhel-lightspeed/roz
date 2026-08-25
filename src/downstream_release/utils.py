"""General-purpose utilities for downstream-release."""

import subprocess

from pathlib import Path


MAKE_BIN = "/usr/bin/make"


def run_make(repo_dir: Path, target: str) -> None:
    """Run a make target in the given directory.

    Args:
        repo_dir: Path to the directory containing the Makefile.
        target: Make target to run (e.g. ``"vendor-tarball"``).
    """
    subprocess.run(  # noqa: S603
        [MAKE_BIN, target],
        cwd=repo_dir,
        check=True,
    )
