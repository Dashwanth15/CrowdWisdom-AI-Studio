import urllib.request

def check(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as res:
            ct = res.headers.get("content-type")
            cl = res.headers.get("content-length")
            print(f"SUCCESS [{res.status}] {url} -> Content-Type: {ct}, Length: {cl}")
    except Exception as e:
        print(f"ERROR {url} -> {e}")

check("http://127.0.0.1:8000/api/health")
check("http://localhost:5173/")
check("http://localhost:5174/")
check("http://localhost:5173/media/videos/video_6aedcb004d0b1bb982f5f488.mp4")
check("http://localhost:5174/media/videos/video_6aedcb004d0b1bb982f5f488.mp4")
check("http://localhost:5174/media/assets/asset_6aedabff3b41067ff03d9851_1_c12e2f7c.jpg")
check("http://localhost:5174/assets/asset_6aedabff3b41067ff03d9851_1_c12e2f7c.jpg")
check("http://localhost:5174/api/campaigns/6aedabfe3b41067ff03d9850")
