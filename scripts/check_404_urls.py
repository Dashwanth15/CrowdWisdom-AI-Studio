import urllib.request
import urllib.parse
import urllib.error
import json

base = "https://crowdwisdom-ai-studio-backend.onrender.com"

# Login
login_url = f"{base}/api/auth/login"
data = urllib.parse.urlencode({"username": "admin@crowdwisdom.ai", "password": "admin123"}).encode()
req = urllib.request.Request(login_url, data=data, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode())["access_token"]

urls = [
    f"{base}/api/scripts/6af1676f009d4af8ba1f9a33",
    f"{base}/api/scripts/6aeffb4b19535e71781335b0",
    f"{base}/api/videos/6af1676f009d4af8ba1f9a33",
    f"{base}/api/videos/6aeffb4b19535e71781335b0",
]
for u in urls:
    try:
        r_req = urllib.request.Request(u)
        r_req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(r_req) as r:
            print(u, r.status)
    except urllib.error.HTTPError as e:
        print(u, "HTTP", e.code)
    except Exception as e:
        print(u, "ERROR", e)
