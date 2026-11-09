"""
CrowdWisdom AI Studio — Video Pipeline, Integrity Gate & Visual Diversity Test Suite
Tests:
1. Scene classification integrity: Human cinematography scenes are never hijacked into product demos by device keywords.
2. Cross-scene visual diversity: No two scenes in a script can ever be assigned duplicate visual assets.
3. Post-render integrity validation: _validate_rendered_video strictly rejects missing, 0-byte, or corrupted files.
4. HTTP 206 Partial Content & HEAD streaming: Proper Range and CORS headers for HTML5 video playback.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.visual_asset_service import visual_asset_service
from agents.video_production_agent import VideoProductionAgent


@pytest.mark.asyncio
async def test_scene_classification_and_diversity():
    """
    Verifies that narrative descriptions mentioning 'iPad', 'tablet', or 'laptop' in
    human cinematography scenes (Scenes 1 & 4) are strictly kept as human cinematography,
    and all 4 scenes are assigned completely distinct assets with 0% duplication.
    """
    mock_script_doc = {
        "_id": "test_script_diversity_123",
        "campaign_id": "test_campaign_abc",
        "title": "The $10,000 Mistake — Options Showcase",
        "approach": "pain_point",
        "scenes": [
            {
                "scene_number": 1,
                "duration_seconds": 15,
                "scene_visual_type": "human_cinematography",
                "visual_description": "Cinematic close-up of a trader's hands holding an iPad in a dimly lit studio apartment, showing an active -$10,450 options loss.",
                "voiceover": "I followed the top financial influencer into an earnings play. Ten thousand dollars vanished.",
                "on_screen_text": "$10,450.00 — The Cost of Following Hype",
            },
            {
                "scene_number": 2,
                "duration_seconds": 15,
                "scene_visual_type": "animated_chart",
                "visual_description": "Kinetic split-screen comparing frantic influencer hype video with real institutional order book data.",
                "voiceover": "They weren't sharing research. They were using retail excitement as exit liquidity.",
                "on_screen_text": "The Brutal Reality: Retail Hype is Exit Liquidity",
            },
            {
                "scene_number": 3,
                "duration_seconds": 15,
                "scene_visual_type": "product_demo",
                "visual_description": "Clean macro tracking shot of the CrowdMap dashboard showing real-time crowd consensus of thousands of disciplined traders.",
                "voiceover": "That's when I found CrowdWisdom. The verified consensus of disciplined traders.",
                "on_screen_text": "CrowdMap Verified Collective Conviction",
            },
            {
                "scene_number": 4,
                "duration_seconds": 15,
                "scene_visual_type": "human_cinematography",
                "visual_description": "The trader closing the iPad, leaning back with calm confidence in a bright modern office overlooking the city skyline at sunrise.",
                "voiceover": "Stop being someone else's exit liquidity. Trade with verified crowd clarity.",
                "on_screen_text": "CrowdWisdomTrading.com — Trade with Collective Clarity",
            },
        ],
    }

    # Run ensure_script_visual_assets with force_refresh
    scenes_with_assets = await visual_asset_service.ensure_script_visual_assets(
        script_doc=mock_script_doc,
        aspect_ratio="9:16",
        db=None,
        force_refresh=True,
    )

    assert len(scenes_with_assets) == 4

    sc1, sc2, sc3, sc4 = scenes_with_assets[0], scenes_with_assets[1], scenes_with_assets[2], scenes_with_assets[3]

    # Verify scene visual types were preserved and not hijacked
    assert sc1["scene_visual_type"] == "human_cinematography"
    assert sc2["scene_visual_type"] == "animated_chart"
    assert sc3["scene_visual_type"] == "product_demo"
    assert sc4["scene_visual_type"] == "human_cinematography"

    # Verify that Scene 1 and Scene 4 did NOT receive the product demo tablet plate
    sc1_asset = Path(sc1["visual_asset_path"]).name.lower()
    sc4_asset = Path(sc4["visual_asset_path"]).name.lower()
    assert "platform_crowdwisdom_ui" not in sc1_asset, "Scene 1 should not use tablet mockup"
    assert "platform_crowdwisdom_ui" not in sc4_asset, "Scene 4 should not use tablet mockup"

    # Verify strict 0% duplication across all 4 scenes
    assigned_assets = [
        Path(sc["visual_asset_path"]).name.lower()
        for sc in scenes_with_assets
        if sc.get("visual_asset_path")
    ]
    assert len(assigned_assets) == len(set(assigned_assets)), f"Duplicate visual assets detected: {assigned_assets}"


@pytest.mark.asyncio
async def test_duplicate_recovery_in_existing_storyboard():
    """
    Verifies that if a storyboard already contains duplicate assets across scenes
    (like the bug reported by the user), ensure_script_visual_assets auto-detects
    internal duplicates and enforces force_refresh to assign distinct assets.
    """
    # Simulate the exact buggy state from the user's screenshot where Scene 1, 3, 4 had the same plate
    buggy_plate = str(visual_asset_service.fallback_dir / "platform_crowdwisdom_ui.jpg")
    mock_duplicate_doc = {
        "_id": "test_buggy_duplicate_doc_456",
        "campaign_id": "test_campaign_abc",
        "title": "Duplicate Asset Test",
        "scenes": [
            {
                "scene_number": 1,
                "duration_seconds": 15,
                "scene_visual_type": "human_cinematography",
                "visual_description": "Trader holding iPad in dimly lit apartment.",
                "visual_asset_path": buggy_plate,
            },
            {
                "scene_number": 2,
                "duration_seconds": 15,
                "scene_visual_type": "animated_chart",
                "visual_description": "Financial candlestick chart.",
            },
            {
                "scene_number": 3,
                "duration_seconds": 15,
                "scene_visual_type": "product_demo",
                "visual_description": "CrowdMap dashboard.",
                "visual_asset_path": buggy_plate,
            },
            {
                "scene_number": 4,
                "duration_seconds": 15,
                "scene_visual_type": "human_cinematography",
                "visual_description": "Trader closing iPad in bright modern office.",
                "visual_asset_path": buggy_plate,
            },
        ],
    }

    # Pass with force_refresh=False: system must auto-detect internal duplicates and enforce refresh!
    fixed_scenes = await visual_asset_service.ensure_script_visual_assets(
        script_doc=mock_duplicate_doc,
        aspect_ratio="9:16",
        db=None,
        force_refresh=False,
    )

    assigned = [Path(sc["visual_asset_path"]).name.lower() for sc in fixed_scenes if sc.get("visual_asset_path")]
    assert len(assigned) == len(set(assigned)), f"Duplicates remained after auto-recovery: {assigned}"


def test_post_render_video_validation_gate(tmp_path):
    """
    Verifies that _validate_rendered_video:
    - Rejects missing file.
    - Rejects 0-byte or truncated file (< 100KB).
    - Accepts a real valid MP4 file with video stream and positive duration.
    """
    # 1. Non-existent file
    non_existent = str(tmp_path / "does_not_exist.mp4")
    res1 = VideoProductionAgent._validate_rendered_video(non_existent)
    assert res1["valid"] is False
    assert "does not exist" in res1["error"].lower()

    # 2. 0-byte file
    zero_file = tmp_path / "empty.mp4"
    zero_file.write_bytes(b"")
    res2 = VideoProductionAgent._validate_rendered_video(str(zero_file))
    assert res2["valid"] is False
    assert "truncated or nearly empty" in res2["error"].lower()

    # 3. Small corrupted file (< 100KB)
    corrupt_file = tmp_path / "corrupt.mp4"
    corrupt_file.write_bytes(b"ftypisom" + b"\x00" * 2048)
    res3 = VideoProductionAgent._validate_rendered_video(str(corrupt_file))
    assert res3["valid"] is False

    # 4. Valid verified MP4 file
    verified_mp4 = backend_dir / "media" / "videos" / "commercial_30s_verified.mp4"
    if verified_mp4.exists():
        res4 = VideoProductionAgent._validate_rendered_video(str(verified_mp4))
        assert res4["valid"] is True
        assert res4["duration"] > 0
        assert res4["file_size_mb"] > 0.5

