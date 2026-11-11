"""
CrowdWisdom AI Studio — Country Localization & Currency Consistency Service
Centralized engine enforcing consistent regional financial terminology, currency formatting,
vocabulary constraints, and cross-country consistency validation across all campaigns and scripts.
"""
import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Currency Specifications by Country
COUNTRY_CURRENCY_MAP = {
    "IN": {
        "code": "INR",
        "symbol": "₹",
        "name": "Indian Rupee",
        "major_loss_figure": "₹1,00,000",
        "major_loss_text": "one lakh rupees",
        "major_loss_num": 100000,
        "sample_figures": ["₹1,00,000", "₹50,000", "₹25,000", "₹10,000", "₹5,000"],
        "number_grouping": "lakhs_crores",  # e.g., 1,00,000
    },
    "PH": {
        "code": "PHP",
        "symbol": "₱",
        "name": "Philippine Peso",
        "major_loss_figure": "₱100,000",
        "major_loss_text": "one hundred thousand pesos",
        "major_loss_num": 100000,
        "sample_figures": ["₱100,000", "₱50,000", "₱20,000", "₱10,000", "₱5,000"],
        "number_grouping": "thousands_millions",  # e.g., 100,000
    },
    "GLOBAL": {
        "code": "USD",
        "symbol": "$",
        "name": "US Dollar",
        "major_loss_figure": "$10,000",
        "major_loss_text": "ten thousand dollars",
        "major_loss_num": 10000,
        "sample_figures": ["$10,000", "$5,000", "$2,500", "$1,000", "$500"],
        "number_grouping": "thousands_millions",
    }
}

# Regional Financial Vocabularies
REGIONAL_VOCABULARY = {
    "IN": {
        "exchanges": ["NSE", "BSE", "National Stock Exchange", "Bombay Stock Exchange"],
        "indices": ["Nifty 50", "Nifty", "Bank Nifty", "Sensex", "FinNifty"],
        "instruments": ["F&O", "Futures and Options", "Options", "Derivatives", "Equities"],
        "accounts": ["Demat", "Trading Account"],
        "regulator": "SEBI",
        "regulator_full": "Securities and Exchange Board of India",
        "hubs": ["Dalal Street", "Mumbai", "BKC", "Bengaluru"],
        "trading_hours": "09:15 AM - 03:30 PM IST (Pre-market 09:00 AM)",
        "pre_market_time": "09:00 AM",
        "local_terms": [
            "Dalal Street", "Nifty 50", "Bank Nifty", "Sensex", "Demat",
            "F&O", "Expiry Day", "Stop-loss", "Telegram tipsters", "Chai and Charts"
        ],
        "mandatory_disclaimer": "For Educational Sentiment Research Only. Subject to SEBI regulatory guidelines. Not investment advice.",
    },
    "PH": {
        "exchanges": ["PSE", "Philippine Stock Exchange"],
        "indices": ["PSEi", "PSE Composite Index", "All Shares Index"],
        "instruments": ["Philippine Stocks", "REITs", "Blue Chips", "Second-liners", "Equities"],
        "accounts": ["Online Brokerage", "COL Financial", "First Metro Sec", "BDO Securities", "GStocks"],
        "regulator": "SEC Philippines",
        "regulator_full": "Securities and Exchange Commission of the Philippines",
        "hubs": ["Bonifacio Global City", "BGC", "Makati CBD", "Ayala Avenue", "Ortigas"],
        "trading_hours": "09:30 AM - 03:00 PM PHT (Pre-open 09:15 AM)",
        "pre_market_time": "09:15 AM",
        "local_terms": [
            "PSEi", "Philippine Stock Exchange", "BGC", "Makati CBD", "Blue Chips",
            "Chismis", "Diskarte", "Bayanihan", "OFW", "Remittance", "GStocks"
        ],
        "mandatory_disclaimer": "For Educational & Market Sentiment Research Only. SEC Philippines disclosures apply. Not personalized investment advice.",
    }
}


