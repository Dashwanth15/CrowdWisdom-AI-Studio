"""
CrowdWisdom AI Studio — Integration Service
Manages API credentials for all external providers.
API keys are stored encrypted in MongoDB and NEVER returned to the frontend.
"""
import base64
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from config import settings
from database.connection import get_database

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    import hashlib
    key_bytes = hashlib.sha256(settings.APP_SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key_bytes))


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage."""
    f = _get_fernet()
    return f.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt a stored API key."""
    f = _get_fernet()
    return f.decrypt(encrypted_key.encode()).decode()


def mask_api_key(api_key: str) -> str:
    """Return a masked version safe to display in the frontend."""
    if len(api_key) <= 8:
        return "***"
    return api_key[:4] + "****" + api_key[-4:]


PROVIDER_DEFAULTS = {
    "gemini": {
        "display_name": "Google Gemini",
        "category": "llm",
        "default_model": "gemini-2.5-flash",
        "env_var": "GEMINI_API_KEY",
    },
    "openrouter": {
        "display_name": "OpenRouter",
        "category": "llm",
        "default_model": "meta-llama/llama-3.1-70b-instruct",
        "env_var": "OPENROUTER_API_KEY",
    },
    "nvidia_nim": {
        "display_name": "NVIDIA NIM",
        "category": "llm",
        "default_model": "nvidia/nemotron-3.5-bolt-e4b",
        "env_var": "NVIDIA_NIM_API_KEY",
    },
    "apify": {
        "display_name": "Apify",
        "category": "research",
        "default_model": None,
        "env_var": "APIFY_API_TOKEN",
    },
    "tavily": {
        "display_name": "Tavily",
        "category": "research",
        "default_model": None,
        "env_var": "TAVILY_API_KEY",
    },
    "exa": {
        "display_name": "Exa",
        "category": "research",
        "default_model": None,
        "env_var": "EXA_API_KEY",
    },
    "openmontage": {
        "display_name": "OpenMontage",
        "category": "video",
        "default_model": None,
        "env_var": None,
    },
}


async def get_integration(provider_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve integration config from database."""
    db = get_database()
    doc = await db.integrations.find_one({"provider_name": provider_name})
    return doc


async def get_decrypted_api_key(provider_name: str) -> Optional[str]:
    """Get the decrypted API key for internal backend use."""
    doc = await get_integration(provider_name)
    if doc and doc.get("api_key_encrypted"):
        try:
            return decrypt_api_key(doc["api_key_encrypted"])
        except Exception as e:
            logger.error(f"Failed to decrypt API key for {provider_name}: {e}")

    # Fall back to settings / env variables
    env_attr = PROVIDER_DEFAULTS.get(provider_name, {}).get("env_var")
    if env_attr:
        env_val = getattr(settings, env_attr, None)
        if env_val:
            return env_val

    return None


async def upsert_integration(
    provider_name: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    extra_config: Optional[Dict] = None,
    is_active: Optional[bool] = None,
) -> Dict[str, Any]:
    """Create or update an integration configuration."""
    db = get_database()
    defaults = PROVIDER_DEFAULTS.get(provider_name, {})

    update_doc: Dict[str, Any] = {
        "provider_name": provider_name,
        "display_name": defaults.get("display_name", provider_name),
        "category": defaults.get("category", "other"),
        "updated_at": datetime.now(timezone.utc),
    }

    if api_key is not None:
        update_doc["api_key_encrypted"] = encrypt_api_key(api_key)
        update_doc["api_key_masked"] = mask_api_key(api_key)
        update_doc["status"] = "configured"
        update_doc["is_active"] = True

    if model_name is not None:
        update_doc["model_name"] = model_name
    elif "default_model" in defaults and model_name is None:
        update_doc.setdefault("model_name", defaults["default_model"])

    if extra_config is not None:
        update_doc["extra_config"] = extra_config

    if is_active is not None:
        update_doc["is_active"] = is_active

    insert_defaults = {
        "created_at": datetime.now(timezone.utc),
        "status": "unconfigured",
        "is_active": False,
        "api_key_encrypted": None,
        "api_key_masked": None,
        "last_tested_at": None,
        "test_result": None,
    }
    set_on_insert = {k: v for k, v in insert_defaults.items() if k not in update_doc}

    await db.integrations.update_one(
        {"provider_name": provider_name},
        {
            "$set": update_doc,
            "$setOnInsert": set_on_insert,
        },
        upsert=True,
    )
    return await db.integrations.find_one({"provider_name": provider_name})


async def initialize_default_integrations() -> None:
    """Create or update default integration records from database or environment."""
    db = get_database()
    for provider_name, defaults in PROVIDER_DEFAULTS.items():
        existing = await db.integrations.find_one({"provider_name": provider_name})

        # Check if environment provides an initial key
        env_attr = defaults.get("env_var")
        env_key = getattr(settings, env_attr, None) if env_attr else None

        if not existing:
            doc = {
                "provider_name": provider_name,
                "display_name": defaults["display_name"],
                "category": defaults["category"],
                "status": "configured" if env_key else "unconfigured",
                "is_active": bool(env_key),
                "api_key_encrypted": encrypt_api_key(env_key) if env_key else None,
                "api_key_masked": mask_api_key(env_key) if env_key else None,
                "model_name": defaults.get("default_model"),
                "extra_config": {},
                "last_tested_at": None,
                "test_result": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            await db.integrations.insert_one(doc)
        elif env_key and not existing.get("api_key_encrypted"):
            # If env key is provided and DB wasn't configured yet, update it
            await db.integrations.update_one(
                {"provider_name": provider_name},
                {
                    "$set": {
                        "api_key_encrypted": encrypt_api_key(env_key),
                        "api_key_masked": mask_api_key(env_key),
                        "status": "configured",
                        "is_active": True,
                        "updated_at": datetime.now(timezone.utc),
                    }
                }
            )

    logger.info("Default integrations initialized with active keys.")
