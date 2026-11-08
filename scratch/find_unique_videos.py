import hashlib
from pathlib import Path

backend_dir = Path(r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend")

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

videos = {}
for p in backend_dir.glob("media/**/*.mp4"):
    if "videos" in str(p.parent) and "video_" in p.name:
        continue # rendered videos
    h = md5(p)
    if h not in videos:
        videos[h] = []
    videos[h].append(p)

print(f"Found {len(videos)} unique video source hashes:")
for h, paths in videos.items():
    p0 = paths[0]
    print(f"\nHash: {h} | Size: {p0.stat().st_size} bytes")
    for p in paths[:3]:
        print(f"  - {p.relative_to(backend_dir)}")
    if len(paths) > 3:
        print(f"  ... and {len(paths) - 3} more copies")

