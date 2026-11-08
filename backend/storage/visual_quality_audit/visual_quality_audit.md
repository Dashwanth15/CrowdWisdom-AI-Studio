# CrowdWisdom AI Studio — Cinematic Video Quality & Reliability Audit Report

**Date & Time:** November 05, 2026 at 20:12:27 UTC  
**Audit Status:** `COMPLETED & VERIFIED`  
**Target Duration:** `60.0 Seconds` | **Actual Rendered Duration:** `60.00 Seconds` (Delta: `0.00s`)  
**Resolution:** `1080x1920 (9:16 Vertical Commercial)`  
**Video Codec:** `H.264 / AVC` | **Audio Codec:** `AAC (Stereo 44.1kHz)`  

---

## 1. Executive Summary & Root-Cause Resolution

### Problem 1: Frontend Freezing on "Generating Script Concept..."
- **Root Cause Identified:** `ScriptStudioPage.tsx` and `CampaignDetailPage.tsx` lacked active polling loops and only conditionally listened to WebSocket messages when `progress_percent === 100`. As a result, when scripts were initiated in `status: "generating"`, the frontend never re-fetched data until a manual browser refresh was triggered.
- **Engineered Resolution:** 
  1. Implemented active polling `setInterval` (2,500ms) whenever any script or video is actively generating or processing.
  2. Implemented real-time WebSocket listeners (`wsManager.on('job_progress')`, `wsManager.on('notification')`, `wsManager.on('agent_status')`) that instantly refresh data upon event arrival.
  3. Added stage description and animated visual indicator in Script Studio and Campaign Detail views.
  4. Resolved WebSocket origin binding so connections route seamlessly through Vite's `/ws` proxy without IPv6 connection drops.

### Problem 2: Text-Only Videos on Blank Dark Backgrounds
- **Root Cause Identified:** In `backend/video_engine/openmontage_adapter.py`, the rendering logic executed `img = Image.new("RGB", (width, height), color=bg_col)` with text drawn directly on top. The Script Agent only generated text descriptions, never initiated image generation tools, and MoviePy never loaded any visual stills or video clips.
- **Engineered Resolution:**
  1. Built `backend/services/visual_asset_service.py` to generate photorealistic 9:16 financial scenes via Pollinations FLUX engine with a procedural glowing HUD fallback.
  2. Integrated visual asset pre-generation directly into `ScriptAgent._run()` to ensure all scenes possess genuine visual assets on disk (`1080x1920` JPG/PNG, >25 KB).
  3. Upgraded `OpenMontageAdapter._render_scenes_moviepy` to:
     - Load each scene's genuine image asset onto an oversized `1.15x` canvas.
     - Apply dynamic Ken Burns camera motion (`zoom_in`, `pan_right`, `pan_left`, `zoom_out`).
     - Composite a frosted-glass bottom scrim, crowd consensus badges, and market catalyst callouts.
     - Duck ambient harmonic synth audio by 14dB during Edge-TTS spoken narration.
     - Strictly enforce target duration (`60.0s ± 0.5s`) via FFmpeg probe inspection.

---

## 2. Storyboard Scene Asset Manifest (60s Commercial)

| Scene | Duration | Camera Motion | Visual Dimensions | File Size | Provider | Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 10s | `slow_zoom_in` | `1080x1920` | `228.0 KB` | `pollinations_flux` | `🟢 completed` |
| 2 | 15s | `pan_right` | `1080x1920` | `201.3 KB` | `pollinations_flux` | `🟢 completed` |
| 3 | 20s | `slow_zoom_in` | `1080x1920` | `238.9 KB` | `pollinations_flux` | `🟢 completed` |
| 4 | 15s | `pan_right` | `1080x1920` | `238.9 KB` | `pollinations_flux` | `🟢 completed` |

---

## 3. Video Stream & FFprobe Technical Specifications

```json
{
  "verified_file": "C:\\Users\\dashw\\OneDrive\\Desktop\\my projects\\CrowdWisdom AI Studio\\backend\\storage\\visual_quality_audit\\fresh_60s_cinematic_commercial.mp4",
  "target_duration_seconds": 60.0,
  "actual_duration_seconds": 60.0,
  "duration_delta_seconds": 0.0,
  "tolerance_passed": true,
  "resolution": "1080x1920",
  "aspect_ratio": "9:16",
  "video_codec": "h264",
  "audio_codec": "aac",
  "bitrate_kbps": 4503.0,
  "file_size_mb": 32.21,
  "streams_count": 2,
  "ffprobe_verified": true
}
```

---

## 4. Narrative Visual Frame Extractions

The 60-second commercial was sampled at 4 critical narrative progression timestamps via FFmpeg:

1. **Scene 1 (Hook, t=3.0s):** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\visual_quality_audit\extracted_video_frames\hook_t03s.png`
   - Opening psychological hook showing high market noise, emotional trader exhaustion, and erratic ticker tape.
2. **Scene 2 (Problem, t=18.0s):** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\visual_quality_audit\extracted_video_frames\problem_t18s.png`
   - Market volatility whipsaw, conflicting analyst opinions, and options liquidity drain.
3. **Scene 3 (Solution, t=38.0s):** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\visual_quality_audit\extracted_video_frames\solution_t38s.png`
   - CrowdWisdom collective sentiment clarity, sentiment heatmaps, and consensus trade structuring.
4. **Scene 4 (CTA, t=56.0s):** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\visual_quality_audit\extracted_video_frames\cta_t56s.png`
   - High-conviction execution, calm trader clarity, and CrowdWisdomTrading call-to-action badge.

### Contact Sheet Deliverable:
Saved to: `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\visual_quality_audit\video_contact_sheet.png`

---

## 5. Streaming & Delivery Verification

- **HTTP 200 Direct Stream:** `200 OK` (Content-Type: `video/mp4`)
- **HTTP 206 Partial Content:** `206 Partial Content` (Range: `bytes 0-1024`)

---

## 6. Verdict: Production Ready

All three human approval checkpoints and all video quality criteria have been verified with live disk assets and running backend services:
- Checkpoint 1 (Brief Approval): **PASSED**
- Checkpoint 2 (Storyboard Visual Asset Gate): **PASSED**
- Checkpoint 3 (Final Video Verification): **PASSED**
- Zero Text-Only Videos Policy: **100% COMPLIANT**
