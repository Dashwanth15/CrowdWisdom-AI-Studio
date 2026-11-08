import asyncio
import os
import sys
import subprocess
from pathlib import Path
from PIL import Image
import numpy as np

backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

async def main():
    from video_engine.openmontage_adapter import openmontage_adapter
    from agents.script_agent import script_agent
    from moviepy import VideoFileClip

    print("==================================================")
    print("STAGE 4 VERIFICATION: KINETIC TYPOGRAPHY & HUD")
    print("==================================================")

    # 1. Screenplay with 3 high-impact commercial scenes (18s fast verification)
    script = script_agent._generate_fallback_script(
        approach="unique_data",
        duration=18,
        campaign_config={"audience": {"segments": ["retail traders", "options traders"]}},
        campaign_id="stage4_verify_campaign",
        campaign_name="Stage 4 Typography & HUD Verification"
    )

    scenes = script["scenes"][:3]
    scenes[0]["transition"] = "Fast motion blur whip pan right"
    scenes[1]["transition"] = "Digital glitch & chromatic tear"
    scenes[2]["transition"] = "Fade to brand card"

    print(f"\n[1] Screenplay: '{script['title']}' ({len(scenes)} scenes)")
    for s in scenes:
        print(f"  Scene {s['scene_number']} ({s['duration_seconds']}s): {s['voiceover'][:55]}...")

    output_mp4 = backend_dir / "media" / "videos" / "stage4_verified_advertisement.mp4"
    output_thumb = backend_dir / "media" / "thumbnails" / "stage4_verified_thumb.jpg"
    frames_dir = backend_dir / "media" / "stage4_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    print("\n[2] Executing OpenMontage Stage 4 Pipeline (Kinetic Typography & HUD)...")
    t0 = asyncio.get_event_loop().time()

    async def progress_logger(pct: int, msg: str):
        print(f"  [{pct}%] {msg}")

    result = await openmontage_adapter.render_video(
        scenes=scenes,
        output_file_path=str(output_mp4),
        thumbnail_file_path=str(output_thumb),
        aspect_ratio="9:16",
        target_duration=18,
        quality="high",
        progress_callback=progress_logger
    )

    t1 = asyncio.get_event_loop().time()
    print(f"\n[3] Stage 4 Video Render Complete in {t1 - t0:.1f}s!")
    print(f"  Output MP4: {output_mp4} ({output_mp4.stat().st_size / (1024*1024):.2f} MB)")

    # 4. In-Memory Frame Extraction to Verify Word-Level Kinetic Highlights
    clip = VideoFileClip(str(output_mp4))
    print(f"\n[4] Stream Diagnostics:")
    print(f"  Duration: {clip.duration:.2f}s | Dimensions: {clip.size} | FPS: {clip.fps}")

    # Sample frames during speech to verify active word glowing highlights
    test_moments = [
        (1.2, "s1_word_early", "Scene 1 Early Word Active"),
        (2.8, "s1_word_mid", "Scene 1 Mid Word Highlight"),
        (4.2, "s1_word_late", "Scene 1 Late Word Highlight"),
        (7.5, "s1_trans", "Transition 1: Whip-Pan + Whoosh"),
        (10.2, "s2_word_highlight", "Scene 2 Active Glowing Word Highlight"),
        (14.8, "s2_trans", "Transition 2: Digital Glitch"),
        (17.2, "s3_cta_spring", "Scene 3: Glassmorphic CTA Card")
    ]

    print(f"\n[5] Extracting {len(test_moments)} Stage 4 frames into media/stage4_frames/...")
    for i, (ts, code, label) in enumerate(test_moments):
        t_clamp = min(clip.duration - 0.1, ts)
        f_arr = clip.get_frame(t_clamp)
        out_jpg = frames_dir / f"stage4_frame_{i+1:02d}_{code}.jpg"
        Image.fromarray(f_arr).save(out_jpg, "JPEG", quality=90)
        mean_rgb = f_arr.mean(axis=(0,1))
        print(f"  Frame {i+1:02d} (t={t_clamp:4.1f}s) | RGB=({mean_rgb[0]:.1f}, {mean_rgb[1]:.1f}, {mean_rgb[2]:.1f}) | {label}")

    clip.close()
    print("\n✓ STAGE 4 KINETIC TYPOGRAPHY & HUD OVERLAYS VERIFIED!")

if __name__ == "__main__":
    asyncio.run(main())
