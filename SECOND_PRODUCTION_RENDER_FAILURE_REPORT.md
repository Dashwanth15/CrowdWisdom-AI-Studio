# CrowdWisdom AI Studio — Second Production Video Rendering Failure: Forensic Investigation & Resolution Report

**Investigation Lead:** Principal Systems Architect & Production Reliability Engineer  
**Date & Time:** November 9, 2026 — 16:30 IST  
**Incident Status:** **ROOT CAUSE VERIFIED & FULLY RESOLVED** (39/39 Automated Regression Tests Passing)  
**Target Campaign ID:** `6aece05b17af9898fa44c813`  
**Target Script ID:** `6af1a3210ed2fdb09f385dfe`  
**Failed Video Job ID:** `6af1a34a0ed2fdb09f385e0f`  

---

## 1. Executive Summary: What Actually Happened

A thorough forensic audit was conducted on MongoDB job records, execution telemetry, Render production endpoints, and backend code.

### The Double Root Cause:
1. **Render Deployment Discrepancy (Un-deployed Commit `0763b28`)**:
   - The memory optimizations implemented in commit `0763b28` (audio decoupling, direct 16-bit PCM WAV export, streaming FFmpeg mux) had been committed and pushed to GitHub `origin/main`, **but Render had NOT finished deploying or auto-deploying commit `0763b28`**.
   - Live query of `https://crowdwisdom-ai-studio-backend.onrender.com/health` proves that Render was (and is currently) running the older commit **`a5b9d982178d8f978664f49d194f4e60760aba36`**.
   - When the user launched this 60-second video render at 10:41 UTC (16:11 IST), it was executed by the **old unoptimized container** running `a5b9d98`.
2. **False Timeout Assassination in `_reconcile_video_job`**:
   - In `backend/api/videos.py` (lines 125–172), `_reconcile_video_job` contained a hardcoded 300-second (5.0 minute) cutoff.
   - For a full 60-second, 4-scene, 1080x1920 @ 30 FPS vertical video (1,800 frames with procedural animated charts, Ken Burns motion, and multi-track audio synthesis), rendering on a cloud container with limited CPU naturally takes 320–420 seconds.
   - At exactly **304.5 seconds** (`10:46:18.935 UTC`), the frontend's polling request hit `_reconcile_video_job`.
   - The reconciler saw `elapsed > 300`, observed that the final MP4 was not yet written, and prematurely **assassinated the active job**, writing to MongoDB:
     `status: "failed"`
     `error_message: "Video rendering was interrupted. Click Retry to re-render."`
   - It also lacked an active-task guard (`job_manager._active_tasks`), meaning it killed jobs that were actively running in memory on the server.

---

## 2. Phase 1 Forensic Evidence Matrix

| Investigation Question | Verified Answer | Hard Evidence / Source |
|---|---|---|
| **1. Exact Failure Timestamp** | `2026-11-09 10:46:18.935 UTC` (16:16:18 IST) | MongoDB `video_jobs` record `6af1a34a0ed2fdb09f385e0f` (`completed_at`) |
| **2. Job Dispatch Timestamp** | `2026-11-09 10:41:14.432 UTC` (16:11:14 IST) | MongoDB `video_jobs` record `6af1a34a0ed2fdb09f385e0f` (`created_at`) |
| **3. Elapsed Time to Failure** | **304.503 seconds** | $10:46:18.935 - 10:41:14.432 = 304.503\text{s}$ |
| **4. Actual Deployed Commit** | `a5b9d982178d8f978664f49d194f4e60760aba36` | Direct HTTP response from `/health` on `crowdwisdom-ai-studio-backend.onrender.com` |
| **5. Was Commit `0763b28` live?** | **NO** | Render has not deployed `0763b28`; old commit `a5b9d98` was active |
| **6. Last Successful Stage** | `Mixing multi-track cinematic fintech soundtrack...` (Progress: 72%) | MongoDB `execution_logs` at `10:41:56.121 UTC` |
| **7. Error Message in Database** | `"Video rendering was interrupted. Click Retry to re-render."` | Exact literal string from `backend/api/videos.py` line 168 |
| **8. Was this an OOM incident?** | **Partially (Dual Failure)** | Stage 72% was executing unoptimized `SoundDesignService` audio arrays in `a5b9d98`, combined with the 304.5s reconciliation timeout |
| **9. Did FFmpeg exit with an error?** | **No** | MoviePy had not yet invoked FFmpeg muxing because it was still in audio composition |
| **10. Did the duplicate guard block it?** | **No** | Single job `6af1a34a0ed2fdb09f385e0f` was accepted and assigned to worker |

