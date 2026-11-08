import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

f_title = get_font(52, bold=True)
f_sub = get_font(32, bold=False)
f_act = get_font(40, bold=True)
f_word = get_font(36, bold=False)

print("Title font:", f_title.getname() if hasattr(f_title, "getname") else "default")
print("Sub font:", f_sub.getname() if hasattr(f_sub, "getname") else "default")

