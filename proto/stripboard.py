"""Stripboard layout for the LOLIN32 Lite pager (docs/pager_wiring.md, current power plan: ring, buzzer, motor on 3V3).
Draws stripboard.png, seen from the COMPONENT side (strips run left-right underneath).
    python3 stripboard.py
"""
from PIL import Image, ImageDraw, ImageFont

COLS, ROWS = 22, 8
ROWNAME = {1: "VBAT rail (after switch)", 2: "3V3 rail (LOLIN 3V)", 3: "DOCK 5V | USB VBUS", 4: "DOCK_SENSE | BAT_SENSE",
           5: "GPIO27 | GPIO25", 6: "BUZ- | MOT-", 7: "Q1 base | Q2 base", 8: "GND rail"}
CUTS = [(11, r) for r in (3, 4, 5, 6, 7)]          # (column, row) holes where the strip is cut
# parts: (label, value, [(col,row), ...], colour)
PARTS = [
    ("R1", "100k", [(2, 3), (2, 4)], "tan"),
    ("R2", "100k", [(3, 4), (3, 8)], "tan"),
    ("R5", "1k", [(7, 5), (7, 7)], "tan"),
    ("Q1", "C B E", [(8, 6), (8, 7), (8, 8)], "black"),
    ("D2", "1N5819 band right", [(10, 3), (12, 3)], "dimgray"),
    ("R3", "100k", [(13, 1), (13, 4)], "tan"),
    ("R4", "100k", [(14, 4), (14, 8)], "tan"),
    ("R6", "330R", [(17, 5), (17, 7)], "tan"),
    ("Q2", "C B E", [(18, 6), (18, 7), (18, 8)], "black"),
    ("D1", "1N5819 band up", [(19, 2), (19, 6)], "dimgray"),
]
# off-board wires: (col,row,text)
WIRES = [
    (1, 3, "bottom pogo 5V (+ top pogo 5V)"), (1, 8, "pogo GND (both) / USB GND"), (4, 4, "to GPIO 34"),
    (6, 5, "from GPIO 27"), (1, 2, "touch VCC"), (2, 8, "touch GND"),
    (10, 2, "buzzer +"), (10, 6, "buzzer -"), (15, 3, "USB-C pigtail VBUS"), (12, 4, "to GPIO 35"),
    (16, 5, "from GPIO 25"), (20, 2, "motor +"), (20, 6, "motor -"),
    (21, 1, "battery + via switch (also LOLIN JST +)"), (21, 2, "LOLIN 3V pin"), (21, 8, "LOLIN G / battery -"),
    (22, 2, "ring VCC"), (22, 8, "ring GND"),
]
P, X0, Y0 = 46, 270, 120
img = Image.new("RGB", (X0 + COLS * P + 40, Y0 + ROWS * P + 200), "white")
d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype("DejaVuSans.ttf", 15); fb = ImageFont.truetype("DejaVuSans-Bold.ttf", 16); fs = ImageFont.truetype("DejaVuSans.ttf", 12)
except OSError:
    f = fb = fs = ImageFont.load_default()
def xy(c, r): return X0 + (c - 1) * P, Y0 + (r - 1) * P
d.text((20, 20), "Pager stripboard, LOLIN32 Lite build - COMPONENT side view (strips run left-right underneath)", font=fb, fill="black")
d.text((20, 45), "X = cut the strip at that hole. Cuts are on the copper side: flip the board left-right, so column 11 counts from the other end. D2 lies flat along strip 3, across the cut.", font=f, fill="black")
for c in range(1, COLS + 1):
    d.text((xy(c, 1)[0] - 6, Y0 - 34), str(c), font=fs, fill="gray")
for r in range(1, ROWS + 1):
    x0, y = xy(1, r); x1, _ = xy(COLS, r)
    d.rectangle([x0 - P / 2 + 3, y - 14, x1 + P / 2 - 3, y + 14], fill=(240, 205, 165))
    d.text((20, y - 9), f"{r}  {ROWNAME[r]}", font=f, fill="black")
    for c in range(1, COLS + 1):
        cx, cy = xy(c, r); d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill="white", outline="gray")
for c, r in CUTS:
    cx, cy = xy(c, r)
    d.line([cx - 13, cy - 13, cx + 13, cy + 13], fill="red", width=4); d.line([cx - 13, cy + 13, cx + 13, cy - 13], fill="red", width=4)
for lab, val, pins, col in PARTS:
    pts = [xy(c, r) for c, r in pins]
    d.line([pts[0], pts[-1]], fill=col, width=16 if lab[0] == "Q" else 9)
    for x, y in pts: d.ellipse([x - 6, y - 6, x + 6, y + 6], fill="silver", outline="black")
    x, y = pts[0]
    if pins[0][1] == 1: d.text((x + 10, (pts[0][1] + pts[-1][1]) / 2 - 10), lab, font=fb, fill="navy")
    else: d.text((x - 14, y - 32), lab, font=fb, fill="navy")
    yb = pts[-1][1]
    d.text((x - 16, yb + 16 + (14 if lab[0] in "RC" and pins[-1][1] == 8 else 0)), val, font=fs, fill="navy")
for c, r, t in WIRES:
    x, y = xy(c, r)
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill="limegreen", outline="darkgreen")
yy = Y0 + ROWS * P + 20
d.text((20, yy), "Green dots = wire points:", font=fb, fill="black")
for i, (c, r, t) in enumerate(WIRES):
    d.text((20 + (i % 3) * 430, yy + 26 + (i // 3) * 22), f"col {c} row {r}: {t}", font=f, fill="black")
img.save("stripboard.png")
print("stripboard.png", img.size)
