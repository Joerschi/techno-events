#!/usr/bin/env python3
"""Erzeugt radio-cover.png (512×512) – das Bild, das beim Radio auf dem Sperrbildschirm erscheint."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HIER = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HIER)
S = 1024
FARBEN = [(57, 255, 20), (255, 16, 240), (0, 240, 255), (255, 106, 0), (244, 255, 0)]
bild = Image.new("RGBA", (S, S), (4, 2, 8, 255))
schimmer = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(schimmer)
sd.ellipse((-300, -300, 600, 500), fill=(255, 106, 0, 110)); sd.ellipse((500, 450, 1400, 1300), fill=(255, 16, 240, 110)); sd.ellipse((300, 700, 800, 1200), fill=(0, 240, 255, 60))
bild.alpha_composite(schimmer.filter(ImageFilter.GaussianBlur(120)))
for quelle, n in (((S // 2, -20), 13), ((-40, S + 40), 7), ((S + 40, S + 40), 7)):
    laser = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(laser)
    for i in range(n):
        ziel = (-200 + i * (S + 400) // (n - 1), S + 20) if quelle[1] < 0 else (i * S // (n - 1), -20)
        ld.line((quelle, ziel), fill=FARBEN[i % 5] + (170,), width=6)
    glow = laser.filter(ImageFilter.GaussianBlur(10)); bild.alpha_composite(glow); bild.alpha_composite(laser.filter(ImageFilter.GaussianBlur(1.5)))
# Schallplatte in der Mitte
d = ImageDraw.Draw(bild); c = S // 2; r = 250
d.ellipse((c - r - 14, c - r - 14, c + r + 14, c + r + 14), outline=(57, 255, 20, 255), width=8)
d.ellipse((c - r, c - r, c + r, c + r), fill=(6, 6, 8, 255))
for rr in range(r - 20, 110, -22): d.ellipse((c - rr, c - rr, c + rr, c + rr), outline=(40, 40, 50, 255), width=3)
d.arc((c - r + 40, c - r + 40, c + r - 40, c + r - 40), 200, 250, fill=(255, 255, 255, 120), width=10)
d.ellipse((c - 100, c - 100, c + 100, c + 100), fill=(255, 106, 0, 255))
for i, h in enumerate((70, 110, 90, 55)):
    x = c - 62 + i * 34; d.rectangle((x, c + 50 - h, x + 22, c + 50), fill=(0, 0, 0, 255))
d.ellipse((c - 9, c - 9, c + 9, c + 9), fill=(0, 0, 0, 255))
f = ImageFont.truetype(os.path.join(HIER, "fonts", "unbounded-latin-900-normal.woff"), 64)
txt = Image.new("RGBA", (S, S), (0, 0, 0, 0)); td = ImageDraw.Draw(txt)
td.text((c, 905), "TECHNO RADIO", font=f, fill=(255, 16, 240, 255), anchor="mm")
bild.alpha_composite(txt.filter(ImageFilter.GaussianBlur(14))); bild.alpha_composite(txt.filter(ImageFilter.GaussianBlur(14)))
ImageDraw.Draw(bild).text((c, 905), "TECHNO RADIO", font=f, fill=(255, 255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=(255, 16, 240, 255))
bild.convert("RGB").resize((512, 512), Image.LANCZOS).save(os.path.join(REPO, "radio-cover.png"), optimize=True)
print("radio-cover.png geschrieben")
