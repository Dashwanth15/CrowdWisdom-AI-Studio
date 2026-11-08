import secrets
import pytest
from config import Settings


def test_production_settings_validation_valid():
    """Verify that cryptographically secure random keys of 32+ chars pass production validation."""
    s = Settings(
        APP_ENV="production",
        APP_SECRET_KEY=secrets.token_hex(32),
        JWT_SECRET_KEY=secrets.token_hex(32),
        MONGODB_URL="mongodb://mock-cluster.test:27017/test",
        _env_file=None,
    )
    res = s.validate_environment()
    assert res["valid"] is True
    assert len(res["issues"]) == 0


def test_production_settings_validation_rejects_short_keys():
    """Verify that keys shorter than 32 characters are rejected in production."""
    s = Settings(
        APP_ENV="production",
        APP_SECRET_KEY="too_short_key",
        JWT_SECRET_KEY="another_short_key",
        MONGODB_URL="mongodb://mock-cluster.test:27017/test",
        _env_file=None,
    )
    res = s.validate_environment()
    assert res["valid"] is False
    assert any("APP_SECRET_KEY" in issue for issue in res["issues"])
    assert any("JWT_SECRET_KEY" in issue for issue in res["issues"])


def test_production_settings_validation_rejects_placeholder_substrings():
    """Verify that placeholder strings containing 'production-secret' are rejected even if long."""
    s = Settings(
        APP_ENV="production",
        APP_SECRET_KEY="crowdwisdom-production-secret-value-longer-than-32-chars",
        JWT_SECRET_KEY="crowdwisdom-jwt-production-secret-value-longer-than-32-chars",
        MONGODB_URL="mongodb://mock-cluster.test:27017/test",
        _env_file=None,
    )
    res = s.validate_environment()
    assert res["valid"] is False
    assert any("APP_SECRET_KEY" in issue for issue in res["issues"])
    assert any("JWT_SECRET_KEY" in issue for issue in res["issues"])


def test_production_settings_whitespace_and_quote_stripping():
    """Verify that leading/trailing quotes and spaces are automatically sanitized."""
    key1 = secrets.token_hex(32)
    key2 = secrets.token_hex(32)
    s = Settings(
        APP_ENV="production",
        APP_SECRET_KEY=f'  "{key1}"  ',
        JWT_SECRET_KEY=f"  '{key2}'  ",
        MONGODB_URL=" mongodb://mock-cluster.test:27017/test ",
        _env_file=None,
    )
    assert s.APP_SECRET_KEY == key1
    assert s.JWT_SECRET_KEY == key2
    assert s.MONGODB_URL == "mongodb://mock-cluster.test:27017/test"
    res = s.validate_environment()
    assert res["valid"] is True


def test_development_settings_permissive():
    """Verify that non-production environments permit shorter keys for convenient local testing."""
    s = Settings(
        APP_ENV="development",
        APP_SECRET_KEY="dev_short_secret",
        JWT_SECRET_KEY="dev_short_secret",
        MONGODB_URL="mongodb://localhost:27017",
        _env_file=None,
    )
    res = s.validate_environment()
    assert res["valid"] is True
