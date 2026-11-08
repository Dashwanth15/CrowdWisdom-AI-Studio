import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_root_endpoint(client):
    """Verify root discovery endpoint returns platform status and valid links."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["service"] == "CrowdWisdom AI Studio API"
    assert data["status"] == "online"
    assert data["docs"] == "/docs"
    assert data["openapi"] == "/openapi.json"
    assert data["health"] == "/health"


def test_docs_endpoint(client):
    """Verify Swagger UI is accessible at /docs."""
    res = client.get("/docs")
    assert res.status_code == 200
    assert "swagger-ui" in res.text.lower() or "html" in res.headers.get("content-type", "")


def test_openapi_endpoint(client):
    """Verify OpenAPI JSON schema is accessible at /openapi.json."""
    res = client.get("/openapi.json")
    assert res.status_code == 200
    data = res.json()
    assert "openapi" in data
    assert data["info"]["title"] == "CrowdWisdom AI Studio API"


def test_redoc_endpoint(client):
    """Verify ReDoc UI is accessible at /redoc."""
    res = client.get("/redoc")
    assert res.status_code == 200


def test_api_docs_redirect(client):
    """Verify /api/docs redirects seamlessly to /docs."""
    res = client.get("/api/docs", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/docs"


def test_api_openapi_redirect(client):
    """Verify /api/openapi.json redirects seamlessly to /openapi.json."""
    res = client.get("/api/openapi.json", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/openapi.json"


def test_api_redoc_redirect(client):
    """Verify /api/redoc redirects seamlessly to /redoc."""
    res = client.get("/api/redoc", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/redoc"


def test_health_endpoints(client):
    """Verify both /health and /api/health return expected status without secret leakage."""
    for path in ["/health", "/api/health"]:
        res = client.get(path)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["service"] == "CrowdWisdom AI Studio"
        # Ensure no secrets or connection strings are leaked
        assert "password" not in str(data).lower()
        assert "mongodb://" not in str(data)
