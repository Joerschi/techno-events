#!/usr/bin/env python3
"""Erzeugt vorschau.png – das kleine Link-Vorschaubild (WhatsApp & Co.) für die aktuelle Ausgabe.

Aufruf im Repository-Ordner:  python3 tools/vorschau.py
Braucht Pillow (pip install pillow). Liest events.json, schreibt vorschau.png (256×256).
"""
import datetime
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HIER)
FONT_TITEL = os.path.join(HIER, "fonts", "unbounded-latin-900-normal.woff")
FONT_MONO = os.path.join(HIER, "fonts", "space-mono-latin-700-normal.woff")
MONATE = ["JAN", "FEB", "MÄR", "APR", "MAI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEZ"]
S = 512          # intern doppelt so gross zeichnen, am Ende verkleinern (schärfer)
AUS = 256        # klein halten → WhatsApp zeigt die kompakte Vorschau

ACID, PINK, CYAN, ORANGE, GELB = (57, 255, 20), (255, 16, 240), (0, 240, 255), (255, 106, 0), (244, 255, 0)


def wochenende_von(datum):
    """Freitag des Wochenendes, zu dem ein Datum gehört (Do-Nacht zählt zum folgenden Fr)."""
    d = datetime.date.fromisoformat(datum)
    versatz = {3: 1, 4: 0, 5: -1, 6: -2, 0: -3, 1: -4, 2: -5}[d.weekday()]
    return d + datetime.timedelta(days=versatz)


def schrift(pfad, groesse):
    return ImageFont.truetype(pfad, groesse)


def passend(draw, text, pfad, start, max_breite):
    g = start
    while g > 10:
        f = schrift(pfad, g)
        if draw.textlength(text, font=f) <= max_breite:
            return f
        g -= 2
    return schrift(pfad, 10)


