# CrowdWisdom AI Studio
### Autonomous AI Marketing Agent & Cinematic Video Advertising Platform

> **Tagline:** From Market Intelligence to Cinematic Advertising.  
> **Target Business:** CrowdWisdomTrading.com  
> **Core Stack:** Python + Hermes Agent Framework + FastAPI + MongoDB + React + Vite + TypeScript + Tailwind CSS + shadcn/ui + React Flow + OpenMontage

---

## 1. Executive Summary

**CrowdWisdom AI Studio** is a commercial-grade, autonomous full-stack SaaS platform designed specifically for **CrowdWisdomTrading.com**. It automates the end-to-end creative marketing pipeline:

1. **Advertisement Discovery & Research** (Meta Ads Library via Apify)
2. **Creative Intelligence Engine** (Synthesis of competitor angles, pain points, and brand USPs)
3. **Checkpoint 1: Creative Brief Approval** (Human-in-the-loop sign-off)
4. **Cinematic Script & Storyboard Studio** (3 distinct strategic approaches: Pain-Point, Unique-Data, Product-Value)
5. **Checkpoint 2: Storyboard Approval** (Strict human gate before video generation)
6. **Cinematic Video Production** (OpenMontage / MoviePy rendering 30–60s 9:16, 16:9, or 1:1 MP4 videos)
7. **Asset Management & Observability** (Centralized media library, live WebSocket progress, execution logs)

---

## 2. Architectural Highlights & Refinements

- **Dedicated Creative Intelligence Engine (CIE):** Bridges the gap between raw ad data and creative scripts by synthesizing observed hooks, emotional triggers, and compliance guardrails into an actionable strategic brief.
- **Persistent Job Architecture & Boot Recovery:** `JobManager` enforces idempotency keys, manages async task cancellation, and scans MongoDB on server restart to recover interrupted jobs.
- **Hermes Agent Adapter Layer:** Isolates `NousResearch/hermes-agent` behind `HermesAgentAdapter`, supporting tool registration, execution threads, and verified LLM fallback.
- **OpenMontage Video Engine Adapter:** Modular integration with tool registry discovery and automated MoviePy compositing that outputs actual MP4 commercial video files.
- **Storage Abstraction:** `BaseStorageService` providing unified media storage (local filesystem storage initially, extensible to AWS S3/Cloudflare R2/MinIO).
- **Cryptographic Credential Security:** All external provider API keys (OpenRouter, NVIDIA NIM, Apify, Tavily, Exa) are encrypted using Fernet symmetric encryption with keys derived from `APP_SECRET_KEY` outside MongoDB.
- **Separate Observability Model:** Decouples high-level execution records (`agent_executions`) from fine-grained, timestamped step logs (`execution_logs`).
- **Human-in-the-Loop Checkpoints:**
  - *Checkpoint 1:* Review & approve Creative Strategic Briefs.
  - *Checkpoint 2:* Review, edit scene-by-scene storyboard, and approve scripts before video generation.
  - *Checkpoint 3:* Preview, review, and download rendered MP4 commercials.

---

## 3. Directory Layout

