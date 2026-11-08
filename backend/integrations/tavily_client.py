"""
CrowdWisdom AI Studio — Tavily Integration Client
Web research for customer pain points and industry discussions.
"""
import logging
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

TAVILY_BASE_URL = "https://api.tavily.com"


class TavilyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Perform a Tavily search with optional date filtering."""
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": True,
            "include_raw_content": False,
            "days": days,
        }
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(f"{TAVILY_BASE_URL}/search", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def research_trading_pain_points(self, days: int = 30) -> List[Dict]:
        """Research current trader frustrations and pain points fast without blocking."""
        queries = [
            "retail trader frustrations stock market information overload",
            "options trading difficulty conflicting signals sentiment analysis"
        ]
        all_results = []
        import asyncio
        async def _run_q(q):
            try:
                res = await self.search(q, max_results=5, days=days)
                return res.get("results", [])
            except Exception as err:
                logger.warning(f"Tavily query failed: {err}")
                return []

        search_tasks = [_run_q(q) for q in queries]
        try:
            results_nested = await asyncio.wait_for(asyncio.gather(*search_tasks), timeout=10.0)
            for sublist in results_nested:
                all_results.extend(sublist)
        except Exception as e:
            logger.warning(f"Tavily search notice: {e}")
        return all_results

    async def test_connection(self) -> Dict[str, Any]:
        """Test Tavily API connection."""
        try:
            result = await self.search("trading market sentiment", max_results=1)
            return {"success": True, "results_count": len(result.get("results", []))}
        except Exception as e:
            return {"success": False, "error": str(e)}

