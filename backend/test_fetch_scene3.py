import httpx
import urllib.parse

p3 = "Ultra-modern financial trading workstation showing glowing interface of CrowdWisdomTrading platform with green bullish consensus indicators and real-time sentiment charts, sleek dark obsidian UI, professional fintech trader workspace, cinematic commercial lighting, 8k vertical 9:16 composition"
enc = urllib.parse.quote(p3[:500])
url = f"https://image.pollinations.ai/prompt/{enc}?width=1080&height=1920&nologo=true"

r = httpx.get(url, timeout=30, follow_redirects=True)
print("Scene 3 Status:", r.status_code, "Length:", len(r.content))
if r.status_code == 200:
    with open("media/assets/asset_scene3_new.jpg", "wb") as f:
        f.write(r.content)
    print("Saved asset_scene3_new.jpg successfully!")

