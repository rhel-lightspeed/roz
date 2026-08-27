"""Shared fedpkg subprocess helper used by koji and bodhi modules."""

import subprocess

from pathlib import Path


_AUTH_SIGNALS = ("kinit", "kerberos", "401", "403", "authentication", "unauthorized")

FEDPKG_BIN: list[str] = ["/usr/bin/fedpkg"]


class AuthenticationError(Exception):
    """Raised when fedpkg fails due to an authentication or connectivity issue."""

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(
            "Authentication failure. Run `fkinit -u <your-user>` to get a valid Kerberos ticket and try again."
        )


def run_fedpkg(args: list[str], cwd: Path, error_cls: type[Exception]) -> str:
    """Run a fedpkg command and return its stdout.

    Args:
        args: Full command list including the fedpkg binary.
        cwd: Directory to run the command in (dist-git checkout).
        error_cls: Exception class to raise on non-auth, non-zero exits
            (e.g. ``BuildSubmissionError``, ``UpdateSubmissionError``).

    Raises:
        AuthenticationError: If stderr contains authentication-related signals.
        error_cls: For any other non-zero exit.
    """
    cmd = FEDPKG_BIN.copy()
    cmd.extend(args)

    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        stderr_lower = result.stderr.lower()
        if any(signal in stderr_lower for signal in _AUTH_SIGNALS):
            raise AuthenticationError(result.stderr.strip())
        raise error_cls(result.stderr.strip())
    return result.stdout
