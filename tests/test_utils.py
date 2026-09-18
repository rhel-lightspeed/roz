import shutil

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from roz.utils import _BODHI_NOTES_MAX, resolve_branches, truncate_changelog


# ---------------------------------------------------------------------------
# truncate_changelog
# ---------------------------------------------------------------------------

FIXTURE = Path(__file__).parent / "fixtures" / "changelog"

# Enough old entries to push the fixture past the Bodhi limit.
_FILLER = "* Mon Jan 01 2024 dev <dev@example.com> - 0.1.0-1\n- old\n" * 500


def _copy(tmp_path, extra: str = "") -> Path:
    dest = tmp_path / "changelog"
    shutil.copy(FIXTURE, dest)
    if extra:
        with dest.open("a", encoding="utf-8") as f:
            f.write(extra)
    return dest


def test_fixture_within_limit_is_not_modified(tmp_path):
    p = _copy(tmp_path)
    original = p.read_text(encoding="utf-8")
    truncate_changelog(p)
    assert p.read_text(encoding="utf-8") == original


def test_over_limit_keeps_only_first_entry(tmp_path):
    p = _copy(tmp_path, extra=_FILLER)
    assert len(p.read_text(encoding="utf-8")) > _BODHI_NOTES_MAX

    first_entry_header = FIXTURE.read_text(encoding="utf-8").splitlines()[0]
    second_entry_header = "* Thu Jun 25 2026 thepetk <thepetk@gmail.com> - 1.39.0-1"

    truncate_changelog(p)
    result = p.read_text(encoding="utf-8")

    assert result.startswith(first_entry_header)
    assert second_entry_header not in result
    assert len(result) <= _BODHI_NOTES_MAX


def test_no_entry_header_falls_back_to_char_limit(tmp_path):
    content = "no changelog header here\n" * 10_000
    p = tmp_path / "changelog"
    p.write_text(content, encoding="utf-8")
    truncate_changelog(p)
    assert len(p.read_text(encoding="utf-8")) == _BODHI_NOTES_MAX


def test_oversized_single_entry_is_hard_truncated(tmp_path):
    header = "* Mon Jan 01 2026 dev <dev@example.com> - 1.0.0-1\n"
    content = header + "- line\n" * 10_000
    p = tmp_path / "changelog"
    p.write_text(content, encoding="utf-8")
    truncate_changelog(p)
    result = p.read_text(encoding="utf-8")
    assert result.startswith(header)
    assert len(result) == _BODHI_NOTES_MAX


# ---------------------------------------------------------------------------
# resolve_branches
# ---------------------------------------------------------------------------

def _project(name: str, branches: list[str], forge: str = "pagure") -> MagicMock:
    p = MagicMock()
    p.NAME = name
    p.DIST_GIT_BRANCHES = {forge: branches}
    return p


def test_resolve_branches_returns_all_when_none_requested():
    valid = ["rawhide", "f45", "f44"]
    project = _project("goose", valid)
    assert resolve_branches(project, "pagure", None) == valid


def test_resolve_branches_returns_requested_subset():
    project = _project("goose", ["rawhide", "f45", "f44", "f43"])
    assert resolve_branches(project, "pagure", ["f45", "f44"]) == ["f45", "f44"]


def test_resolve_branches_raises_on_unknown_branch():
    project = _project("goose", ["rawhide", "f45"])
    with pytest.raises(SystemExit) as exc:
        resolve_branches(project, "pagure", ["f45", "f99"])
    assert "f99" in str(exc.value)


def test_resolve_branches_raises_lists_all_unknown_sorted():
    project = _project("goose", ["rawhide", "f45"])
    with pytest.raises(SystemExit) as exc:
        resolve_branches(project, "pagure", ["f99", "f100", "f45"])
    msg = str(exc.value)
    assert "f100" in msg
    assert "f99" in msg
    assert msg.index("f100") < msg.index("f99")
