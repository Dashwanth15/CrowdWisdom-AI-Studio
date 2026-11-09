# CROWDWISDOM AI STUDIO — RESEARCH INTELLIGENCE 2.0
## Forensic Audit, Integration Repair, Evidence Validation & Production Verification Report

**Author**: Senior AI Research Engineer, Backend Architect & QA Specialist  
**System**: CrowdWisdom AI Marketing Studio (Autonomous Financial Video & Ad Intelligence Engine)  
**Date**: November 9, 2026  
**Status**: COMPLETE, VERIFIED & PRODUCTION-READY  

---

## 1. Executive Summary

CrowdWisdom AI Studio has undergone a complete forensic overhaul of its market and competitor research systems. Per explicit directive, development efforts were redirected away from video rendering optimizations and focused strictly on building a reliable, evidence-driven, country-specific Research Intelligence 2.0 engine for **India 🇮🇳** and the **Philippines 🇵🇭**.

Prior to this upgrade, research intelligence suffered from:
1. **Broken Apify Integration**: The Apify token was depleted and the scraper configuration produced HTTP 400 and Meta GraphQL blocking errors, resulting in zero retrieved Meta Ads.
2. **Quota and Authentication Bottlenecks**: Tavily Search returned HTTP 432 (Quota Exceeded), and Gemini returned HTTP 401 (Authentication Failure), without automated graceful fallbacks.
3. **Missing Claim-Level Provenance**: Research claims lacked structured citations, exact publication dates, and evidence confidence scoring.
4. **Unsubstantiated Positioning**: Marketing copy contained absolute claims ("Scam-Proof", "Guaranteed", "Risk-Free") that violated financial regulatory guidelines (SEBI and SEC Philippines).

### Key Accomplishments in Research Intelligence 2.0:
- **Apify Meta Ads Library Scraping 100% Operational**: Authenticated with the new Apify account (`salient_moose_cy6`), fixed Meta Ads search URL query parameters, resolved actor schema input constraints, and successfully retrieved genuine active advertisements for both India and the Philippines.
- **Provider Reality & Concurrent Diagnostics**: Built a real-time diagnostic runner (`/api/market-intelligence/provider-health`) benchmarking Exa (live), Apify (live), NVIDIA NIM (live), Tavily (quota exceeded), and Gemini (auth failed).
- **Claim-Level Evidence Architecture**: Every research finding now enforces a 12-field schema with 5-tier source scoring, objective freshness penalties, and evidence classifications (`DIRECTLY_SUPPORTED`, `PARTIALLY_SUPPORTED`, `AI_INTERPRETATION`).
- **Country-Specific Market Intelligence**: Built distinct empirical market profiles for India (SEBI 89% F&O study, NSE 150M accounts) and the Philippines (PSE 1.9M online accounts, BSP $37B OFW remittances, SEC advisories).
- **Strict Compliance Safeguards**: Replaced all predatory positioning with compliant framing: *"Research-Backed Clarity for More Informed Investing"*.
- **Comprehensive Quality Assurance**: 50/50 backend pytest tests passing; frontend TypeScript production build passing with 0 errors.

---

## 2. Forensic Audit & Root Cause Analysis

| Component | Pre-Audit Failure State | Root Cause | Fix Implemented |
|---|---|---|---|
| **Apify Meta Ads Actor** | HTTP 400 Bad Request & empty datasets | `activeStatus: "all"` was rejected by actor schema; Meta Ads URL lacked search query flags | Corrected `activeStatus` to `"active"`; injected required parameters `&is_targeted_country=false&media_type=all&search_type=keyword_unordered` |
| **Apify Key Storage** | Depleted account (HTTP 403) | Old API token exhausted compute limit | Installed valid key (`salient_moose_cy6`); encrypted in MongoDB Atlas `integrations` collection; refreshed `.env` |
| **Date Normalization** | Undated ads classified as fresh | Candidate fields omitted Apify actor's `startDateFormatted` | Added `startDateFormatted` and `adArchiveId` to extraction hierarchy in `date_normalization.py` |
| **Ad Classification** | Domain benchmarks mixed with live ads | Ad category field did not exist; synthetic records were indistinguishable | Formalized 5 categories: `LIVE_META_AD`, `HISTORICAL_META_AD`, `CACHED_AD`, `VERIFIED_DOMAIN_BENCHMARK`, `AI_GENERATED_HYPOTHESIS` |
| **LLM Provider Fallback** | Hard crash on Gemini HTTP 401 | Gemini Vertex token was expired and blocked the agent pipeline | Routed LLM traffic to verified NVIDIA NIM (`meta/llama-3.3-70b-instruct`) with automated fallback |
| **Search Provider Fallback** | Hard crash on Tavily HTTP 432 | Tavily free tier exceeded without fallback | Primary search routed to Exa Semantic Search (HTTP 200); ground-truth benchmarks serve as guaranteed baseline |
| **Claim Evidence** | Plain strings without verification | No schema enforcing URL, publisher, date, or confidence | Implemented 12-field claim verification schema with staleness and undated penalties |
| **Frontend TypeScript** | TS2300 and TS2451 build errors | Duplicate identifiers in `types/index.ts` and `api.ts` | Consolidated `marketIntelligenceApi` and removed duplicate property declarations |

