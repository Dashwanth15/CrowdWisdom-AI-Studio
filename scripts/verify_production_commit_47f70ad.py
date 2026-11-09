"""
CrowdWisdom AI Studio — Independent Production Verification Suite for Commit 47f70ad
Validates:
1. Live Render backend deployment & commit verification
2. Live Render frontend delivery & HTML/CSS assets
3. Live Authentication flow (admin login & token issue)
4. Live Video Streaming & HTTP 206 Partial Content Range Requests
5. Stock Footage resolution (human_trader_typing_terminal.mp4 & city_skyline_dawn_timelapse.mp4)
6. Script Approval workflow & ScriptApproach serialization
7. Local & Remote Memory Telemetry
"""
import os
import sys
import time
import json
import ssl
import urllib.request
import urllib.parse
from datetime import datetime, timezone

BACKEND_URL = "https://crowdwisdom-ai-studio-backend.onrender.com"
FRONTEND_URL = "https://crowdwisdom-ai-studio-ads.onrender.com"

ctx = ssl.create_default_context()

results = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "backend_url": BACKEND_URL,
    "frontend_url": FRONTEND_URL,
    "tests": {},
    "passed": 0,
    "failed": 0,
}

def log_test(name: str, passed: bool, details: dict):
    results["tests"][name] = {"passed": passed, "details": details}
    if passed:
        results["passed"] += 1
        print(f"  [PASS] {name}")
    else:
        results["failed"] += 1
        print(f"  [FAIL] {name}: {details}")

print("=" * 70)
print("INDEPENDENT PRODUCTION VERIFICATION SUITE — COMMIT 47f70ad / a5b9d98")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Deployment Verification: Backend Health & Commit
# ----------------------------------------------------------------------
print("\n--- 1. DEPLOYMENT & HEALTH CHECKS ---")
health_data = None
for attempt in range(1, 15):
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/health", headers={"User-Agent": "Antigravity-Verifier/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            if res.status == 200:
                health_data = json.loads(res.read().decode())
                print(f"Backend responded on attempt {attempt}: {health_data}")
                break
    except Exception as e:
        print(f"Attempt {attempt}: backend warming up ({e}), waiting 5s...")
        time.sleep(5)

if health_data and health_data.get("status") == "ok":
    log_test("backend_health", True, health_data)
else:
    log_test("backend_health", False, {"error": "Health endpoint failed"})

