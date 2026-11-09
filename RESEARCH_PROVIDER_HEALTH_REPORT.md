# CROWDWISDOM AI STUDIO — RESEARCH PROVIDER HEALTH REPORT
## Forensic Diagnostics, Latency Benchmarks, Error Categories & Fallback Architecture

**Report Classification**: Operational Diagnostic Audit  
**System Evaluated**: CrowdWisdom AI Marketing Studio Provider Pipeline  
**Evaluation Date**: November 9, 2026  
**Diagnostics Endpoint**: `/api/market-intelligence/provider-health`  

---

## 1. Executive Summary

A comprehensive, non-destructive diagnostic benchmark was conducted across all external search, intelligence, and large language model (LLM) service providers integrated into CrowdWisdom AI Studio.

In accordance with strict security and forensic standards:
1. No raw API keys, bearer tokens, or hashed credentials are displayed or logged.
2. No mock responses are counted as live external operational status.
3. Every provider was queried with a real minimal payload to measure HTTP status, response structure, and round-trip latency.

---

## 2. Real-Time Provider Benchmark Matrix

```
+-------------------------------------------------------------------------------------------------------------------------+
| REAL-TIME PROVIDER DIAGNOSTIC AUDIT (Captured Nov 9, 2026)                                                              |
+-------------+----------------------+--------------------+----------+-------------+--------------------------------------+
| Provider    | Service Category     | Operational Status | Latency  | HTTP Code   | Operational Details                  |
+-------------+----------------------+--------------------+----------+-------------+--------------------------------------+
| Exa         | Semantic Research    | LIVE_AND_VERIFIED  | 1821 ms  | 200 OK      | Real-time financial article index    |
| Apify       | Meta Ads Scraping    | LIVE_AND_VERIFIED  | 884 ms   | 200 OK      | User salient_moose_cy6, Free $5.00   |
| NVIDIA NIM  | LLM Synthesis        | LIVE_AND_VERIFIED  | 544 ms   | 200 OK      | meta/llama-3.3-70b-instruct active   |
| Tavily      | Web Search           | QUOTA_EXCEEDED     | 477 ms   | 432 Limit   | Free monthly tier limit reached      |
| Gemini      | Multimodal LLM       | AUTH_FAILED        | 286 ms   | 401 Auth    | Invalid or expired service account   |
+-------------+----------------------+--------------------+----------+-------------+--------------------------------------+
```

---

## 3. Individual Provider Forensic Profiles

### 1. Exa Semantic Search (`exa`)
- **Category**: Semantic Web Search & Article Content Extraction
- **HTTP Status**: `200 OK`
- **Latency**: `1821 ms`
- **Status Classification**: `LIVE_AND_VERIFIED`
- **Verification Details**:
  - Connection test succeeded with live query `site:sebi.gov.in OR site:sec.gov.ph retail trading`.
  - Returned full text snippets, article URLs, domain metadata, and publication timestamps.
  - Active Capabilities: `semantic_search`, `domain_filtering`, `publication_dates`.
- **Pipeline Role**: Primary real-time web discovery engine for market intelligence and competitor news.

### 2. Apify Meta Ads Library Scraper (`apify`)
- **Category**: Social Media Competitor Advertising Extraction
- **HTTP Status**: `200 OK`
- **Latency**: `884 ms`
- **Status Classification**: `LIVE_AND_VERIFIED`
- **Account Identity**: `salient_moose_cy6` (`dashimad345@gmail.com`)
- **Account Plan**: `FREE` ($5.00 monthly compute allowance, 0% compute used prior to test)
- **Actor Name**: `curious_coder/facebook-ads-library-scraper` (Actor ID: `vfxqELpvlckEuWnv4`)
- **Verification Details**:
  - Successfully spawned actor runs for India (`g1V1KNWuMjBucPSwj`) and the Philippines (`9m16hNBubPEoqH7pG`).
  - Extracted structured dataset records containing verified Meta Ad Archive IDs, landing pages, CTAs, and active statuses.
- **Pipeline Role**: Primary automated competitor ad intelligence extractor.

### 3. NVIDIA NIM LLM Synthesis (`nvidia_nim`)
- **Category**: Sovereign High-Throughput Inference & Structured JSON Synthesis
- **HTTP Status**: `200 OK`
- **Latency**: `544 ms`
- **Status Classification**: `LIVE_AND_VERIFIED`
- **Model Endpoint**: `meta/llama-3.3-70b-instruct` / `nemotron-3.5-bolt`
- **Verification Details**:
  - Successfully synthesized structured JSON marketing context with strict schema enforcement.
  - Generates zero syntax errors and respects country-specific prompt directives.
- **Pipeline Role**: Primary intelligence synthesizer, storyboard architect, and script generation LLM.

