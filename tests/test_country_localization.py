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


def test_nse_sebi_leak_detection_in_philippines():
    """Verify that NSE, BSE, Bank Nifty, and SEBI terms are flagged as inconsistencies in PH."""
    bad_ph_script = {
        "title": "The Noise Trap — NSE Blue Chip & Dividend Alpha — Philippines 🇵🇭",
        "core_message": "Trading on Bank Nifty volatility requires SEBI compliance.",
        "scenes": [
            {
                "scene_number": 1,
                "visual_description": "Close-up macro of trader hands typing rapidly",
                "voiceover": "Market makers love retail chaos on the NSE.",
                "on_screen_text": "NSE Volatility Alert"
            },
            {
                "scene_number": 2,
                "visual_description": "Trader in modern glass office",
                "voiceover": "Institutional capital uses Demat accounts.",
                "on_screen_text": "SEBI Compliant Research"
            }
        ]
    }
    report = country_localization_service.validate_script_country_consistency(bad_ph_script, "PH")
    assert report["is_consistent"] is False
    assert report["inconsistencies_count"] >= 3
    issues = [item["snippet"] for item in report["inconsistencies"]]
    assert any("NSE" in snip for snip in issues)
    assert any("SEBI" in snip for snip in issues)


def test_cinematic_prompt_macro_separation():
    """Verify that macro scenes of hands/keyboards do not inject persona facial descriptions."""
    from services.visual_asset_service import visual_asset_service

    vis_desc = "Close-up macro of an intense trader's hands typing rapidly at a trading workstation amidst flashing sell-off candlestick monitors"
    prompt = visual_asset_service._construct_cinematic_prompt(
        scene_num=1,
        vis_desc=vis_desc,
        is_product_demo=False,
        approach="pain_point",
        aspect_ratio="9:16",
        campaign_id="test_camp_ph",
        target_country="PH",
    )
    # Must NOT contain facial portrait persona
    assert "portraying" not in prompt
    assert "eyes" not in prompt
    assert "calculating eyes" not in prompt
    # Must contain macro focusing tokens
    assert "hands typing rapidly on mechanical keyboard" in prompt
    assert "no human faces visible" in prompt


def test_philippines_regulatory_disclaimer():
    """Verify that regulatory disclaimer for PH does NOT falsely claim SEC compliance or approval."""
    script_dict = {
        "title": "PSE Alpha",
        "scenes": [
            {
                "scene_number": 1,
                "visual_description": "Makati office view",
                "voiceover": "Trade with data",
                "on_screen_text": "CrowdWisdomTrading.com"
            }
        ]
    }
    localized = country_localization_service.localize_script_dict(script_dict, "PH")
    final_ost = localized["scenes"][-1]["on_screen_text"]
    assert "SEC Philippines Disclosures Apply" in final_ost
    assert "SEC Philippines Approved" not in final_ost
    assert "SEC Philippines Compliance." not in final_ost


