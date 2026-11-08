import urllib.request

for url in [
    'http://localhost:5173/media/videos/video_6aedcb004d0b1bb982f5f488.mp4',
    'http://localhost:5173/media/assets/asset_6aedabff3b41067ff03d9851_1_c12e2f7c.jpg',
    'http://localhost:5173/assets/asset_6aedabff3b41067ff03d9851_1_c12e2f7c.jpg'
]:
    try:
        r = urllib.request.urlopen(url, timeout=3)
        ct = r.headers.get("content-type")
        cl = r.headers.get("content-length")
        print(f"SUCCESS: {url} -> HTTP {r.status} [{ct}, {cl} bytes]")
    except Exception as e:
        print(f"ERROR: {url} -> {e}")
