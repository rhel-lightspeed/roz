"""Tests for GoosePackage._open_pull_request title/commit logic and the --title CLI argument."""

import argparse

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from roz.cli import _build_parser
from roz.commands import propose as propose_cmd
from roz.packages.goose import GoosePackage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(branches, version, title_template=None, **kwargs):
    """Run _open_pull_request with all external I/O mocked out.

    Returns (mock_open_pr, mock_commit) so callers can assert on both.
    """
    package = GoosePackage()

    mock_project = MagicMock()
    mock_project.repo = "goose"

    mock_clone = MagicMock()
    mock_clone.return_value.__enter__ = MagicMock(return_value=Path("/tmp/fake-distgit"))
    mock_clone.return_value.__exit__ = MagicMock(return_value=False)

    with (
        patch("roz.packages.goose.forge.get_project", return_value=mock_project),
        patch("roz.packages.goose.forge.get_fork_push_url", return_value="ssh://fork"),
        patch("roz.packages.goose.forge.get_fork_username", return_value="testuser"),
        patch("roz.packages.goose.forge.open_pr") as mock_open_pr,
        patch("roz.packages.goose.git.clone", mock_clone),
        patch("roz.packages.goose.git.checkout"),
        patch("roz.packages.goose.git.create_branch"),
        patch("roz.packages.goose.srpm.import_srpm"),
        patch("roz.packages.goose.git.commit") as mock_commit,
        patch("roz.packages.goose.git.push"),
    ):
        package._open_pull_request(
            branches=branches,
            version=version,
            forge_name="pagure",
            srpm_path=Path("/tmp/fake.src.rpm"),
            title_template=title_template,
            **kwargs,
        )
        return mock_open_pr, mock_commit


# ---------------------------------------------------------------------------
# _open_pull_request — default behaviour (no --title)
# ---------------------------------------------------------------------------


def test_default_commit_message():
    _, mock_commit = _run(["rawhide"], "1.45.0")
    assert mock_commit.call_args.args[1] == "Rebase for goose 1.45.0"


def test_default_pr_title():
    mock_open_pr, _ = _run(["rawhide"], "1.45.0")
    assert mock_open_pr.call_args.kwargs["title"] == "Rebase for goose 1.45.0 for rawhide"


def test_default_pr_title_per_branch():
    mock_open_pr, _ = _run(["rawhide", "f45"], "1.45.0")
    titles = [c.kwargs["title"] for c in mock_open_pr.call_args_list]
    assert titles == [
        "Rebase for goose 1.45.0 for rawhide",
        "Rebase for goose 1.45.0 for f45",
    ]


# ---------------------------------------------------------------------------
# _open_pull_request — custom --title
# ---------------------------------------------------------------------------


def test_custom_title_sets_commit_message():
    _, mock_commit = _run(["rawhide"], "1.45.0", title_template="Rebase goose {version}")
    assert mock_commit.call_args.args[1] == "Rebase goose 1.45.0"


def test_custom_title_derives_pr_title():
    mock_open_pr, _ = _run(["rawhide"], "1.45.0", title_template="Rebase goose {version}")
    assert mock_open_pr.call_args.kwargs["title"] == "Rebase goose 1.45.0 for rawhide"


def test_custom_title_plain_string():
    mock_open_pr, mock_commit = _run(["rawhide"], "1.45.0", title_template="My title")
    assert mock_commit.call_args.args[1] == "My title"
    assert mock_open_pr.call_args.kwargs["title"] == "My title for rawhide"


def test_custom_title_pr_title_per_branch():
    mock_open_pr, _ = _run(["rawhide", "f45", "f44"], "1.45.0", title_template="Goose {version}")
    titles = [c.kwargs["title"] for c in mock_open_pr.call_args_list]
    assert titles == [
        "Goose 1.45.0 for rawhide",
        "Goose 1.45.0 for f45",
        "Goose 1.45.0 for f44",
    ]


def test_commit_message_same_across_branches():
    _, mock_commit = _run(["rawhide", "f45"], "1.45.0", title_template="Rebase {version}")
    messages = [c.args[1] for c in mock_commit.call_args_list]
    assert messages == ["Rebase 1.45.0", "Rebase 1.45.0"]


# ---------------------------------------------------------------------------
# CLI — --title argument parsing
# ---------------------------------------------------------------------------


def test_cli_title_is_parsed():
    parser = _build_parser()
    args = parser.parse_args(["propose", "--project", "goose", "--forge", "pagure", "--title", "My title"])
    assert args.title == "My title"


def test_cli_title_defaults_to_none():
    parser = _build_parser()
    args = parser.parse_args(["propose", "--project", "goose", "--forge", "pagure"])
    assert args.title is None


def test_cli_title_forwarded_to_propose():
    """propose.run() passes title= to project.propose()."""
    mock_project = MagicMock()
    mock_branches = ["rawhide"]

    with (
        patch("roz.commands.propose.PACKAGES_MAP", {"goose": mock_project}),
        patch("roz.commands.propose.utils.resolve_branches", return_value=mock_branches),
    ):
        args = argparse.Namespace(
            project="goose",
            forge="pagure",
            branches=None,
            offline=False,
            yes=False,
            keep=False,
            resolves=None,
            title="Custom {version}",
        )
        propose_cmd.run(args)

    mock_project.propose.assert_called_once_with(
        forge_name="pagure",
        branches=mock_branches,
        offline=False,
        yes=False,
        keep=False,
        resolves=None,
        title="Custom {version}",
    )
