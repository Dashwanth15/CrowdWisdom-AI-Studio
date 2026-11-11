import asyncio
import os
import sys
import json

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from config import settings
from integrations.apify_client import ApifyClient

async def test_ph_extraction():
    token = settings.APIFY_API_TOKEN
    print(f"Apify token present: {bool(token)}")
    client = ApifyClient(token)
    keywords = ["philippine stock exchange", "forex trading philippines", "crypto investing philippines"]
    print(f"Starting Meta Ads search for country=PH with keywords: {keywords}")
    ads = await client.search_meta_ads(keywords=keywords, country="PH", max_results=15)
    print(f"Retrieved {len(ads)} ads from Apify for PH")
    for i, ad in enumerate(ads[:5]):
        snapshot = ad.get("snapshot") or {}
        page_name = ad.get("pageName") or ad.get("page_name") or snapshot.get("page_name") or "Unknown"
        body = snapshot.get("body", {}).get("text") if isinstance(snapshot.get("body"), dict) else ad.get("body")
        archive_id = ad.get("adArchiveId") or ad.get("adArchiveID") or ad.get("id") or snapshot.get("ad_archive_id")
        start_date = ad.get("startDate") or snapshot.get("start_date")
        print(f"--- Ad {i+1} ---")
        print(f"ID: {archive_id}")
        print(f"Page: {page_name}")
        print(f"Start Date: {start_date}")
        print(f"Body snippet: {str(body)[:120] if body else 'N/A'}")

if __name__ == "__main__":
    asyncio.run(test_ph_extraction())

