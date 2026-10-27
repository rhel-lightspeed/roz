import argparse

from unittest.mock import patch

from roz.cli import _build_parser
from roz.commands import propose as propose_cmd


def test_cli_title_is_parsed():
    parser = _build_parser()
    args = parser.parse_args(["propose", "--project", "goose", "--forge", "pagure", "--title", "My title"])
    assert args.title == "My title"


def test_cli_title_defaults_to_none():
    parser = _build_parser()
    args = parser.parse_args(["propose", "--project", "goose", "--forge", "pagure"])
    assert args.title is None


def test_cli_title_forwarded_to_propose():
    mock_project = mock_branches = None
    mock_project = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()
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
