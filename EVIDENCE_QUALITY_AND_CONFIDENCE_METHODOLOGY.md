# CROWDWISDOM AI STUDIO — EVIDENCE QUALITY & CONFIDENCE METHODOLOGY
## Mathematical Scoring, 5-Tier Source Hierarchy, Freshness Penalties & Claim Verification Schema

**Document Class**: Data Engineering & Intelligence Verification Specification  
**System Module**: `backend/services/market_intelligence/market_research_service.py`  
**Version**: 2.0  
**Date**: November 9, 2026  

---

## 1. Overview & Core Philosophy

Research Intelligence 2.0 replaces superficial, unverified AI assertions with an empirical provenance pipeline. Under this methodology:
1. **No assertion is accepted as fact** without a verified publisher and source URL.
2. Domain authority is balanced against publication freshness and independent corroboration.
3. Every claim is strictly classified into one of five evidence classifications (`DIRECTLY_SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTRADICTED`, `AI_INTERPRETATION`, `UNVERIFIED`).

---

## 2. Five-Tier Source Quality Hierarchy

All external domains and publishers are mapped into a standardized 5-tier credibility hierarchy:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Official Regulators & Central Exchanges (9.5 - 10.0) │
│ SEBI, SEC PH, NSE, BSE, PSE, BSP, RBI, Official Disclosures │
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Institutional Financial Media (8.5 - 9.4)            │
│ Livemint, Economic Times, BusinessWorld, PhilStar, Reuters  │
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Industry Portals & Broker Platforms (7.0 - 8.4)     │
│ Zerodha, COL Financial, Angel One, Moneycontrol, Investagrams│
├─────────────────────────────────────────────────────────────┤
│ Tier 4: Professional Discussions & Communities (5.0 - 6.9)   │
│ TradingView, Reddit (r/IndiaInvestments), LinkedIn, Quora   │
├─────────────────────────────────────────────────────────────┤
│ Tier 5: General & Unverified Web Sources (3.0 - 4.9)         │
│ Unvetted blogs, promotional aggregators, unknown forums     │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Tier Scoring Matrix:

| Tier | Tier Name | Base Score | Confidence Rating | Evidence Classification | Representative Domains |
|---|---|---|---|---|---|
| **Tier 1** | Official Regulators & Central Exchanges | 9.8 / 10 | `verified` | `official_regulatory_data` | `sebi.gov.in`, `sec.gov.ph`, `nseindia.com`, `bseindia.com`, `pse.com.ph`, `bsp.gov.ph`, `rbi.org.in` |
| **Tier 2** | Institutional Financial Media | 8.8 / 10 | `high` | `financial_journalism` | `livemint.com`, `thehindubusinessline.com`, `bworldonline.com`, `philstar.com`, `reuters.com`, `bloomberg.com`, `economictimes.indiatimes.com` |
| **Tier 3** | Industry Portals & Broker Platforms | 7.5 / 10 | `moderate` | `industry_analysis` | `zerodha.com`, `colfinancial.com`, `angelone.in`, `moneycontrol.com`, `investagrams.com`, `groww.in`, `firstmetrosec.com.ph` |
| **Tier 4** | Professional Discussions & Communities | 5.8 / 10 | `low` | `community_sentiment` | `tradingview.com`, `reddit.com`, `quora.com`, `linkedin.com` |
| **Tier 5** | General & Unverified Web Sources | 4.2 / 10 | `low` | `unverified_web` | Other unvetted web domains |

---

## 3. Freshness & Staleness Mathematical Formula

Market data and investor trends decay over time. To prevent obsolete statistics from masquerading as current market truths, the engine applies an automated date-decay penalty.

### Formula:
$$\text{Final Score} = \text{round}(\text{Base Score} \times \text{Staleness Penalty}, 2)$$

Where the Staleness Penalty is defined piecewise by age relative to evaluation date:

$$\text{Staleness Penalty} = 
\begin{cases} 
1.00 & \text{if } \text{Age} \le 180 \text{ days (Fresh)} \\
0.93 & \text{if } 180 < \text{Age} \le 365 \text{ days (Moderate Age)} \\
0.85 & \text{if } \text{Age} > 365 \text{ days (Aged Over 1 Year)} \\
0.90 & \text{if Date is Missing / Unverified (Undated Penalty)}
\end{cases}$$

*(Note: Regulatory benchmark ground-truth reports from SEBI/PSE maintain their full base score as historical empirical baselines).*

---

## 4. Twelve Claim-Level Verification Fields

Every research claim produced or displayed by CrowdWisdom AI Studio must fulfill the following 12 mandatory fields:

1. `claim_text`: The specific empirical finding or market claim.
2. `source_url`: Full canonical destination URL of the source article or report.
3. `publisher`: Publishing entity or institutional author.
4. `article_title`: Exact published title or headline of the referenced source.
5. `publication_date`: Verified publication date in ISO 8601 (`YYYY-MM-DD`).
6. `retrieval_timestamp`: Exact UTC datetime when the crawler extracted the record.
7. `target_country`: Target nation code (`IN` or `PH`).
8. `source_tier`: Numeric tier between 1 and 5.
9. `supporting_excerpt`: Verbatim text snippet from the source supporting the claim.
10. `evidence_classification`: Explicit status classification (see Section 5).
11. `confidence_score`: Computed score between 0.0 and 10.0.
12. `verification_status`: String flag (`verified` or `unverified`).

---

## 5. Five Evidence Classifications

| Classification | Definition | Application Standard |
|---|---|---|
| `DIRECTLY_SUPPORTED` | The claim is supported word-for-word or by exact numerical data in a Tier 1 or Tier 2 source with a verified date. | Regulatory statistics (e.g. SEBI 89% loss figure, PSE 1.9M accounts). |
| `PARTIALLY_SUPPORTED` | The finding is supported by general reporting or secondary discussion in Tier 3 or Tier 4 sources, but lacks official regulator corroboration. | General market sentiment observations, emerging broker market share discussions. |
| `CONTRADICTED` | The claim is refuted by higher-tier empirical evidence. | Claims that "retail traders consistently beat the market" or "forex bots guarantee 10% weekly". |
| `AI_INTERPRETATION` | Strategic deductions, persona hypotheses, or creative angles generated by the LLM based on evidence. | Target audience pain points, storyboard hooks, recommended messaging tone. |
| `UNVERIFIED` | Third-party claim lacking a verified source URL or credible publication date. | Unattributed social media claims or forum rumors. |

---

## 6. Cross-Source Corroboration & Deduplication Rules

1. **Canonical URL Deduplication**: URLs are normalized (stripping tracking parameters like `utm_source`, `fbclid`, and trailing slashes) to prevent duplicate articles from inflating confidence.
2. **Syndication Independence**: Multiple news aggregators reprinting the exact same wire report (e.g., identical PTI or Reuters wire syndicated across 5 portals) are treated as **a single primary source**, not 5 independent confirmations.
3. **Audience Persona Hypotheses**: Customer personas (e.g., `in_young_tech_investor` or `ph_ofw_wealth_builder`) are formally cataloged as *hypotheses* until substantiated by empirical demographic or trading account data.