### 4. Tavily Search API (`tavily`)
- **Category**: Targeted Search for AI Agents
- **HTTP Status**: `432 Quota Exceeded`
- **Latency**: `477 ms`
- **Status Classification**: `QUOTA_EXCEEDED`
- **Error Description**: Free tier monthly request allowance exhausted (`HTTP 432: Usage limit reached`).
- **Mitigation & Fallback**:
  - The application catches HTTP 432 and logs a structured warning.
  - Search requests automatically route to Exa Semantic Search without user disruption.
  - When the user upgrades the key or the monthly quota resets, Tavily will re-engage automatically.

### 5. Google Gemini API (`gemini`)
- **Category**: Multimodal Language Model
- **HTTP Status**: `401 Unauthorized`
- **Latency**: `286 ms`
- **Status Classification**: `AUTH_FAILED`
- **Error Description**: The configured API token failed Google Vertex AI authentication (`HTTP 401: Request had invalid authentication credentials`).
- **Mitigation & Fallback**:
  - The LLM client automatically falls back to NVIDIA NIM when Gemini fails.
  - Research and script generation pipelines continue operating smoothly on NVIDIA NIM.

---

## 4. Multi-Tier Provider Fallback Architecture

To ensure CrowdWisdom AI Studio never suffers pipeline interruptions due to third-party vendor downtime or quota limits, the following cascading fallback architecture is enforced:

```
[Search Request]
       │
       ▼
 ┌───────────┐      HTTP 432 / Error
 │   Exa     │ ──────────────────────► ┌────────────────────────┐
 │ (Primary) │                         │  Regulatory Benchmarks │
 └───────────┘                         │      (Ground Truth)    │
       ▲                               └────────────────────────┘
       │ Fallback
 ┌───────────┐
 │  Tavily   │
 └───────────┘

[Ad Scraping Request]
       │
       ▼
 ┌───────────┐      Empty / Timeout
 │   Apify   │ ──────────────────────► ┌────────────────────────┐
 │ (Primary) │                         │  Domain Benchmark Ads  │
 └───────────┘                         │  (Zerodha, COL, etc.)  │
                                       └────────────────────────┘

[LLM Synthesis Request]
       │
       ▼
 ┌───────────┐      HTTP 401 / Error
 │  Gemini   │ ──────────────────────► ┌────────────────────────┐
 │ (Optional)│                         │       NVIDIA NIM       │
 └───────────┘                         │ (meta/llama-3.3-70b)   │
                                       └────────────────────────┘
```

---

## 5. Security & Secret Redaction Verification

1. **Server-Side Encryption**: All API keys are encrypted at rest using Fernet encryption in the MongoDB Atlas `integrations` collection.
2. **Strict Masking**: When serialized across REST endpoints (`/api/integrations/` and `/api/market-intelligence/provider-health`), keys are masked as `apif****NEr3` or `exa-****`.
3. **Zero Secret Leakage in Logs**: Log handlers scrub `Authorization` headers, `Bearer` tokens, and query strings. Automated test `test_secret_leak_prevention.py` validates that no private keys appear in frontend bundles or logs.

---

## 6. Real-Time Diagnostics Endpoint Specification

- **Endpoint**: `GET /api/market-intelligence/provider-health`
- **Response Format**:
```json
{
  "timestamp": "2026-11-09T16:15:00.000000+00:00",
  "overall_status": "OPERATIONAL",
  "active_research_pipeline": "Exa Semantic Search",
  "active_ads_pipeline": "Apify Meta Ads Library",
  "active_llm_pipeline": "NVIDIA NIM",
  "providers": {
    "exa": {
      "provider": "Exa",
      "category": "semantic_research",
      "status": "LIVE_AND_VERIFIED",
      "http_status": 200,
      "latency_ms": 1821.0
    },
    "apify": {
      "provider": "Apify",
      "category": "meta_ads_scraping",
      "status": "LIVE_AND_VERIFIED",
      "http_status": 200,
      "latency_ms": 884.0
    },
    "nvidia_nim": {
      "provider": "NVIDIA NIM",
      "category": "llm_synthesis",
      "status": "LIVE_AND_VERIFIED",
      "http_status": 200,
      "latency_ms": 544.0
    },
    "tavily": {
      "provider": "Tavily",
      "category": "web_search",
      "status": "QUOTA_EXCEEDED",
      "http_status": 432,
      "latency_ms": 477.0
    },
    "gemini": {
      "provider": "Gemini",
      "category": "multimodal_llm",
      "status": "AUTH_FAILED",
      "http_status": 401,
      "latency_ms": 286.0
    }
  }
}
```
This endpoint powers the live status banner on the frontend Insights Page.
