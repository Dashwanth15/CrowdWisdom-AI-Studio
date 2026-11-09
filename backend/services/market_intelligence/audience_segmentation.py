"""
CrowdWisdom AI Studio — Country-Aware Audience Segmentation Engine
Dynamic audience segmentation, demographic profiling, and interest matching
tailored specifically for India (IN) and the Philippines (PH).
"""
import logging
from typing import Any, Dict, List, Optional
from services.market_intelligence.india_market_profile import INDIA_MARKET_PROFILE
from services.market_intelligence.philippines_market_profile import PHILIPPINES_MARKET_PROFILE

logger = logging.getLogger(__name__)


class AudienceSegmentationEngine:
    """
    Manages and dynamically generates country-aware audience segments for
    advertising campaigns, script generation, and creative targeting.
    """

    def __init__(self):
        self._profiles = {
            "IN": INDIA_MARKET_PROFILE,
            "PH": PHILIPPINES_MARKET_PROFILE,
        }

    def get_segments_for_country(
        self,
        country_code: str,
        experience_level: Optional[str] = None,
        interest: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves audience segments for a country with optional filtering.
        """
        norm_country = country_code.upper().strip()
        if norm_country not in self._profiles:
            # Fallback to India if unknown
            norm_country = "IN"

        segments = self._profiles[norm_country].get("audience_segments", [])
        filtered = []

        for seg in segments:
            # Experience level filter
            if experience_level and experience_level.lower() != "all":
                if experience_level.lower() not in seg.get("experience_level", "").lower():
                    continue

            # Interest filter
            if interest:
                int_match = any(
                    interest.lower() in p.lower()
                    for p in seg.get("primary_focus", [])
                )
                if not int_match:
                    continue

            # Channel filter
            if channel:
                ch_match = any(
                    channel.lower() in ch.lower()
                    for ch in seg.get("dominant_channels", [])
                )
                if not ch_match:
                    continue

            filtered.append(seg)

        return filtered

    def get_segment_by_id(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """Finds a specific segment across all supported countries."""
        for country_code, profile in self._profiles.items():
            for seg in profile.get("audience_segments", []):
                if seg.get("segment_id") == segment_id:
                    res = dict(seg)
                    res["country_code"] = country_code
                    return res
        return None

    def match_campaign_audience(
        self,
        country_code: str,
        audience_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Matches a generic or user-defined audience configuration to the most relevant
        country-specific audience segment and extracts targeting parameters.
        """
        norm_country = country_code.upper().strip() if country_code else "IN"
        segments = self.get_segments_for_country(norm_country)

        selected_segment_ids = audience_config.get("segments", [])
        matched_segment = None

        # Try to find direct match by segment_id or keyword
        for seg in segments:
            if seg["segment_id"] in selected_segment_ids:
                matched_segment = seg
                break
            for sel_id in selected_segment_ids:
                if sel_id.lower() in seg["name"].lower() or sel_id.lower() in seg["segment_id"].lower():
                    matched_segment = seg
                    break
            if matched_segment:
                break

        # Default to first segment if no explicit match
        if not matched_segment and segments:
            matched_segment = segments[0]

        profile = self._profiles.get(norm_country, INDIA_MARKET_PROFILE)
        regional_info = profile.get("regional_intelligence", {})
        marketing_info = profile.get("marketing_intelligence", {})

        return {
            "country_code": norm_country,
            "country_name": profile.get("country_name"),
            "matched_segment": matched_segment,
            "available_segments": [s["segment_id"] for s in segments],
            "regional_targeting": regional_info,
            "recommended_channels": matched_segment.get("dominant_channels", []) if matched_segment else [],
            "preferred_languages": matched_segment.get("preferred_languages", []) if matched_segment else [],
            "pain_points": matched_segment.get("pain_points", []) if matched_segment else [],
            "local_terminology": marketing_info.get("local_terminology", []),
            "voiceover_spec": marketing_info.get("voiceover_specifications", {}),
        }


audience_segmentation_engine = AudienceSegmentationEngine()

