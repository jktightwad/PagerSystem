"""Top view of the LOLIN32 Lite (USB-C, CH340C) with each wire's stripboard hole (R=strip, C=column).
Header order read from the seller's pinout image (antenna up, components facing you, USB-C down).
    python3 lolin_wiring.py  -> lolin_wiring.png
"""
from PIL import Image, ImageDraw, ImageFont

LEFT = ["VP (36)", "VN (39)", "EN", "34", "35", "32", "33", "25", "26", "27", "14", "12", "G"]
RIGHT = ["3V", "22", "19", "23", "18", "5", "17", "16", "4", "0", "2", "15", "13"]
# pin -> (destination, colour)
WIRE = {
    "34": ("R6C1  dock sense", "orange"), "35": ("R6C9  battery sense", "orange"),
    "25": ("R2C9  motor driver", "purple"), "27": ("R2C1  buzzer driver", "purple"),
    "26": ("ring DI, 330R at the ring (direct)", "gray"),
    "3V": ("R1C5  3V3 rail", "red"), "G": ("R5C5  GND rail", "black"), "4": ("touch OUT (direct)", "gray"),
}
P = 34; BX0, BX1, TOP = 470, 760, 120
W, H = 1250, 760
img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype("DejaVuSans.ttf", 17); fb = ImageFont.truetype("DejaVuSans-Bold.ttf", 18); fs = ImageFont.truetype("DejaVuSans.ttf", 14)
except OSError:
    f = fb = fs = ImageFont.load_default()
d.text((20, 15), "LOLIN32 Lite (USB-C) - TOP view, components facing you, antenna up", font=fb, fill="black")
d.text((20, 42), "R#C# = stripboard strip (row) and column, as in stripboard.png. Check every pin against your board's silkscreen.", font=f, fill="black")
y_last = TOP + 60 + 12 * P
d.rounded_rectangle([BX0, TOP, BX1, y_last + 110], 18, fill=(30, 30, 30))
d.rectangle([BX0 + 60, TOP + 8, BX1 - 60, TOP + 40], outline=(200, 160, 60), width=3)
d.text((BX0 + 95, TOP + 12), "antenna", font=fs, fill=(200, 160, 60))
# USB-C (bottom right) and JST (bottom left)
d.rounded_rectangle([BX1 - 120, y_last + 70, BX1 - 50, y_last + 125], 8, fill=(170, 170, 170)); d.text((BX1 - 112, y_last + 88), "USB-C", font=fs, fill="black")
d.rectangle([BX0 + 40, y_last + 55, BX0 + 110, y_last + 118], fill=(235, 230, 215), outline="gray")
for k, (lab, x) in enumerate((("+", BX0 + 58), ("-", BX0 + 92))):
    d.ellipse([x - 7, y_last + 75, x + 7, y_last + 89], fill="silver", outline="black")
    d.text((x - 5, y_last + 93), lab, font=fb, fill="black")
for side, pins, x in (("L", LEFT, BX0 + 22), ("R", RIGHT, BX1 - 22)):
    for i, name in enumerate(pins):
        y = TOP + 60 + i * P
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(200, 160, 60), outline="black")
        tx = x + 16 if side == "L" else x - 16 - d.textlength(name, font=fs)
        d.text((tx, y - 8), name, font=fs, fill="white")
        if name in WIRE:
            text, col = WIRE[name]
            if side == "L":
                d.line([x - 9, y, 300, y], fill=col, width=4); tw = d.textlength(text, font=f)
                d.text((290 - tw, y - 10), text, font=f, fill=col if col != "orange" else (200, 100, 0))
            else:
                d.line([x + 9, y, 930, y], fill=col, width=4)
                d.text((940, y - 10), text, font=f, fill=col if col != "orange" else (200, 100, 0))
# JST wires
jy = y_last + 82
d.line([BX0 + 58, jy, BX0 + 58, H - 95, 300, H - 95], fill="red", width=4)
d.text((20, H - 105), "JST +  ->  R8C2  VBAT rail", font=f, fill="red")
d.line([BX0 + 92, jy, BX0 + 125, jy, BX0 + 125, H - 60, 300, H - 60], fill="black", width=4)
d.text((20, H - 70), "JST -  ->  battery - (direct)", font=f, fill="black")
d.text((780, H - 105), "Battery - goes straight to the JST -; the stripboard", font=fs, fill="black")
d.text((780, H - 85), "GND joins at the G pin. JST + = pin nearest the board", font=fs, fill="black")
d.text((780, H - 65), "edge on this silkscreen: confirm with a meter.", font=fs, fill="black")
img.save("lolin_wiring.png"); print("lolin_wiring.png", img.size)
