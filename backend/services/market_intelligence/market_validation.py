"""
CrowdWisdom AI Studio — Market & Financial Regulatory Compliance Validator
Evaluates marketing campaign copy, scripts, creative briefs, and voiceover text
against regulatory requirements for India (SEBI) and the Philippines (SEC Philippines).
"""
import re
import logging
from typing import Any, Dict, List, Tuple
from services.market_intelligence.india_market_profile import INDIA_MARKET_PROFILE
from services.market_intelligence.philippines_market_profile import PHILIPPINES_MARKET_PROFILE

logger = logging.getLogger(__name__)

# Common universal predatory financial claims prohibited globally
UNIVERSAL_PROHIBITED_PATTERNS = [
    r"\bguaranteed (returns?|profits?|income|gains?)\b",
    r"\b100%\s*(win\s*rate|risk[\s-]free|accurate|guarantee)\b",
    r"\b(risk[\s-]free|zero[\s-]risk)\s*(trading|investing|strategy)\b",
    r"\b(become|get)\s*rich\s*(quick|fast|overnight)\b",
    r"\bdouble\s*your\s*(money|capital|investment)\s*in\b",
    r"\bsurefire\s*(trade|call|tip|profit)\b",
    r"\bjackpot\s*(call|trade|stocks?)\b",
    r"\bsecret\s*(formula|insider\s*tips?|cheat\s*code)\s*to\s*wealth\b",
]

# Country specific prohibitions and nuances
INDIA_SPECIFIC_PATTERNS = [
    r"\b(sure|guaranteed)\s*nifty\s*target\b",
    r"\bjackpot\s*expiry\s*trade\b",
    r"\bzero[\s-]to[\s-]hero\s*call\b",
    r"\b100%\s*accurate\s*calls?\b",
    r"\btelegram\s*insider\s*levels?\b",
    r"\bguaranteed\s*multibagger\b",
]

PHILIPPINES_SPECIFIC_PATTERNS = [
    r"\bsure\s*win\s*sa\s*(stocks?|pse)\b",
    r"\binstant\s*millionaire\b",
    r"\bpassive\s*income\s*guarantee\b",
    r"\bpyramid\s*(scheme|earnings?)\b",
    r"\b100%\s*sure\s*payout\b",
]


class MarketComplianceValidator:
    """
    Validates marketing copy, scripts, and campaign artifacts against
    applicable securities advertising codes for India and the Philippines.
    """

    def validate_content(
        self,
        country_code: str,
        text_content: str,
        content_type: str = "script"
    ) -> Dict[str, Any]:
        """
        Validates text against compliance rules.
        Returns a compliance report with score, flagged violations, and required disclaimers.
        """
        country = country_code.upper().strip() if country_code else "IN"
        violations: List[Dict[str, str]] = []
        warnings: List[Dict[str, str]] = []

        lower_text = text_content.lower()

        # 1. Check universal prohibited patterns
        for pattern in UNIVERSAL_PROHIBITED_PATTERNS:
            matches = re.findall(pattern, lower_text)
            if matches:
                violations.append({
                    "rule": "Universal Securities Marketing Code",
                    "severity": "CRITICAL",
                    "issue": f"Prohibited predatory claim detected matching pattern: '{pattern}'",
                    "recommendation": "Remove claim of guaranteed returns or risk-free profits. Position platform as analytical research only.",
                })

        # 2. Check country-specific regulations
        if country == "IN":
            reg_profile = INDIA_MARKET_PROFILE.get("regulatory_safeguards", {})
            for pattern in INDIA_SPECIFIC_PATTERNS:
                if re.search(pattern, lower_text):
                    violations.append({
                        "rule": "SEBI Advertising Code & Circular SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2023/43",
                        "severity": "HIGH",
                        "issue": f"Non-compliant financial promotion pattern: '{pattern}'",
                        "recommendation": "SEBI prohibits guaranteed calls or misleading derivatives claims. Ensure content emphasizes risk and market research.",
                    })
        elif country == "PH":
            reg_profile = PHILIPPINES_MARKET_PROFILE.get("regulatory_safeguards", {})
            for pattern in PHILIPPINES_SPECIFIC_PATTERNS:
                if re.search(pattern, lower_text):
                    violations.append({
                        "rule": "SEC Philippines SRC Rule 56 & Public Solicitations Directives",
                        "severity": "HIGH",
                        "issue": f"Non-compliant investment solicitation pattern: '{pattern}'",
                        "recommendation": "SEC Philippines strictly regulates public solicitations. Distinguish educational software from registered advisory.",
                    })
        else:
            reg_profile = INDIA_MARKET_PROFILE.get("regulatory_safeguards", {})

        # 3. Check for advisory vs educational distinction
        advisory_claims = [
            r"\bwe\s*tell\s*you\s*(exactly\s*)?what\s*to\s*buy\b",
            r"\bour\s*licensed\s*advisers?\s*pick\s*for\s*you\b",
            r"\bguaranteed\s*portfolio\s*growth\b",
        ]
        for pattern in advisory_claims:
            if re.search(pattern, lower_text):
                warnings.append({
                    "rule": "Advisory License Boundary",
                    "severity": "MEDIUM",
                    "issue": "Language implies individual investment advisory rather than analytical tools.",
                    "recommendation": "Clarify that CrowdWisdom aggregates sentiment and users execute trades independently on their own brokerages.",
                })

        # 4. Check mandatory disclaimer presence for long-form scripts or briefs
        mandatory_disclaimers = reg_profile.get("mandatory_disclaimers", [])
        has_risk_acknowledgement = any(
            kw in lower_text
            for kw in ["market risk", "subject to market risks", "educational", "sentiment research", "past performance"]
        )
        if not has_risk_acknowledgement and content_type in ("script", "brief"):
            warnings.append({
                "rule": "Mandatory Risk Disclosure",
                "severity": "MEDIUM",
                "issue": "Content lacks explicit risk acknowledgment or educational classification.",
                "recommendation": f"Append standard disclaimer: '{mandatory_disclaimers[0] if mandatory_disclaimers else 'Trading involves market risk.'}'",
            })

        # Calculate compliance score (0.0 - 10.0)
        critical_count = sum(1 for v in violations if v.get("severity") == "CRITICAL")
        high_count = sum(1 for v in violations if v.get("severity") == "HIGH")
        medium_count = len(warnings)

        penalty = (critical_count * 4.0) + (high_count * 2.5) + (medium_count * 0.5)
        score = max(1.0, round(10.0 - penalty, 1))

        is_compliant = critical_count == 0 and high_count == 0

        return {
            "country_code": country,
            "regulator": reg_profile.get("regulator", "Securities Regulator"),
            "compliance_score": score,
            "is_compliant": is_compliant,
            "requires_human_review": not is_compliant or medium_count > 1,
            "violations": violations,
            "warnings": warnings,
            "mandatory_disclaimers": mandatory_disclaimers,
            "required_labeling": reg_profile.get("required_labeling", "For Educational Research Only"),
        }


compliance_validator = MarketComplianceValidator()
