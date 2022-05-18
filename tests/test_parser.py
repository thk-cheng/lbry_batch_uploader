import pytest
from lbry_batch_uploader.parser import Parser
from typing import Optional, Sequence


def assert_namespace(
    p: Parser,
    file_directory: str,
    channel_name: str,
    optimize_file: bool,
    port: int,
    bid: str,
    fee_amount: str,
    tags: list,
    languages: list,
    license: Optional[str],
    license_url: Optional[str],
) -> None:
    """Helper function for asserting namespace."""
    assert p.args.file_directory == file_directory
    assert p.args.channel_name == channel_name
    assert p.args.optimize_file is optimize_file
    assert p.args.port == port
    assert p.args.bid == bid
    assert p.args.fee_amount == fee_amount
    assert p.args.tags == tags
    assert p.args.languages == languages

    if license is None:
        assert p.args.license is license
    else:
        assert p.args.license == license

    if license_url is None:
        assert p.args.license_url is license_url
    else:
        assert p.args.license_url == license_url


def check_no_args(p: Parser, err_msg_args=None) -> None:
    """Helper function for checking the 'args' attribute is not present."""
    if err_msg_args is None:
        err_msg_args = "'Parser' object has no attribute 'args'"
    with pytest.raises(AttributeError, match=err_msg_args):
        _ = p.args


@pytest.fixture
def parser() -> Parser:
    """Fixture for creating a Parser instance."""
    return Parser()


class TestPositionalArgs:
    """Tests related to positional arguments."""

    @pytest.mark.parametrize("args", [("path/to/dir", "test_ch")])
    def test_pos_args_all(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when both positional arguments are present."""
        parser.parse(args)

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

        assert_namespace(
            parser,
            "path/to/dir",
            "test_ch",
            False,
            5279,
            "0.0001",
            "0",
            [],
            ["en"],
            None,
            None,
        )

    @pytest.mark.parametrize(
        "args",
        [
            (),
            ("path/to/dir",),
            ("path/to/dir", "--optimize-file"),
            ("path/to/dir", "--bid", "0.5"),
        ],
    )
    def test_pos_args_missing(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when only zero/one positional argument is present."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        missing_args = "file_directory, channel_name" if not args else "channel_name"
        err_msg = (
            f"{parser.argparser.prog}: error"
            + f": the following arguments are required: {missing_args}"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize("args", [("path/to/dir", "test_ch", "0.1")])
    def test_pos_args_extra(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when more than two positional arguments are specified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = (
            f"{parser.argparser.prog}: error" + f": unrecognized arguments: {args[-1]}"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)


class TestOptionalArgs:
    """Test related to optional arguments."""

    @pytest.mark.parametrize(
        "args",
        [
            (
                "path/to/dir",
                "test_ch",
                "--optimize-file",
                "--port",
                "5000",
                "--bid",
                "0.5",
                "--fee-amount",
                "0.1",
                "--tags",
                "tag0",
                "tag1",
                "--languages",
                "en",
                "zh",
                "--license",
                "Other",
                "--license-url",
                "https://www.123.xyz",
            )
        ],
    )
    def test_opt_args_all(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when all optional arguments are specified."""
        parser.parse(args)

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

        assert_namespace(
            parser,
            "path/to/dir",
            "test_ch",
            True,
            5000,
            "0.5",
            "0.1",
            ["tag0", "tag1"],
            ["en", "zh"],
            "Other",
            "https://www.123.xyz",
        )

    @pytest.mark.parametrize(
        "args", [("path/to/dir", "test_ch", "--optimize-file", "0.1")]
    )
    def test_optimize_file_misspec(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --optimize-file is misspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = (
            f"{parser.argparser.prog}: error" + f": unrecognized arguments: {args[-1]}"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize(
        "args",
        [
            ("path/to/dir", "test_ch", "--port"),
            ("path/to/dir", "test_ch", "--bid"),
            ("path/to/dir", "test_ch", "--fee-amount"),
        ],
    )
    def test_port_bid_fee_misspec(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --port, --bid or --fee-amount is misspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = (
            f"{parser.argparser.prog}: error: argument {args[-1]}"
            + ": expected one argument"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize(
        "args",
        [
            ("path/to/dir", "test_ch", "--port", "1000", "2000"),
            ("path/to/dir", "test_ch", "--bid", "0.1", "0.2"),
            ("path/to/dir", "test_ch", "--fee-amount", "1.0", "2.0"),
        ],
    )
    def test_port_bid_fee_extra(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --port, --bid or --fee-amount are overspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = (
            f"{parser.argparser.prog}: error" + f": unrecognized arguments: {args[-1]}"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize("args", [("path/to/dir", "test_ch", "--tags")])
    def test_tags_misspec(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --tags is misspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = (
            f"{parser.argparser.prog}: error: argument --tags"
            + ": expected at least one argument"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize(
        "args",
        [
            ("path/to/dir", "test_ch", "--languages"),
            ("path/to/dir", "test_ch", "--languages", "abc"),
            ("path/to/dir", "test_ch", "--languages", "en", "abc"),
        ],
    )
    def test_languages_misspec(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --languages is misspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = f"{parser.argparser.prog}: error: argument --languages"
        if len(args) == 3:
            err_msg += ": expected at least one argument"
        else:
            err_msg += f": invalid choice: '{args[-1]}'"
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize(
        "args",
        [
            ("path/to/dir", "test_ch", "--license"),
            ("path/to/dir", "test_ch", "--license", "abc"),
        ],
    )
    def test_license_misspec(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --license is misspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = f"{parser.argparser.prog}: error: argument --license"
        if len(args) == 3:
            err_msg += ": expected one argument"
        else:
            err_msg += f": invalid choice: '{args[-1]}'"
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize(
        "args",
        [
            ("path/to/dir", "test_ch", "--license", "Other"),
            (
                "path/to/dir",
                "test_ch",
                "--license",
                "Public Domain",
                "--license-url",
                "https://www.123.xyz",
            ),
        ],
    )
    def test_license_url_misspec(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --license is misspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = (
            f"{parser.argparser.prog}: error"
            + ": --license-url should be specified "
            + "if and only if --license='Other'"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)

    @pytest.mark.parametrize(
        "args",
        [
            ("path/to/dir", "test_ch", "--license", "Other", "--license-url"),
            ("path/to/dir", "test_ch", "--license-url"),
            ("path/to/dir", "test_ch", "--license", "Public Domain", "--license-url"),
        ],
    )
    def test_license_url_missing(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when --license is misspecified."""
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        err_msg = (
            f"{parser.argparser.prog}: error: argument {args[-1]}"
            + ": expected one argument"
        )
        assert captured.out == ""
        assert err_msg in captured.err
        check_no_args(parser)


class TestHelpOption:
    """Tests related to the help option."""

    @pytest.mark.parametrize("args", ["-h", "--help"])
    def test_help(
        self, parser: Parser, args: Sequence[str], capsys: pytest.CaptureFixture
    ) -> None:
        """Test when -h or --help is specified."""
        with pytest.raises(SystemExit):
            parser.parse([args])

        captured = capsys.readouterr()
        help_string_head = f"usage: {parser.argparser.prog} [-h]"
        assert help_string_head in captured.out
        assert captured.err == ""
        check_no_args(parser)
