import os
from PIL import Image

for name in ["scene_1_6s.jpg", "scene_2_18s.jpg", "scene_3_30s.jpg", "scene_4_41s.jpg"]:
    if os.path.exists(name):
        im = Image.open(name)
        print(f"{name}: size={im.size}, mode={im.mode}")
    else:
        print(f"{name}: not found")

