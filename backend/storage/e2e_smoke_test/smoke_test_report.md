# CrowdWisdom AI Studio — Real End-to-End Workflow Execution & Smoke Test Report

**Execution Timestamp:** `2026-11-05T16:41:00.080391+00:00`  
**Total Execution Time:** `486.68 seconds`  
**Final Verdict:** **`PASS`**

---

## 1. Executive Summary

| Metric | Result |
| :--- | :--- |
| **Total Tests Executed** | **21** |
| **Passed Tests** | **21** |
| **Failed Tests** | **0** |
| **Blocked Tests** | **0** |
| **Final Compliance Verdict** | **PASS** |

---

## 2. Stage-by-Stage Test Results

### Startup & Health

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| FastAPI Health & MongoDB Connection | **PASS** | 3.267s | `{"status": "ok", "service": "CrowdWisdom AI Studio", "version": "1.0.0", "database": "conn` |
| Integration Credentials Availability | **PASS** | 0.267s | `{"openrouter": true, "apify": true, "tavily": true, "exa": true, "nvidia_nim": true}` |

### Hermes Runtime

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Hermes Native AIAgent Tool Execution | **PASS** | 11.433s | `{"execution_id": "6aecb1aba2ae3588b32c6040", "mode": "native_hermes", "response": "The Cro` |

### Stage A: Campaign Creation

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Campaign Persistence & Schema Serialization | **PASS** | 0.178s | `{"id": "6aecb1aba2ae3588b32c6041", "status": "draft"}` |

### Stage B: Ads Manager Agent

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Apify Scraping, 30-Day Window & JSON Export | **PASS** | 93.5s | `{"ads_found": 0, "insights": 0, "export_path": "C:\\Users\\dashw\\OneDrive\\Desktop\\my pr` |

### Stage C: Script Agent

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Checkpoint 1: Creative Brief Synthesis & Approval | **PASS** | 6.464s | `{"brief_id": "6aecb20fa2ae3588b32c6047", "status": "approved"}` |
| Script Generation (PAIN_POINT + JSON Export) | **PASS** | 29.696s | `{"script_id": "6aecb20fa2ae3588b32c6048", "scenes": 5, "title": "Cut Through the Noise"}` |
| Script Generation (UNIQUE_DATA + JSON Export) | **PASS** | 10.099s | `{"script_id": "6aecb22ca2ae3588b32c6054", "scenes": 4, "title": "Unlock the Wisdom of the ` |
| Script Generation (PRODUCT_VALUE + JSON Export) | **PASS** | 21.541s | `{"script_id": "6aecb237a2ae3588b32c605e", "scenes": 4, "title": "Find Clarity in the Chaos` |

### Stage D: Human Approval Gate

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Checkpoint 2: Incomplete Storyboard Rejection (HTTP 400) | **PASS** | 0.112s | `{"rejected": true}` |
| Checkpoint 2: Valid Storyboard Approval | **PASS** | 0.287s | `{"script_id": "6aecb20fa2ae3588b32c6048", "status": "approved"}` |

### Stage E: Video Production Agent

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Render & Media Probe (30s Commercial) | **PASS** | 72.085s | `{"file_path": "C:\\Users\\dashw\\OneDrive\\Desktop\\my projects\\CrowdWisdom AI Studio\\ba` |
| Render & Media Probe (45s Commercial) | **PASS** | 101.972s | `{"file_path": "C:\\Users\\dashw\\OneDrive\\Desktop\\my projects\\CrowdWisdom AI Studio\\ba` |
| Render & Media Probe (60s Commercial) | **PASS** | 134.406s | `{"file_path": "C:\\Users\\dashw\\OneDrive\\Desktop\\my projects\\CrowdWisdom AI Studio\\ba` |

### Stage F: Video Streaming & Playback

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Video Endpoint Full Request (HTTP 200) | **PASS** | 0.016s | `{"status_code": 200, "content_length": 1384288, "accept_ranges": "bytes"}` |
| Video Endpoint Range Streaming (HTTP 206) | **PASS** | 0.003s | `{"status_code": 206, "content_range": "bytes 0-1023/1384288", "bytes_received": 1024}` |

