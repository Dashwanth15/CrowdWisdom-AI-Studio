# CrowdWisdom AI Studio — Render Production Deployment Guide

**Target Platform:** Render ([render.com](https://render.com))  
**Repository:** `https://github.com/Dashwanth15/CrowdWisdom-AI-Studio.git`  
**Branch:** `main`  
**Configuration File:** `render.yaml`  

---

## Pre-Deployment Verification Status

All 6 production blockers have been resolved and locally verified:

| Component | Audit Item | Status | Verification Detail |
| :--- | :--- | :--- | :--- |
| **Frontend** | SPA Client-Side Routing | **PASS** | `frontend/public/_redirects` created (`/* /index.html 200`). |
| **Frontend** | API Base URL Configuration | **PASS** | `api.ts` binds `import.meta.env.VITE_API_BASE_URL`. |
| **Frontend** | Dynamic WebSocket URL | **PASS** | `websocket.ts` binds `VITE_WS_URL` with auto-protocol upgrade. |
| **Frontend** | Media Asset Resolution | **PASS** | `utils.ts` routes `/media/...` through backend URL. |
| **Frontend** | Production Build | **PASS** | `tsc -b && vite build` completed in 8.21s (0 errors). |
| **Backend** | Dynamic `$PORT` Binding | **PASS** | `config.py` binds `$PORT` via `AliasChoices("APP_PORT", "PORT")`. |
| **Backend** | Production CORS Whitelist | **PASS** | `config.py` automatically includes `FRONTEND_URL`. |
| **Backend** | Health Probes | **PASS** | Both `/health` and `/api/health` return `200 OK`. |
| **Backend** | FFmpeg Precompiled Binary | **PASS** | `imageio-ffmpeg>=0.4.9` and `gunicorn` pinned in `backend/requirements.txt`. |
| **Security** | Zero Secret Leakage | **PASS** | `git_secret_check.py` scanned all staged files (0 secrets detected). |

---

## Step 1: Push Verified Production Code to GitHub

Because the Git repository underwent history cleaning to permanently remove previously exposed credentials, push to GitHub using the `--force` flag:

Open your terminal in the project directory and run:

```bash
git push --force origin main
```

*(If prompted, complete authentication in your browser via Git Credential Manager.)*

---

## Step 2: Deploy on Render

You can deploy using either **Method A (Automated Blueprint - Recommended)** or **Method B (Manual Dashboard)**.

---

### METHOD A: Automated Blueprint Deployment (Recommended)

Render provides native support for `render.yaml` Blueprints. This automatically configures both services, their build commands, health checks, and service-to-service links in one step.

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. In the top-right header, click **New +** and select **Blueprint**.
3. Connect your GitHub account (if not already connected) and select the repository:  
   `Dashwanth15/CrowdWisdom-AI-Studio`
4. Render will parse `render.yaml` and display the **Blueprint Plan**:
   - Service 1: `crowdwisdom-backend` (Web Service, Python)
   - Service 2: `crowdwisdom-frontend` (Static Site)
5. **Enter your Secret Environment Variables** when prompted:
   - `MONGODB_URL`: Your MongoDB Atlas connection URI (`mongodb+srv://<username>:<password>@cluster0.mongodb.net/`)
   - `GEMINI_API_KEY`: Your Google AI Studio API key
   - `OPENROUTER_API_KEY`: *(Optional)* OpenRouter key
   - `NVIDIA_NIM_API_KEY`: *(Optional)* NVIDIA NIM key
   - `APIFY_API_TOKEN`: *(Optional)* Apify Meta Ads scraper token
   - `TAVILY_API_KEY`: *(Optional)* Tavily AI search key
   - `EXA_API_KEY`: *(Optional)* Exa neural search key
   *(Note: `APP_SECRET_KEY` and `JWT_SECRET_KEY` are auto-generated as secure random strings by Render!)*
6. Click **Apply Blueprint**.
7. Render will automatically build and deploy both services!

---

### METHOD B: Manual Dashboard Deployment (Step-by-Step)

If you prefer to configure each service manually in the Render dashboard:

#### 1. Deploy Service 1: Backend Web Service (`crowdwisdom-backend`)

1. In Render Dashboard, click **New +** > **Web Service**.
2. Select repository: `Dashwanth15/CrowdWisdom-AI-Studio` (Branch: `main`).
3. Configure the fields:
   - **Name:** `crowdwisdom-backend`
   - **Region:** `Oregon (US West)` (or closest to your MongoDB Atlas region)
   - **Runtime:** `Python 3`
   - **Build Command:**  
     ```bash
     pip install --upgrade pip && pip install -r backend/requirements.txt
     ```
   - **Start Command:**  
     ```bash
     cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --limit-concurrency 50
     ```
   - **Plan:** `Starter` ($7/mo) or `Free`
4. Expand **Advanced**:
   - **Health Check Path:** `/health`
   - **Auto-Deploy:** `Yes`
5. Under **Environment Variables**, add the following:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | Enforces production security checks |
| `APP_HOST` | `0.0.0.0` | Binds to all network interfaces |
| `PYTHON_VERSION` | `3.11.10` | Pinned Python runtime |
| `MAX_CONCURRENT_VIDEO_RENDERS` | `1` | Enforces sequential video rendering to prevent Render OOM restarts |
| `VIDEO_FFMPEG_THREADS` | `2` | Limits libx264 encoding threads on single vCPU |
| `VIDEO_FFMPEG_PRESET` | `veryfast` | Memory-efficient low-lookahead encoder preset |
| `VIDEO_RENDER_TIMEOUT_SECONDS` | `300` | Automated timeout and cleanup for stalled renders |
| `VIDEO_RENDER_MEMORY_LIMIT_MB` | `450` | RSS memory threshold with automated GC & alert logging |
| `MONGODB_DB_NAME` | `crowdwisdom_ai_studio` | Database name |
| `APP_SECRET_KEY` | *(32+ char random string)* | Used for Fernet encryption of API keys |
| `JWT_SECRET_KEY` | *(32+ char random string)* | Used for signing user auth tokens |
| `MONGODB_URL` | `mongodb+srv://...` | MongoDB Atlas connection string |
| `FRONTEND_URL` | `https://crowdwisdom-frontend.onrender.com` | *(Update with your actual frontend URL once created)* |
| `CORS_ORIGINS` | `https://crowdwisdom-frontend.onrender.com` | *(Update with your actual frontend URL)* |
| `GEMINI_API_KEY` | `your_gemini_api_key` | Primary LLM key |
| `OPENROUTER_API_KEY`| *(Optional)* | Alternative LLM key |
| `NVIDIA_NIM_API_KEY`| *(Optional)* | NVIDIA key |
| `APIFY_API_TOKEN` | *(Optional)* | Meta Ads scraper token |
| `TAVILY_API_KEY` | *(Optional)* | Tavily search key |
| `EXA_API_KEY` | *(Optional)* | Exa search key |

6. Click **Create Web Service**.
7. Wait for the build to complete. Verify the build log shows `CrowdWisdom AI Studio backend ready.` and status turns **Live**.
8. Copy your Backend URL (e.g. `https://crowdwisdom-backend.onrender.com`).

---

#### 2. Deploy Service 2: Frontend Static Site (`crowdwisdom-frontend`)

1. In Render Dashboard, click **New +** > **Static Site**.
2. Select repository: `Dashwanth15/CrowdWisdom-AI-Studio` (Branch: `main`).
3. Configure the fields:
   - **Name:** `crowdwisdom-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `pnpm install && pnpm build` (or `npm install && npm run build`)
   - **Publish Directory:** `dist`
4. Under **Environment Variables**, add:

| Key | Value |
| :--- | :--- |
| `VITE_API_BASE_URL` | `https://crowdwisdom-backend.onrender.com/api` *(Your backend URL + /api)* |
| `VITE_WS_URL` | `wss://crowdwisdom-backend.onrender.com` *(Your backend URL with wss://)* |

5. Under **Redirects/Rewrites**:
   - Render automatically reads the `frontend/public/_redirects` file that is now present in the build (`/* /index.html 200`).
6. Click **Create Static Site**.
7. Wait for the build to finish (typically ~1-2 minutes).
8. Once live, copy your Frontend URL (e.g. `https://crowdwisdom-frontend.onrender.com`).
9. *(Important)*: Go back to your Backend Web Service's **Environment** tab and update `FRONTEND_URL` and `CORS_ORIGINS` with this exact frontend URL so that CORS and cookies match.

---

## Step 3: Production Validation Checklist

Once both services are deployed, execute these tests:

### 1. Backend Verification
- [ ] Open `https://<your-backend>.onrender.com/health` in your browser.  
  **Expected response:**
  ```json
  {
    "status": "ok",
    "service": "CrowdWisdom AI Studio",
    "version": "1.0.0",
    "database": "connected",
    "environment": "production"
  }
  ```
- [ ] Open `https://<your-backend>.onrender.com/api/docs` to verify OpenAPI Swagger documentation loads.

### 2. Frontend Verification
- [ ] Navigate to `https://<your-frontend>.onrender.com/`.
- [ ] Verify the official CrowdWisdom bears-and-bulls logo displays cleanly in the top-left sidebar and login screen.
- [ ] Open Browser DevTools (F12) > Network Tab. Verify:
  - No 404s on static assets.
  - Zero requests to `localhost`.
  - API requests point to `https://<your-backend>.onrender.com/api/...` with HTTP 200 responses.
- [ ] Test client-side routing: Navigate to `/campaigns` or `/dashboard` and refresh the page (F5). It should reload without a 404 error.
- [ ] Test WebSocket connection: In DevTools > Network > WS, verify a WebSocket connection to `wss://<your-backend>.onrender.com/ws/...` is established with status 101 Switching Protocols.

### 3. AI Marketing & Video Production Verification
- [ ] Create a test campaign or open an existing one.
- [ ] Launch the Script Agent: generate a cinematic storyboard.
- [ ] Approve the storyboard concept (Checkpoint 2).
- [ ] Launch Video Production: verify `JobManager` queues and renders the 1080p commercial.
- [ ] Verify the rendered video plays in the preview modal and download functions properly.

