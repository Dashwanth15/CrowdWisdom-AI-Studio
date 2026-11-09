import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from config import settings
from integrations.apify_client import ApifyClient

async def test_apify_run():
    client = ApifyClient(settings.APIFY_API_TOKEN)
    try:
        run_id = await client.run_actor(
            "apify~facebook-ads-scraper",
            {"startUrls": [{"url": "https://www.facebook.com/ads/library/?country=IN&q=trading"}], "resultsLimit": 1}
        )
        print(f"Apify Run ID: {run_id}")
    except Exception as e:
        print(f"Apify Run Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_apify_run())