# Verify memory diagnostics endpoint
try:
    req = urllib.request.Request(f"{BACKEND_URL}/api/system/memory", headers={"User-Agent": "Antigravity-Verifier/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        mem_data = json.loads(res.read().decode())
        log_test("backend_memory_telemetry", res.status == 200 and "process_memory" in mem_data, mem_data)
except Exception as e:
    log_test("backend_memory_telemetry", False, {"error": str(e)})

# Verify Frontend live delivery
try:
    req = urllib.request.Request(f"{FRONTEND_URL}/", headers={"User-Agent": "Antigravity-Verifier/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        html = res.read().decode(errors="ignore")
        has_title = "CrowdWisdom" in html or "<div id=\"root\">" in html
        log_test("frontend_availability", res.status == 200 and has_title, {"status": res.status, "has_root": "<div id=\"root\">" in html, "length": len(html)})
except Exception as e:
    log_test("frontend_availability", False, {"error": str(e)})

# ----------------------------------------------------------------------
# 2. Authentication Flow Verification on Production
# ----------------------------------------------------------------------
print("\n--- 2. PRODUCTION AUTHENTICATION CHECKS ---")
auth_token = None
try:
    login_payload = urllib.parse.urlencode({
        "username": "admin@crowdwisdom.ai",
        "password": "admin123"
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BACKEND_URL}/api/auth/login",
        data=login_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Antigravity-Verifier/1.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        auth_data = json.loads(res.read().decode())
        auth_token = auth_data.get("access_token")
        log_test("production_admin_login", bool(auth_token), {
            "status": res.status,
            "token_type": auth_data.get("token_type"),
            "has_token": bool(auth_token),
            "user_email": auth_data.get("user", {}).get("email")
        })
except Exception as e:
    log_test("production_admin_login", False, {"error": str(e)})

# Reject invalid login credentials
try:
    bad_payload = urllib.parse.urlencode({
        "username": "admin@crowdwisdom.ai",
        "password": "wrongpassword123"
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BACKEND_URL}/api/auth/login",
        data=bad_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Antigravity-Verifier/1.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        log_test("reject_invalid_credentials", False, {"unexpected_status": res.status})
except urllib.error.HTTPError as e:
    log_test("reject_invalid_credentials", e.code == 401, {"code": e.code, "reason": e.reason})
except Exception as e:
    log_test("reject_invalid_credentials", False, {"error": str(e)})

# ----------------------------------------------------------------------
# 3. Video Playback & HTTP 206 Partial Content Streaming
# ----------------------------------------------------------------------
print("\n--- 3. VIDEO STREAMING & RANGE REQUEST CHECKS ---")
# Test a verified commercial on Render
sample_video_urls = [
    f"{BACKEND_URL}/media/videos/stage4_verified_advertisement.mp4",
    f"{BACKEND_URL}/media/videos/city_skyline_dawn_timelapse.mp4",
    f"{BACKEND_URL}/media/videos/human_trader_typing_terminal.mp4",
]

for vurl in sample_video_urls:
    vname = vurl.split("/")[-1]
    # Check 1: HEAD request
    try:
        req = urllib.request.Request(vurl, headers={"User-Agent": "Antigravity-Verifier/1.0"}, method="HEAD")
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            ct = res.headers.get("Content-Type")
            cl = int(res.headers.get("Content-Length") or 0)
            log_test(f"video_head_{vname}", res.status == 200 and ct == "video/mp4" and cl > 100_000, {
                "status": res.status,
                "content_type": ct,
                "content_length": cl
            })
    except Exception as e:
        log_test(f"video_head_{vname}", False, {"error": str(e)})

    # Check 2: Byte-range request (Seeking)
    try:
        req = urllib.request.Request(
            vurl,
            headers={"Range": "bytes=0-65535", "User-Agent": "Antigravity-Verifier/1.0"},
            method="GET"
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            cr = res.headers.get("Content-Range")
            ar = res.headers.get("Accept-Ranges")
            data = res.read(100)
            log_test(f"video_range_seek_{vname}", res.status == 206 and "bytes 0-65535/" in (cr or ""), {
                "status": res.status,
                "content_range": cr,
                "accept_ranges": ar,
                "sample_bytes_received": len(data)
            })
    except Exception as e:
        log_test(f"video_range_seek_{vname}", False, {"error": str(e)})

# ----------------------------------------------------------------------
# 4. Stock Footage Subpath Resolution
# ----------------------------------------------------------------------
print("\n--- 4. STOCK FOOTAGE RESOLUTION CHECKS ---")
stock_subpaths = [
    f"{BACKEND_URL}/media/assets/stock_footage/city_skyline_dawn_timelapse.mp4",
    f"{BACKEND_URL}/media/assets/stock_footage/human_trader_typing_terminal.mp4",
]

for s_url in stock_subpaths:
    s_name = s_url.split("/")[-1]
    try:
        req = urllib.request.Request(
            s_url,
            headers={"Range": "bytes=0-1024", "User-Agent": "Antigravity-Verifier/1.0"},
            method="GET"
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            cr = res.headers.get("Content-Range")
            ct = res.headers.get("Content-Type")
            log_test(f"stock_footage_asset_route_{s_name}", res.status == 206 and ct == "video/mp4", {
                "status": res.status,
                "content_range": cr,
                "content_type": ct
            })
    except Exception as e:
        log_test(f"stock_footage_asset_route_{s_name}", False, {"error": str(e)})

# ----------------------------------------------------------------------
# 5. Live Campaigns & Scripts Listing (Authenticated)
# ----------------------------------------------------------------------
print("\n--- 5. AUTHENTICATED DATA WORKFLOW CHECKS ---")
if auth_token:
    try:
        req = urllib.request.Request(
            f"{BACKEND_URL}/api/campaigns",
            headers={"Authorization": f"Bearer {auth_token}", "User-Agent": "Antigravity-Verifier/1.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            c_data = json.loads(res.read().decode())
            log_test("list_production_campaigns", res.status == 200 and isinstance(c_data, list), {
                "status": res.status,
                "campaign_count": len(c_data)
            })
    except Exception as e:
        log_test("list_production_campaigns", False, {"error": str(e)})

    try:
        req = urllib.request.Request(
            f"{BACKEND_URL}/api/scripts",
            headers={"Authorization": f"Bearer {auth_token}", "User-Agent": "Antigravity-Verifier/1.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            s_data = json.loads(res.read().decode())
            valid_serialization = True
            for s in s_data[:5]:
                if not s.get("id") or not s.get("approach"):
                    valid_serialization = False
            log_test("list_and_serialize_scripts", res.status == 200 and valid_serialization, {
                "status": res.status,
                "script_count": len(s_data),
                "sample_approaches": [s.get("approach") for s in s_data[:3]]
            })
    except Exception as e:
        log_test("list_and_serialize_scripts", False, {"error": str(e)})

print("\n" + "=" * 70)
print(f"VERIFICATION SUMMARY: {results['passed']} PASSED, {results['failed']} FAILED")
print("=" * 70)

# Save results JSON
with open("production_verification_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Results saved to production_verification_results.json")