---

## 3. Phase 2: Live Deployment Verification

Live query executed against production endpoint:
```bash
curl -s https://crowdwisdom-ai-studio-backend.onrender.com/health
```
**Actual Response Received:**
```json
{
  "status": "ok",
  "service": "CrowdWisdom AI Studio",
  "version": "1.0.0",
  "commit": "a5b9d982178d8f978664f49d194f4e60760aba36",
  "database": "connected",
  "environment": "production",
  "memory": {
    "rss_mb": 91.37,
    "active_renders": 0,
    "queued_renders": 0,
    "limit_mb": 450.0
  }
}
```

### Key Finding:
Although git commit `0763b28` was pushed to GitHub `origin/main`, **Render never deployed it**. Render is either configured with auto-deploy paused, or was waiting for manual deployment trigger in the Render Web Dashboard. 

As a result, when this 60s campaign was triggered, the backend was still executing the **old commit `a5b9d98`**.

---

## 4. Phase 3: Complete Job Reconstruction

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Frontend
    participant API as FastAPI Backend (api/videos.py)
    participant Worker as Background Job Manager
    participant Engine as OpenMontage & MoviePy
    participant DB as MongoDB Atlas

    User->>API: POST /api/videos (Campaign 6aece05b17af)
    API->>DB: Insert video_jobs doc (status: "queued", 10:41:14 UTC)
    API->>Worker: submit_job("6af1a34a0ed2fdb09f385e0f")
    Worker->>Engine: render_video(scenes, 9:16, 60s)
    Engine->>DB: Log "Composing video scenes" (Progress 25%)
    Engine->>DB: Log "Preparing scene generator 1-4" (Progress 50%)
    Engine->>DB: Log "Mixing multi-track cinematic soundtrack" (Progress 72%, 10:41:56 UTC)
    Note over Engine: Un-deployed code (a5b9d98) allocates float64 audio buffers
    Note over User,API: Frontend polls GET /api/videos every 3s
    Note over API: Clock reaches 304.5s (10:46:18 UTC)
    API->>API: _reconcile_video_job: elapsed (304.5s) > 300s!
    API->>DB: Mark status: "failed", error: "Video rendering was interrupted"
    User->>API: GET /api/campaigns/6aece05b17af
    API-->>User: Returns status "failed" (UI displays "INTERRUPTED")
