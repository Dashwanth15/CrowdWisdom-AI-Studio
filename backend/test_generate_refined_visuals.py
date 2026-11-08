import asyncio
import io
import urllib.parse
from PIL import Image
import httpx

prompts = {
    1: "A single dark espresso coffee droplet falling toward a cup on a luxury financial trader desk, background filled with glowing neon green and red stock market ticker screens and candlestick charts in soft cinematic bokeh, moody cinematic lighting, high-contrast fintech commercial aesthetic, 8k vertical 9:16 composition",
    3: "Ultra-modern financial trading workstation showing glowing interface of CrowdWisdomTrading platform with green bullish consensus indicators and real-time sentiment charts, sleek dark obsidian UI, professional fintech trader workspace, cinematic commercial lighting, 8k vertical 9:16 composition",
    4: "Cinematic shot of a confident professional trader in modern office looking out through floor-to-ceiling glass windows at a panoramic city skyline at sunrise, subtle green trading charts glowing on a sleek curved monitor nearby, calm decisive certainty, 8k vertical 9:16 composition"
}

async def generate_all():
    async with httpx.AsyncClient(timeout=40.0, follow_redirects=True) as client:
        for snum, p in prompts.items():
            enc = urllib.parse.quote(p[:500])
            url = f"https://image.pollinations.ai/prompt/{enc}?width=1080&height=1920&nologo=true"
            print(f"Generating Scene {snum}...")
            r = await client.get(url)
            print(f"Scene {snum}: HTTP {r.status_code}, len={len(r.content)}")
            if r.status_code == 200:
                with open(f"test_free_scene_{snum}.jpg", "wb") as f:
                    f.write(r.content)
                print(f"Saved test_free_scene_{snum}.jpg")

if __name__ == "__main__":
    asyncio.run(generate_all())