### Stage G: Database & Kanban Persistence

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Database Referential Integrity & Kanban Persistence | **PASS** | 0.37s | `{"campaign_id": "6aecb1aba2ae3588b32c6041", "scripts_count": 4, "video_jobs_count": 3, "ka` |

### Stage H: Failure & Edge Cases

| Test Case | Status | Duration | Output Summary |
| :--- | :---: | :---: | :--- |
| Invalid Campaign ID Handling (HTTP 400) | **PASS** | 0.044s | `""` |
| Non-existent Campaign Handling (HTTP 404) | **PASS** | 0.116s | `""` |
| Unauthorized Access Rejection (HTTP 401) | **PASS** | 0.002s | `""` |
| Boot Recovery Stale Threshold Safety | **PASS** | 0.366s | `""` |

---

## 3. Video Validation & Technical Media Inspection (FFprobe / FFmpeg)

All three required commercial advertisement durations were freshly rendered and inspected with FFmpeg:

| Video Duration | Output Resolution | Video Codec | Audio Codec | Audio Track | File Size | Discrepancy | Media Path |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **30.0s** | 1080x1920 (9:16) | h264 | aac | True | 0.88 MB | 0.0s | `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\e2e_smoke_30s_261105_164115.mp4` |
| **45.0s** | 1080x1920 (9:16) | h264 | aac | True | 1.32 MB | 0.0s | `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\e2e_smoke_45s_261105_164115.mp4` |
| **60.0s** | 1080x1920 (9:16) | h264 | aac | True | 1.54 MB | 0.0s | `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\e2e_smoke_60s_261105_164115.mp4` |

---

## 4. HTTP Playback & Streaming Validation

- **Normal Request (`GET /api/media/videos/e2e_smoke_45s_261105_164115.mp4`):**
  - Status Code: **`200 OK`**
  - Content-Length: **`1384288 bytes`**
  - Accept-Ranges: **`bytes`**
  - Result: Complete video stream readable.

- **Range Request (`GET /api/media/videos/e2e_smoke_45s_261105_164115.mp4` with `Range: bytes=0-1023`):**
  - Status Code: **`206 Partial Content`**
  - Content-Range: **`bytes 0-1023/1384288`**
  - Content-Length: **`1024 bytes`**
  - Result: Byte-range slicing verified for fluid scrubbing in HTML5 video players.

---

## 5. Generated Artifacts Catalog

- **Campaign ID:** `6aecb1aba2ae3588b32c6041`
- **Exported Advertisements JSON:** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\e2e_smoke_test\exported_advertisements.json` (158 bytes)
- **Pain-Point Script JSON:** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\e2e_smoke_test\script_pain_point.json`
- **Unique-Data Script JSON:** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\e2e_smoke_test\script_unique_data.json`
- **Product-Value Script JSON:** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\storage\e2e_smoke_test\script_product_value.json`
- **Rendered 30s Video:** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\e2e_smoke_30s_261105_164115.mp4`
- **Rendered 45s Video:** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\e2e_smoke_45s_261105_164115.mp4`
- **Rendered 60s Video:** `C:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\e2e_smoke_60s_261105_164115.mp4`

---

## 6. Final Submission Readiness

- **Native Hermes Framework:** NousResearch/hermes-agent@c55af2c9 initialized and executed natively.
- **OpenMontage Video Engine:** calesthio/OpenMontage@d21f5d4e tool registry loaded with 155 tools.
- **Audible Spoken Narration:** Edge-TTS `en-US-ChristopherNeural` synchronized across all scenes.
- **Human Approval Gates:** Checkpoint 1 (Brief) & Checkpoint 2 (Storyboard) strictly enforced with 0-scene rejection.
- **Persistent Kanban Tasks:** 5 tasks tracked and persisted in MongoDB Atlas.