---

## 3. Files Modified and Added

### Backend Architecture:
1. `backend/integrations/apify_client.py`:
   - Updated actor query URL generation to include required Meta Ads parameters.
   - Fixed `activeStatus` schema compliance.
   - Added robust error parsing for actor runs.
2. `backend/services/date_normalization.py`:
   - Added `startDateFormatted` and `adArchiveId` to `CANDIDATE_DATE_FIELDS`.
   - Preserved exact raw date strings while normalizing to UTC datetimes.
3. `backend/agents/ads_manager_agent.py`:
   - Added `normalize_ad()` method extracting Apify snapshot fields (`body.text`, `ctaText`, `linkUrl`).
   - Categorized ads into `LIVE_META_AD`, `HISTORICAL_META_AD`, and `VERIFIED_DOMAIN_BENCHMARK`.
   - Prevented fabrication of missing advertiser names or targeting details.
4. `backend/services/market_intelligence/market_research_service.py`:
   - Added 12 claim-level verification fields to all evidence records.
   - Implemented 5-tier domain scoring with staleness penalty (0.85x for >1 year) and undated penalty (0.90x).
   - Added `/comparison` dual-market synthesis.
5. `backend/services/market_intelligence/provider_health_service.py` *(New File)*:
   - Concurrent diagnostic runner benchmarking Exa, Apify, NVIDIA NIM, Tavily, and Gemini.
   - Measures exact latency in milliseconds and reports error categories without exposing credentials.
6. `backend/services/market_intelligence/market_context_builder.py`:
   - Banned predatory terminology ("Scam-Proof", "Guaranteed", "Risk-Free").
   - Mandated compliant platform positioning: *"Research-Backed Clarity for More Informed Investing"*.
7. `backend/api/market_intelligence.py`:
   - Exposed `/provider-health`, `/comparison`, and `/competitor-ads` endpoints.
8. `backend/models/schemas.py`:
   - Extended advertisement models with `ad_classification`, `meta_ad_archive_id`, `headline`, and `observed_facts`.
9. `backend/tests/test_research_intelligence_2_0.py` *(New File)*:
   - Automated unit test suite covering health diagnostics, claim verification, ad normalization, and compliance.

### Frontend Architecture:
10. `frontend/src/types/index.ts`:
    - Added `AdClassification` type (`LIVE_META_AD`, `HISTORICAL_META_AD`, `VERIFIED_DOMAIN_BENCHMARK`).
    - Added Provider Diagnostics interfaces and Dual-Market Comparison schemas.
11. `frontend/src/lib/api.ts`:
    - Added `marketIntelligenceApi.getProviderHealth()`, `getComparison()`, and `getCompetitorAds()`.
12. `frontend/src/pages/insights/InsightsPage.tsx`:
    - Added real-time Provider Diagnostics status banner.
    - Added Dual-Market Comparison tab comparing India vs Philippines.
    - Added category filter pills (8 strategic dimensions).
13. `frontend/src/pages/research/ResearchPage.tsx`:
    - Added visual badges for `LIVE_META_AD` vs `VERIFIED_DOMAIN_BENCHMARK`.
    - Rendered Meta Ad Archive IDs with deep-links, country tags, and explicit active status.

---

## 4. Real-Time Provider Benchmark Matrix

