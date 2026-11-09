# CrowdWisdom AI Studio — Interactive Demonstration Guide

This guide provides a structured, 9-step demonstration sequence to evaluate the platform in either the live production environment or a local development instance.

- **Live Production URL**: [https://crowdwisdom-ai-studio-ads.onrender.com](https://crowdwisdom-ai-studio-ads.onrender.com/)
- **Local Development URL**: `http://localhost:5173`

---

## Step 1: Platform Login

1. Navigate to the login page (`/login`).
2. Notice the modern editorial authentication interface featuring live platform telemetry metrics and feature storytelling.
3. Use the pre-seeded administrative credentials:
   - **Email**: `admin@crowdwisdom.ai`
   - **Password**: `admin1234`
4. Click **"Access Command Center"**.

---

## Step 2: Dashboard & Fleet Overview

1. Arrive at the **Platform Dashboard** (`/`).
2. Review real-time KPIs:
   - *Total Campaigns*
   - *Researched Competitor Ads*
   - *Active Agent Units*
   - *Rendered Video Commercials*
3. View the **Agent Fleet Status** cards (*Ads Manager*, *Script Studio*, *Video Production*, *Creative Intelligence Engine*).

---

## Step 3: Campaign Hub & Creation

1. Navigate to **Campaigns** (`/campaigns`).
2. Click **"+ Create Campaign"**:
   - **Title**: `Options Volatility & Retail Trap Campaign`
   - **Target Audience**: `Retail Options & Momentum Traders`
   - **Target Duration**: `60 seconds`
   - **Aspect Ratio**: `9:16 Vertical (1080x1920)`
3. Click **"Create Campaign"** and enter the newly created campaign detail view (`/campaigns/:id`).

---

## Step 4: Ad Research & Competitor Intelligence

1. From the Campaign detail view or **Ad Intelligence** tab, review the scraped competitor ads from the Meta Ads Library.
2. Note the date verification badges:
   - Ads strictly within the last 30 days display green `VERIFIED (30D WINDOW)` tags.
   - Click any ad card to inspect the direct link to the live Meta Ads Library listing.
3. Review the AI creative scores:
   - *Hook Strength (0–10)*
   - *Emotional Appeal (0–10)*
   - *Clarity & Compliance Rationale*
4. Click **"Export Research JSON"** to download the structured ad intelligence export.

---

## Step 5: Creative Brief Synthesis (Checkpoint 1)

1. Open the **Creative Brief** tab.
2. The Creative Intelligence Engine synthesizes research into:
   - *Target Persona Profile*
   - *Primary Value Proposition*
   - *Competitor Angles to Avoid*
   - *Compliance Guardrails* (No guaranteed returns, no fake urgency)
3. Click **"Approve Brief"** to unlock the Script & Storyboard Studio.

---

## Step 6: Multi-Angle Script Studio (Checkpoint 2)

1. Open the **Scripts & Storyboards** tab.
2. Notice the three strategic generation approaches:
   - **Pain-Point**: Focuses on emotional losses from following social media influencer hype.
   - **Unique-Data**: Focuses on CrowdWisdom's order-book telemetry and sentiment divergence.
   - **Product-Value**: Demonstrates the 60-second morning routine and crowd clarity.
3. Review the generated 4-scene storyboard:
   - **Visual Hook**: Visceral 3–5-second opening scene.
   - **Scene 1**: Cinematic human cinematography.
   - **Scene 2**: Procedurally generated candlestick breakout chart.
   - **Scene 3**: Product interface plate showcasing CrowdMap.
   - **Scene 4**: Call-to-action scene directing viewers to `CrowdWisdomTrading.com`.
4. Click **"Export Script JSON"** to download the human-readable script payload.
5. Click **"Approve Storyboard"** to authorize video production.

---

## Step 7: Hermes Workflow & Task Kanban

1. Navigate to **Workflow & Tasks** (`/workflow`).
2. Switch to the **Task Kanban Board** view:
   - Observe the 5 pipeline columns: *Backlog*, *Todo*, *In Progress*, *In Review*, *Done*.
   - View task priorities and agent assignments.
3. Switch to the **Interactive Node Workflow** tab:
   - Interact with the live React Flow Directed Acyclic Graph (DAG) visualizing agent dependencies.

---

## Step 8: Video Production & Rendering Queue

1. Navigate to **Rendered Videos** (`/videos` or inside Campaign detail).
2. Click **"Dispatch Video Agent"** on the approved storyboard.
3. Observe the live WebSocket progress bar:
   - *Validating scene visual assets*
   - *Synthesizing Edge-TTS neural voiceover*
   - *Compositing 120 BPM fintech soundtrack & audio ducking*
   - *Executing MoviePy transitions & text overlays*
   - *Running FFprobe post-render validation gate*

---

## Step 9: Final Commercial Playback & Download

1. Once the render is complete, the HTML5 video player displays the broadcast-ready commercial.
2. Hit **Play**:
   - Listen to the high-fidelity neural voiceover with automated music ducking.
   - Observe the frame transitions (directional whip-pans and smooth zooms).
   - Verify the crisp 1080x1920 9:16 vertical orientation.
   - Test seeking forward and backward (supported via HTTP 206 Partial Content range requests).
3. Click **"Download MP4 Commercial"** to download the completed commercial file directly to your workstation.
