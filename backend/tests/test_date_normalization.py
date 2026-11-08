"""
Unit tests for Advertisement Publication Date Normalization & Verification.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timezone, timedelta
import pytest
from services.date_normalization import parse_timestamp_value, extract_and_normalize_publication_date


def test_parse_timestamp_formats():
    # Unix seconds
    dt_sec = parse_timestamp_value(1729000000)
    assert dt_sec is not None
    assert dt_sec.tzinfo == timezone.utc

    # Unix milliseconds
    dt_ms = parse_timestamp_value(1729000000000)
    assert dt_ms is not None
    assert dt_ms.tzinfo == timezone.utc
    assert dt_ms == dt_sec

    # ISO 8601
    dt_iso = parse_timestamp_value("2026-10-15T12:30:00Z")
    assert dt_iso is not None
    assert dt_iso.year == 2026
    assert dt_iso.month == 10
    assert dt_iso.day == 15

    # Date only string
    dt_date = parse_timestamp_value("2026-10-20")
    assert dt_date is not None
    assert dt_date.day == 20

    # None and empty
    assert parse_timestamp_value(None) is None
    assert parse_timestamp_value("") is None
    assert parse_timestamp_value("invalid-date-string") is None


def test_extract_and_normalize_verified_ad():
    now = datetime.now(timezone.utc)
    ten_days_ago = now - timedelta(days=10)

    ad_record = {
        "ad_id": "meta_123456789",
        "page_name": "Test Trader Pro",
        "ad_delivery_start_time": int(ten_days_ago.timestamp()),
        "body": "Trading indicators",
    }

    norm = extract_and_normalize_publication_date(ad_record, window_days=30)
    assert norm["date_verification_status"] == "verified"
    assert norm["published_at"] is not None
    assert norm["published_date_source"] == "ad_delivery_start_time"
    assert norm["is_within_30_days"] is True
    assert norm["age_days"] in (9, 10, 11)
    assert norm["meta_ads_url"] == "https://www.facebook.com/ads/library/?id=meta_123456789"


def test_extract_and_normalize_unverified_missing_date():
    ad_record = {
        "ad_id": "meta_no_date_123",
        "page_name": "Old Trader",
        "body": "No date information anywhere",
    }

    norm = extract_and_normalize_publication_date(ad_record, window_days=30)
    assert norm["date_verification_status"] == "unverified"
    assert norm["published_at"] is None
    assert norm["is_within_30_days"] is False
    assert norm["age_days"] is None


def test_extract_and_normalize_outside_30_day_window():
    now = datetime.now(timezone.utc)
    sixty_days_ago = now - timedelta(days=60)

    ad_record = {
        "ad_id": "meta_old_ad",
        "start_date": sixty_days_ago.isoformat(),
    }

    norm = extract_and_normalize_publication_date(ad_record, window_days=30)
    assert norm["date_verification_status"] == "verified"
    assert norm["published_at"] is not None
    assert norm["is_within_30_days"] is False
    assert norm["age_days"] >= 59


def test_extract_and_normalize_future_dated():
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    ad_record = {
        "ad_id": "meta_future_ad",
        "start_date": future.isoformat(),
    }

    norm = extract_and_normalize_publication_date(ad_record, window_days=30)
    assert norm["date_verification_status"] == "unverified"
    assert norm["published_at"] is None
    assert norm["is_within_30_days"] is False
