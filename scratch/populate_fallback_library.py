import shutil
from pathlib import Path

backend_dir = Path(r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend")
assets_dir = backend_dir / "media" / "assets"
fb_dir = assets_dir / "fallback_library"
fb_dir.mkdir(parents=True, exist_ok=True)

mappings = [
    ("test_natural_trader_scene4.jpg", "human_trader_dawn_confidence.jpg"),
    ("test_real_scene4.jpg", "human_executive_boardroom.jpg"),
    ("test_product_projection.jpg", "platform_laptop_projection.jpg"),
    ("test_product_fullscreen.jpg", "platform_fullscreen_terminal.jpg"),
    ("tech_flow_18.jpg", "environment_market_screens.jpg"),
]

for src_name, dst_name in mappings:
    src = assets_dir / src_name
    dst = fb_dir / dst_name
    if src.exists():
        shutil.copyfile(src, dst)
        print(f"Copied {src_name} -> fallback_library/{dst_name} ({dst.stat().st_size} bytes)")
    else:
        print(f"Source not found: {src_name}")

