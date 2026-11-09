import urllib.request
import urllib.parse
import json
import ssl
import sys
import asyncio
import websockets

BACKEND_URL = "https://crowdwisdom-ai-studio-backend.onrender.com"
WS_URL = "wss://crowdwisdom-ai-studio-backend.onrender.com"
PROD_ORIGIN = "https://crowdwisdom-ai-studio-ads.onrender.com"

ssl_ctx = ssl.create_default_context()

def test_options(path):
    url = f"{BACKEND_URL}{path}"
    req = urllib.request.Request(url, method="OPTIONS")
    req.add_header("Origin", PROD_ORIGIN)
    req.add_header("Access-Control-Request-Method", "GET")
    req.add_header("Access-Control-Request-Headers", "authorization,content-type")
    try:
        with urllib.request.urlopen(req, context=ssl_ctx) as resp:
            headers = dict(resp.headers)
            status = resp.status
            origin_hdr = headers.get("Access-Control-Allow-Origin") or headers.get("access-control-allow-origin")
            cred_hdr = headers.get("Access-Control-Allow-Credentials") or headers.get("access-control-allow-credentials")
            return {
                "path": path,
                "status": status,
                "allow_origin": origin_hdr,
                "allow_credentials": cred_hdr,
                "success": status == 200 and origin_hdr == PROD_ORIGIN,
            }
    except Exception as e:
        return {"path": path, "status": "ERROR", "error": str(e), "success": False}

def test_login():
    url = f"{BACKEND_URL}/api/auth/login"
    data = urllib.parse.urlencode({"username": "admin@crowdwisdom.ai", "password": "admin123"}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Origin", PROD_ORIGIN)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, context=ssl_ctx) as resp:
            headers = dict(resp.headers)
            body = json.loads(resp.read().decode())
            return {
                "status": resp.status,
                "allow_origin": headers.get("access-control-allow-origin"),
                "token": body.get("access_token"),
            }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "token": None}

def test_get_auth(path, token):
    url = f"{BACKEND_URL}{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Origin", PROD_ORIGIN)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, context=ssl_ctx) as resp:
            headers = dict(resp.headers)
            data = resp.read().decode()
            return {
                "path": path,
                "status": resp.status,
                "allow_origin": headers.get("access-control-allow-origin"),
                "allow_credentials": headers.get("access-control-allow-credentials"),
                "body_len": len(data),
                "success": resp.status == 200,
            }
    except urllib.error.HTTPError as he:
        headers = dict(he.headers)
        return {
            "path": path,
            "status": he.code,
            "allow_origin": headers.get("access-control-allow-origin"),
            "allow_credentials": headers.get("access-control-allow-credentials"),
            "error": str(he),
            "success": False,
        }
    except Exception as e:
        return {"path": path, "status": "ERROR", "error": str(e), "success": False}

async def test_websocket(token=None):
    cid = f"client_test_{int(asyncio.get_event_loop().time() * 1000)}"
    param = f"?token={token}" if token else ""
    uri = f"{WS_URL}/ws/{cid}{param}"
    try:
        async with websockets.connect(uri, origin=PROD_ORIGIN) as ws:
            msg = await ws.recv()
            await ws.send(json.dumps({"type": "ping"}))
            resp = await ws.recv()
            return {"status": "CONNECTED", "welcome": json.loads(msg), "ping_resp": json.loads(resp), "success": True}
    except Exception as e:
        return {"status": "FAILED", "error": str(e), "success": False}

def run_suite():
    print("=" * 70)
    print("CrowdWisdom AI Studio — Production CORS & WebSocket Verification Suite")
    print(f"Target Backend:  {BACKEND_URL}")
    print(f"Target Frontend: {PROD_ORIGIN}")
    print("=" * 70)

    # 1. Health check
    print("\n[1] Testing /health...")
    req = urllib.request.Request(f"{BACKEND_URL}/health")
    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        h_data = json.loads(resp.read().decode())
        print(f"    Status: {resp.status} | Commit: {h_data.get('commit')} | RSS: {h_data.get('memory', {}).get('rss_mb')} MB")

    # 2. OPTIONS Preflight
    print("\n[2] Testing OPTIONS Preflight across all critical routes...")
    routes = [
        "/api/campaigns/",
        "/api/scripts/",
        "/api/creative-briefs/",
        "/api/assets/",
        "/api/videos/",
    ]
    for r in routes:
        res = test_options(r)
        status_str = f"HTTP {res['status']}"
        origin_str = f"Allow-Origin: {res.get('allow_origin')}"
        cred_str = f"Allow-Creds: {res.get('allow_credentials')}"
        print(f"    {r:<25} -> {status_str:<10} | {origin_str:<55} | {cred_str}")

    # 3. Authentication
    print("\n[3] Authenticating via POST /api/auth/login from production origin...")
    login_res = test_login()
    print(f"    Login Status: {login_res['status']} | Allow-Origin: {login_res.get('allow_origin')}")
    token = login_res.get("token")
    if not token:
        print("    FAILED to retrieve access token!")
        sys.exit(1)
    print(f"    JWT Token Acquired (len={len(token)})")

    # 4. Authenticated API Routes
    print("\n[4] Testing Authenticated GET Requests...")
    auth_routes = [
        "/api/campaigns",
        "/api/campaigns/6aece05b17af9898fa44c813",
        "/api/scripts?campaign_id=6aece05b17af9898fa44c813",
        "/api/creative-briefs/campaign/6aece05b17af9898fa44c813",
        "/api/assets?campaign_id=6aece05b17af9898fa44c813",
        "/api/videos?campaign_id=6aece05b17af9898fa44c813",
    ]
    for r in auth_routes:
        res = test_get_auth(r, token)
        status_str = f"HTTP {res['status']}"
        origin_str = f"Allow-Origin: {res.get('allow_origin')}"
        bytes_str = f"Bytes: {res.get('body_len', 0)}"
        print(f"    {r:<55} -> {status_str:<10} | {origin_str:<55} | {bytes_str}")

    # 5. WebSocket Connection
    print("\n[5] Testing WebSocket with Origin header...")
    ws_unauth = asyncio.run(test_websocket(None))
    print(f"    Unauthenticated WS: {ws_unauth['status']} | Ping response: {ws_unauth.get('ping_resp')}")
    ws_auth = asyncio.run(test_websocket(token))
    print(f"    Authenticated WS:   {ws_auth['status']} | Ping response: {ws_auth.get('ping_resp')}")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    run_suite()

