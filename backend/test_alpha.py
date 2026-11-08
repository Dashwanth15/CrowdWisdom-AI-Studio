from PIL import Image
a = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
b = Image.new("RGBA", (100, 100), (56, 189, 248, 50))
c = Image.alpha_composite(a, b)
print("alpha_composite alpha:", c.getpixel((50, 50))[3], "RGB:", c.getpixel((50, 50))[:3])
a.paste(b, (0, 0), b)
print("paste alpha:", a.getpixel((50, 50))[3], "RGB when converted to RGB:", a.convert("RGB").getpixel((50, 50)))