```
CrowdWisdom AI Studio/
├── backend/
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Pydantic environment configuration
│   ├── requirements.txt            # Python dependencies
│   ├── api/                        # REST & WebSocket routers
│   │   ├── auth.py                 # JWT authentication & user roles
│   │   ├── campaigns.py            # Campaign CRUD & duplication
│   │   ├── agents.py               # Agent execution & task dispatching
│   │   ├── creative_briefs.py      # Checkpoint 1: Creative Brief review & approval
│   │   ├── scripts.py              # Checkpoint 2: Storyboard review, editing, approval
│   │   ├── videos.py               # Video job dispatch & rendering
│   │   ├── research.py             # Ad discovery, scores, marketing insights
│   │   ├── integrations.py         # Secure provider credentials & live connection testing
│   │   ├── dashboard.py            # Stats, assets, and media delivery
│   │   └── websocket.py            # Real-time WebSocket channel
│   ├── agents/                     # Specialized AI Agents
│   │   ├── base_agent.py           # Base agent wrapper with MongoDB logging
│   │   ├── ads_manager_agent.py    # Discovers & scores competitor ads (Apify)
│   │   ├── script_agent.py         # Drafts cinematic storyboards (Tavily/Exa/LLM)
│   │   └── video_production_agent.py # Coordinates video compositing
│   ├── orchestrator/
│   │   └── hermes_orchestrator.py  # Coordinates workflow pipeline & state
│   ├── services/
│   │   ├── auth_service.py         # Password hashing & JWT token issuing
│   │   ├── integration_service.py  # Fernet key encryption & masking
│   │   ├── storage_service.py      # Local / S3 unified storage abstraction
│   │   ├── websocket_manager.py    # Live event broadcasting
│   │   ├── hermes_adapter.py       # Isolated Hermes framework adapter
│   │   └── creative_intelligence_engine.py # Strategic synthesis engine
│   ├── workers/
│   │   └── job_manager.py          # Idempotency, task tracking, boot recovery
│   ├── integrations/               # External client integrations
│   │   ├── apify_client.py         # Meta Ads Library scraper
│   │   ├── tavily_client.py        # Web search & trader pain points
│   │   ├── exa_client.py           # Semantic search & content discovery
│   │   └── llm_client.py           # OpenRouter & NVIDIA NIM unified client
│   ├── video_engine/
│   │   └── openmontage_adapter.py  # OpenMontage & MoviePy video composition
│   ├── database/
│   │   └── connection.py           # Async Motor MongoDB connection & indexes
│   ├── models/
│   │   └── schemas.py              # Pydantic schemas & MongoDB models
│   └── utils/
│       └── seed_data.py            # Initial admin seed script
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── layout/             # Sidebar, Header, AppLayout
    │   │   └── ui/                 # shadcn/ui components (Button, Card, Dialog, etc.)
    │   ├── pages/
    │   │   ├── auth/               # LoginPage (Login & Register tabs)
    │   │   ├── dashboard/          # DashboardPage (KPIs, Agent Units, Timeline)
    │   │   ├── campaigns/          # CampaignsPage & CampaignDetailPage
    │   │   ├── agents/             # AgentCommandCenterPage (Live execution queue)
    │   │   ├── research/           # ResearchPage (Meta Ads explorer & scores)
    │   │   ├── insights/           # InsightsPage (Categorized marketing intelligence)
    │   │   ├── scripts/            # ScriptStudioPage (3 Approaches & Storyboard editor)
    │   │   ├── videos/             # VideoProductionPage (Player & Rendering queue)
    │   │   ├── workflow/           # WorkflowPage (Hermes Kanban & React Flow diagram)
    │   │   ├── assets/             # AssetsPage (Media library & downloads)
    │   │   ├── settings/           # SettingsPage (Encrypted integrations & connection testing)
    │   │   └── logs/               # LogsPage (Telemetry stream)
    │   ├── lib/                    # API client, WebSocket manager, utilities
    │   ├── stores/                 # Zustand authStore and themeStore
    │   ├── types/                  # TypeScript interface definitions
    │   ├── App.tsx                 # Route configuration & React Query provider
    │   └── main.tsx                # React DOM mounting
    ├── tailwind.config.js          # Dark-first theme with brand colors
    ├── vite.config.ts              # Vite configuration with proxy
    └── package.json
```

---

## 4. Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and **pnpm**
- **MongoDB** running locally on port 27017 (or MongoDB Atlas connection string)

---

### Step 1: Backend Setup

```bash
# Navigate to the backend directory
cd backend

# (Optional) Verify live integrations & MongoDB Atlas connection
python utils/setup_and_verify.py

# Run the complete end-to-end pipeline smoke test
python utils/pipeline_smoke_test.py

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API Base: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/api/health`

