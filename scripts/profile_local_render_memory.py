"""
Test local memory profile of openmontage_adapter.render_video
"""
import asyncio
import os
import time
import tracemalloc
from pathlib import Path
from services.memory_monitor import get_process_memory_mb, release_system_memory
from video_engine.openmontage_adapter import openmontage_adapter

async def main():
    print("=" * 60)
    print("LOCAL VIDEO RENDERING MEMORY PROFILER")
    print("=" * 60)
    
    release_system_memory()
    m0 = get_process_memory_mb()["rss_mb"]
    print(f"Initial RSS: {m0:.2f} MB")
    
    # 4 scenes
    scenes = [
        {
            "scene_number": 1,
            "duration_seconds": 7.5,
            "visual_asset_path": "media/assets/fallback_library/human_dawn_workstation.jpg",
            "media_type": "ai_image",
            "voiceover": "I followed the top financial influencer into an earnings play. Ten thousand dollars vanished.",
            "on_screen_text": "The $10,000 Mistake",
            "transition": "digital_glitch",
        },
        {
            "scene_number": 2,
            "duration_seconds": 7.5,
            "visual_asset_path": None,
            "media_type": "animated_chart",
            "chart_theme": "sentiment_divergence",
            "voiceover": "They were not sharing research. They were using retail excitement as exit liquidity.",
            "on_screen_text": "Retail Hype Is Exit Liquidity",
            "transition": "zoom_punch",
        },
        {
            "scene_number": 3,
            "duration_seconds": 7.5,
            "visual_asset_path": "media/assets/fallback_library/platform_crowdwisdom_ui.jpg",
            "media_type": "product_demo",
            "product_demo_mode": "fullscreen",
            "voiceover": "That is when I found CrowdWisdom. Not one person opinion, but verified consensus.",
            "on_screen_text": "Verified Collective Conviction",
            "transition": "optical_bloom",
        },
        {
            "scene_number": 4,
            "duration_seconds": 7.5,
            "visual_asset_path": "media/assets/fallback_library/human_dawn_workstation.jpg",
            "media_type": "ai_image",
            "voiceover": "Stop being someone else exit liquidity. Trade with clarity at CrowdWisdomTrading.com",
            "on_screen_text": "CrowdWisdomTrading.com",
            "transition": "luma_dissolve",
        },
    ]

    out_mp4 = Path("media/videos/test_profile_30s.mp4")
    out_thumb = Path("media/thumbnails/test_profile_30s.jpg")
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    out_thumb.parent.mkdir(parents=True, exist_ok=True)

    peak_rss = m0
    
    def on_progress(pct, msg):
        nonlocal peak_rss
        curr = get_process_memory_mb()["rss_mb"]
        if curr > peak_rss:
            peak_rss = curr
        print(f"[{pct}%] {msg} | Current RSS: {curr:.1f} MB (Peak: {peak_rss:.1f} MB)", flush=True)

    t0 = time.time()
    res = await openmontage_adapter.render_video(
        scenes=scenes,
        output_file_path=str(out_mp4),
        thumbnail_file_path=str(out_thumb),
        aspect_ratio="9:16",
        target_duration=30,
        quality="high",
        progress_callback=on_progress
    )
    t_dur = time.time() - t0
    
    release_system_memory()
    m_final = get_process_memory_mb()["rss_mb"]
    print("-" * 60)
    print(f"Render completed in {t_dur:.1f}s")
    print(f"Initial RSS: {m0:.1f} MB")
    print(f"Peak RSS:    {peak_rss:.1f} MB")
    print(f"Final RSS:   {m_final:.1f} MB")
    print(f"Net Delta:   {m_final - m0:+.1f} MB")
    print(f"Output File: {res['output_path']} ({res['file_size_mb']} MB, {res['duration_seconds']}s)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
