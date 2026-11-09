import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from config import settings
from integrations.llm_client import LLMClient

async def test_nim_json():
    client = LLMClient(api_key=settings.NVIDIA_NIM_API_KEY, provider="nvidia_nim")
    prompt = [
        {"role": "system", "content": "You are a market analyst. Respond ONLY in valid JSON format."},
        {"role": "user", "content": "Return a JSON object with key 'status': 'ok' and key 'market': 'India'."}
    ]
    res = await client.chat_json(prompt)
    print("NVIDIA NIM chat_json result:", res)

if __name__ == "__main__":
    asyncio.run(test_nim_json())

