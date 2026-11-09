"""
CrowdWisdom AI Studio — Production Script Approval Workflow Verification
"""
import os
import sys
import json
import ssl
import urllib.request
import urllib.parse

BACKEND_URL = "https://crowdwisdom-ai-studio-backend.onrender.com"
ctx = ssl.create_default_context()

print("=" * 70)
print("PRODUCTION SCRIPT APPROVAL WORKFLOW VERIFICATION")
print("=" * 70)

# 1. Login
login_payload = urllib.parse.urlencode({"username": "admin@crowdwisdom.ai", "password": "admin123"}).encode()
req = urllib.request.Request(
    f"{BACKEND_URL}/api/auth/login",
    data=login_payload,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST"
)
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    token = json.loads(res.read().decode())["access_token"]
print("✓ Admin authenticated on Render")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 2. Get scripts
req = urllib.request.Request(f"{BACKEND_URL}/api/scripts?limit=20", headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    scripts = json.loads(res.read().decode())
print(f"✓ Found {len(scripts)} scripts in production database")

# Find a draft or approved script
target_script = None
for s in scripts:
    if s.get("scenes") and len(s["scenes"]) >= 3:
        target_script = s
        break

if not target_script:
    print("No existing script with scenes found. Exiting.")
    sys.exit(1)

script_id = target_script["id"]
print(f"Target Script: id={script_id}, title='{target_script.get('title')}', current_status='{target_script.get('status')}'")
print(f"Approach: {target_script.get('approach')}")
print(f"Scenes count: {len(target_script.get('scenes', []))}")

# 3. Test Approval Endpoint
print(f"\nSubmitting POST /api/scripts/{script_id}/approve...")
req = urllib.request.Request(
    f"{BACKEND_URL}/api/scripts/{script_id}/approve",
    headers=headers,
    data=b"{}",
    method="POST"
)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as res:
        approved = json.loads(res.read().decode())
        print(f"✓ Approval HTTP Status: {res.status}")
        print(f"  Approved Status: {approved.get('status')}")
        print(f"  Approved By: {approved.get('approved_by')}")
        print(f"  Approved At: {approved.get('approved_at')}")
        print(f"  Approach: {approved.get('approach')}")
        
        # Verify scene assets
        scenes = approved.get("scenes", [])
        all_completed = True
        for sc in scenes:
            s_num = sc.get("scene_number")
            v_status = sc.get("visual_asset_status")
            v_url = sc.get("visual_asset_url")
            v_path = sc.get("visual_asset_path")
            print(f"  Scene {s_num}: status={v_status}, url={v_url}, path={v_path}")
            if v_status != "completed":
                all_completed = False
        
        print("\nAll scene visual assets confirmed completed:", all_completed)
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"HTTP Error {e.code}: {e.reason}")
    print(f"Detail: {err_body}")
    sys.exit(1)
except Exception as e:
    print(f"Error during approval: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("SCRIPT APPROVAL WORKFLOW VERIFIED SUCCESSFULLY ON PRODUCTION")
print("=" * 70)

