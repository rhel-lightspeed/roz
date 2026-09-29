from unittest.mock import MagicMock, patch

import pytest

from roz.koji import LatestBuildError, latest_build


_KOJI_SUCCESS = (
    "Build                                     Tag                   Built by\n"
    "----------------------------------------  --------------------  ----------------\n"
    "goose-1.45.0-1.fc45                       f45                   thepetk\n"
)


def test_latest_build_returns_nvr():
    result = MagicMock(returncode=0, stdout=_KOJI_SUCCESS, stderr="")
    with patch("subprocess.run", return_value=result):
        assert latest_build("goose", "f45-build") == "goose-1.45.0-1.fc45"


def test_latest_build_raises_on_nonzero_exit():
    result = MagicMock(returncode=1, stdout="", stderr="No such tag: f99-build")
    with patch("subprocess.run", return_value=result):
        with pytest.raises(LatestBuildError) as exc:
            latest_build("goose", "f99-build")
    assert "No such tag" in str(exc.value)


def test_latest_build_raises_when_no_build_found():
    result = MagicMock(returncode=0, stdout="Build                Tag              Built by\n", stderr="")
    with patch("subprocess.run", return_value=result):
        with pytest.raises(LatestBuildError) as exc:
            latest_build("goose", "f45-build")
    assert "No build found" in str(exc.value)
    assert "goose" in str(exc.value)
    assert "f45-build" in str(exc.value)
