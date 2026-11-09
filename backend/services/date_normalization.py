"""
CrowdWisdom AI Studio — Advertisement Publication Date Normalization & Verification Service
Extracts, parses, and normalizes publication/delivery start timestamps from Meta Ads Library records (via Apify).
Enforces verifiable 30-day research windows and prevents fabrication of missing dates.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Primary publication/start date fields found in Meta Ads Library / Apify actors in priority order
CANDIDATE_DATE_FIELDS = [
    "startDateFormatted",
    "startDate",
    "ad_delivery_start_time",
    "adDeliveryStartTime",
    "delivery_start_time",
    "start_date",
    "first_seen",
    "firstSeenDate",
]

# Raw actor payload fields (checked only inside raw_data or snapshot, never top-level document)
RAW_ONLY_DATE_FIELDS = [
    "creation_time",
    "creationTime",
    "creationDate",
]


def parse_timestamp_value(val: Any) -> Optional[datetime]:
    """
    Safely parse various date/timestamp formats into a timezone-aware UTC datetime.
    Supports Unix timestamps (seconds & milliseconds), ISO 8601 strings, and date strings.
    Never invents missing time.
    """
    if val is None or val == "":
        return None

    # Handle already parsed datetime
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)

    # Handle numeric Unix epoch timestamps
    if isinstance(val, (int, float)):
        try:
            # If value > 1e11, it's in milliseconds (e.g. 1729000000000)
            if val > 1e11:
                return datetime.fromtimestamp(val / 1000.0, tz=timezone.utc)
            # If value > 1e8, it's in seconds (e.g. 1729000000)
            if val > 1e8:
                return datetime.fromtimestamp(val, tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            return None

    # Handle string representations
    if isinstance(val, str):
        val_str = val.strip()
        if not val_str:
            return None

        # Check if numeric string (Unix timestamp)
        try:
            if val_str.isdigit():
                num = int(val_str)
                if num > 1e11:
                    return datetime.fromtimestamp(num / 1000.0, tz=timezone.utc)
                if num > 1e8:
                    return datetime.fromtimestamp(num, tz=timezone.utc)
        except Exception:
            pass

        # Try standard ISO 8601 (handles 'Z' and offset)
        try:
            clean_iso = val_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

        # Try YYYY-MM-DD
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%b %d, %Y"):
            try:
                dt = datetime.strptime(val_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except Exception:
                continue

    return None


def extract_and_normalize_publication_date(
    raw_ad: Dict[str, Any],
    scraped_at: Optional[datetime] = None,
    window_days: int = 30,
) -> Dict[str, Any]:
    """
    Extracts the genuine publication/delivery start timestamp from raw ad data.
    
    Returns a dictionary containing:
    - published_at: Optional[datetime] (UTC)
    - published_at_raw: Optional[str] (exact source value preserved)
    - published_date_source: Optional[str] (source field name)
    - scraped_at: datetime (UTC extraction timestamp, separate from publication date)
    - date_verification_status: "verified" | "unverified"
    - is_within_30_days: bool (True only if verified and falls strictly in [now - 30d, now + 1d])
    - age_days: Optional[int] (days between publication and now)
    - meta_ads_url: Optional[str] (direct Meta Ads Library URL if ad ID is available)
    """
    now = datetime.now(timezone.utc)
    scraped_dt = scraped_at or now

    # Extract ad ID for Meta Ads Library deep-link
    ad_id = str(
        raw_ad.get("adArchiveId")
        or raw_ad.get("adArchiveID")
        or raw_ad.get("ad_archive_id")
        or raw_ad.get("ad_id")
        or raw_ad.get("id")
        or raw_ad.get("adId")
        or ""
    ).strip()
    
    meta_ads_url = None
    if ad_id and not ad_id.startswith("ad_meta_benchmark"):
        # Real Meta Ads Library URL
        meta_ads_url = f"https://www.facebook.com/ads/library/?id={ad_id}"

    # Search for publication date in candidate fields in raw_ad and raw_ad.get("raw_data")
    extracted_dt: Optional[datetime] = None
    extracted_source: Optional[str] = None
    extracted_raw_val: Optional[str] = None

    # First check raw_data and snapshot for delivery start or creation time
    sub_sources = []
    if isinstance(raw_ad.get("raw_data"), dict):
        sub_sources.append(raw_ad["raw_data"])
    if isinstance(raw_ad.get("snapshot"), dict):
        sub_sources.append(raw_ad["snapshot"])

    # Priority 1: Check candidate delivery/start date fields across all sources
    for src in [raw_ad] + sub_sources:
        for field in CANDIDATE_DATE_FIELDS:
            if field in src and src[field] is not None and src[field] != "":
                parsed = parse_timestamp_value(src[field])
                if parsed is not None:
                    extracted_dt = parsed
                    extracted_source = field
                    extracted_raw_val = str(src[field])
                    break
        if extracted_dt is not None:
            break

    # Priority 2: Check creation date only inside raw actor payload (never top-level doc)
    if extracted_dt is None:
        for src in sub_sources:
            for field in RAW_ONLY_DATE_FIELDS:
                if field in src and src[field] is not None and src[field] != "":
                    parsed = parse_timestamp_value(src[field])
                    if parsed is not None:
                        extracted_dt = parsed
                        extracted_source = f"raw_data.{field}"
                        extracted_raw_val = str(src[field])
                        break
            if extracted_dt is not None:
                break

    # Verification criteria:
    # 1. Date was successfully extracted and parsed
    # 2. Date is not in the future (allow 24h clock/timezone skew)
    # 3. Date is not corrupted/ancient (>= 2015)
    is_verified = False
    if extracted_dt is not None:
        future_limit = now + timedelta(days=1)
        ancient_limit = datetime(2015, 1, 1, tzinfo=timezone.utc)
        if ancient_limit <= extracted_dt <= future_limit:
            is_verified = True

    # 30-day window enforcement:
    # Window: [now - window_days, now + 1 day]
    window_start = now - timedelta(days=window_days)
    window_end = now + timedelta(days=1)
    is_within_window = False

    age_days: Optional[int] = None
    if is_verified and extracted_dt is not None:
        age_days = max(0, (now - extracted_dt).days)
        if window_start <= extracted_dt <= window_end:
            is_within_window = True

    return {
        "published_at": extracted_dt if is_verified else None,
        "published_at_raw": extracted_raw_val,
        "published_date_source": extracted_source,
        "scraped_at": scraped_dt,
        "date_verification_status": "verified" if is_verified else "unverified",
        "is_within_30_days": is_within_window,
        "age_days": age_days,
        "meta_ads_url": meta_ads_url,
    }
