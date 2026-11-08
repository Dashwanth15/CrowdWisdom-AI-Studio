from PIL import Image, ImageDraw, ImageFont

im = Image.new("RGBA", (1080, 200), (10, 16, 28, 240))
draw = ImageDraw.Draw(im)
font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 40)

words = ["Every", "day,", "a", "million"]
# 1. Compute fixed positions using exact textbbox
space_w = 18
word_bboxes = []
cur_x = 50
text_y = 75

for w in words:
    bbox = draw.textbbox((cur_x, text_y), w, font=font)
    word_bboxes.append((w, cur_x, bbox))
    w_width = bbox[2] - bbox[0]
    cur_x += w_width + space_w

print("Calculated word positions:")
for w, x, b in word_bboxes:
    print(f"  Word '{w}': x={x}, bbox={b}, ink_w={b[2]-b[0]}, ink_h={b[3]-b[1]}")

