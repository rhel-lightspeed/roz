from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from roz.packages.goose import GoosePackage


KOJI_BUILD = "goose-1.45.0-1.fc45"


@pytest.fixture
def goose():
    return GoosePackage()


@pytest.fixture
def run_open_pr():
    """Fixture factory: runs _open_pull_request with all external I/O mocked.

    Returns (mock_open_pr, mock_commit) so callers can assert on either.
    """

    def _run(branches, version, title_template=None, **kwargs):
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

    return _run


@pytest.mark.parametrize(
    "title_template,expected_commit",
    [
        (None, "Rebase for goose 1.45.0"),
        ("Rebase goose {version}", "Rebase goose 1.45.0"),
        ("My title", "My title"),
    ],
)
def test_commit_message(run_open_pr, title_template, expected_commit):
    _, mock_commit = run_open_pr(["rawhide"], "1.45.0", title_template=title_template)
    assert mock_commit.call_args.args[1] == expected_commit


def test_commit_message_same_across_branches(run_open_pr):
    _, mock_commit = run_open_pr(["rawhide", "f45"], "1.45.0", title_template="Rebase {version}")
    messages = [c.args[1] for c in mock_commit.call_args_list]
    assert messages == ["Rebase 1.45.0", "Rebase 1.45.0"]


@pytest.mark.parametrize(
    "branches,title_template,expected_pr_titles",
    [
        (["rawhide"], None, ["Rebase for goose 1.45.0 for rawhide"]),
        (
            ["rawhide", "f45"],
            None,
            ["Rebase for goose 1.45.0 for rawhide", "Rebase for goose 1.45.0 for f45"],
        ),
        (["rawhide"], "Rebase goose {version}", ["Rebase goose 1.45.0 for rawhide"]),
        (
            ["rawhide", "f45", "f44"],
            "Goose {version}",
            ["Goose 1.45.0 for rawhide", "Goose 1.45.0 for f45", "Goose 1.45.0 for f44"],
        ),
        (["rawhide"], "My title", ["My title for rawhide"]),
    ],
)
def test_pr_title(run_open_pr, branches, title_template, expected_pr_titles):
    mock_open_pr, _ = run_open_pr(branches, "1.45.0", title_template=title_template)
    titles = [c.kwargs["title"] for c in mock_open_pr.call_args_list]
    assert titles == expected_pr_titles


def test_update_queries_koji_per_branch(goose):
    with (
        patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD) as mock_koji,
        patch("roz.packages.goose.bodhi.update"),
    ):
        goose.update("enhancement", "unspecified", None, ["f45", "f44"], None, 1, -3, 7)
    assert mock_koji.call_args_list == [
        call("goose", "f45-testing"),
        call("goose", "f44-testing"),
    ]


def test_update_auto_generates_notes_from_nvr(goose):
    with (
        patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD),
        patch("roz.packages.goose.bodhi.update") as mock_bodhi,
    ):
        goose.update("enhancement", "unspecified", None, ["f45"], None, 1, -3, 7)
    notes = mock_bodhi.call_args[0][4]
    assert notes == f"Update to {KOJI_BUILD}."


def test_update_passes_user_notes_unchanged(goose):
    with (
        patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD),
        patch("roz.packages.goose.bodhi.update") as mock_bodhi,
    ):
        goose.update("enhancement", "unspecified", None, ["f45"], "custom notes", 1, -3, 7)
    notes = mock_bodhi.call_args[0][4]
    assert notes == "custom notes"


def test_update_prints_progress_per_branch(goose, capsys):
    with (
        patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD),
        patch("roz.packages.goose.bodhi.update"),
    ):
        goose.update("enhancement", "unspecified", None, ["f45", "f44"], None, 1, -3, 7)
    out = capsys.readouterr().out
    assert f"[f45] Bodhi update submitted: {KOJI_BUILD}" in out
    assert f"[f44] Bodhi update submitted: {KOJI_BUILD}" in out
