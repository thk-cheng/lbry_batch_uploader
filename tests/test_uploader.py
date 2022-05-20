import pytest
import os
import time
import requests
from requests import RequestException, ConnectionError
from lbry_batch_uploader.parser import Parser
from lbry_batch_uploader.uploader import Uploader
from typing import Dict, Type
import argparse
import pathlib


class MockResponse:
    """Dummy mock request.Resopnse class."""

    pass


class MockResponseVersion(MockResponse):
    """Mocking good request.Resopnse.json for the "version" query."""

    @staticmethod
    def json() -> Dict[str, Dict[str, str]]:
        return {"result": {"version": "0.107.1"}}


class MockResponseFfmpeg(MockResponse):
    """Mocking good request.Resopnse.json for the "ffmpeg_find" query."""

    @staticmethod
    def json() -> Dict[str, Dict[str, bool]]:
        return {"result": {"available": True}}


class MockResponseFfmpegMissing(MockResponse):
    """Mocking bad request.Resopnse.json for the "ffmpeg_find" query."""

    @staticmethod
    def json() -> Dict[str, Dict[str, bool]]:
        return {"result": {"available": False}}


class MockResponseFile(MockResponse):
    """Mocking good request.Resopnse.json for file upload."""

    @staticmethod
    def json() -> Dict[str, Dict[str, Dict[int, Dict[str, str]]]]:
        return {"result": {"outputs": {0: {"claim_id": "123abc"}}}}


class MockResponseThumbnail(MockResponse):
    """Mocking good request.Resopnse.json for thumbnail upload."""

    @staticmethod
    def json() -> Dict[str, Dict[str, str]]:
        return {"data": {"serveUrl": "https://abc123.xyz"}}


