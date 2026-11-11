"""
Unit & Integration tests for Country Localization & Consistency Service.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from services.market_intelligence.country_localization_service import country_localization_service


def test_currency_formatting():
    # India numbering
    assert country_localization_service.format_currency_amount(100000, "IN") == "₹1,00,000"
    assert country_localization_service.format_currency_amount(50000, "IN") == "₹50,000"
    assert country_localization_service.format_currency_amount(10000000, "IN") == "₹1,00,00,000"
    
    # Philippines numbering
    assert country_localization_service.format_currency_amount(100000, "PH") == "₱100,000"
    assert country_localization_service.format_currency_amount(50000, "PH") == "₱50,000"


def test_india_localization_replaces_dollars():
    raw_title = "The $10,000 Mistake — Options Volatility Master"
    localized_title = country_localization_service.localize_text(raw_title, "IN")
    assert "₹1,00,000" in localized_title
    assert "$10,000" not in localized_title

    raw_hook = "A dimly lit room illuminated only by an iPad showing an active -$10,450 options loss in flashing red."
    localized_hook = country_localization_service.localize_text(raw_hook, "IN")
    assert "-₹1,00,000.00" in localized_hook or "₹1,00,000" in localized_hook
    assert "$10,450" not in localized_hook
    assert "$" not in localized_hook

    raw_vo = "I followed the top financial influencer into an earnings play. Ten thousand dollars vanished in four minutes."
    localized_vo = country_localization_service.localize_text(raw_vo, "IN")
    assert "one lakh rupees" in localized_vo
    assert "dollars" not in localized_vo.lower()

    raw_scene_visual = "Cinematic close-up of a trader's hands holding an iPad showing an active -$10,450 drawdown."
    localized_visual = country_localization_service.localize_text(raw_scene_visual, "IN")
    assert "$" not in localized_visual


def test_philippines_localization_replaces_dollars():
    raw_title = "The $10,000 Mistake — Options Volatility Master"
    localized_title = country_localization_service.localize_text(raw_title, "PH")
    assert "₱100,000" in localized_title
    assert "$" not in localized_title

    raw_hook = "A dimly lit room illuminated only by an iPad showing an active -$10,450 options loss in flashing red."
    localized_hook = country_localization_service.localize_text(raw_hook, "PH")
    assert "-₱100,000.00" in localized_hook or "₱100,000" in localized_hook
    assert "$" not in localized_hook

    raw_vo = "I followed the top financial influencer into an earnings play. Ten thousand dollars vanished in four minutes."
    localized_vo = country_localization_service.localize_text(raw_vo, "PH")
    assert "one hundred thousand pesos" in localized_vo
    assert "dollars" not in localized_vo.lower()


def test_deep_script_dict_localization_india():
    script_dict = {
        "title": "The $10,000 Mistake — Options Alpha",
        "visual_hook": "Dimly lit room with iPad showing -$10,450 loss",
        "core_message": "Following viral financial influencers cost retail traders millions on Wall Street.",
        "scenes": [
            {
                "scene_number": 1,
                "visual_description": "iPad showing -$10,450 drawdown on earnings",
                "voiceover": "Ten thousand dollars vanished in four minutes.",
                "on_screen_text": "-$10,450.00 • The Cost of Hype"
            },
            {
                "scene_number": 2,
                "visual_description": "Traders burning hours skimming forty contradictory newsletters.",
                "voiceover": "Skimming forty contradictory newsletters before 06:30 AM.",
                "on_screen_text": "06:30 AM • Pre-Market Noise"
            },
            {
                "scene_number": 3,
                "visual_description": "CrowdWisdom CrowdMap dashboard with consensus entries",
                "voiceover": "CrowdMap visualizes verified collective conviction.",
                "on_screen_text": "CrowdMap™ • Verified Conviction"
            },
            {
                "scene_number": 4,
                "visual_description": "Trader in modern office at dawn",
                "voiceover": "Trade with verified crowd clarity at CrowdWisdomTrading.com.",
                "on_screen_text": "CrowdWisdomTrading.com"
            }
        ]
    }

    localized = country_localization_service.localize_script_dict(script_dict, "IN")
    
    assert "₹1,00,000" in localized["title"]
    assert "$" not in localized["visual_hook"]
    assert "₹" in localized["visual_hook"]
    assert "Dalal Street" in localized["core_message"]
    assert "SEBI" in localized["scenes"][-1]["on_screen_text"]
    assert "09:00 AM" in localized["scenes"][1]["on_screen_text"]

    report = country_localization_service.validate_script_country_consistency(localized, "IN")
    assert report["is_consistent"] is True
    assert report["inconsistencies_count"] == 0
    assert "USD" not in report["detected_currencies"]
    assert "PHP" not in report["detected_currencies"]


def test_deep_script_dict_localization_philippines():
    script_dict = {
        "title": "The $10,000 Mistake — Alpha Trader",
        "visual_hook": "Dimly lit room with iPad showing -$10,450 loss",
        "core_message": "Following viral financial influencers cost retail traders millions on Wall Street.",
        "scenes": [
            {
                "scene_number": 1,
                "visual_description": "iPad showing -$10,450 drawdown on earnings",
                "voiceover": "Ten thousand dollars vanished in four minutes.",
                "on_screen_text": "-$10,450.00 • The Cost of Hype"
            },
            {
                "scene_number": 2,
                "visual_description": "Traders burning hours skimming forty contradictory newsletters.",
                "voiceover": "Skimming forty contradictory newsletters before 06:30 AM.",
                "on_screen_text": "06:30 AM • Pre-Market Noise"
            },
            {
                "scene_number": 3,
                "visual_description": "CrowdWisdom CrowdMap dashboard with consensus entries",
                "voiceover": "CrowdMap visualizes verified collective conviction.",
                "on_screen_text": "CrowdMap™ • Verified Conviction"
            },
            {
                "scene_number": 4,
                "visual_description": "Trader in modern office at dawn",
                "voiceover": "Trade with verified crowd clarity at CrowdWisdomTrading.com.",
                "on_screen_text": "CrowdWisdomTrading.com"
            }
        ]
    }

    localized = country_localization_service.localize_script_dict(script_dict, "PH")
    
    assert "₱100,000" in localized["title"]
    assert "$" not in localized["visual_hook"]
    assert "₱" in localized["visual_hook"]
    assert "Philippine Stock Exchange" in localized["core_message"]
    assert "SEC Philippines" in localized["scenes"][-1]["on_screen_text"]
    assert "unverified Facebook stock rumors" in localized["scenes"][1]["voiceover"]

    report = country_localization_service.validate_script_country_consistency(localized, "PH")
    assert report["is_consistent"] is True
    assert report["inconsistencies_count"] == 0
    assert "USD" not in report["detected_currencies"]
    assert "INR" not in report["detected_currencies"]

