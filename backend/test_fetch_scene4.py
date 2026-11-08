import httpx
import urllib.parse
import time

p4 = "Cinematic shot of a confident professional trader in modern office looking out through floor-to-ceiling glass windows at a panoramic city skyline at sunrise, subtle green trading charts glowing on a sleek curved monitor nearby, calm decisive certainty, 8k vertical 9:16 composition"
enc = urllib.parse.quote(p4[:500])
url = f"https://image.pollinations.ai/prompt/{enc}?width=1080&height=1920&nologo=true"

# Polling loop until 45s rate limit clears
for attempt in range(5):
    print(f"Attempt {attempt + 1}...")
    r = httpx.get(url, timeout=30, follow_redirects=True)
    if r.status_code == 200:
        with open("media/assets/asset_scene4_new.jpg", "wb") as f:
            f.write(r.content)
        print("Saved asset_scene4_new.jpg successfully!")
        break
    elif r.status_code == 402:
        print("Rate limit: waiting 15s...")
        time.sleep(15)
    else:
        print("HTTP", r.status_code)
        time.sleep(5)