def neon(bild, xy, text, font, farbe, anker="mm", blur=10, staerke=2):
    """Text mit Neon-Leuchten: weichgezeichnete Farbschicht + weisser Kern."""
    glow = Image.new("RGBA", bild.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text(xy, text, font=font, fill=farbe + (255,), anchor=anker)
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    for _ in range(staerke):
        bild.alpha_composite(glow)
    d = ImageDraw.Draw(bild)
    d.text(xy, text, font=font, fill=(255, 255, 255, 255), anchor=anker, stroke_width=2, stroke_fill=farbe + (255,))


def main():
    with open(os.path.join(REPO, "events.json"), encoding="utf-8") as f:
        daten = json.load(f)
    events = [e for e in daten.get("events", []) if e.get("datum")]
    if not events:
        print("Keine Events – vorschau.png bleibt unverändert")
        return 0
    erstes = min(wochenende_von(e["datum"]) for e in events)
    n = sum(1 for e in events if wochenende_von(e["datum"]) == erstes)
    so = erstes + datetime.timedelta(days=2)
    if erstes.month == so.month:
        zeile1 = f"{erstes.day}.–{so.day}. {MONATE[so.month - 1]}"
    else:
        zeile1 = f"{erstes.day}.{erstes.month}.–{so.day}.{so.month}."

    bild = Image.new("RGBA", (S, S), (6, 3, 12, 255))
    farben = [ACID, PINK, CYAN, ORANGE, GELB]
    # Farbschimmer hinter dem DJ
    schimmer = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(schimmer)
    sd.ellipse((S * .1, S * .05, S * .9, S * .75), fill=PINK + (120,))
    sd.ellipse((-S * .3, S * .3, S * .4, S * 1.1), fill=CYAN + (70,))
    sd.ellipse((S * .6, S * .3, S * 1.3, S * 1.1), fill=ORANGE + (70,))
    bild.alpha_composite(schimmer.filter(ImageFilter.GaussianBlur(70)))
    # Laser-Fächer von hinter dem Pult
    laser = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(laser)
    for i in range(15):
        ld.line((S // 2, int(S * .48), -S * .4 + i * S * 1.8 / 14, -10), fill=farben[i % 5] + (150,), width=4)
    bild.alpha_composite(laser.filter(ImageFilter.GaussianBlur(6))); bild.alpha_composite(laser.filter(ImageFilter.GaussianBlur(1)))
    d = ImageDraw.Draw(bild)
    schwarz = (4, 2, 8, 255)
    # DJ-Silhouette: Kopf mit Kopfhörern, Schultern, ein Arm hoch
    cx = S // 2
    d.ellipse((cx - 34, 150, cx + 34, 222), fill=schwarz)                       # Kopf
    d.arc((cx - 46, 140, cx + 46, 220), 180, 360, fill=schwarz, width=10)        # Kopfhörer-Bügel
    d.ellipse((cx - 52, 172, cx - 30, 206), fill=schwarz); d.ellipse((cx + 30, 172, cx + 52, 206), fill=schwarz)
    d.polygon([(cx - 95, 330), (cx - 70, 240), (cx - 30, 222), (cx + 30, 222), (cx + 70, 240), (cx + 95, 330)], fill=schwarz)   # Oberkörper
    d.line((cx + 62, 245, cx + 120, 150), fill=schwarz, width=26); d.ellipse((cx + 104, 118, cx + 140, 156), fill=schwarz)   # Arm hoch
    d.line((cx - 62, 248, cx - 110, 300), fill=schwarz, width=24)               # Hand am Mixer
    # Pult mit Plattentellern
    d.rectangle((40, 300, S - 40, 372), fill=(14, 10, 20, 255), outline=ACID + (255,), width=4)
    for x0 in (70, S - 70 - 120):
        d.ellipse((x0, 306, x0 + 120, 366), fill=(8, 8, 12, 255), outline=CYAN + (255,), width=3)
        d.ellipse((x0 + 44, 324, x0 + 76, 348), fill=PINK + (255,) if x0 < S // 2 else ORANGE + (255,))
    d.rectangle((cx - 40, 312, cx + 40, 360), fill=(20, 16, 28, 255), outline=ORANGE + (255,), width=3)
    for i in range(3):
        d.ellipse((cx - 30 + i * 22, 318, cx - 18 + i * 22, 330), outline=GELB + (255,), width=2)
    # Glow an den Kanten des Pults
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(glow).rectangle((40, 300, S - 40, 372), outline=ACID + (255,), width=8)
    bild.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    # Crowd-Silhouetten mit Händen in der Luft
    d = ImageDraw.Draw(bild)
    for i, x in enumerate(range(-10, S + 40, 46)):
        h = 395 + (i * 37 % 30)
        d.ellipse((x - 18, h - 18, x + 18, h + 18), fill=schwarz)
        d.rectangle((x - 26, h + 10, x + 26, S), fill=schwarz)
        if i % 2 == 0:
            d.line((x + 16, h + 14, x + 34, h - 40), fill=schwarz, width=12); d.ellipse((x + 26, h - 52, x + 42, h - 36), fill=schwarz)
        if i % 3 == 1:
            d.line((x - 16, h + 14, x - 36, h - 34), fill=schwarz, width=12); d.ellipse((x - 44, h - 46, x - 28, h - 30), fill=schwarz)
    # Texte: oben klein, unten Wochenende & Anzahl
    f_kopf = schrift(FONT_MONO, 30)
    neon(bild, (S // 2, 50), "TECHNO EVENTS", f_kopf, ACID, blur=8, staerke=1)
    leiste = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(leiste).rectangle((0, S - 92, S, S), fill=(0, 0, 0, 200))
    bild.alpha_composite(leiste)
    text = "PARTY PEOPLE"
    f_unten = passend(ImageDraw.Draw(bild), text, FONT_TITEL, 58, S - 60)
    neon(bild, (S // 2, S - 46), text, f_unten, PINK, blur=10)

    bild = bild.convert("RGB").resize((AUS, AUS), Image.LANCZOS)
    ziel = os.path.join(REPO, "vorschau.png")
    bild.save(ziel, optimize=True)
    print(f"vorschau.png: {zeile1} · {n} Events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
