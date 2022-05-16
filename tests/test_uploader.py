import pytest
import requests
from lbry_batch_uploader.parser import Parser
from lbry_batch_uploader.uploader import Uploader
from typing import Dict, Type
import argparse
import pathlib


class MockResponseVersion:
    """Custom class to be the mock return value."""
    @staticmethod
    def json() -> Dict[str, Dict[str, str]]:
        return {"result": {"version": "0.107.1"}}


class MockResponseFfmpeg:
    """Custom class to be the mock return value."""
    @staticmethod
    def json() -> Dict[str, Dict[str, bool]]:
        return {"result": {"available": True}}


@pytest.fixture
def mock_response(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Requests.post() mocked to return {"result": {"version": ...}}."""

    def mock_post(*args, **kwargs):
        method = kwargs["json"]["method"]
        if method == "version":
            mock_response_instance = MockResponseVersion()
        elif method == "ffmpeg_find":
            mock_response_instance = MockResponseFfmpeg()
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
        "--tags", "tag0", "tag1", "tag2", "tag3", "tag4"
        "--languages", "en",
        "--license", "Other",
        "--license-url", "https://www.123.xyz"
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def uploader(args_normal: Type[argparse.Namespace],
             mock_response: None) -> Type[Uploader]:
    return Uploader(args_normal)


class TestInit:
    """Test the state of an Uploader instance after __init__"""

    def test_methods_exist(self, uploader: Type[Uploader]) -> None:
        dir_full = dir(uploader)
        dir_clean = [attr for attr in dir_full if not attr.startswith("_")]
        assert "get_all_files" in dir_clean
        assert "upload_all_files" in dir_clean


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
                    uploader: Type[Uploader],
                    req_json: dict,
                    info_type: str) -> None:
        req_info = uploader._get_req_info(req_json, info_type)
        assert req_info == {"abc": "123"}

    @pytest.mark.parametrize(
        "req_json, info_type",
        [
            ({"jsonrpc": "2.0","result": {}}, "abc"),
            ({"jsonrpc": "2.0","data": {}}, "xyz"),
        ]
    )
    def test_wrong_info_type(self,
                             uploader: Type[Uploader],
                             req_json: dict,
                             info_type: str) -> None:
        err_msg = "'info_type' should be either 'data' or 'result'."
        with pytest.raises(ValueError, match=err_msg):
            uploader._get_req_info(req_json, info_type)

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
                        uploader: Type[Uploader],
                        req_json: dict,
                        info_type: str) -> None:
        err_msg = "This is a test error message."
        with pytest.raises(ValueError, match=err_msg):
            uploader._get_req_info(req_json, info_type)

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
                         uploader: Type[Uploader],
                         req_json: dict,
                         info_type: str) -> None:
        with pytest.raises(KeyError):
            uploader._get_req_info(req_json, info_type)