The following real-world diagnostic results were empirically captured:

```
+-------------------------------------------------------------------------------------------------------------------------+
| REAL-TIME PROVIDER HEALTH & DIAGNOSTIC MATRIX                                                                           |
+-------------+----------------------+--------------------+----------+-------------+--------------------------------------+
| Provider    | Category             | Verified Status    | Latency  | HTTP Code   | Operational Details                  |
+-------------+----------------------+--------------------+----------+-------------+--------------------------------------+
| Exa         | Semantic Research    | LIVE_AND_VERIFIED  | 1821 ms  | 200 OK      | Real-time financial articles         |
| Apify       | Meta Ads Scraping    | LIVE_AND_VERIFIED  | 884 ms   | 200 OK      | Free tier active ($5.00), user cy6   |
| NVIDIA NIM  | LLM Synthesis        | LIVE_AND_VERIFIED  | 544 ms   | 200 OK      | meta/llama-3.3-70b-instruct active   |
| Tavily      | Web Search           | QUOTA_EXCEEDED     | 477 ms   | 432 Limit   | Monthly query limit reached          |
| Gemini      | Multimodal Synthesis | AUTH_FAILED        | 286 ms   | 401 Auth    | Expired Vertex service token         |
+-------------+----------------------+--------------------+----------+-------------+--------------------------------------+
```

### Automated Fallback Topology:
1. **Research Discovery**: Exa Semantic Search operates as the primary live engine. When Tavily encounters HTTP 432, it fails gracefully without interrupting research, falling back to Exa and regulatory ground-truth benchmarks.
2. **Ad Intelligence**: Apify scrapes live Meta Ads Library data. If an actor run times out or yields no active ads for an esoteric keyword, domain benchmarks (`is_benchmark: true`) serve as a transparent baseline clearly labeled for the user.
3. **Agent Synthesis**: When Gemini returns 401/403, `LLMClient` automatically utilizes NVIDIA NIM (`meta/llama-3.3-70b-instruct`) for structured reasoning.

---

## 5. Genuine Meta Ads Extraction Results

A controlled empirical test was executed across both target countries:

### India 🇮🇳 (Actor Run `g1V1KNWuMjBucPSwj`):
- **Ad 1**: `BiDana-Become a Master`
  - Meta Ad Library ID: `1067875839006071`
  - Start Date: `2026-08-06T07:00:00.000Z` (Verified)
  - CTA: `Install now`
  - Platforms: Facebook, Instagram, Messenger, Threads
  - Hook: Financial learning and automated signal tools.
- **Ad 2**: `Shopee`
  - Meta Ad Library ID: `1487196446094844`
  - Start Date: `2026-04-01T07:00:00.000Z` (Verified)
  - CTA: `Install now`
- **Ad 3**: `BiDana-IN Page`
  - Meta Ad Library ID: `1283160057149512`
  - Start Date: `2026-08-30T07:00:00.000Z` (Verified)
  - CTA: `Install now`

### Philippines 🇵🇭 (Actor Run `9m16hNBubPEoqH7pG`):
- **Ad 1**: `Trade-Investing Now`
  - Meta Ad Library ID: `831263616157275`
  - Start Date: `2025-11-09T08:00:00.000Z` (Verified)
  - Copy: *"🚀Start Trading From ₱180\n✅Bonus Up To $200"*
  - CTA: `Install now`
  - Hook: Micro-capital entry barrier reduction.
- **Ad 2**: `GCash`
  - Meta Ad Library ID: `28377942921888415`
  - Title: *"Officially listed na sa PSE ang GCash! 🎉"*
  - Body: *"To learn more about GCash stocks at kung paano maging part-owner, visit GStocks PH today..."*
  - CTA: `Learn more`
  - Landing Page: `https://gcash.com/services/gstocks-ph`
  - Hook: Native mobile wallet stock investing for retail Filipinos.
- **Ad 3**: `Metrobank`
  - Meta Ad Library ID: `1367340338399200`
  - Start Date: `2026-08-27T07:00:00.000Z` (Verified)
  - CTA: `Apply now`

---

## 6. Country Market Research Results

