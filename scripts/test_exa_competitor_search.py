import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from config import settings
from integrations.exa_client import ExaClient

async def test_exa_ad_intelligence():
    client = ExaClient(settings.EXA_API_KEY)

    print("=== EXA AD & COMPETITOR SEARCH (INDIA) ===")
    queries_in = [
        "site:facebook.com/ads/library/ Nifty trading options",
        "Zerodha Groww Angel One options trading ad copy campaign",
        "India retail options trading pain points Telegram tips"
    ]
    for q in queries_in:
        print(f"\nQuery: {q}")
        res = await client.search(q, num_results=2)
        for r in res.get("results", []):
            print(f"  * Title: {r.get('title')}")
            print(f"    URL: {r.get('url')}")
            print(f"    Published: {r.get('publishedDate')}")
            print(f"    Snippet: {str(r.get('text', ''))[:180]}...")

    print("\n=== EXA AD & COMPETITOR SEARCH (PHILIPPINES) ===")
    queries_ph = [
        "site:facebook.com/ads/library/ PSE stock trading Philippines",
        "COL Financial First Metro Sec stock market trading ad campaign",
        "Philippines retail stock market PSEi investor frustration"
    ]
    for q in queries_ph:
        print(f"\nQuery: {q}")
        res = await client.search(q, num_results=2)
        for r in res.get("results", []):
            print(f"  * Title: {r.get('title')}")
            print(f"    URL: {r.get('url')}")
            print(f"    Published: {r.get('publishedDate')}")
            print(f"    Snippet: {str(r.get('text', ''))[:180]}...")

if __name__ == "__main__":
    asyncio.run(test_exa_ad_intelligence())
