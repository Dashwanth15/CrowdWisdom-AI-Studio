# CROWDWISDOM AI STUDIO — RESEARCH TEST RESULTS REPORT
## Complete Quality Assurance, Automated Unit & Integration Suite & Frontend Verification

**QA Engineer**: Senior QA & Backend Systems Engineer  
**Execution Environment**: Windows 11 / Python 3.14.6 / Node.js v20.x  
**Test Framework**: pytest 8.4.2 (asyncio, mock, cov plugins) + Vite 6.4.5 TypeScript Compiler  
**Test Suite Status**: 100% PASSED (50/50 tests passing)  
**Date**: November 9, 2026  

---

## 1. Executive Summary

A comprehensive quality assurance validation was executed across both the backend FastAPI service and the React 18 TypeScript frontend to ensure that all Research Intelligence 2.0 components function with 100% reliability, zero test regressions, and zero secret exposure.

---

## 2. Backend Automated Test Suite Execution

### Command Executed:
```powershell
pytest -o pythonpath=backend \
  backend/tests/test_docs_and_health_routes.py \
  backend/tests/test_secret_leak_prevention.py \
  backend/tests/test_date_normalization.py \
  backend/tests/test_market_intelligence.py \
  backend/tests/test_research_intelligence_2_0.py \
  -v
```

### Result:
- **Total Tests Collected**: 50
- **Total Tests Passed**: 50
- **Total Tests Failed**: 0
- **Pass Rate**: 100%
- **Execution Time**: 3.26 seconds

---

## 3. Detailed Test Module Breakdown

### Module 1: `backend/tests/test_docs_and_health_routes.py` (8 Tests — 100% Passed)
- `test_root_endpoint`: Verifies API root status response. [PASSED]
- `test_docs_endpoint`: Verifies Swagger UI route. [PASSED]
- `test_openapi_endpoint`: Verifies OpenAPI schema generation. [PASSED]
- `test_redoc_endpoint`: Verifies ReDoc documentation endpoint. [PASSED]
- `test_api_docs_redirect`: Verifies `/api/docs` redirects to `/docs`. [PASSED]
- `test_api_openapi_redirect`: Verifies `/api/openapi.json` redirect. [PASSED]
- `test_api_redoc_redirect`: Verifies `/api/redoc` redirect. [PASSED]
- `test_health_endpoints`: Verifies both `/health` and `/api/health` respond with 200 OK. [PASSED]

### Module 2: `backend/tests/test_secret_leak_prevention.py` (6 Tests — 100% Passed)
- `test_mask_secret_value`: Verifies string masking helper (`apif****NEr3`). [PASSED]
- `test_mask_connection_url`: Verifies MongoDB connection string password redaction. [PASSED]
- `test_settings_safe_representation`: Confirms configuration dictionary redacts all API keys. [PASSED]
- `test_exception_handler_sanitizes_errors`: Confirms FastAPI global exception handler never outputs raw tokens in stack traces. [PASSED]
- `test_integration_serialization_hides_raw_keys`: Verifies `/api/integrations/` responses hide raw keys. [PASSED]
- `test_frontend_has_no_private_api_keys`: Scans all frontend files for accidentally bundled private API keys. [PASSED]

### Module 3: `backend/tests/test_date_normalization.py` (5 Tests — 100% Passed)
- `test_parse_timestamp_formats`: Tests epoch timestamps, ISO 8601 strings, and date strings. [PASSED]
- `test_extract_and_normalize_verified_ad`: Confirms verified dates inside 30-day window are accepted. [PASSED]
- `test_extract_and_normalize_unverified_missing_date`: Confirms missing dates are flagged `unverified`. [PASSED]
- `test_extract_and_normalize_outside_30_day_window`: Confirms older ads are flagged as outside window. [PASSED]
- `test_extract_and_normalize_future_dated`: Confirms future timestamps are caught and flagged. [PASSED]

### Module 4: `backend/tests/test_market_intelligence.py` (22 Tests — 100% Passed)
- `TestMarketProfiles`:
  - `test_india_market_profile_structure`: Verifies INR currency, NSE/BSE exchanges, SEBI regulator. [PASSED]
  - `test_philippines_market_profile_structure`: Verifies PHP currency, PSE exchange, SEC Philippines regulator. [PASSED]
- `TestAudienceSegmentation`:
  - `test_get_india_segments`: Verifies 5 distinct Indian investor segments. [PASSED]
  - `test_get_philippines_segments`: Verifies 5 distinct Philippine investor segments. [PASSED]
  - `test_segment_filtering_by_experience`: Verifies beginner vs advanced filtering. [PASSED]
