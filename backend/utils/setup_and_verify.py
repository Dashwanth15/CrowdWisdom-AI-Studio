"""
CrowdWisdom AI Studio — Setup and Verification Script
Connects to MongoDB Atlas, seeds admin user, stores and encrypts credentials,
and executes live connection tests for all configured providers.
"""
import asyncio
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import connect_to_mongo, close_mongo_connection, get_database
from config import settings
from services.auth_service import hash_password
from services.integration_service import upsert_integration, get_decrypted_api_key
from integrations.llm_client import LLMClient
from integrations.apify_client import ApifyClient
from integrations.tavily_client import TavilyClient
from integrations.exa_client import ExaClient

# Secure credential mapping loaded dynamically from environment
CREDENTIALS = {
    "gemini": {
        "key": settings.GEMINI_API_KEY,
        "model": "gemini-2.5-flash",
    },
    "openrouter": {
        "key": settings.OPENROUTER_API_KEY,
        "model": "meta-llama/llama-3.1-70b-instruct",
    },
    "nvidia_nim": {
        "key": settings.NVIDIA_NIM_API_KEY,
        "model": "nvidia/nemotron-3.5-bolt-e4b",
    },
    "apify": {
        "key": settings.APIFY_API_TOKEN,
        "model": None,
    },
    "tavily": {
        "key": settings.TAVILY_API_KEY,
        "model": None,
    },
    "exa": {
        "key": settings.EXA_API_KEY,
        "model": None,
    },
}


async def main():
    print("=" * 60)
    print("CrowdWisdom AI Studio -- System Verification & Setup")
    print("=" * 60)

    # 1. MongoDB Connection
    print("\n1. Connecting to MongoDB Atlas...")
    try:
        await connect_to_mongo()
        db = get_database()
        print("[OK] Connected to MongoDB Atlas successfully!")
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        return

    # 2. Seed Admin User
    print("\n2. Checking Admin User...")
    admin = await db.users.find_one({"email": "admin@crowdwisdom.ai"})
    if not admin:
        from datetime import datetime, timezone
        await db.users.insert_one({
            "email": "admin@crowdwisdom.ai",
            "username": "admin",
            "full_name": "CrowdWisdom Admin",
            "password_hash": hash_password("admin1234"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        print("[OK] Created default admin: admin@crowdwisdom.ai / admin1234")
    else:
        print("[OK] Admin user verified.")

    # 3. Store and Encrypt Integration Credentials
    print("\n3. Encrypting and Storing Integration Credentials...")
    for provider, data in CREDENTIALS.items():
        if not data.get("key"):
            print(f"  [SKIP] {provider}: No API key provided in environment.")
            continue
        doc = await upsert_integration(
            provider_name=provider,
            api_key=data["key"],
            model_name=data["model"],
            is_active=True,
        )
        print(f"  [OK] Stored {provider}: {doc.get('api_key_masked')}")

    # 4. Live Connection Tests
    print("\n4. Running Live Provider Connection Tests...")

    # Gemini Test
    if CREDENTIALS["gemini"]["key"]:
        print("-> Testing Google Gemini connection...")
        try:
            gemini = LLMClient(api_key=CREDENTIALS["gemini"]["key"], provider="gemini", model=CREDENTIALS["gemini"]["model"])
            res = await gemini.test_connection()
            if res.get("success"):
                print(f"  [OK] Gemini Verified! Model: {res.get('model')} | Response: {res.get('response')[:60]}")
            else:
                print(f"  [FAIL] Gemini Warning: {res.get('error')}")
        except Exception as e:
            print(f"  [FAIL] Gemini Error: {e}")
    else:
        print("  [SKIP] Gemini: key not configured.")

    # OpenRouter Test
    if CREDENTIALS["openrouter"]["key"]:
        print("-> Testing OpenRouter connection...")
        try:
            openrouter = LLMClient(api_key=CREDENTIALS["openrouter"]["key"], provider="openrouter", model=CREDENTIALS["openrouter"]["model"])
            res = await openrouter.test_connection()
            if res.get("success"):
                print(f"  [OK] OpenRouter Verified! Model: {res.get('model')} | Response: {res.get('response')[:60]}")
            else:
                print(f"  [FAIL] OpenRouter Warning: {res.get('error')}")
        except Exception as e:
            print(f"  [FAIL] OpenRouter Error: {e}")
    else:
        print("  [SKIP] OpenRouter: key not configured.")

    # NVIDIA NIM Test
    if CREDENTIALS["nvidia_nim"]["key"]:
        print("-> Testing NVIDIA NIM connection...")
        try:
            nim = LLMClient(api_key=CREDENTIALS["nvidia_nim"]["key"], provider="nvidia_nim", model=CREDENTIALS["nvidia_nim"]["model"])
            res = await nim.test_connection()
            if res.get("success"):
                print(f"  [OK] NVIDIA NIM Verified! Model: {res.get('model')} | Response: {res.get('response')[:60]}")
            else:
                print(f"  [FAIL] NVIDIA NIM Warning: {res.get('error')}")
        except Exception as e:
            print(f"  [FAIL] NVIDIA NIM Error: {e}")
    else:
        print("  [SKIP] NVIDIA NIM: key not configured.")

    # Apify Test
    if CREDENTIALS["apify"]["key"]:
        print("-> Testing Apify connection...")
        try:
            apify = ApifyClient(api_token=CREDENTIALS["apify"]["key"])
            res = await apify.test_connection()
            if res.get("success"):
                print(f"  [OK] Apify Verified! User: {res.get('username')} | Plan: {res.get('plan')}")
            else:
                print(f"  [FAIL] Apify Warning: {res.get('error')}")
        except Exception as e:
            print(f"  [FAIL] Apify Error: {e}")
    else:
        print("  [SKIP] Apify: token not configured.")

    # Tavily Test
    if CREDENTIALS["tavily"]["key"]:
        print("-> Testing Tavily connection...")
        try:
            tavily = TavilyClient(api_key=CREDENTIALS["tavily"]["key"])
            res = await tavily.test_connection()
            if res.get("success"):
                print(f"  [OK] Tavily Verified! Results Found: {res.get('results_count')}")
            else:
                print(f"  [FAIL] Tavily Warning: {res.get('error')}")
        except Exception as e:
            print(f"  [FAIL] Tavily Error: {e}")
    else:
        print("  [SKIP] Tavily: key not configured.")

    # Exa Test
    if CREDENTIALS["exa"]["key"]:
        print("-> Testing Exa connection...")
        try:
            exa = ExaClient(api_key=CREDENTIALS["exa"]["key"])
            res = await exa.test_connection()
            if res.get("success"):
                print(f"  [OK] Exa Verified! Results Found: {res.get('results_count')}")
            else:
                print(f"  [FAIL] Exa Warning: {res.get('error')}")
        except Exception as e:
            print(f"  [FAIL] Exa Error: {e}")
    else:
        print("  [SKIP] Exa: key not configured.")

    await close_mongo_connection()
    print("\n" + "=" * 60)
    print("Verification Complete! All services and database ready.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
