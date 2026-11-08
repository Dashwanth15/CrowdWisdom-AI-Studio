"""
CrowdWisdom AI Studio — Secret Leak Prevention & Security Unit Tests
Verifies that:
1. Environment configuration always masks credentials in logs, strings, and representations.
2. Connection URIs never expose passwords in logs or exception messages.
3. Exception handlers sanitize internal error messages before returning them to clients.
4. Integration API serialization NEVER leaks raw or encrypted API keys.
5. Frontend source files and production assets contain no private provider API credentials.
"""
import os
import re
from pathlib import Path
import pytest

from config import (
    Settings,
    mask_secret_value,
    mask_connection_url,
)
from main import _sanitize_error_message
from api.integrations import _serialize_integration
from models.schemas import IntegrationOut


def test_mask_secret_value():
    """Verify secret masking handles various lengths safely without leaking."""
    assert mask_secret_value(None) == "<NOT_SET>"
    assert mask_secret_value("") == "<NOT_SET>"
    # Short secret
    assert mask_secret_value("12345678") == "********"
    # Long API Key
    long_key = "mock_key_prefix_1234567890abcdef1234567890abcdef12345678"
    masked = mask_secret_value(long_key, 4, 4)
    assert masked.startswith("mock...")
    assert masked.endswith("5678")
    assert "1234567890abcdef1234567890abcdef" not in masked


def test_mask_connection_url():
    """Verify database connection strings with passwords are redacted."""
    raw_uri = "mongodb+srv://mock_user:mock_secret_password%40123@cluster1.mongodb.net/testdb?retryWrites=true"
    masked = mask_connection_url(raw_uri)
    assert "mock_secret_password%40123" not in masked
    assert "mock_user:****@" in masked
    assert "cluster1.mongodb.net" in masked

    raw_redis = "redis://:mock_redis_secret_pass@redis.internal:6379/0"
    masked_redis = mask_connection_url(raw_redis)
    assert "mock_redis_secret_pass" not in masked_redis
    assert ":****@" in masked_redis


def test_settings_safe_representation():
    """Verify Settings repr and dictionary masking never leak raw secrets."""
    test_settings = Settings(
        APP_SECRET_KEY="placeholder_random_secret_app_key_32_chars",
        JWT_SECRET_KEY="placeholder_random_secret_jwt_key_32_chars",
        MONGODB_URL="mongodb+srv://mock_admin:mock_secret_password@cluster.mongodb.net/",
        GEMINI_API_KEY="mock_gemini_key_1234567890abcdef123456",
        OPENROUTER_API_KEY="mock_openrouter_key_1234567890abcdef123",
        NVIDIA_NIM_API_KEY="mock_nvidia_nim_key_1234567890abcdef12",
        APIFY_API_TOKEN="mock_apify_token_1234567890abcdef12345",
        TAVILY_API_KEY="mock_tavily_key_1234567890abcdef1234567",
        EXA_API_KEY="mock_exa_key_1234567890abcdef1234567890",
    )

    repr_str = repr(test_settings)
    masked_dict = test_settings.get_masked_dictionary()

    # Raw secrets must NOT be present in repr or dictionary
    forbidden = [
        "mock_secret_password",
        "mock_gemini_key_1234567890abcdef123456",
        "mock_openrouter_key_1234567890abcdef123",
        "mock_nvidia_nim_key_1234567890abcdef12",
        "mock_apify_token_1234567890abcdef12345",
        "mock_tavily_key_1234567890abcdef1234567",
        "placeholder_random_secret_app_key_32_chars",
    ]

    for secret in forbidden:
        assert secret not in repr_str, f"Secret leaked in repr: {secret}"
        for k, v in masked_dict.items():
            assert secret not in str(v), f"Secret leaked in masked dict field {k}: {secret}"


def test_exception_handler_sanitizes_errors():
    """Verify exception handler scrubs credentials from error messages."""
    raw_error = Exception("Connection failed to mongodb+srv://mock_admin:mock_secret_password@cluster0.net/ with token sk-mock-supersecret-token-12345")
    sanitized = _sanitize_error_message(raw_error)

    assert "mock_secret_password" not in sanitized
    assert "supersecret" not in sanitized
    assert "****" in sanitized or "[REDACTED]" in sanitized


def test_integration_serialization_hides_raw_keys():
    """Verify integration API serialization outputs ONLY masked version."""
    from datetime import datetime, timezone
    from bson import ObjectId

    mock_doc = {
        "_id": ObjectId(),
        "provider_name": "openrouter",
        "display_name": "OpenRouter",
        "category": "llm",
        "status": "configured",
        "is_active": True,
        "api_key_encrypted": "mock_encrypted_fernet_token_do_not_leak",
        "api_key_masked": "sk-o****8432",
        "model_name": "meta-llama/llama-3.1-70b-instruct",
        "extra_config": {},
        "updated_at": datetime.now(timezone.utc),
    }

    serialized: IntegrationOut = _serialize_integration(mock_doc)
    dumped = serialized.model_dump()

    assert dumped["api_key_configured"] is True
    assert dumped["api_key_masked"] == "sk-o****8432"
    # Ensure neither encrypted token nor raw key exists on the output schema
    assert "api_key" not in dumped
    assert "api_key_encrypted" not in dumped


def test_frontend_has_no_private_api_keys():
    """Scan all frontend source code and verify zero exposed private provider keys."""
    frontend_src = Path(__file__).resolve().parent.parent.parent / "frontend" / "src"
    assert frontend_src.exists(), "frontend/src must exist"

    patterns = [
        re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"nvapi-[A-Za-z0-9_-]{20,}"),
        re.compile(r"apify_api_[A-Za-z0-9_-]{20,}"),
        re.compile(r"tvly-[A-Za-z0-9_-]{20,}"),
        re.compile(r"mongodb(?:\+srv)?://[^:]+:[^@]+@"),
    ]

    for root, dirs, files in os.walk(frontend_src):
        for f in files:
            if f.endswith((".ts", ".tsx", ".js", ".jsx", ".json", ".html")):
                fp = Path(root) / f
                content = fp.read_text(encoding="utf-8", errors="ignore")
                for pat in patterns:
                    match = pat.search(content)
                    assert match is None, f"Found private credential in {fp.name}: {match.group(0)[:6]}..."
