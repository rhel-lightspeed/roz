from unittest.mock import call, patch

import pytest

from roz.packages.goose import GoosePackage


KOJI_BUILD = "goose-1.45.0-1.fc45"


@pytest.fixture
def goose():
    return GoosePackage()


def test_update_queries_koji_per_branch(goose):
    with patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD) as mock_koji, \
         patch("roz.packages.goose.bodhi.update"):
        goose.update("enhancement", "unspecified", None, ["f45", "f44"], None, 1, -3, 7)
    assert mock_koji.call_args_list == [
        call("goose", "f45-build"),
        call("goose", "f44-build"),
    ]


def test_update_auto_generates_notes_from_nvr(goose):
    with patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD), \
         patch("roz.packages.goose.bodhi.update") as mock_bodhi:
        goose.update("enhancement", "unspecified", None, ["f45"], None, 1, -3, 7)
    notes = mock_bodhi.call_args[0][4]
    assert notes == f"Update to {KOJI_BUILD}."


def test_update_passes_user_notes_unchanged(goose):
    with patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD), \
         patch("roz.packages.goose.bodhi.update") as mock_bodhi:
        goose.update("enhancement", "unspecified", None, ["f45"], "custom notes", 1, -3, 7)
    notes = mock_bodhi.call_args[0][4]
    assert notes == "custom notes"


def test_update_prints_progress_per_branch(goose, capsys):
    with patch("roz.packages.goose.koji.latest_build", return_value=KOJI_BUILD), \
         patch("roz.packages.goose.bodhi.update"):
        goose.update("enhancement", "unspecified", None, ["f45", "f44"], None, 1, -3, 7)
    out = capsys.readouterr().out
    assert f"[f45] Bodhi update submitted: {KOJI_BUILD}" in out
    assert f"[f44] Bodhi update submitted: {KOJI_BUILD}" in out