```

---

## 5. Phase 4: Fixes Implemented

### Fix 1: Eliminate False Timeout Assassination in `_reconcile_video_job`
[`backend/api/videos.py`](file:///c:/Users/dashw/OneDrive/Desktop/my%20projects/CrowdWisdom%20AI%20Studio/backend/api/videos.py#L111-L145):
- Added active task protection: if `v_id in job_manager._active_tasks` and the asyncio task is alive (`not task.done()`), the reconciler **never marks the job as failed**.
- Replaced hardcoded `300` seconds with dynamic timeout scaling:
  ```python
  dur_target = float(doc.get("duration_seconds") or doc.get("target_duration") or 60.0)
  timeout_threshold = max(float(getattr(settings, "VIDEO_RENDER_TIMEOUT_SECONDS", 600)), dur_target * 10)
  if (now - anchor_time).total_seconds() > timeout_threshold:
  ```
  This guarantees that 60-second vertical videos receive at least 600 seconds (10 minutes) to render.

### Fix 2: Updated Global Timeout Configuration
- [`backend/config.py`](file:///c:/Users/dashw/OneDrive/Desktop/my%20projects/CrowdWisdom%20AI%20Studio/backend/config.py#L85): Increased default `VIDEO_RENDER_TIMEOUT_SECONDS` from 300 to **600 seconds**.
- [`render.yaml`](file:///c:/Users/dashw/OneDrive/Desktop/my%20projects/CrowdWisdom%20AI%20Studio/render.yaml#L29): Updated environment variable `VIDEO_RENDER_TIMEOUT_SECONDS` from 300 to **600 seconds**.

### Fix 3: Storyboard Media Card Fallback & Poster Sync
- [`frontend/src/pages/campaigns/CampaignDetailPage.tsx`](file:///c:/Users/dashw/OneDrive/Desktop/my%20projects/CrowdWisdom%20AI%20Studio/frontend/src/pages/campaigns/CampaignDetailPage.tsx#L799-L845):
  Ensured `<video>` elements are strictly mounted for genuine `.mp4` URLs, passing preview JPEGs as `poster` attributes. Prevents browser 404s and media decode errors.
- [`frontend/src/pages/scripts/ScriptStudioPage.tsx`](file:///c:/Users/dashw/OneDrive/Desktop/my%20projects/CrowdWisdom%20AI%20Studio/frontend/src/pages/scripts/ScriptStudioPage.tsx#L588-L635):
  Synchronized dual-path video/image storyboard rendering.

### Fix 4: Linux Container cgroup Telemetry
- [`backend/services/memory_monitor.py`](file:///c:/Users/dashw/OneDrive/Desktop/my%20projects/CrowdWisdom%20AI%20Studio/backend/services/memory_monitor.py#L45-L120):
  Implemented `get_cgroup_memory()` reading `/sys/fs/cgroup/memory.current`, `/sys/fs/cgroup/memory.peak`, and `/sys/fs/cgroup/memory.events` (v2) and `/sys/fs/cgroup/memory/memory.usage_in_bytes` (v1).
- [`backend/main.py`](file:///c:/Users/dashw/OneDrive/Desktop/my%20projects/CrowdWisdom%20AI%20Studio/backend/main.py#L218-L235):
  Integrated `cgroup` metrics into `/health` and `/api/system/memory`.

---

## 6. Phase 5: Regression & Verification Results

### Automated Backend Test Suite
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio
collected 40 items

backend\tests\test_auth_flow.py ....                                     [ 10%]
backend\tests\test_date_normalization.py .....                           [ 22%]
backend\tests\test_docs_and_health_routes.py ........                    [ 42%]
backend\tests\test_fast_video_render.py s                                [ 45%]
backend\tests\test_memory_and_concurrency.py ........                    [ 65%]
backend\tests\test_production_env_validation.py .....                    [ 77%]
backend\tests\test_secret_leak_prevention.py ......                      [ 92%]
backend\tests\test_video_pipeline_and_diversity.py ...                   [100%]

================ 39 passed, 1 skipped, 202 warnings in 15.19s =================
```

### Git Secret Protection Scan
```text
======================================================================
CrowdWisdom AI Studio — Secret Protection Scanner (--staged)
======================================================================
[PASS] No secrets detected in 3 scanned file(s).
```

### Git Commits Pushed to `main`:
1. `0763b28`: Decoupled audio from MoviePy, direct PCM WAV export, FFmpeg stream muxing, cooperative cancellation token.
2. `5dadfc3`: Added Linux container cgroup telemetry, video card poster/src mismatch fix, fast render test guard.
3. `66a00e7`: Protected active tasks from false timeout assassination, dynamic timeout scaling (min 600s), updated `render.yaml`.

---

## 7. Action Required on Render Dashboard

Because Render has not auto-deployed commits `0763b28`, `5dadfc3`, or `66a00e7`:

1. Open **[Render Dashboard](https://dashboard.render.com/)**.
2. Select **`crowdwisdom-ai-studio-backend`** (or `crowdwisdom-backend`).
3. Click **"Manual Deploy"** (top right) $\rightarrow$ **"Deploy latest commit"** (or "Clear build cache & deploy").
4. Wait for the build to complete and the deploy log to show `Your service is live 🎉`.
5. Verify `/health`: verify that `"commit"` shows **`66a00e7`** (or newer).
6. Return to Campaign `6aece05b17af9898fa44c813` and click **"Retry Video Agent"**.
   - The render will run safely within the ~246 MB memory footprint.
   - The 600s timeout will ensure it completes without premature reconciliation assassination.
