import pytest


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """
    Remove requests.sessions.Session.request for all tests.

    Prevents "requests" from making http requests in all tests.
    """
    monkeypatch.delattr("requests.sessions.Session.request")
