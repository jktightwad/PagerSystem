"""Stripboard layout for the LOLIN32 Lite pager (docs/pager_wiring.md, current power plan: ring, buzzer, motor on 3V3).
Draws stripboard.png, seen from the COMPONENT side (strips run left-right underneath).
    python3 stripboard.py
"""
from PIL import Image, ImageDraw, ImageFont

COLS, ROWS = 9, 8
ROWNAME = {1: "3V3 rail (LOLIN 3V)", 2: "GPIO27 | GPIO25", 3: "BUZ- | MOT-", 4: "Q1 base | Q2 base",
           5: "GND rail", 6: "DOCK_SENSE | BAT_SENSE", 7: "DOCK 5V | USB VBUS", 8: "VBAT rail (after switch)"}
CUTS = [(5, r) for r in (2, 3, 4, 6, 7)]          # (column, row) holes where the strip is cut
# parts: (label, value, [(col,row), ...], colour)
PARTS = [
    ("R5", "1k", [(2, 2), (2, 4)], "tan"),
    ("R1", "100k", [(2, 7), (2, 6)], "tan"),
    ("Q1", "C B E", [(3, 3), (3, 4), (3, 5)], "black"),
    ("R2", "100k", [(4, 6), (4, 5)], "tan"),
    ("D2", "1N5819 band right", [(4, 7), (6, 7)], "dimgray"),
    ("Q2", "C B E", [(6, 3), (6, 4), (6, 5)], "black"),
    ("R6", "330R", [(7, 2), (7, 4)], "tan"),
    ("R3", "100k", [(7, 8), (7, 6)], "tan"),
    ("D1", "band up", [(8, 1), (8, 3)], "dimgray"),
    ("R4", "100k", [(8, 6), (8, 5)], "tan"),
]
# off-board wires: (col,row,text)
WIRES = [
    (1, 1, "touch VCC"), (4, 1, "buzzer +"), (5, 1, "LOLIN 3V pin"), (6, 1, "ring VCC"), (9, 1, "motor +"),
    (1, 2, "from GPIO 27"), (9, 2, "from GPIO 25"),
    (1, 3, "buzzer -"), (9, 3, "motor -"),
    (1, 5, "pogo GND (top + bottom joined at the pogos)"), (5, 5, "LOLIN G / battery -"), (7, 5, "touch GND"), (9, 5, "ring GND"),
    (1, 6, "to GPIO 34"), (9, 6, "to GPIO 35"),
    (1, 7, "pogo 5V (top + bottom joined at the pogos)"), (9, 7, "USB-C pigtail VBUS"),
    (1, 8, "battery + via switch (also LOLIN JST +)"),
]
P, X0, Y0 = 56, 270, 120
img = Image.new("RGB", (max(X0 + COLS * P + 40, 1300), Y0 + ROWS * P + 230), "white")
d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype("DejaVuSans.ttf", 15); fb = ImageFont.truetype("DejaVuSans-Bold.ttf", 16); fs = ImageFont.truetype("DejaVuSans.ttf", 12)
except OSError:
    f = fb = fs = ImageFont.load_default()
def xy(c, r): return X0 + (c - 1) * P, Y0 + (r - 1) * P
d.text((20, 20), "Pager stripboard 9 x 8, LOLIN32 Lite - COMPONENT side", font=fb, fill="black")
d.text((20, 45), "X = cut the strip at that hole. Cuts are on the copper side: flip the board left-right, so column 5 is still the middle. D2 bridges the cut on strip 7.", font=f, fill="black")
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
    xs = [x for x, _ in pts]; ys = [y for _, y in pts]
    if len(set(ys)) == 1:      # lying along a strip: label below
        d.text((min(xs), ys[0] + 14), f"{lab} {val}", font=fs, fill="navy")
    else:
        d.text((xs[0] + 10, min(ys) + 4), lab, font=fb, fill="navy")
        d.text((xs[0] + 10, min(ys) + 22), val, font=fs, fill="navy")
for c, r, t in WIRES:
    x, y = xy(c, r)
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill="limegreen", outline="darkgreen")
yy = Y0 + ROWS * P + 20
d.text((20, yy), "Green dots = wire points:", font=fb, fill="black")
for i, (c, r, t) in enumerate(WIRES):
    d.text((20 + (i % 3) * 430, yy + 26 + (i // 3) * 22), f"col {c} row {r}: {t}", font=f, fill="black")
img.save("stripboard.png")
print("stripboard.png", img.size)
