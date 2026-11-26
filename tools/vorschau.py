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

    bild = Image.new("RGBA", (S, S), (6, 4, 10, 255))
    d = ImageDraw.Draw(bild)
    # Hintergrund: Laserfächer + Farbschimmer
    schimmer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(schimmer)
    sd.ellipse((-160, -200, 300, 220), fill=ORANGE + (90,))
    sd.ellipse((260, 200, 700, 640), fill=PINK + (80,))
    schimmer = schimmer.filter(ImageFilter.GaussianBlur(70))
    bild.alpha_composite(schimmer)
    laser = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(laser)
    farben = [ACID, PINK, CYAN, ORANGE, GELB]
    for i in range(11):
        ld.line((S // 2, -10, -120 + i * 75, S + 10), fill=farben[i % 5] + (110,), width=3)
    laser = laser.filter(ImageFilter.GaussianBlur(1.2))
    bild.alpha_composite(laser)
    # untere Hälfte abdunkeln, damit der Text knallt
    dunkel = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dunkel)
    for y in range(S):
        a = int(max(0, (y - S * .25) / (S * .75)) * 200)
        dd.line((0, y, S, y), fill=(0, 0, 0, a))
    bild.alpha_composite(dunkel)
    # Equalizer unten
    for i in range(16):
        h = 18 + ((i * 37 + n * 13) % 70)
        d.rectangle((24 + i * 29, S - 26 - h, 24 + i * 29 + 18, S - 26), fill=(farben[i % 5] + (150,)))

    # Texte
    f_kopf = schrift(FONT_MONO, 30)
    neon(bild, (S // 2, 62), "TECHNO EVENTS", f_kopf, ACID, blur=8, staerke=1)
    f_datum = passend(d, zeile1, FONT_TITEL, 86, S - 50)
    neon(bild, (S // 2, 210), zeile1, f_datum, PINK, blur=14)
    f_zahl = schrift(FONT_TITEL, 120)
    f_events = schrift(FONT_MONO, 40)
    bz, be = d.textlength(str(n), font=f_zahl), d.textlength("EVENTS", font=f_events)
    x0 = (S - (bz + 16 + be)) / 2
    neon(bild, (x0, 335), str(n), f_zahl, GELB, anker="lm", blur=16)
    ImageDraw.Draw(bild).text((x0 + bz + 16, 335), "EVENTS", font=f_events, fill=CYAN + (255,), anchor="lm")

    bild = bild.convert("RGB").resize((AUS, AUS), Image.LANCZOS)
    ziel = os.path.join(REPO, "vorschau.png")
    bild.save(ziel, optimize=True)
    print(f"vorschau.png: {zeile1} · {n} Events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
