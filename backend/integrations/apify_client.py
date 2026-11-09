"""
CrowdWisdom AI Studio — Apify Integration Client
Fetches advertisement data from Meta Ads Library via Apify actors.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import httpx

logger = logging.getLogger(__name__)

APIFY_BASE_URL = "https://api.apify.com/v2"
# Apify actor for Meta Ads Library (uses tilde notation for username~name endpoint)
META_ADS_ACTOR_ID = "apify~facebook-ads-scraper"


class ApifyClient:
    def __init__(self, api_token: Optional[str] = None, api_key: Optional[str] = None):
        token = api_token or api_key or ""
        self.api_token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def run_actor(self, actor_id: str, input_data: Dict) -> Optional[str]:
        """Start an Apify actor run and return the run ID."""
        normalized_actor_id = actor_id.replace("/", "~")
        url = f"{APIFY_BASE_URL}/acts/{normalized_actor_id}/runs"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                json=input_data,
                headers=self.headers,
                params={"token": self.api_token} if self.api_token else {}
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("id")

    async def get_run_status(self, run_id: str) -> Dict:
        """Get the status of an Apify actor run."""
        url = f"{APIFY_BASE_URL}/actor-runs/{run_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                url,
                headers=self.headers,
                params={"token": self.api_token} if self.api_token else {}
            )
            resp.raise_for_status()
            return resp.json().get("data", {})

    async def get_dataset_items(self, run_id: str) -> List[Dict]:
        """Retrieve dataset items from a completed run."""
        url = f"{APIFY_BASE_URL}/actor-runs/{run_id}/dataset/items"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                url,
                headers=self.headers,
                params={"format": "json", "clean": "true", "token": self.api_token} if self.api_token else {"format": "json", "clean": "true"}
            )
            resp.raise_for_status()
            return resp.json()

    async def wait_for_run(self, run_id: str, max_wait_seconds: int = 300) -> bool:
        """Poll until the actor run completes or times out."""
        import asyncio
        elapsed = 0
        poll_interval = 5
        while elapsed < max_wait_seconds:
            status_data = await self.get_run_status(run_id)
            status = status_data.get("status", "")
            if status in ("SUCCEEDED", "FINISHED"):
                return True
            if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                logger.error(f"Apify run {run_id} ended with status: {status}")
                return False
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        logger.warning(f"Apify run {run_id} timed out after {max_wait_seconds}s")
        return False

    async def search_meta_ads(
        self,
        keywords: List[str],
        country: str = "US",
        date_range_days: int = 30,
        max_results: int = 100,
    ) -> List[Dict]:
        """
        Search Meta Ads Library via Apify actor (apify~facebook-ads-scraper).
        Returns raw ad data items.
        Note: Meta Ads Library exposes activity data, not verified performance metrics.
        """
        import urllib.parse

        start_urls = []
        for kw in keywords:
            clean_kw = kw.strip().strip('"')
            if clean_kw:
                encoded = urllib.parse.quote_plus(clean_kw)
                start_urls.append({
                    "url": f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&is_targeted_country=false&media_type=all&q={encoded}&search_type=keyword_unordered"
                })
        if not start_urls:
            start_urls.append({
                "url": f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&is_targeted_country=false&media_type=all&q=trading&search_type=keyword_unordered"
            })

        input_data = {
            "startUrls": start_urls,
            "resultsLimit": min(max_results, 30),
            "activeStatus": "active",
        }
        logger.info(f"Starting Meta Ads Apify run for actor {META_ADS_ACTOR_ID}: country={country}, keywords={keywords}")
        run_id = await self.run_actor(META_ADS_ACTOR_ID, input_data)
        if not run_id:
            raise RuntimeError("Failed to start Apify actor run.")

        success = await self.wait_for_run(run_id, max_wait_seconds=90)
        if not success:
            logger.warning(f"Apify actor run {run_id} did not finish within timeout or returned non-success.")
            return []

        items = await self.get_dataset_items(run_id)
        # Filter out Apify empty/error response records, supporting full snapshot schemas
        valid_items = [
            it for it in items 
            if isinstance(it, dict) and not it.get("error") and (
                it.get("adArchiveId") or it.get("adArchiveID") or it.get("adId") or it.get("id") or
                it.get("pageName") or it.get("page_name") or it.get("advertiserName") or
                it.get("snapshot") or it.get("ad_creative_bodies") or it.get("body")
            )
        ]
        logger.info(f"Apify returned {len(items)} items ({len(valid_items)} valid ads) for country: {country}")
        return valid_items

    async def get_account_info(self) -> Dict[str, Any]:
        """Fetch detailed Apify user profile, plan, limits, and compute usage."""
        try:
            url = f"{APIFY_BASE_URL}/users/me"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                resp.raise_for_status()
                data = resp.json().get("data", {})
                plan = data.get("plan", {})
                return {
                    "username": data.get("username", "unknown"),
                    "email": data.get("email", "unknown"),
                    "plan_id": plan.get("id", "FREE"),
                    "is_enabled": plan.get("isEnabled", True),
                    "monthly_credits_usd": plan.get("monthlyUsageCreditsUsd", 0),
                    "max_concurrent_runs": plan.get("maxConcurrentActorRuns", 1),
                }
        except Exception as e:
            logger.warning(f"Failed to fetch Apify account details: {e}")
            return {"error": str(e)}

    async def test_connection(self) -> Dict[str, Any]:
        """Test the Apify API connection."""
        try:
            url = f"{APIFY_BASE_URL}/users/me"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    user = resp.json().get("data", {})
                    return {
                        "success": True,
                        "username": user.get("username", "unknown"),
                        "plan": user.get("plan", {}).get("id", "unknown"),
                    }
                return {"success": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

