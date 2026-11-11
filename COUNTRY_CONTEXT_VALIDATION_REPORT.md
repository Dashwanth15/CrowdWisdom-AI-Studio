# CrowdWisdom AI Studio — Country Context Validation Report

**Audit Date:** 2026-11-11  
**Scope:** Regulatory Compliance, Financial Terminology & Cross-Country Boundary Enforcement  
**Status:** Validated  

---

## 1. Compliance & Legal Standard

The platform enforces strict market intelligence boundaries between:
- **India (IN):** INR (₹), NSE, BSE, Nifty 50, Bank Nifty, Demat, Dalal Street, BKC Mumbai, SEBI regulatory disclosures.
- **Philippines (PH):** PHP (₱), PSE, PSEi, Philippine Blue Chips (SM, BDO, Ayala, ICTSI), Makati CBD, BGC, SEC Philippines educational disclosures.

### Regulatory Claim Rules
1. **Never claim regulatory certification, compliance, or registration.**
   - Falsely asserting `"SEBI Compliant Research"` or `"SEC Philippines Compliance"` risks regulatory scrutiny if CrowdWisdom is not registered as an Investment Adviser (RIA) or Research Analyst (RA).
2. **Proper Educational & Sentiment Research Disclosures:**
   - **For India:**  
     `"CrowdWisdomTrading.com — Trade What the Data Shows • For Educational Sentiment Research Only (SEBI Disclosures Apply)"`
   - **For Philippines:**  
     `"CrowdWisdomTrading.com — Trade What the Data Shows • For Educational & Market Sentiment Research Only (SEC Philippines Disclosures Apply)"`

---

## 2. Multi-Market Vocabulary & Forbidden Token Matrix

| Target Country | Mandatory Currency / Symbol | Permitted Exchanges / Hubs | Forbidden Leaked Terms (Triggers Failure) |
| :--- | :--- | :--- | :--- |
| **Philippines (`PH`)** | PHP (`₱`) | PSE, PSEi, Philippine Stock Exchange, Makati CBD, Ayala Avenue, BGC, Ortigas | INR, ₹, rupees, Nifty, Bank Nifty, FinNifty, Sensex, SEBI, NSE, BSE, Dalal Street, Demat, Lakh, Crore, Zerodha, Groww, AngelOne |
| **India (`IN`)** | INR (`₹`) | NSE, BSE, Nifty 50, Bank Nifty, Sensex, Dalal Street, BKC Mumbai, Bengaluru | PHP, ₱, pesos, PSE, PSEi, BGC, Makati, Ayala, Ortigas, Bonifacio, SEC Philippines, chismis |

---

## 3. Automated Consistency Verification Pipeline

The consistency verification algorithm in `country_localization_service.py` (`validate_script_country_consistency`) runs on every generated, updated, or localized script across all fields:
- Script Title (`campaign_title`, `title`)
- Core Message (`core_message`)
- Visual Hook (`visual_hook`)
- Marketing Angle (`marketing_angle`)
- Pain Point (`pain_point`)
- Storyboard Scenes (`visual_description`, `voiceover`, `on_screen_text`)

### Validation Output Structure
```json
{
  "is_consistent": true,
  "target_country": "PH",
  "inconsistencies_count": 0,
  "inconsistencies": [],
  "detected_currencies": ["PHP"],
  "recommendation": "Script is clean and consistently localized."
}
```

If any forbidden cross-border term or unexpected foreign currency is detected:
- `is_consistent` evaluates to `False`.
- `inconsistencies_count` is incremented.
- Detailed snippets indicating field name, offending text, and expected replacement are recorded.
- An alert is logged and attached to the script record in MongoDB.

---

## 4. Test Suite Validation Results

Executed via `pytest tests/test_country_localization.py`:
- `test_currency_formatting`: PASSED
- `test_india_localization_replaces_dollars`: PASSED
- `test_philippines_localization_replaces_dollars`: PASSED
- `test_deep_script_dict_localization_india`: PASSED
- `test_deep_script_dict_localization_philippines`: PASSED
- `test_nse_sebi_leak_detection_in_philippines`: PASSED (Flags `NSE`, `Bank Nifty`, and `SEBI` in PH scripts)
- `test_cinematic_prompt_macro_separation`: PASSED (Confirms macro hands prompt isolation)
- `test_philippines_regulatory_disclaimer`: PASSED (Confirms proper SEC disclosures without false compliance claims)

**Result:** 8 tests passed, 0 failures.
