import sys
from pathlib import Path
from PIL import Image

backend_dir = Path(r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend")
assets_dir = backend_dir / "media" / "assets"

for f in assets_dir.glob("*.jpg"):
    if f.stat().st_size > 150000:
        print(f"File: {f.name} ({f.stat().st_size // 1024} KB)")

