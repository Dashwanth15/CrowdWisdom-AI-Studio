import hashlib
from pathlib import Path
from PIL import Image

backend_dir = Path(r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend")
assets_dir = backend_dir / "media" / "assets"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

images = {}
for p in assets_dir.glob("*.jpg"):
    h = md5(p)
    if h not in images:
        images[h] = []
    images[h].append(p)

print(f"Total unique JPG images in media/assets: {len(images)}")
for h, paths in sorted(images.items(), key=lambda x: len(x[1]), reverse=True):
    p0 = paths[0]
    im = Image.open(p0)
    print(f"\nHash: {h[:12]} | Count: {len(paths)} | Size: {p0.stat().st_size} bytes | Dims: {im.size} | Example: {p0.name}")

