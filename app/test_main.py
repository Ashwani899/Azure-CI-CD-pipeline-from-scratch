import pytest

from main import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_home_page_displays_build_metadata(client, monkeypatch):
    monkeypatch.setenv("BUILD_ID", "test-build-42")
    monkeypatch.setenv("BUILD_TIME", "2026-11-14T12:00:00Z")
    response = client.get("/")
    assert response.status_code == 200
    assert b"test-build-42" in response.data
    assert b"2026-11-14T12:00:00Z" in response.data


def test_home_page_uses_local_defaults(client, monkeypatch):
    monkeypatch.delenv("BUILD_ID", raising=False)
    monkeypatch.delenv("BUILD_TIME", raising=False)
    response = client.get("/")
    assert response.status_code == 200
    assert b"local-dev" in response.data
    assert b"not-set" in response.data