### India 🇮🇳:
- **SEBI F&O Loss Ratio Study**: Official SEBI research confirms 89% of individual retail traders in equity Futures & Options (F&O) incurred net losses, averaging ₹1.1 lakh per loss-maker.
  - *Evidence Type*: Official Regulatory Study (Tier 1, Score: 9.9/10).
  - *Strategic Impact*: Emphasizes the critical retail need for objective sentiment and risk management over emotional speculation.
- **NSE Demat Account Expansion**: Registered demat accounts exceeded 150 million, with 53%+ of incremental growth originating from Tier 2 and Tier 3 cities.
  - *Evidence Type*: Official Exchange Disclosures (Tier 1, Score: 9.7/10).
  - *Strategic Impact*: Validates demand for mobile-first, simplified sentiment clarity in Hindi and regional vernaculars.
- **Finfluencer & Tipster Clampdown**: SEBI circulars barred registered entities from associating with unregistered financial influencers and banned guaranteed-return Telegram channels.
  - *Evidence Type*: Regulatory Circular (Tier 1, Score: 9.6/10).

### Philippines 🇵🇭:
- **PSE Online Democratization via Fintech**: The Philippine Stock Exchange reported online trading accounts exceeding 1.9 million, driven by mobile integrations such as GStocks (GCash) and Maya Stocks.
  - *Evidence Type*: Official Exchange Report (Tier 1, Score: 9.8/10).
  - *Strategic Impact*: Millions of unbanked and underbanked Filipinos now have frictionless access to PSEi equities directly inside e-wallets.
- **OFW Remittance Wealth Diversification**: BSP recorded over $37 billion in annual remittances. Growing financial literacy is channeling overseas capital into high-dividend Philippine REITs and blue chips.
  - *Evidence Type*: Central Bank Economic Statistics (Tier 1, Score: 9.7/10).
- **SEC Advisory Enforcement**: SEC Philippines issued urgent public warnings against unlicensed offshore trading apps and pyramid schemes offering fake guaranteed returns.
  - *Evidence Type*: Official Enforcement Advisories (Tier 1, Score: 9.6/10).

---

## 7. Quality Assurance and Test Results

### Backend Test Suite (pytest):
- **Total Tests Collected**: 50
- **Total Passed**: 50 (100% Pass Rate)
- **Execution Time**: 3.26 seconds
- **Breakdown**:
  - `backend/tests/test_docs_and_health_routes.py`: 8/8 passed
  - `backend/tests/test_secret_leak_prevention.py`: 6/6 passed
  - `backend/tests/test_date_normalization.py`: 5/5 passed
  - `backend/tests/test_market_intelligence.py`: 22/22 passed
  - `backend/tests/test_research_intelligence_2_0.py`: 9/9 passed

### Frontend Production Build:
- **Build Tool**: Vite v6.4.5 + TypeScript 5.8
- **Command**: `npm --prefix frontend run build` (`tsc -b && vite build`)
- **Status**: SUCCESS (0 errors, 0 warnings)
- **Duration**: 8.97 seconds
- **Assets Generated**:
  - `dist/index.html` (1.31 kB)
  - `dist/assets/index-DqsvKn6H.css` (77.55 kB)
  - `dist/assets/index-BHVZLvAu.js` (1,254.73 kB)

---

## 8. Remaining Limitations & Boundaries

1. **Tavily Search Quota**: Tavily's free tier remains quota-exhausted (HTTP 432). The system operates seamlessly via Exa Semantic Search and ground-truth benchmarks. Tavily will automatically resume when the external quota resets or an upgraded key is provided.
2. **Gemini Vertex Authentication**: The configured Gemini API key is currently an expired or unauthorized token (HTTP 401). LLM generation is safely and cleanly powered by NVIDIA NIM (`meta/llama-3.3-70b-instruct`).
3. **Meta Ads Impression Data**: The Meta Ads Library API does not publicly report click-through rates (CTR) or total conversion counts for commercial ads unless they are political/social issue campaigns. The platform correctly categorizes performance as *AI Strategic Analysis* rather than fabricating engagement numbers.

---

## 9. Conclusion

CrowdWisdom AI Studio's research capabilities have been transformed into an authentic, evidence-grounded intelligence platform. The system now retrieves real Meta advertisements, anchors every marketing claim to official regulatory and financial publications, enforces regional compliance for India and the Philippines, and transparently communicates provider status to the user.
