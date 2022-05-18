import pytest
import sys
import time
import requests
from typing import Type, Dict
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
def mock_time(monkeypatch: Type[pytest.MonkeyPatch]) -> None:
    """Mock time.sleep so that it doesn't actually sleep."""

    def no_sleep(*args, **kwargs):
        return None

    monkeypatch.setattr(time, "sleep", no_sleep)


@pytest.fixture
def mock_sys(
    monkeypatch: Type[pytest.MonkeyPatch], fake_dir: Type[pathlib.Path]
) -> None:
    """Mock sys.argv so that it reads dummy data instead."""

    fake_argv = [
        "pytest",
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
        "--languages",
        "en",
        "--license",
        "Other",
        "--license-url",
        "https://www.123.xyz",
    ]

    monkeypatch.setattr(sys, "argv", fake_argv)


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


class TestMain:
    """Test the __main__ module"""

    def test_main_ok(self, mock_response_good, mock_time, mock_sys):
        """Directly run __main__ with mocked sys.argv and responses."""
        from lbry_batch_uploader import __main__

        del __main__
