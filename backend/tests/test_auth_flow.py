import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from datetime import datetime, timezone
from main import app
from services.auth_service import hash_password, verify_password, create_access_token, decode_access_token


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_password_hashing_and_verification():
    """Verify bcrypt password hashing and verification works with admin123."""
    password = "admin123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_token_creation_and_decoding():
    """Verify JWT access token creation and decoding with claims."""
    claims = {"sub": "admin@crowdwisdom.ai", "role": "admin"}
    token = create_access_token(claims)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "admin@crowdwisdom.ai"
    assert decoded["role"] == "admin"


def test_admin_login_success(client):
    """Verify that logging in with admin@crowdwisdom.ai / admin123 returns access token and serialized user."""
    mock_admin_user = {
        "_id": ObjectId("650000000000000000000001"),
        "email": "admin@crowdwisdom.ai",
        "username": "admin",
        "full_name": "Studio Administrator",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }

    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value=mock_admin_user)
    mock_db.users.update_one = AsyncMock()

    with patch("api.auth.get_database", return_value=mock_db):
        res = client.post(
            "/api/auth/login",
            data={"username": "admin@crowdwisdom.ai", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@crowdwisdom.ai"
        assert data["user"]["role"] == "admin"


def test_invalid_credentials_rejected(client):
    """Verify that wrong passwords return 401 Unauthorized."""
    mock_admin_user = {
        "_id": ObjectId("650000000000000000000001"),
        "email": "admin@crowdwisdom.ai",
        "username": "admin",
        "full_name": "Studio Administrator",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }

    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value=mock_admin_user)

    with patch("api.auth.get_database", return_value=mock_db):
        res = client.post(
            "/api/auth/login",
            data={"username": "admin@crowdwisdom.ai", "password": "wrong_password_999"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert res.status_code == 401
        assert "Invalid credentials" in res.json().get("detail", "")

