import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database
from services.integration_service import get_decrypted_api_key
from integrations.tavily_client import TavilyClient
from integrations.exa_client import ExaClient
from integrations.apify_client import ApifyClient
from config import settings

async def main():
    print("=== ENVIRONMENT CHECK ===")
    print(f"settings.TAVILY_API_KEY: {'Configured' if settings.TAVILY_API_KEY else 'None'}")
    print(f"settings.EXA_API_KEY: {'Configured' if settings.EXA_API_KEY else 'None'}")
    print(f"settings.APIFY_API_TOKEN: {'Configured' if settings.APIFY_API_TOKEN else 'None'}")
    print(f"settings.GEMINI_API_KEY: {'Configured' if settings.GEMINI_API_KEY else 'None'}")
    print(f"settings.OPENROUTER_API_KEY: {'Configured' if settings.OPENROUTER_API_KEY else 'None'}")
    print(f"settings.NVIDIA_NIM_API_KEY: {'Configured' if settings.NVIDIA_NIM_API_KEY else 'None'}")

    print("\n=== MONGODB INTEGRATIONS CHECK ===")
    try:
        await connect_to_mongo()
        db = get_database()
        integrations = await db.integrations.find().to_list(100)
        for doc in integrations:
            p = doc.get("provider_name")
            s = doc.get("status")
            m = doc.get("api_key_masked")
            cat = doc.get("category")
            print(f"[{p}] category={cat}, status={s}, masked_key={m}")
    except Exception as e:
        print(f"MongoDB connection notice: {e}")

    print("\n=== DECRYPTED API KEYS & LIVE PROVIDER PROBES ===")
    # 1. Tavily
    tavily_key = await get_decrypted_api_key("tavily")
    if tavily_key:
        print(f"[Tavily] Key found (len={len(tavily_key)}, starts with {tavily_key[:4]}...)")
        client = TavilyClient(tavily_key)
        try:
            res = await client.test_connection()
            print(f"[Tavily] test_connection result: {res}")
            # Try India query
            res_in = await client.search("NSE Nifty options retail trader sentiment India", max_results=2)
            print(f"[Tavily India Query] Returned {len(res_in.get('results', []))} results")
            # Try PH query
            res_ph = await client.search("PSEi equities retail investor sentiment Philippines", max_results=2)
            print(f"[Tavily PH Query] Returned {len(res_ph.get('results', []))} results")
        except Exception as e:
            print(f"[Tavily ERROR] {type(e).__name__}: {e}")
    else:
        print("[Tavily] No key available.")

    # 2. Exa
    exa_key = await get_decrypted_api_key("exa")
    if exa_key:
        print(f"[Exa] Key found (len={len(exa_key)}, starts with {exa_key[:4]}...)")
        client = ExaClient(exa_key)
        try:
            res = await client.test_connection()
            print(f"[Exa] test_connection result: {res}")
            res_in = await client.search("SEBI retail trading study loss percentage", num_results=2)
            print(f"[Exa India Query] Returned {len(res_in.get('results', []))} results")
            res_ph = await client.search("Philippine stock exchange retail participation", num_results=2)
            print(f"[Exa PH Query] Returned {len(res_ph.get('results', []))} results")
        except Exception as e:
            print(f"[Exa ERROR] {type(e).__name__}: {e}")
    else:
        print("[Exa] No key available.")

    # 3. Apify
    apify_key = await get_decrypted_api_key("apify")
    if apify_key:
        print(f"[Apify] Key found (len={len(apify_key)}, starts with {apify_key[:4]}...)")
        client = ApifyClient(apify_key)
        try:
            res = await client.test_connection()
            print(f"[Apify] test_connection result: {res}")
        except Exception as e:
            print(f"[Apify ERROR] {type(e).__name__}: {e}")
    else:
        print("[Apify] No key available.")

if __name__ == "__main__":
    asyncio.run(main())
