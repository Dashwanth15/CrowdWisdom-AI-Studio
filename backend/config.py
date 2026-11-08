"""
CrowdWisdom AI Studio — Application Configuration & Centralized Environment Security
Loads, validates, and masks all environment variables using pydantic-settings.
Enforces strict secret masking to prevent credentials leaking in logs or error traces.
"""
from functools import lru_cache
from pathlib import Path
import re
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field, AliasChoices

# Determine paths to canonical root .env and backend/.env
_BACKEND_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _BACKEND_DIR.parent
_ENV_FILES = [
    _ROOT_DIR / ".env",
    _BACKEND_DIR / ".env",
]


def mask_secret_value(val: Optional[str], show_prefix: int = 4, show_suffix: int = 4) -> str:
    """Mask a secret string for safe logging and error reporting."""
    if not val:
        return "<NOT_SET>"
    val_str = str(val).strip()
    if len(val_str) <= (show_prefix + show_suffix):
        return "*" * len(val_str)
    return f"{val_str[:show_prefix]}...{val_str[-show_suffix:]}"


def mask_connection_url(url: Optional[str]) -> str:
    """Mask credentials inside connection URIs (e.g., mongodb://<user>:<password>@host)."""
    if not url:
        return "<NOT_SET>"
    return re.sub(r"://([^:]*):([^@]+)@", r"://\1:****@", str(url))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(p) for p in _ENV_FILES if p.exists()] or [str(_ROOT_DIR / ".env")],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "replace_with_app_secret"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000"

    # MongoDB (Accepts both MONGODB_URL and MONGODB_URI)
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", validation_alias=AliasChoices("MONGODB_URL", "MONGODB_URI"))
    MONGODB_DB_NAME: str = "crowdwisdom_ai_studio"

    # Redis (Optional)
    REDIS_URL: Optional[str] = None

    # JWT
    JWT_SECRET_KEY: str = "replace_with_jwt_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for development
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Provider Credentials (Optional fallbacks / initial values)
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    NVIDIA_NIM_API_KEY: Optional[str] = None
    APIFY_API_TOKEN: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    EXA_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None

    # File Storage
    MEDIA_DIR: str = str((Path(__file__).parent / "media").resolve())
    MAX_VIDEO_SIZE_MB: int = 500

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    def get_masked_dictionary(self) -> Dict[str, Any]:
        """Return a safe representation of configuration with all credentials masked."""
        return {
            "APP_ENV": self.APP_ENV,
            "APP_HOST": self.APP_HOST,
            "APP_PORT": self.APP_PORT,
            "FRONTEND_URL": self.FRONTEND_URL,
            "CORS_ORIGINS": self.cors_origins_list,
            "MONGODB_URL": mask_connection_url(self.MONGODB_URL),
            "MONGODB_DB_NAME": self.MONGODB_DB_NAME,
            "REDIS_URL": mask_connection_url(self.REDIS_URL) if self.REDIS_URL else None,
            "APP_SECRET_KEY": mask_secret_value(self.APP_SECRET_KEY, 3, 3),
            "JWT_SECRET_KEY": mask_secret_value(self.JWT_SECRET_KEY, 3, 3),
            "GEMINI_API_KEY": mask_secret_value(self.GEMINI_API_KEY),
            "OPENROUTER_API_KEY": mask_secret_value(self.OPENROUTER_API_KEY),
            "NVIDIA_NIM_API_KEY": mask_secret_value(self.NVIDIA_NIM_API_KEY),
            "APIFY_API_TOKEN": mask_secret_value(self.APIFY_API_TOKEN),
            "TAVILY_API_KEY": mask_secret_value(self.TAVILY_API_KEY),
            "EXA_API_KEY": mask_secret_value(self.EXA_API_KEY),
            "OPENAI_API_KEY": mask_secret_value(self.OPENAI_API_KEY),
            "ANTHROPIC_API_KEY": mask_secret_value(self.ANTHROPIC_API_KEY),
            "RESEND_API_KEY": mask_secret_value(self.RESEND_API_KEY),
            "MEDIA_DIR": self.MEDIA_DIR,
            "MAX_VIDEO_SIZE_MB": self.MAX_VIDEO_SIZE_MB,
        }

    def __repr__(self) -> str:
        """Safe representation preventing accidental secret exposure in tracebacks or logs."""
        masked = self.get_masked_dictionary()
        fields = ", ".join(f"{k}={v!r}" for k, v in masked.items())
        return f"Settings({fields})"

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate security and operational readiness of environment configuration.
        Fails safely when mandatory requirements are not met.
        """
        issues: List[str] = []
        warnings: List[str] = []

        # 1. Secret keys validation in production
        if self.is_production:
            if "production-secret" in self.APP_SECRET_KEY or len(self.APP_SECRET_KEY) < 32:
                issues.append("APP_SECRET_KEY must be a secure random string of at least 32 characters in production.")
            if "jwt-production-secret" in self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                issues.append("JWT_SECRET_KEY must be a secure random string of at least 32 characters in production.")

        # 2. Database validation
        if not self.MONGODB_URL:
            issues.append("MONGODB_URL is required.")

        # 3. Provider presence checks (warnings if not configured)
        has_llm = any([self.GEMINI_API_KEY, self.OPENROUTER_API_KEY, self.NVIDIA_NIM_API_KEY, self.OPENAI_API_KEY])
        if not has_llm:
            warnings.append("No primary LLM provider API key configured (GEMINI, OPENROUTER, NVIDIA_NIM, OPENAI).")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config": self.get_masked_dictionary(),
        }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