@pytest.fixture
def mock_response_good(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Mock Requests.post() to return MockResponse instead."""

    def mock_post(*args, **kwargs):
        try:
            method = kwargs["json"]["method"]
            if method == "version":
                mock_response_instance = MockResponseVersion()
            elif method == "ffmpeg_find":
                mock_response_instance = MockResponseFfmpeg()
            elif method == "publish":
                mock_response_instance = MockResponseFile()
        except KeyError:
            mock_response_instance = MockResponseThumbnail()
        return mock_response_instance

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def mock_response_badport(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Mock Requests.post() to raise requests.ConnectionError instead."""

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
    """Mock Requests.post() to return MockResponseFfmpegMissing instead."""

    def mock_post(*args, **kwargs):
        method = kwargs["json"]["method"]
        if method == "version":
            mock_response_instance = MockResponseVersion()
        elif method == "ffmpeg_find":
            mock_response_instance = MockResponseFfmpegMissing()
        return mock_response_instance

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def mock_time(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Mock time.sleep so that it doesn't actually sleep."""

    def no_sleep(*args, **kwargs):
        return None

    monkeypatch.setattr(time, "sleep", no_sleep)


@pytest.fixture
def fake_dir(tmp_path: Type[pathlib.Path]) -> Type[pathlib.Path]:
    """Create a fake directory with essential files for testing."""
    d = tmp_path / "sub"
    d.mkdir()

    ext_file = ("mp4", "mkv", "webm", "mp3", "opus")
    for idx, ext in enumerate(ext_file):
        fake_file = d / f"{idx}.{ext}"
        fake_file.touch()

    ext_desc = ("txt", "txt", "txt", "description", "description")
    for idx, ext in enumerate(ext_desc):
        fake_file_desc = d / f"{idx}.{ext}"
        fake_file_desc.touch()

    ext_thumbnail = ("gif", "jpg", "jpg", "png", "png")
    for idx, ext in enumerate(ext_thumbnail):
        fake_file = d / f"{idx}.{ext}"
        fake_file.touch()

    for idx, ext in enumerate(("mov", "md", "webp")):
        ignore_file = d / f"this_file_is_ignored_{idx}.{ext}"
        ignore_file.touch()

    return d


@pytest.fixture
def parser() -> Type[Parser]:
    """Return a well-behaved Parser instance."""
    return Parser()


@pytest.fixture
def args_normal(
    parser: Type[Parser], fake_dir: Type[pathlib.Path]
) -> Type[argparse.Namespace]:
    """Return a well-behaved argparse.Namespace object."""
    args = [
        str(fake_dir),
        "@batch-upload-testing",
        "--optimize-file",
        "--bid",
        "0.56",
        "--fee-amount",
        "1.23",
        "--tags",
        "tag0",
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "--languages",
        "en",
        "--license",
        "Other",
        "--license-url",
        "https://www.123.xyz",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_normal_no_optimize(
    parser: Type[Parser], fake_dir: Type[pathlib.Path]
) -> Type[argparse.Namespace]:
    """Return a well-behaved argparse.Namespace object, don't optimize file."""
    args = [
        str(fake_dir),
        "@batch-upload-testing",
        "--bid",
        "0.56",
        "--fee-amount",
        "1.23",
        "--tags",
        "tag0",
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "--languages",
        "en",
        "--license",
        "Other",
        "--license-url",
        "https://www.123.xyz",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_wrong_path(parser: Type[Parser]) -> Type[argparse.Namespace]:
    """Return a argparse.Namespace object, with wrong file directory."""
    args = [
        "this/is/a/wrong/path",
        "@batch-upload-testing",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_wrong_port0(
    parser: Type[Parser], fake_dir: Type[pathlib.Path]
) -> Type[argparse.Namespace]:
    """Return a argparse.Namespace object, with out of range port number."""
    args = [
        str(fake_dir),
        "@batch-upload-testing",
        "--port",
        "70000",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_wrong_port1(
    parser: Type[Parser], fake_dir: Type[pathlib.Path]
) -> Type[argparse.Namespace]:
    """Return a argparse.Namespace object, with ill-configured port."""
    args = [
        str(fake_dir),
        "@batch-upload-testing",
        "--port",
        "9999",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def args_no_ffmpeg(
    parser: Type[Parser], fake_dir: Type[pathlib.Path]
) -> Type[argparse.Namespace]:
    """Return a argparse.Namespace object, with ill-configured ffmpeg."""
    args = [
        str(fake_dir),
        "@batch-upload-testing",
        "--optimize-file",
    ]
    parser.parse(args)
    return parser.args


@pytest.fixture
def uploader_normal(
    args_normal: Type[argparse.Namespace], mock_response_good: None
) -> Type[Uploader]:
    """Return a well-behaved Uploader instance."""
    return Uploader(args_normal)


@pytest.fixture
def uploader_normal_no_optimize(
    args_normal_no_optimize: Type[argparse.Namespace], mock_response_good: None
) -> Type[Uploader]:
    """Return a well-behaved Uploader instance, don't optimize file."""
    return Uploader(args_normal_no_optimize)


class TestInit:
    """Testing the __init__ method and related helper methods."""

    def test_wrong_path(self, args_wrong_path: Type[argparse.Namespace]) -> None:
        """Test the case when the specified file directory unreachable."""
        wrong_path = os.path.abspath(args_wrong_path.file_directory)
        err_msg = f"The directory {wrong_path} does not exist."
        with pytest.raises(FileNotFoundError, match=err_msg):
            _ = Uploader(args_wrong_path)

    def test_wrong_port0(self, args_wrong_port0: Type[argparse.Namespace]) -> None:
        """Test the case when the specified port is out of range."""
        wrong_port = args_wrong_port0.port
        err_msg = f"The port {wrong_port} is not between 0 and 65353."
        with pytest.raises(TypeError, match=err_msg):
            _ = Uploader(args_wrong_port0)

    def test_wrong_port1(
        self, args_wrong_port1: Type[argparse.Namespace], mock_response_badport: None
    ) -> None:
        """Test the case when the specified port is not accessible."""
        wrong_port = args_wrong_port1.port
        with pytest.raises(RequestException, match=f"port={wrong_port}"):
            _ = Uploader(args_wrong_port1)

    def test_no_ffmpeg(
        self,
        args_no_ffmpeg: Type[argparse.Namespace],
        mock_response_noffmpeg: None,
        capsys: Type[pytest.CaptureFixture],
    ) -> None:
        """Test the case when ffmpeg is not configured properly."""
        uploader_no_ffmpeg = Uploader(args_no_ffmpeg)
        assert not uploader_no_ffmpeg.base_params["optimize_file"]

        captured = capsys.readouterr()
        msg = "ffmpeg is not configured properly." + "--optimize-file set to False."
        assert msg in captured.out
        assert captured.err == ""

    def test_normal(self, uploader_normal: Type[Uploader]) -> None:
        """Test that the attributes are correct with the correct input."""
        assert uploader_normal.base_path is not None
        assert uploader_normal.port_url == "http://localhost:5279"

        base_params = uploader_normal.base_params
        assert base_params["channel_name"] == "@batch-upload-testing"
        assert base_params["optimize_file"]
        assert base_params["bid"] == "0.56"
        assert base_params["fee_currency"] == "lbc"
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
            ({"jsonrpc": "2.0", "result": {}}, "abc"),
            ({"jsonrpc": "2.0", "data": {}}, "xyz"),
        ],
    )
    def test_wrong_info_type(
        self, uploader_normal: Type[Uploader], req_json: dict, info_type: str
    ) -> None:
        """Test that the correct exception is raised when a wrong info_type is queried."""
        err_msg = "'info_type' should be either 'data' or 'result'."
        with pytest.raises(ValueError, match=err_msg):
            uploader_normal._get_req_info(req_json, info_type)

    @pytest.mark.parametrize(
        "req_json, info_type",
        [
            (
                {
                    "error": {
                        "data": {"name": "ValueError"},
                        "message": "This is a test error message.",
                    }
                },
                "result",
            ),
            (
                {
                    "error": {
                        "data": {"name": "ValueError"},
                        "message": "This is a test error message.",
                    }
                },
                "data",
            ),
        ],
    )
    def test_valueerror(
        self, uploader_normal: Type[Uploader], req_json: dict, info_type: str
    ) -> None:
        """Test the case when ValueError is passed back from lbrynet."""
        err_msg = "This is a test error message."
        with pytest.raises(ValueError, match=err_msg):
            uploader_normal._get_req_info(req_json, info_type)

    @pytest.mark.parametrize(
        "req_json, info_type",
        [
            (
                {
                    "error": {
                        "data": {"name": "OtherError"},
                    }
                },
                "result",
            ),
            (
                {
                    "error": {
                        "data": {"name": "OtherError"},
                    }
                },
                "data",
            ),
        ],
    )
    def test_othererrors(
        self, uploader_normal: Type[Uploader], req_json: dict, info_type: str
    ) -> None:
        """Test the case when other exception is passed back from lbrynet."""
        with pytest.raises(KeyError):
            uploader_normal._get_req_info(req_json, info_type)


class TestGetAllFiles:
    """Testing the get_all_files method."""

    def test_check_fake_dir(self, uploader_normal: Type[Uploader]) -> None:
        """Test that all the files in the fake directory are intact."""
        base_path = pathlib.Path(uploader_normal.base_path)
        files = list(base_path.iterdir())
        assert len(files) == 18

    def test_get_all(self, uploader_normal: Type[Uploader]) -> None:
        """Test that all the relavent fake files are caught."""
        uploader_normal.get_all_files()
        files_valid = uploader_normal.files_valid
        assert isinstance(files_valid, dict)
        assert len(files_valid) == 5

        ext_file = ("mp4", "mkv", "webm", "mp3", "opus")
        ext_desc = ("txt", "txt", "txt", "description", "description")
        ext_thumbnail = ("gif", "jpg", "jpg", "png", "png")
        ext_zip = zip(files_valid.keys(), ext_file, ext_desc, ext_thumbnail)
        for key, ext_f, ext_d, ext_t in ext_zip:
            assert files_valid[key]["file_name"] == f"{key}.{ext_f}"
            assert files_valid[key]["desc_name"] == f"{key}.{ext_d}"
            assert files_valid[key]["thumbnail_name"] == f"{key}.{ext_t}"

        for idx in range(3):
            ignore_file = f"this_file_is_ignored_{idx}"
            assert ignore_file not in list(files_valid.keys())

    def test_get_invalid_ftypes(self, uploader_normal: Type[Uploader]) -> None:
        """Test that the correct exception is raised for invalid ftypes."""
        base_path = pathlib.Path(uploader_normal.base_path)
        files = list(base_path.iterdir())

        err_msg = "Only support getting thumbnails or descriptions."
        with pytest.raises(ValueError, match=err_msg):
            uploader_normal._get_valid_ftypes(files, "abc", ("abc",))


class TestUploadAllFiles:
    """Testing the upload_all_files method."""

    def test_upload_all(
        self,
        uploader_normal: Type[Uploader],
        mock_response_good: None,
        mock_time: None,
        capsys: Type[pytest.CaptureFixture],
    ) -> None:
        """Test that the upload_all_files method returns the correct output(s)."""
        uploader_normal.get_all_files()
        uploader_normal.upload_all_files()
        captured = capsys.readouterr()

        for params in uploader_normal.files_valid.values():
            out_msg = (
                f"Sucessfully uploaded {params['file_name']}\n"
                + "The claim id is 123abc\n"
            )
            assert out_msg in captured.out

        assert captured.err == ""

    def test_upload_all_no_optimize(
        self,
        uploader_normal_no_optimize: Type[Uploader],
        mock_response_good: None,
        mock_time: None,
        capsys: Type[pytest.CaptureFixture],
    ) -> None:
        """Same as above, but with the --optimize-file flag not specified."""
        uploader_normal_no_optimize.get_all_files()
        uploader_normal_no_optimize.upload_all_files()
        captured = capsys.readouterr()

        for params in uploader_normal_no_optimize.files_valid.values():
            out_msg = (
                f"Sucessfully uploaded {params['file_name']}\n"
                + "The claim id is 123abc\n"
            )
            assert out_msg in captured.out

        assert captured.err == ""
