import asyncio
import os
import sys
import httpx
import json

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from config import settings
from integrations.exa_client import ExaClient
from integrations.apify_client import ApifyClient

async def audit_tavily_details():
    print("=== TAVILY DETAILED AUDIT ===")
    if not settings.TAVILY_API_KEY:
        print("Tavily key missing.")
        return
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": "NSE India market",
        "max_results": 1
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        print(f"Status Code: {resp.status_code}")
        print(f"Response Body: {resp.text}")

async def audit_exa_details():
    print("\n=== EXA DETAILED AUDIT ===")
    client = ExaClient(settings.EXA_API_KEY)
    # Search India
    in_res = await client.search("NSE Nifty options retail trader sentiment India", num_results=3)
    print("India Results:")
    for r in in_res.get("results", []):
        print(f"  - Title: {r.get('title')}")
        print(f"    URL: {r.get('url')}")
        print(f"    Published: {r.get('publishedDate')}")
        print(f"    Text snippet: {str(r.get('text', ''))[:150]}...")

    # Search Philippines
    ph_res = await client.search("PSEi equities retail investor sentiment Philippines", num_results=3)
    print("\nPhilippines Results:")
    for r in ph_res.get("results", []):
        print(f"  - Title: {r.get('title')}")
        print(f"    URL: {r.get('url')}")
        print(f"    Published: {r.get('publishedDate')}")
        print(f"    Text snippet: {str(r.get('text', ''))[:150]}...")

async def audit_apify_meta_ads():
    print("\n=== APIFY META ADS SCRAPER AUDIT ===")
    client = ApifyClient(settings.APIFY_API_TOKEN)
    # Let's inspect user and limits
    async with httpx.AsyncClient() as http:
        user_res = await http.get("https://api.apify.com/v2/users/me", headers={"Authorization": f"Bearer {settings.APIFY_API_TOKEN}"})
        print("Apify User Profile:", json.dumps(user_res.json().get("data", {}), indent=2))

        # Check actor info for apify~facebook-ads-scraper
        actor_res = await http.get("https://api.apify.com/v2/acts/apify~facebook-ads-scraper", headers={"Authorization": f"Bearer {settings.APIFY_API_TOKEN}"})
        print(f"Actor apify~facebook-ads-scraper status: {actor_res.status_code}")
        if actor_res.status_code != 200:
            print("Actor response:", actor_res.text[:300])

if __name__ == "__main__":
    asyncio.run(audit_tavily_details())
    asyncio.run(audit_exa_details())
    asyncio.run(audit_apify_meta_ads())
