import pytest
import os
import requests
from requests import RequestException, ConnectionError
from lbry_batch_uploader.parser import Parser
from lbry_batch_uploader.uploader import Uploader, post_req
from typing import Dict, Type
import argparse
import pathlib


class MockResponseVersion:
    """Mocking good request.Resopnse.json for the "version" query."""
    @staticmethod
    def json() -> Dict[str, Dict[str, str]]:
        return {"result": {"version": "0.107.1"}}


class MockResponseFfmpeg:
    """Mocking good request.Resopnse.json for the "ffmpeg_find" query."""
    @staticmethod
    def json() -> Dict[str, Dict[str, bool]]:
        return {"result": {"available": True}}


class MockResponseFfmpegMissing:
    """Mocking bad request.Resopnse.json for the "ffmpeg_find" query."""
    @staticmethod
    def json() -> Dict[str, Dict[str, bool]]:
        return {"result": {"available": False}}


@pytest.fixture
def mock_response_good(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Requests.post() mocked to return {"result": ...}."""

    def mock_post(*args, **kwargs):
        method = kwargs["json"]["method"]
        if method == "version":
            mock_response_instance = MockResponseVersion()
        elif method == "ffmpeg_find":
            mock_response_instance = MockResponseFfmpeg()
        return mock_response_instance

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def mock_response_badport(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Requests.post() mocked to return bad port response."""

    def mock_post(*args, **kwargs):
        method = kwargs["json"]["method"]
        if method == "version":
            port = int(args[0].split(":")[-1])
            err_msg = f"HTTPConnectionPool(host='localhost', {port=})"
            raise ConnectionError(err_msg)
        elif method == "ffmpeg_find":
            mock_response_instance = MockResponseFfmpeg()
        return mock_response_instance

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def mock_response_noffmpeg(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Requests.post() mocked to return missing ffmpeg response."""

    def mock_post(*args, **kwargs):
        method = kwargs["json"]["method"]
        if method == "version":
            mock_response_instance = MockResponseVersion()
        elif method == "ffmpeg_find":
            mock_response_instance = MockResponseFfmpegMissing()
        return mock_response_instance

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def parser() -> Type[Parser]:
    """Fixture for creating a Parser instance."""
    return Parser()


@pytest.fixture
def args_normal(parser: Type[Parser],
                tmp_path: Type[pathlib.Path]) -> Type[argparse.Namespace]:
    """Namespace object, returned by a Parser object."""
    args = [
        str(tmp_path),
        "@batch-upload-testing",
        "--optimize-file",
        "--bid", "0.56",
        "--fee-amount", "1.23",
        "--tags", "tag0", "tag1", "tag2", "tag3", "tag4",
        "--languages", "en",
        "--license", "Other",
        "--license-url", "https://www.123.xyz"
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_wrong_path(parser: Type[Parser]) -> Type[argparse.Namespace]:
    """Namespace object, with wrong file directory."""
    args = [
        "this/is/a/wrong/path",
        "@batch-upload-testing",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_wrong_port0(parser: Type[Parser],
                     tmp_path: Type[pathlib.Path]) -> Type[argparse.Namespace]:
    """Namespace object, with wrong port number."""
    args = [
        str(tmp_path),
        "@batch-upload-testing",
        "--port",  "70000",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_wrong_port1(parser: Type[Parser],
                     tmp_path: Type[pathlib.Path]) -> Type[argparse.Namespace]:
    """Namespace object, with ill-configured port."""
    args = [
        str(tmp_path),
        "@batch-upload-testing",
        "--port",  "9999",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_no_ffmpeg(parser: Type[Parser],
                   tmp_path: Type[pathlib.Path]) -> Type[argparse.Namespace]:
    """Namespace object, with ill-configured port."""
    args = [
        str(tmp_path),
        "@batch-upload-testing",
        "--optimize-file",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def uploader_normal(args_normal: Type[argparse.Namespace],
                    mock_response_good: None) -> Type[Uploader]:
    return Uploader(args_normal)


class TestInit:
    """Test the state of an Uploader instance after __init__"""

    def test_wrong_path(self,
                        args_wrong_path: Type[argparse.Namespace]) -> None:
        """"""
        wrong_path = os.path.abspath(args_wrong_path.file_directory)
        err_msg = f"The directory {wrong_path} does not exist."
        with pytest.raises(FileNotFoundError, match=err_msg):
            _ = Uploader(args_wrong_path)

    def test_wrong_port0(self,
                         args_wrong_port0: Type[argparse.Namespace]) -> None:
        """"""
        wrong_port = args_wrong_port0.port
        err_msg = f"The port {wrong_port} is not between 0 and 65353."
        with pytest.raises(TypeError, match=err_msg):
            _ = Uploader(args_wrong_port0)

    def test_wrong_port1(self,
                         args_wrong_port1: Type[argparse.Namespace],
                         mock_response_badport: None) -> None:
        """"""
        wrong_port = args_wrong_port1.port
        with pytest.raises(RequestException, match=f"port={wrong_port}"):
            _ = Uploader(args_wrong_port1)

    def test_no_ffmpeg(self,
                       args_no_ffmpeg: Type[argparse.Namespace],
                       mock_response_noffmpeg: None,
                       capsys: pytest.CaptureFixture) -> None:
        """"""
        uploader_no_ffmpeg = Uploader(args_no_ffmpeg)
        assert not uploader_no_ffmpeg.base_params["optimize_file"]

        captured = capsys.readouterr()
        msg = "ffmpeg is not configured properly." + \
                "--optimize-file set to False."
        assert msg in captured.out
        assert captured.err == ""

    def test_normal(self, uploader_normal: Type[Uploader]) -> None:
        assert uploader_normal.base_path is not None
        assert uploader_normal.port_url == "http://localhost:5279"

        base_params = uploader_normal.base_params
        assert base_params["channel_name"] == "@batch-upload-testing"
        assert base_params["optimize_file"]
        assert base_params["bid"] == "0.56"
        assert base_params["fee_amount"] == "1.23"
        assert base_params["tags"] == ["tag0", "tag1", "tag2", "tag3", "tag4"]
        assert base_params["languages"] == ["en"]
        assert base_params["license"] == "Other"
        assert base_params["license_url"] == "https://www.123.xyz"


class TestGetReqInfo:
    """Testing the _get_req_info helper function."""

    @pytest.mark.parametrize(
        "req_json, info_type",
        [
            ({"jsonrpc": "2.0","result": {"abc": "123"}}, "result"),
            ({"jsonrpc": "2.0","data": {"abc": "123"}}, "data"),
        ]
    )
    def test_normal(self,
                    uploader_normal: Type[Uploader],
                    req_json: dict,
                    info_type: str) -> None:
        req_info = uploader_normal._get_req_info(req_json, info_type)
        assert req_info == {"abc": "123"}

    @pytest.mark.parametrize(
        "req_json, info_type",
        [
            ({"jsonrpc": "2.0","result": {}}, "abc"),
            ({"jsonrpc": "2.0","data": {}}, "xyz"),
        ]
    )
    def test_wrong_info_type(self,
                             uploader_normal: Type[Uploader],
                             req_json: dict,
                             info_type: str) -> None:
        err_msg = "'info_type' should be either 'data' or 'result'."
        with pytest.raises(ValueError, match=err_msg):
            uploader_normal._get_req_info(req_json, info_type)

    @pytest.mark.parametrize(
        "req_json, info_type",
        [
            ({"error": {
                "data": {"name": "ValueError"},
                "message": "This is a test error message.",
            }}, "result"),
            ({"error": {
                "data": {"name": "ValueError"},
                "message": "This is a test error message.",
            }}, "data"),
        ]
    )
    def test_valueerror(self,
                        uploader_normal: Type[Uploader],
                        req_json: dict,
                        info_type: str) -> None:
        err_msg = "This is a test error message."
        with pytest.raises(ValueError, match=err_msg):
            uploader_normal._get_req_info(req_json, info_type)

    @pytest.mark.parametrize(
        "req_json, info_type",
        [
            ({"error": {
                "data": {"name": "OtherError"},
            }}, "result"),
            ({"error": {
                "data": {"name": "OtherError"},
            }}, "data"),
        ]
    )
    def test_othererrors(self,
                         uploader_normal: Type[Uploader],
                         req_json: dict,
                         info_type: str) -> None:
        with pytest.raises(KeyError):
            uploader_normal._get_req_info(req_json, info_type)
