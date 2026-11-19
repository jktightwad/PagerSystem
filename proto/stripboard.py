"""Stripboard layout for the pager driver circuits (same parts/nets as pcb/pager_main/design_main.py).
Draws stripboard.png, seen from the COMPONENT side (strips run left-right underneath).
    python3 stripboard.py
"""
from PIL import Image, ImageDraw, ImageFont

COLS, ROWS = 28, 8
ROWNAME = {1: "VBAT rail", 2: "3V3 rail", 3: "DOCK 5V", 4: "DOCK_SENSE | BAT_SENSE",
           5: "BUZ_IO | MOT_IO", 6: "BUZ- | MOT-", 7: "BUZ_G | MOT_G", 8: "GND rail"}
CUTS = [(14, r) for r in (3, 4, 5, 6, 7)]          # (column, row) holes where the strip is cut
# parts: (label, value, [(col,row), ...], colour)
PARTS = [
    ("R8", "100k", [(3, 3), (3, 4)], "tan"),
    ("R9", "100k", [(4, 4), (4, 8)], "tan"),
    ("C2", "100n", [(5, 4), (5, 8)], "gold"),
    ("R1", "330R", [(9, 5), (9, 7)], "tan"),
    ("R2", "100k", [(10, 7), (10, 8)], "tan"),
    ("Q1", "D G S", [(11, 6), (11, 7), (11, 8)], "black"),
    ("R6", "100k", [(16, 1), (16, 4)], "tan"),
    ("R7", "100k", [(17, 4), (17, 8)], "tan"),
    ("C1", "100n", [(18, 4), (18, 8)], "gold"),
    ("R3", "330R", [(21, 5), (21, 7)], "tan"),
    ("R4", "100k", [(22, 7), (22, 8)], "tan"),
    ("Q2", "D G S", [(23, 6), (23, 7), (23, 8)], "black"),
    ("D1", "B5819 band up", [(24, 1), (24, 6)], "dimgray"),
    ("C3", "47u + up", [(26, 1), (26, 8)], "steelblue"),
]
# off-board wires: (col,row,text)
WIRES = [
    (2, 3, "dock J2 5V"), (1, 8, "ESP GND"), (6, 4, "to GP1"), (8, 5, "from GP12"),
    (13, 1, "buzzer +"), (13, 6, "buzzer -"), (15, 4, "to GP2"), (20, 5, "from GP13"),
    (25, 1, "motor +"), (25, 6, "motor -"), (27, 1, "VBAT in (switch ON / ESP B+)"),
    (28, 8, "battery - / ESP B-"), (27, 2, "ESP 3V3"), (28, 2, "touch 3V3"), (2, 8, "touch / dock GND"),
]
P, X0, Y0 = 46, 270, 120
img = Image.new("RGB", (X0 + COLS * P + 40, Y0 + ROWS * P + 200), "white")
d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype("DejaVuSans.ttf", 15); fb = ImageFont.truetype("DejaVuSans-Bold.ttf", 16); fs = ImageFont.truetype("DejaVuSans.ttf", 12)
except OSError:
    f = fb = fs = ImageFont.load_default()
def xy(c, r): return X0 + (c - 1) * P, Y0 + (r - 1) * P
d.text((20, 20), "Pager driver stripboard - COMPONENT side view (strips run left-right underneath)", font=fb, fill="black")
d.text((20, 45), "X = cut the strip at that hole. Cuts are on the copper side: flip the board left-right, so column 14 counts from the other end.", font=f, fill="black")
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
    d.line([pts[0], pts[-1]], fill=col, width=9 if lab[0] != "Q" else 16)
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
