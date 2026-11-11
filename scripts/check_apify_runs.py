import asyncio
import sys
import os
import httpx

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)
from config import settings

async def list_runs():
    token = settings.APIFY_API_TOKEN
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.apify.com/v2/actor-runs?token={token}&desc=true&limit=10")
        items = r.json().get("data", {}).get("items", [])
        for it in items:
            run_id = it.get("id")
            status = it.get("status")
            item_count = it.get("defaultDatasetId")
            print(f"Run ID: {run_id} | Status: {status} | Dataset: {item_count}")

if __name__ == "__main__":
    asyncio.run(list_runs())