---

### Step 2: Frontend Setup

```bash
# In a new terminal, navigate to the frontend directory
cd frontend

# Start the Vite development server
pnpm dev
```

- Web Application: `http://localhost:5173`

---

### Step 3: Login & Live Credentials Status

The platform is pre-connected to the live **MongoDB Atlas** cluster and the following integrations have been encrypted and verified live:
- **OpenRouter LLM:** `meta-llama/llama-3.1-70b-instruct` (Active & Verified)
- **NVIDIA NIM:** `nvidia/nemotron-3.5-bolt-e4b` (Active & Verified)
- **Apify:** Meta Ads Library Scraper (Active & Verified)
- **Tavily:** Search & Market Sentiment (Active & Verified)
- **Exa:** Neural Semantic Content Discovery (Active & Verified)

1. Open `http://localhost:5173` in your browser.
2. Sign in with the seeded credentials:
   - **Email:** `admin@crowdwisdom.ai`
   - **Password:** `admin1234`
3. Navigate through the 12 platform modules:
   - **Dashboard:** Platform KPIs, active agents, campaign throughput.
   - **Campaign Hub:** Manage campaigns, configure audiences, objectives, and compliance.
   - **Agent Command Center:** Live execution monitor and agent fleet telemetry.
   - **Ad Research & Insights:** Meta Ads explorer with AI scoring and marketing insights.
   - **Creative Intelligence & Briefs:** Checkpoint 1 strategic synthesis engine.
   - **Script & Storyboard Studio:** Checkpoint 2 scene-by-scene script editor.
   - **Video Production & Player:** Checkpoint 3 cinematic video player and MP4 rendering queue.
   - **Visual Hermes Workflow:** React Flow DAG & Kanban task board.
   - **Assets & Media Library:** Filtered catalog of rendered videos, scripts, and thumbnails.
   - **Settings & Integrations:** Fernet encrypted credential vault with one-click connection tests.
   - **Audit Logs:** Fine-grained event logs and system telemetry.

---

## 5. End-to-End Campaign Workflow

1. **Create Campaign:** Navigate to `/campaigns` and click **"Create Campaign"**. Set the objective, audience segments, target video duration (e.g. 45s), and aspect ratio (9:16).
2. **Launch Ads Research:** From the Campaign Hub or `/agents`, click **"Launch Ads Research"**. The Ads Manager Agent collects competitor ads via Apify, deduplicates them, and computes evaluation scores.
3. **Synthesize Creative Brief (Checkpoint 1):** The Creative Intelligence Engine automatically synthesizes research into a structured brief. Review and click **"Approve Brief"**.
4. **Draft Cinematic Script:** In `/scripts`, select an approach (*Pain-Point*, *Unique-Data*, or *Product-Value*) and click **"Generate Concept"**. The Script Agent creates a complete scene-by-scene storyboard.
5. **Approve Storyboard (Checkpoint 2):** Edit individual scene descriptions or narration if needed, then click **"Approve Storyboard"**.
6. **Produce Video Advertisement:** Navigate to `/videos`, select the approved script, and click **"Dispatch Video Agent"**.
7. **Preview & Download:** Monitor real-time rendering progress over WebSockets. Once finished, preview the MP4 video directly in the web player and download the commercial file.

---

## 6. Financial Advertising Compliance Guardrails

As required for CrowdWisdomTrading.com marketing materials, the platform strictly enforces compliance rules:
- No guaranteed profits or investment return claims.
- No fabricated testimonials or misleading urgency.
- Distinguishes observable ad activity from verified performance.
- Positions the platform accurately as an objective market sentiment and research validation tool.

---

## 7. License

Proprietary — Developed for CrowdWisdomTrading.com. All rights reserved.
#   C r o w d W i s d o m - A I - S t u d i o  
 