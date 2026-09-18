from unittest.mock import MagicMock, patch

import pytest

from roz.bodhi import UpdateSubmissionError, update
from roz.fedpkg import AuthenticationError


FIXTURE_NOTES = "* Thu Aug 20 2026 thepetk <thepetk@gmail.com> - 1.45.0-1\n- Update to version 1.45.0\n"
KOJI_BUILD = "goose-1.45.0-1.fc45"


def make_repo(tmp_path, notes: str = FIXTURE_NOTES) -> None:
    (tmp_path / "changelog").write_text(notes, encoding="utf-8")
    return tmp_path


def test_update_passes_notes_arg_when_provided(tmp_path):
    make_repo(tmp_path)
    with patch("roz.bodhi.run_bodhi") as mock_run:
        update(tmp_path, "enhancement", "unspecified", KOJI_BUILD, notes="custom notes")
    args = mock_run.call_args[0][0]
    assert "--notes" in args
    assert args[args.index("--notes") + 1] == "custom notes"


def test_update_reads_changelog_when_notes_not_provided(tmp_path):
    make_repo(tmp_path, notes=FIXTURE_NOTES)
    with patch("roz.bodhi.run_bodhi") as mock_run:
        update(tmp_path, "enhancement", "unspecified", KOJI_BUILD)
    args = mock_run.call_args[0][0]
    assert args[args.index("--notes") + 1] == FIXTURE_NOTES


def test_update_appends_koji_build_as_last_arg(tmp_path):
    make_repo(tmp_path)
    with patch("roz.bodhi.run_bodhi") as mock_run:
        update(tmp_path, "enhancement", "unspecified", KOJI_BUILD, notes="n")
    args = mock_run.call_args[0][0]
    assert args[-1] == KOJI_BUILD


def test_update_includes_required_bodhi_flags(tmp_path):
    make_repo(tmp_path)
    with patch("roz.bodhi.run_bodhi") as mock_run:
        update(tmp_path, "enhancement", "unspecified", KOJI_BUILD, notes="n",
               stable_karma=2, unstable_karma=-2, stable_days=14)
    args = mock_run.call_args[0][0]
    assert args[:2] == ["updates", "new"]
    assert "--request" in args and args[args.index("--request") + 1] == "testing"
    assert "--autotime" in args
    assert "--autokarma" in args
    assert "--stable-days" in args and args[args.index("--stable-days") + 1] == "14"
    assert "--stable-karma" in args and args[args.index("--stable-karma") + 1] == "2"
    assert "--unstable-karma" in args and args[args.index("--unstable-karma") + 1] == "-2"


def test_update_appends_bugs_when_provided(tmp_path):
    make_repo(tmp_path)
    with patch("roz.bodhi.run_bodhi") as mock_run:
        update(tmp_path, "enhancement", "unspecified", KOJI_BUILD, notes="n", bugs=["2514571"])
    args = mock_run.call_args[0][0]
    assert "--bugs" in args
    assert "2514571" in args


def test_run_bodhi_raises_auth_error_on_kerberos_signal(tmp_path):
    result = MagicMock(returncode=1, stderr="kerberos ticket expired")
    with patch("subprocess.run", return_value=result):
        with pytest.raises(AuthenticationError):
            from roz.bodhi import run_bodhi
            run_bodhi(["updates", "new"], tmp_path, error_cls=UpdateSubmissionError)


def test_run_bodhi_raises_update_error_on_other_failure(tmp_path):
    result = MagicMock(returncode=1, stderr="Build does not exist: goose-1.45.0-2.fc45")
    with patch("subprocess.run", return_value=result):
        with pytest.raises(UpdateSubmissionError) as exc:
            from roz.bodhi import run_bodhi
            run_bodhi(["updates", "new"], tmp_path, error_cls=UpdateSubmissionError)
        assert "goose-1.45.0-2.fc45" in str(exc.value)


def test_run_bodhi_returns_stdout_on_success(tmp_path):
    result = MagicMock(returncode=0, stdout="Update created: FEDORA-2026-abc123\n")
    with patch("subprocess.run", return_value=result):
        from roz.bodhi import run_bodhi
        out = run_bodhi(["updates", "new"], tmp_path, error_cls=UpdateSubmissionError)
    assert "FEDORA-2026-abc123" in out
