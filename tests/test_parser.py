import pytest
from lbry_batch_uploader.parser import Parser


@pytest.fixture
def parser():
    return Parser()


def assert_namespace(
    p,
    file_directory, channel_name,
    optimize_file, port, bid, fee_amount,
    tags, languages, license, license_url
):
    assert p.args.file_directory == file_directory
    assert p.args.channel_name == channel_name

    if optimize_file:
        assert p.args.optimize_file
    else:
        assert not p.args.optimize_file

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


class TestPositionalArgs:
    @pytest.mark.parametrize(
        "args",
        [("path/to/dir", "test_ch")]
    )
    def test_pos_args_all(self, parser, args, capsys):
        parser.parse(args)

        captured = capsys.readouterr()
        assert (captured.out == "") and (captured.err == "")

        assert_namespace(
            parser,
            "path/to/dir", "test_ch",
            False, 5279, 0.0001, 0.,
            [], ["en"], None, None
        )

    @pytest.mark.parametrize(
        "args",
        [
            (),
            ("path/to/dir",),
            ("path/to/dir", "--optimize-file"),
            ("path/to/dir", "--bid", "0.5")
        ]
    )
    def test_pos_args_missing(self, parser, args, capsys):
        with pytest.raises(SystemExit):
            parser.parse(args)

        captured = capsys.readouterr()
        missing_args = "file_directory, channel_name" \
                        if not args else "channel_name"
        err_msg = f"{parser.argparser.prog}: error: " + \
                    "the following arguments are required: " + \
                    f"{missing_args}"
        assert captured.out == ""
        assert err_msg in captured.err

        err_msg_args = "'Parser' object has no attribute 'args'"
        with pytest.raises(AttributeError,match=err_msg_args):
            args = parser.args


class TestHelpOption:
    @pytest.mark.parametrize(
        "args",
        ["-h", "--help"]
    )
    def test_help(self, parser, args, capsys):
        with pytest.raises(SystemExit):
            parser.parse([args])

        captured = capsys.readouterr()
        help_string_head = f"usage: {parser.argparser.prog} [-h]"
        assert help_string_head in captured.out
        assert captured.err == ""

        err_msg_args = "'Parser' object has no attribute 'args'"
        with pytest.raises(AttributeError,match=err_msg_args):
            args = parser.args
