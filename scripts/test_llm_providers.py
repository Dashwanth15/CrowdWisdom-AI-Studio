import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from config import settings
from integrations.llm_client import LLMClient

async def test_llms():
    print("=== TESTING LLM CLIENTS ===")
    if settings.GEMINI_API_KEY:
        try:
            client = LLMClient(api_key=settings.GEMINI_API_KEY, provider="gemini")
            res = await client.chat([{"role": "user", "content": "Respond with 'Gemini OK'"}])
            print(f"Gemini: SUCCESS -> {res.strip()[:50]}")
        except Exception as e:
            print(f"Gemini ERROR: {e}")

    if settings.OPENROUTER_API_KEY:
        try:
            client = LLMClient(api_key=settings.OPENROUTER_API_KEY, provider="openrouter", model="meta-llama/llama-3.1-8b-instruct")
            res = await client.chat([{"role": "user", "content": "Respond with 'OpenRouter OK'"}])
            print(f"OpenRouter: SUCCESS -> {res.strip()[:50]}")
        except Exception as e:
            print(f"OpenRouter ERROR: {e}")

    if settings.NVIDIA_NIM_API_KEY:
        try:
            client = LLMClient(api_key=settings.NVIDIA_NIM_API_KEY, provider="nvidia_nim")
            res = await client.chat([{"role": "user", "content": "Respond with 'NVIDIA NIM OK'"}])
            print(f"NVIDIA NIM: SUCCESS -> {res.strip()[:50]}")
        except Exception as e:
            print(f"NVIDIA NIM ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_llms())

