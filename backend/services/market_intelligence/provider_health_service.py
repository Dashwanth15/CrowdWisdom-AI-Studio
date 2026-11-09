"""
CrowdWisdom AI Studio — Research Provider Health & Diagnostics Service
Monitors, benchmarks, and diagnostically tests all research and LLM providers:
Exa, Apify, NVIDIA NIM, Tavily, and Google Gemini.
NEVER exposes API keys or sensitive authorization headers.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from config import settings
from services.integration_service import get_decrypted_api_key

logger = logging.getLogger(__name__)


class ProviderHealthService:
    """Diagnoses and reports real-time health, latency, and status for all research providers."""

    async def check_all_providers(self) -> Dict[str, Any]:
        """Runs concurrent diagnostic checks across all external providers."""
        now = datetime.now(timezone.utc).isoformat()
        results = await asyncio.gather(
            self.check_exa(),
            self.check_apify(),
            self.check_nvidia_nim(),
            self.check_tavily(),
            self.check_gemini(),
            return_exceptions=True,
        )

        provider_map = {
            "exa": results[0] if not isinstance(results[0], Exception) else {"status": "ERROR", "error": str(results[0])},
            "apify": results[1] if not isinstance(results[1], Exception) else {"status": "ERROR", "error": str(results[1])},
            "nvidia_nim": results[2] if not isinstance(results[2], Exception) else {"status": "ERROR", "error": str(results[2])},
            "tavily": results[3] if not isinstance(results[3], Exception) else {"status": "ERROR", "error": str(results[3])},
            "gemini": results[4] if not isinstance(results[4], Exception) else {"status": "ERROR", "error": str(results[4])},
        }

        # Overall operational assessment
        live_research = provider_map["exa"]["status"] == "LIVE_AND_VERIFIED"
        live_ads = provider_map["apify"]["status"] == "LIVE_AND_VERIFIED"
        live_llm = provider_map["nvidia_nim"]["status"] == "LIVE_AND_VERIFIED"

        return {
            "timestamp": now,
            "overall_status": "OPERATIONAL" if (live_research and live_llm) else "DEGRADED",
            "active_research_pipeline": "Exa Semantic Search" if live_research else "Domain Benchmarks",
            "active_ads_pipeline": "Apify Meta Ads Library" if live_ads else "Domain Benchmark Ads",
            "active_llm_pipeline": "NVIDIA NIM" if live_llm else "Fallback Required",
            "providers": provider_map,
        }

    async def ping_provider(self, provider_name: str) -> Dict[str, Any]:
        """Diagnoses a specific provider by name."""
        name = provider_name.lower().replace("-", "_")
        dispatch = {
            "exa": self.check_exa,
            "apify": self.check_apify,
            "nvidia_nim": self.check_nvidia_nim,
            "tavily": self.check_tavily,
            "gemini": self.check_gemini,
        }
        if name in dispatch:
            return await dispatch[name]()
        return {"provider": provider_name, "status": "UNKNOWN_PROVIDER", "error": f"Provider {provider_name} not recognized"}

    async def check_exa(self) -> Dict[str, Any]:
        """Diagnoses Exa Semantic Search API."""
        key = await get_decrypted_api_key("exa") or settings.EXA_API_KEY
        if not key:
            return {"provider": "Exa", "category": "semantic_research", "status": "NOT_CONFIGURED", "is_configured": False}

        start = time.perf_counter()
        try:
            from integrations.exa_client import ExaClient
            client = ExaClient(key)
            test_res = await client.test_connection()
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            if test_res.get("success"):
                return {
                    "provider": "Exa",
                    "category": "semantic_research",
                    "status": "LIVE_AND_VERIFIED",
                    "is_configured": True,
                    "http_status": 200,
                    "latency_ms": latency_ms,
                    "capabilities": ["semantic_search", "domain_filtering", "publication_dates"],
                }
            return {
                "provider": "Exa",
                "category": "semantic_research",
                "status": "ERROR",
                "is_configured": True,
                "latency_ms": latency_ms,
                "error": test_res.get("error", "Unknown error"),
            }
        except Exception as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            return {
                "provider": "Exa",
                "category": "semantic_research",
                "status": "ERROR",
                "is_configured": True,
                "latency_ms": latency_ms,
                "error": str(e),
            }

    async def check_apify(self) -> Dict[str, Any]:
        """Diagnoses Apify Meta Ads Library Scraper integration."""
        key = await get_decrypted_api_key("apify") or settings.APIFY_API_TOKEN
        if not key:
            return {"provider": "Apify", "category": "meta_ads_scraping", "status": "NOT_CONFIGURED", "is_configured": False}

        start = time.perf_counter()
        try:
            from integrations.apify_client import ApifyClient
            client = ApifyClient(key)
            account_info = await client.get_account_info()
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            if not account_info.get("error"):
                return {
                    "provider": "Apify",
                    "category": "meta_ads_scraping",
                    "status": "LIVE_AND_VERIFIED",
                    "is_configured": True,
                    "http_status": 200,
                    "latency_ms": latency_ms,
                    "account_username": account_info.get("username"),
                    "plan": account_info.get("plan_id"),
                    "monthly_credits_usd": account_info.get("monthly_credits_usd"),
                    "capabilities": ["meta_ads_library_scraping", "brand_profiling", "targeting_extraction"],
                }
            return {
                "provider": "Apify",
                "category": "meta_ads_scraping",
                "status": "AUTHENTICATION_FAILED" if "401" in str(account_info.get("error")) else "ERROR",
                "is_configured": True,
                "latency_ms": latency_ms,
                "error": account_info.get("error"),
            }
        except Exception as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            err_str = str(e)
            status = "QUOTA_EXCEEDED" if "403" in err_str else ("AUTHENTICATION_FAILED" if "401" in err_str else "ERROR")
            return {
                "provider": "Apify",
                "category": "meta_ads_scraping",
                "status": status,
                "is_configured": True,
                "latency_ms": latency_ms,
                "error": err_str,
            }

    async def check_nvidia_nim(self) -> Dict[str, Any]:
        """Diagnoses NVIDIA NIM Structured LLM provider."""
        key = await get_decrypted_api_key("nvidia_nim") or settings.NVIDIA_NIM_API_KEY
        if not key:
            return {"provider": "NVIDIA NIM", "category": "llm_synthesis", "status": "NOT_CONFIGURED", "is_configured": False}

        start = time.perf_counter()
        try:
            from integrations.llm_client import LLMClient
            client = LLMClient(api_key=key, provider="nvidia_nim")
            reply = await client.chat([{"role": "user", "content": "respond with OK"}], max_tokens=10)
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            return {
                "provider": "NVIDIA NIM",
                "category": "llm_synthesis",
                "status": "LIVE_AND_VERIFIED",
                "is_configured": True,
                "http_status": 200,
                "latency_ms": latency_ms,
                "model": client.model,
                "capabilities": ["structured_json_synthesis", "market_intelligence", "creative_evaluation"],
            }
        except Exception as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            return {
                "provider": "NVIDIA NIM",
                "category": "llm_synthesis",
                "status": "ERROR",
                "is_configured": True,
                "latency_ms": latency_ms,
                "error": str(e),
            }

    async def check_tavily(self) -> Dict[str, Any]:
        """Diagnoses Tavily Web Search API."""
        key = await get_decrypted_api_key("tavily") or settings.TAVILY_API_KEY
        if not key:
            return {"provider": "Tavily", "category": "web_search", "status": "NOT_CONFIGURED", "is_configured": False}

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": key, "query": "ping", "max_results": 1},
                )
                latency_ms = round((time.perf_counter() - start) * 1000, 1)
                if resp.status_code == 200:
                    return {
                        "provider": "Tavily",
                        "category": "web_search",
                        "status": "LIVE_AND_VERIFIED",
                        "is_configured": True,
                        "http_status": 200,
                        "latency_ms": latency_ms,
                    }
                elif resp.status_code == 432:
                    return {
                        "provider": "Tavily",
                        "category": "web_search",
                        "status": "QUOTA_EXCEEDED",
                        "is_configured": True,
                        "http_status": 432,
                        "latency_ms": latency_ms,
                        "error": "Monthly request quota exhausted. System gracefully routes research to Exa.",
                    }
                else:
                    return {
                        "provider": "Tavily",
                        "category": "web_search",
                        "status": "ERROR",
                        "is_configured": True,
                        "http_status": resp.status_code,
                        "latency_ms": latency_ms,
                        "error": f"HTTP {resp.status_code}",
                    }
        except Exception as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            return {
                "provider": "Tavily",
                "category": "web_search",
                "status": "ERROR",
                "is_configured": True,
                "latency_ms": latency_ms,
                "error": str(e),
            }

    async def check_gemini(self) -> Dict[str, Any]:
        """Diagnoses Google Gemini API."""
        key = await get_decrypted_api_key("gemini") or settings.GEMINI_API_KEY
        if not key:
            return {"provider": "Gemini", "category": "llm_synthesis", "status": "NOT_CONFIGURED", "is_configured": False}

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": "ping"}]}]}
                resp = await client.post(url, json=payload)
                latency_ms = round((time.perf_counter() - start) * 1000, 1)
                if resp.status_code == 200:
                    return {
                        "provider": "Gemini",
                        "category": "llm_synthesis",
                        "status": "LIVE_AND_VERIFIED",
                        "is_configured": True,
                        "http_status": 200,
                        "latency_ms": latency_ms,
                    }
                elif resp.status_code in (401, 403):
                    return {
                        "provider": "Gemini",
                        "category": "llm_synthesis",
                        "status": "AUTHENTICATION_FAILED",
                        "is_configured": True,
                        "http_status": resp.status_code,
                        "latency_ms": latency_ms,
                        "error": "Authentication token expired or unauthorized. Automated fallback to NVIDIA NIM active.",
                    }
                else:
                    return {
                        "provider": "Gemini",
                        "category": "llm_synthesis",
                        "status": "ERROR",
                        "is_configured": True,
                        "http_status": resp.status_code,
                        "latency_ms": latency_ms,
                        "error": f"HTTP {resp.status_code}",
                    }
        except Exception as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            return {
                "provider": "Gemini",
                "category": "llm_synthesis",
                "status": "ERROR",
                "is_configured": True,
                "latency_ms": latency_ms,
                "error": str(e),
            }


provider_health_service = ProviderHealthService()
