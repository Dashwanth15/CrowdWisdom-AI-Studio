"""
CrowdWisdom AI Studio — Integrations API Routes
Manage API credentials for all external providers.
API keys are stored encrypted server-side and NEVER returned in full to the frontend.
"""
from datetime import datetime, timezone
from typing import Annotated, Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from bson import ObjectId

from database.connection import get_database
from models.schemas import IntegrationOut, IntegrationUpdate, IntegrationStatus
from api.auth import get_current_user
from services.integration_service import upsert_integration, get_decrypted_api_key
from integrations.llm_client import LLMClient
from integrations.apify_client import ApifyClient
from integrations.tavily_client import TavilyClient
from integrations.exa_client import ExaClient

router = APIRouter(prefix="/integrations", tags=["Integrations"])

SUPPORTED_PROVIDERS = ["gemini", "openrouter", "nvidia_nim", "apify", "tavily", "exa", "openmontage"]


def _serialize_integration(doc: dict) -> IntegrationOut:
    return IntegrationOut(
        id=str(doc["_id"]),
        provider_name=doc["provider_name"],
        display_name=doc.get("display_name", doc["provider_name"]),
        category=doc.get("category", "other"),
        status=doc.get("status", "unconfigured"),
        is_active=doc.get("is_active", False),
        api_key_configured=bool(doc.get("api_key_encrypted")),
        api_key_masked=doc.get("api_key_masked"),  # Safe masked version only
        model_name=doc.get("model_name"),
        extra_config=doc.get("extra_config"),
        last_tested_at=doc.get("last_tested_at"),
        test_result=doc.get("test_result"),
        updated_at=doc.get("updated_at", datetime.now(timezone.utc)),
    )


@router.get("", response_model=List[IntegrationOut])
async def list_integrations(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """List all integration configurations (without exposing API keys)."""
    db = get_database()
    docs = await db.integrations.find({}).to_list(50)
    return [_serialize_integration(d) for d in docs]


@router.patch("/{provider_name}", response_model=IntegrationOut)
async def update_integration(
    provider_name: str,
    data: IntegrationUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Update integration credentials. API keys are stored encrypted server-side."""
    if provider_name not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider_name}")

    if current_user.get("role") not in ("admin", "marketing_manager"):
        raise HTTPException(status_code=403, detail="Only admins and marketing managers can configure integrations.")

    doc = await upsert_integration(
        provider_name=provider_name,
        api_key=data.api_key,  # Will be encrypted before storage
        model_name=data.model_name,
        extra_config=data.extra_config,
        is_active=data.is_active,
    )
    return _serialize_integration(doc)


@router.post("/{provider_name}/test")
async def test_integration(
    provider_name: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Test the connection for a configured integration."""
    if provider_name not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider_name}")

    api_key = await get_decrypted_api_key(provider_name)
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"{provider_name} API key not configured. Add it in Settings first.",
        )

    db = get_database()
    result: Dict[str, Any] = {}

    try:
        if provider_name == "gemini":
            integration = await db.integrations.find_one({"provider_name": "gemini"})
            model = integration.get("model_name") if integration else "gemini-3.5-flash-lite"
            llm = LLMClient(api_key=api_key, provider="gemini", model=model)
            result = await llm.test_connection()

        elif provider_name == "openrouter":
            integration = await db.integrations.find_one({"provider_name": "openrouter"})
            model = integration.get("model_name") if integration else None
            llm = LLMClient(api_key=api_key, provider="openrouter", model=model)
            result = await llm.test_connection()

        elif provider_name == "nvidia_nim":
            integration = await db.integrations.find_one({"provider_name": "nvidia_nim"})
            model = integration.get("model_name") if integration else None
            llm = LLMClient(api_key=api_key, provider="nvidia_nim", model=model)
            result = await llm.test_connection()

        elif provider_name == "apify":
            apify = ApifyClient(api_key)
            result = await apify.test_connection()

        elif provider_name == "tavily":
            tavily = TavilyClient(api_key)
            result = await tavily.test_connection()

        elif provider_name == "exa":
            exa = ExaClient(api_key)
            result = await exa.test_connection()

        elif provider_name == "openmontage":
            # Test OpenMontage by checking if it's installed
            from pathlib import Path
            from config import settings
            openmontage_path = Path(settings.MEDIA_DIR).parent / "video_engine" / "openmontage"
            if openmontage_path.exists():
                result = {"success": True, "message": "OpenMontage found at expected path."}
            else:
                result = {
                    "success": False,
                    "message": "OpenMontage not found. Clone it to backend/video_engine/openmontage/",
                }

    except Exception as e:
        result = {"success": False, "error": str(e)}

    # Save test result
    test_status = "configured" if result.get("success") else "error"
    await db.integrations.update_one(
        {"provider_name": provider_name},
        {
            "$set": {
                "last_tested_at": datetime.now(timezone.utc),
                "test_result": str(result),
                "status": test_status,
            }
        },
    )

    return {
        "provider": provider_name,
        "success": result.get("success", False),
        "result": {k: v for k, v in result.items() if k != "api_key"},
    }