- `TestComplianceValidator`:
  - `test_flags_predatory_claims_universally`: Rejects "guaranteed profit" and "scam-proof" phrasing. [PASSED]
  - `test_validates_clean_script_with_disclaimer_india`: Validates compliant Indian script. [PASSED]
  - `test_validates_clean_script_philippines`: Validates compliant Philippine script. [PASSED]
- `TestMarketResearchService`:
  - `test_get_india_research_evidence`: Verifies retrieval of India research evidence. [PASSED]
  - `test_get_philippines_research_evidence`: Verifies retrieval of Philippines research evidence. [PASSED]
  - `test_research_cache_hit`: Verifies MongoDB research caching layer. [PASSED]
  - `test_calculate_source_quality_tier1_regulator`: Verifies Tier-1 scoring (9.8). [PASSED]
  - `test_calculate_source_quality_tier2_financial_press`: Verifies Tier-2 scoring (8.8). [PASSED]
  - `test_calculate_source_quality_staleness_penalty`: Verifies date decay penalty. [PASSED]
  - `test_calculate_source_quality_unverified_date`: Verifies undated penalty (0.90x). [PASSED]
- `TestMarketContextBuilder`:
  - `test_build_india_prompt_directive`: Verifies SEBI disclaimers and prompt injection. [PASSED]
  - `test_build_philippines_prompt_directive`: Verifies SEC PH disclaimers and prompt injection. [PASSED]
- `TestMarketIntelligenceEngine`:
  - `test_supported_countries`: Verifies IN and PH are supported. [PASSED]
  - `test_country_overview_in`: Verifies full India market overview payload. [PASSED]
  - `test_country_overview_ph`: Verifies full Philippines market overview payload. [PASSED]
  - `test_campaign_recommendations`: Verifies country-specific angle suggestions. [PASSED]
  - `test_create_dual_market_campaign_variants`: Verifies dual-market generation. [PASSED]

### Module 5: `backend/tests/test_research_intelligence_2_0.py` (9 Tests — 100% Passed)
- `TestProviderHealthService`:
  - `test_check_all_providers_returns_all_expected_keys`: Benchmarks concurrent diagnostic runner. [PASSED]
  - `test_ping_provider_gemini_fails_gracefully`: Confirms graceful handling of Gemini 401 error. [PASSED]
  - `test_ping_provider_tavily_reports_quota_or_status`: Confirms graceful handling of Tavily 432 limit. [PASSED]
- `TestClaimLevelEvidenceVerification`:
  - `test_claim_structure_contains_all_12_required_fields`: Enforces 12 claim-level verification fields. [PASSED]
  - `test_staleness_penalty_calculation`: Verifies 0.85x penalty for data >365 days old. [PASSED]
  - `test_undated_penalty_calculation`: Verifies 0.90x penalty for undated sources. [PASSED]
- `TestCompetitorAdNormalization`:
  - `test_apify_date_normalization_start_date_formatted`: Verifies Apify `startDateFormatted` field. [PASSED]
  - `test_ad_classification_distinguishes_live_vs_benchmark`: Verifies `LIVE_META_AD` vs `VERIFIED_DOMAIN_BENCHMARK`. [PASSED]
- `TestComplianceAndContextBuilder`:
  - `test_market_context_builder_forbids_absolute_claims`: Verifies ban on "Scam-Proof" in favor of "Research-Backed Clarity". [PASSED]

---

## 4. Frontend Production Build Verification

### Command Executed:
```bash
npm --prefix frontend run build
# (Runs `tsc -b && vite build`)
```

### Build Log Output:
```
vite v6.4.5 building for production...
transforming...
✓ 2543 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                     1.31 kB │ gzip:   0.66 kB
dist/assets/index-DqsvKn6H.css     77.55 kB │ gzip:  13.42 kB
dist/assets/index-BHVZLvAu.js   1,254.73 kB │ gzip: 358.53 kB
✓ built in 8.97s
```

### Verification Findings:
1. **0 TypeScript Errors**: Full type safety across all interfaces and API contracts.
2. **0 Bundle Leaks**: Scanned `dist/` directory; confirmed no raw API keys or sensitive secrets are embedded in compiled JavaScript or CSS bundles.
3. **Clean Asset Generation**: All components (`InsightsPage`, `ResearchPage`, navigation bars, provider pills) compiled without warnings.