class CountryLocalizationService:
    """
    Central service for regional localization, regex replacements,
    and cross-country consistency verification.
    """

    def get_currency_spec(self, country_code: str) -> Dict[str, Any]:
        norm = (country_code or "IN").upper().strip()
        if norm not in COUNTRY_CURRENCY_MAP:
            norm = "IN"
        return COUNTRY_CURRENCY_MAP[norm]

    def get_vocabulary(self, country_code: str) -> Dict[str, Any]:
        norm = (country_code or "IN").upper().strip()
        if norm not in REGIONAL_VOCABULARY:
            norm = "IN"
        return REGIONAL_VOCABULARY[norm]

    def format_currency_amount(self, amount: float, country_code: str) -> str:
        """
        Formats numbers using proper country-specific grouping and currency symbol.
        """
        norm = (country_code or "IN").upper().strip()
        if norm == "IN":
            # Indian numbering: 1,00,000
            int_val = int(amount)
            s = str(int_val)
            if len(s) <= 3:
                grouped = s
            else:
                last_three = s[-3:]
                remaining = s[:-3]
                # Split remaining in pairs of 2 from right to left
                parts = []
                while len(remaining) > 2:
                    parts.insert(0, remaining[-2:])
                    remaining = remaining[:-2]
                if remaining:
                    parts.insert(0, remaining)
                grouped = ",".join(parts) + "," + last_three
            return f"₹{grouped}"
        elif norm == "PH":
            return f"₱{amount:,.0f}"
        else:
            return f"${amount:,.0f}"

    def localize_script_dict(self, script_dict: Dict[str, Any], country_code: str) -> Dict[str, Any]:
        """
        Deeply localizes all fields of a script dictionary:
        - title / campaign_title
        - visual_hook
        - core_message
        - marketing_angle
        - pain_point
        - scenes: visual_description, voiceover, on_screen_text
        - call_to_action
        """
        norm = (country_code or "IN").upper().strip()
        if norm == "BOTH":
            norm = "IN"

        out = dict(script_dict)

        # 1. Title localization
        title = out.get("campaign_title") or out.get("title") or ""
        out["campaign_title"] = self.localize_text(title, norm)
        out["title"] = out["campaign_title"]

        # 2. Visual hook localization (CRITICAL: prevents -$10,450 from slipping into hook)
        if "visual_hook" in out and out["visual_hook"]:
            out["visual_hook"] = self.localize_text(out["visual_hook"], norm)

        # 3. Core message
        if "core_message" in out and out["core_message"]:
            out["core_message"] = self.localize_text(out["core_message"], norm)

        # 4. Marketing angle & Pain point
        if "marketing_angle" in out and out["marketing_angle"]:
            out["marketing_angle"] = self.localize_text(out["marketing_angle"], norm)
        if "pain_point" in out and out["pain_point"]:
            out["pain_point"] = self.localize_text(out["pain_point"], norm)

        # 5. Localize each storyboard scene
        scenes = out.get("scenes", [])
        localized_scenes = []
        for sc in scenes:
            sc_copy = dict(sc)
            if "visual_description" in sc_copy and sc_copy["visual_description"]:
                sc_copy["visual_description"] = self.localize_text(sc_copy["visual_description"], norm)
            if "voiceover" in sc_copy and sc_copy["voiceover"]:
                sc_copy["voiceover"] = self.localize_text(sc_copy["voiceover"], norm)
            if "on_screen_text" in sc_copy and sc_copy["on_screen_text"]:
                sc_copy["on_screen_text"] = self.localize_text(sc_copy["on_screen_text"], norm)
            localized_scenes.append(sc_copy)

        # Guarantee regulatory disclaimer in final scene
        vocab = self.get_vocabulary(norm)
        disclaimer_tag = f"• {vocab['mandatory_disclaimer']}"
        if localized_scenes:
            final_scene = localized_scenes[-1]
            ost = final_scene.get("on_screen_text", "").rstrip(" •")
            if norm == "IN":
                if "SEBI" not in ost and "Disclosures" not in ost and "Educational" not in ost:
                    final_scene["on_screen_text"] = f"{ost} • For Educational Sentiment Research Only (SEBI Disclosures Apply)".strip(" •")
            elif norm == "PH":
                if "SEC" not in ost and "Disclosures" not in ost and "Educational" not in ost:
                    final_scene["on_screen_text"] = f"{ost} • For Educational & Market Sentiment Research Only (SEC Philippines Disclosures Apply)".strip(" •")
            # Clean up any accidental double bullets
            final_scene["on_screen_text"] = re.sub(r'•\s*•', '•', final_scene["on_screen_text"]).strip()

        out["scenes"] = localized_scenes
        out["target_country"] = norm

        # Recalculate voiceover_full and on_screen_texts
        out["voiceover_full"] = " ".join(s.get("voiceover", "") for s in localized_scenes if s.get("voiceover"))
        out["on_screen_texts"] = [s.get("on_screen_text", "") for s in localized_scenes if s.get("on_screen_text")]
        if localized_scenes and "on_screen_text" in localized_scenes[-1]:
            out["call_to_action"] = localized_scenes[-1]["on_screen_text"]

        return out

    def localize_text(self, text: str, country_code: str) -> str:
        """
        Regex-based robust text localization replacing US references and mismatched currencies.
        """
        if not text:
            return ""

        norm = (country_code or "IN").upper().strip()
        result = text

        if norm == "IN":
            # --- CURRENCY & AMOUNTS (Case-insensitive robust regex) ---
            # -$10,450.00 / -$10,450 / $10,450.00 / $10,450
            result = re.sub(r'-\$10[,\.]450(?:\.00)?', '-₹1,00,000.00', result)
            result = re.sub(r'\$10[,\.]450(?:\.00)?', '₹1,00,000', result)
            # $10,000 / $10000
            result = re.sub(r'\$10,?000(?:\.00)?', '₹1,00,000', result)
            result = re.sub(r'\$5,?000(?:\.00)?', '₹50,000', result)
            result = re.sub(r'\$1,?000(?:\.00)?', '₹10,000', result)
            result = re.sub(r'\$500(?:\.00)?', '₹5,000', result)
            # Generic dollar expressions
            result = re.sub(r'(?i)\bten thousand dollars\b', 'one lakh rupees', result)
            result = re.sub(r'(?i)\bfive thousand dollars\b', 'fifty thousand rupees', result)
            result = re.sub(r'(?i)\bdollars\b', 'rupees', result)

            # --- FINANCIAL HUBS & GEOGRAPHY ---
            result = re.sub(r'\bWall Street\b', 'Dalal Street', result)
            result = re.sub(r'\bNew York\b', 'Mumbai', result)
            result = re.sub(r'\bLondon\b', 'Bengaluru', result)

            # --- CHANNELS & NOISE SOURCES ---
            result = re.sub(r'(?i)\b40 contradictory newsletters\b', 'forty noisy Telegram channels', result)
            result = re.sub(r'(?i)\bforty contradictory newsletters\b', 'forty noisy Telegram channels', result)

            # --- TRADING SESSIONS & HOURS ---
            result = re.sub(r'\b06:30 AM\b', '09:00 AM', result)
            result = re.sub(r'\b5:30 AM\b', '08:30 AM', result)
            result = re.sub(r'\b6:30 AM\b', '09:00 AM', result)

            # --- AUDIENCE SPECIFICATION ---
            result = re.sub(r'(?i)\bretail traders\b', 'Indian retail traders', result)
            result = re.sub(r'Indian Indian retail traders', 'Indian retail traders', result)

            # --- REMOVE ANY LEAKED PHILIPPINE PESOS OR TERMS ---
            result = re.sub(r'₱100,?000(?:\.00)?', '₹1,00,000', result)
            result = re.sub(r'Philippine Stock Exchange', 'National Stock Exchange', result)
            result = re.sub(r'\bPSEi\b', 'Nifty 50', result)
            result = re.sub(r'\bPSE\b', 'NSE', result)
            result = re.sub(r'\bBGC\b', 'Dalal Street', result)

        elif norm == "PH":
            # --- CURRENCY & AMOUNTS ---
            result = re.sub(r'-\$10[,\.]450(?:\.00)?', '-₱100,000.00', result)
            result = re.sub(r'\$10[,\.]450(?:\.00)?', '₱100,000', result)
            result = re.sub(r'\$10,?000(?:\.00)?', '₱100,000', result)
            result = re.sub(r'\$5,?000(?:\.00)?', '₱50,000', result)
            result = re.sub(r'\$1,?000(?:\.00)?', '₱10,000', result)
            result = re.sub(r'\$500(?:\.00)?', '₱5,000', result)
            result = re.sub(r'(?i)\bten thousand dollars\b', 'one hundred thousand pesos', result)
            result = re.sub(r'(?i)\bfive thousand dollars\b', 'fifty thousand pesos', result)
            result = re.sub(r'(?i)\bdollars\b', 'pesos', result)

            # --- FINANCIAL HUBS & GEOGRAPHY ---
            result = re.sub(r'\bWall Street\b', 'Philippine Stock Exchange', result)
            result = re.sub(r'\bDalal Street\b', 'Bonifacio Global City', result)
            result = re.sub(r'\bNew York\b', 'Bonifacio Global City', result)
            result = re.sub(r'\bMumbai\b', 'Makati CBD', result)
            result = re.sub(r'\bLondon\b', 'Makati CBD', result)

            # --- CHANNELS & NOISE SOURCES ---
            result = re.sub(r'(?i)\b40 contradictory newsletters\b', 'unverified Facebook stock rumors', result)
            result = re.sub(r'(?i)\bforty contradictory newsletters\b', 'unverified Facebook stock rumors', result)
            result = re.sub(r'(?i)\bforty noisy Telegram channels\b', 'unverified Facebook stock rumors', result)

            # --- TRADING SESSIONS & HOURS ---
            result = re.sub(r'\b06:30 AM\b', '09:15 AM', result)
            result = re.sub(r'\b09:00 AM\b', '09:15 AM', result)
            result = re.sub(r'\b6:30 AM\b', '09:15 AM', result)
            result = re.sub(r'\b5:30 AM\b', '08:45 AM', result)

            # --- AUDIENCE SPECIFICATION ---
            result = re.sub(r'(?i)\bretail traders\b', 'Filipino retail investors', result)
            result = re.sub(r'Filipino Filipino retail investors', 'Filipino retail investors', result)

            # --- REMOVE ANY LEAKED RUPEES OR INDIAN TERMS ---
            result = re.sub(r'₹1,00,000(?:\.00)?', '₱100,000', result)
            result = re.sub(r'₹50,000(?:\.00)?', '₱50,000', result)
            result = re.sub(r'₹10,000(?:\.00)?', '₱10,000', result)
            result = re.sub(r'\bNifty 50\b', 'PSEi', result)
            result = re.sub(r'\bBank Nifty\b', 'PSE Blue Chips', result)
            result = re.sub(r'\bNSE\b', 'PSE', result)
            result = re.sub(r'\bBSE\b', 'PSE', result)
            result = re.sub(r'\bSEBI\b', 'SEC Philippines', result)

        return result

    def validate_script_country_consistency(
        self, script_dict: Dict[str, Any], country_code: str
    ) -> Dict[str, Any]:
        """
        Validates country and currency consistency across title, visual_hook, scenes, and text.
        Returns a structured report:
        {
            "is_consistent": bool,
            "target_country": "IN" | "PH",
            "inconsistencies": List[Dict[str, Any]],
            "detected_currencies": List[str],
            "recommendation": str
        }
        """
        norm = (country_code or "IN").upper().strip()
        inconsistencies = []
        detected_currencies = set()

        text_corpus = [
            ("title", script_dict.get("title") or script_dict.get("campaign_title") or ""),
            ("visual_hook", script_dict.get("visual_hook") or ""),
            ("core_message", script_dict.get("core_message") or ""),
            ("marketing_angle", script_dict.get("marketing_angle") or ""),
            ("voiceover_full", script_dict.get("voiceover_full") or ""),
        ]

        for sc in script_dict.get("scenes", []):
            s_num = sc.get("scene_number", "?")
            text_corpus.append((f"scene_{s_num}_visual", sc.get("visual_description") or ""))
            text_corpus.append((f"scene_{s_num}_voiceover", sc.get("voiceover") or ""))
            text_corpus.append((f"scene_{s_num}_on_screen_text", sc.get("on_screen_text") or ""))

        # Check currency leaks
        for field_name, raw_val in text_corpus:
            if not raw_val:
                continue
            if isinstance(raw_val, dict):
                val = json.dumps(raw_val)
            elif not isinstance(raw_val, str):
                val = str(raw_val)
            else:
                val = raw_val

            # Check USD in IN or PH
            if "$" in val or re.search(r'\b(?:USD|dollars?)\b', val, re.I):
                detected_currencies.add("USD")
                inconsistencies.append({
                    "field": field_name,
                    "issue": "Unexplained USD / Dollar reference in localized campaign",
                    "snippet": val[:120],
                    "expected": "INR (₹)" if norm == "IN" else "PHP (₱)"
                })

            # Check PHP in IN
            if norm == "IN" and ("₱" in val or re.search(r'\b(?:PHP|pesos?|PSEi|PSE|BGC|Makati|Ayala|Ortigas|Bonifacio|SEC Philippines|chismis)\b', val, re.I)):
                detected_currencies.add("PHP")
                inconsistencies.append({
                    "field": field_name,
                    "issue": "Philippine currency/term leaked into India campaign",
                    "snippet": val[:120],
                    "expected": "INR (₹) / NSE / Dalal Street"
                })

            # Check INR in PH
            if norm == "PH" and ("₹" in val or re.search(r'\b(?:INR|rupees?|Nifty|Bank\s*Nifty|FinNifty|Sensex|SEBI|NSE|BSE|Dalal Street|Demat|Lakhs?|Crores?|Zerodha|Groww|AngelOne)\b', val, re.I)):
                detected_currencies.add("INR")
                inconsistencies.append({
                    "field": field_name,
                    "issue": "Indian currency/term leaked into Philippines campaign",
                    "snippet": val[:120],
                    "expected": "PHP (₱) / PSEi / BGC"
                })

            if "₹" in val:
                detected_currencies.add("INR")
            if "₱" in val:
                detected_currencies.add("PHP")

        is_consistent = len(inconsistencies) == 0

        return {
            "is_consistent": is_consistent,
            "target_country": norm,
            "inconsistencies_count": len(inconsistencies),
            "inconsistencies": inconsistencies,
            "detected_currencies": list(detected_currencies),
            "recommendation": (
                "Script is clean and consistently localized."
                if is_consistent
                else f"Found {len(inconsistencies)} localization mismatches. Please run country auto-repair or regenerate."
            )
        }


country_localization_service = CountryLocalizationService()
