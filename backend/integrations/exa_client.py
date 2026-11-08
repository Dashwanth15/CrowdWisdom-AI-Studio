"""
CrowdWisdom AI Studio — Exa Integration Client
Semantic search for research and content discovery.
"""
import logging
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

EXA_BASE_URL = "https://api.exa.ai"


class ExaClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

    async def search(
        self,
        query: str,
        num_results: int = 10,
        use_autoprompt: bool = True,
        start_published_date: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Semantic search via Exa."""
        payload: Dict[str, Any] = {
            "query": query,
            "num_results": num_results,
            "useAutoprompt": use_autoprompt,
            "contents": {"text": True},
        }
        if start_published_date:
            payload["startPublishedDate"] = start_published_date
        if include_domains:
            payload["includeDomains"] = include_domains

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{EXA_BASE_URL}/search", json=payload, headers=self.headers
            )
            resp.raise_for_status()
            return resp.json()

    async def find_content_opportunities(
        self, topic: str, days_back: int = 30
    ) -> List[Dict]:
        """Find relevant content and discussions about a topic."""
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        result = await self.search(
            query=topic,
            num_results=15,
            use_autoprompt=True,
            start_published_date=cutoff,
        )
        return result.get("results", [])

    async def test_connection(self) -> Dict[str, Any]:
        """Test Exa API connection."""
        try:
            result = await self.search("trading sentiment analysis", num_results=1)
            return {"success": True, "results_count": len(result.get("results", []))}
        except Exception as e:
            return {"success": False, "error": str(e)}

