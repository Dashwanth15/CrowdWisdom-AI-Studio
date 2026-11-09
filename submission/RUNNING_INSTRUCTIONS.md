# CrowdWisdom AI Studio — Local Execution & Evaluator Guide

This document contains step-by-step instructions for evaluating, configuring, and running **CrowdWisdom AI Studio** locally.

---

## 1. System Prerequisites

Before starting, ensure your local development workstation has the following installed:

- **Python**: Version `3.11` or higher (`python --version`)
- **Node.js**: Version `20.18.0` or higher (`node --version`)
- **Package Manager**: `pnpm` version `9.0.0` or higher (`pnpm --version`)
  - If pnpm is not installed: `npm install -g pnpm`
- **Database**: 
  - Local MongoDB instance (`mongodb://localhost:27017`), OR
  - Free [MongoDB Atlas](https://www.mongodb.com/atlas) cloud connection URI (`mongodb+srv://...`)
- **Media Engine**: `ffmpeg` (automatically resolved via `imageio-ffmpeg` or system PATH)

---

## 2. Repository Cloning & Environment Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/Dashwanth15/CrowdWisdom-AI-Studio.git
cd CrowdWisdom-AI-Studio
```

---

### Step 2: Configure Environment Variables (.env)

Copy the safe template from the project root:

```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On Linux / macOS:
cp .env.example .env
```

Open `.env` and set the following baseline values:
```ini
# Application Mode & Security
APP_ENV=development
APP_SECRET_KEY=32_random_characters_secret_key_here
JWT_SECRET_KEY=32_random_characters_jwt_secret_key_here
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=crowdwisdom_ai_studio

# Storage Configuration
MEDIA_DIR=./backend/media
```

---

## 3. Backend Setup

### Step 1: Create a Python Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on Linux / macOS:
source .venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### Step 3: Seed Administrative Credentials

```bash
# On Windows PowerShell:
$env:PYTHONPATH="backend"
python backend/utils/seed_data.py

# On Linux / macOS:
PYTHONPATH=backend python backend/utils/seed_data.py
```

*Default Seeded Credentials:*
- **Email**: `admin@crowdwisdom.ai`
- **Password**: `admin1234`

### Step 4: Start the FastAPI Backend Server

```bash
# On Windows PowerShell:
$env:PYTHONPATH="backend"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

# On Linux / macOS:
PYTHONPATH=backend uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

- **Backend Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Health Endpoint**: `http://localhost:8000/health`

---

## 4. Frontend Setup

In a separate terminal window:

### Step 1: Navigate to the Frontend Directory
```bash
cd frontend
```

### Step 2: Install Node Dependencies
```bash
pnpm install
```

### Step 3: Start the Vite Development Server
```bash
pnpm dev
```

- **Web Application URL**: `http://localhost:5173`

---

## 5. Configuring External AI Providers

You can provide API keys via `.env` or through the platform's **Settings & Integrations** UI.

Keys configured in the UI are encrypted at rest using Fernet symmetric encryption:

| Provider | Purpose | How to Configure |
|---|---|---|
| **Apify** | Meta Ads Library scraping | Set `APIFY_API_TOKEN` in `.env` OR add in `http://localhost:5173/settings` under *Apify*. |
| **Tavily** | Trading pain point research | Set `TAVILY_API_KEY` in `.env` OR add in `http://localhost:5173/settings` under *Tavily*. |
| **Exa** | Neural semantic market research | Set `EXA_API_KEY` in `.env` OR add in `http://localhost:5173/settings` under *Exa*. |
| **OpenRouter / NVIDIA NIM** | Scriptwriting and brief synthesis | Set `OPENROUTER_API_KEY` or `NVIDIA_NIM_API_KEY` in `.env` OR add in `http://localhost:5173/settings`. |

*Note: For evaluator convenience, if external API tokens are not provided, the platform automatically utilizes benchmark market intelligence and pre-seeded research to allow complete end-to-end evaluation without API quota limits.*

---

## 6. Running the Automated Test Suite

To verify all system components without making expensive API calls:

```bash
# On Windows PowerShell:
$env:PYTHONPATH="backend"
python -m pytest backend/tests/test_video_pipeline_and_diversity.py backend/tests/test_docs_and_health_routes.py backend/tests/test_auth_flow.py backend/tests/test_date_normalization.py backend/tests/test_secret_leak_prevention.py backend/tests/test_production_env_validation.py -v

# On Linux / macOS:
PYTHONPATH=backend python -m pytest backend/tests/test_video_pipeline_and_diversity.py backend/tests/test_docs_and_health_routes.py backend/tests/test_auth_flow.py backend/tests/test_date_normalization.py backend/tests/test_secret_leak_prevention.py backend/tests/test_production_env_validation.py -v
```

**Expected Result:** `31 passed in ~10 seconds`.

---

## 7. Running the Full Pipeline Smoke Test

To execute an end-to-end simulation covering campaign creation, ad research, brief synthesis, scriptwriting, and video composition:

```bash
# On Windows PowerShell:
$env:PYTHONPATH="backend"
python backend/utils/pipeline_smoke_test.py

# On Linux / macOS:
PYTHONPATH=backend python backend/utils/pipeline_smoke_test.py
```
