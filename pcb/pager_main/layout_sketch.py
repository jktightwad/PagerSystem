"""Top-down layout sketch for the combined LED + ESP32 board inside the Rev 2 ball.
Board-local coords: x right, y up, origin = ball centre; angles as in the .scad
(at_angle: 0 deg = +y, clockwise). Writes layout_sketch.svg. Numbers from
pager_rev2.scad (ball) and the agreed part sizes; positions are proposals."""
import math
S, C = 6.0, 330.0                       # px per mm, centre
def P(x, y): return C + x * S, C - y * S
def at(r, a): return r * math.sin(math.radians(a)), r * math.cos(math.radians(a))
el = []
def circle(x, y, r, stroke, fill="none", dash=None, w=1.5):
    X, Y = P(x, y); d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r*S:.1f}" stroke="{stroke}" fill="{fill}" stroke-width="{w}"{d}/>')
def rect(cx, cy, w, h, stroke, fill="none", rot=0, dash=None, sw=1.5):
    X, Y = P(cx, cy); d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<rect x="{X - w*S/2:.1f}" y="{Y - h*S/2:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}" transform="rotate({rot} {X:.1f} {Y:.1f})"{d}/>')
def label(t, x, y, size=11, color="#222"):
    X, Y = P(x, y); el.append(f'<text x="{X:.1f}" y="{Y:.1f}" font-size="{size}" text-anchor="middle" font-family="sans-serif" fill="{color}">{t}</text>')

# ---- ball (from pager_rev2.scad) ----
circle(0, 0, 49.6, "#888", w=2); label("ball inside wall r 49.6", 0, -47, 10, "#888")
circle(0, 0, 35, "#ddd", dash="4 3"); label("light pocket (70)", -25, 27, 9, "#aaa")
for a in [45, 159.5, 200.5, 315]:
    x, y = at(46.6, a); circle(x, y, 3.5, "#555", "#ddd"); label("col", x, y - 5.5, 9, "#555")
for a in [60, 300]:
    x, y = at(43, a); circle(x, y, 3, "#a33", "#f5d5d5"); label("mag", x, y - 4.5, 9, "#a33")
x, y = at(44, 180); rect(x, y, 22.4, 7.1, "#555", "#eee"); label("pogo tower", x, y + 5, 10, "#555")
x, y = at(41.4, 0); rect(x + 0.8, y, 14.6, 11, "#555", "#eee"); label("touch (under top)", x, y - 8.5, 9, "#555")

# ---- board (proposal) ----
BW, BH = 64.0, 48.0                     # rectangle; LED ring centred on the ball centre
MOD_X0, MOD_L, MOD_W, ANT = 8.0, 24.0, 18.0, 5.0   # SuperMini under, along +x, antenna end at the right edge
R_LED = 20.5
rect(0, 0, BW, BH, "#2e7d32", "#2e7d32", sw=2); el[-1] = el[-1].replace('fill="#2e7d32"', 'fill="#2e7d32" fill-opacity="0.10"')
label(f"BOARD {BW:.0f} x {BH:.0f}", -21, 21, 11, "#2e7d32")
for i in range(16):
    a = 90 + 11.25 + 22.5 * i
    x, y = at(R_LED, a); rect(x, y, 5, 5, "#e65100", "#ffe0b2", rot=a)
circle(0, 0, R_LED, "#e65100", dash="2 3", w=1)
label("16 LEDs (top)", 0, 23.5 - 2.5 - 20.5 + 14, 10, "#e65100")
rect(MOD_X0 + MOD_L / 2, 0, MOD_L, MOD_W, "#1565c0", "#bbdefb", dash="6 3")
rect(MOD_X0 + MOD_L - ANT / 2, 0, ANT, MOD_W, "#1565c0", "#90caf9", dash="2 2")
label("ESP32 (under)", MOD_X0 + 9, -6, 10, "#1565c0"); label("ant", MOD_X0 + MOD_L - ANT / 2, -1, 9, "#1565c0")
label("USB", MOD_X0 + 2.5, 6.5, 9, "#1565c0")
rect(MOD_X0 + 1 + 4.75, 0, 9.5, 9.5, "#000", "none", dash="3 2", sw=1); label("cut-out", MOD_X0 + 5.75, 2.5, 8, "#000")
rect(-14, 0, 35, 30, "#6a1b9a", "#e1bee7", dash="6 3"); label("battery 35x30 (under)", -14, -1, 10, "#6a1b9a")
rect(-2, 0, 12, 10, "#2e7d32", "none", dash="2 2"); label("SMD (top)", -2, -7, 9, "#2e7d32")
# edge parts (under), cables leave outward
circle(25.5, 17.5, 4.7, "#00695c", "#b2dfdb", dash="6 3"); label("buzzer", 25.5, 16.5, 9, "#00695c")
rect(21.0, -19.5, 12, 5.7, "#4e342e", "#d7ccc8", dash="6 3"); label("switch", 21.0, -20.5, 9, "#4e342e")
for nm, x, y, w, rot in [("touch XH", -3, 20.5, 10, 0), ("motor XH", 10, 20.5, 7.5, 0), ("dock XH", -3, -20.5, 7.5, 0)]:
    rect(x, y, w, 6.5, "#37474f", "#cfd8dc", dash="6 3", rot=rot); label(nm, x, y - 1, 8, "#37474f")

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="660" height="660" viewBox="0 0 660 660"><rect width="660" height="660" fill="#fff"/>' + "".join(el) + \
      '<text x="10" y="18" font-size="12" font-family="sans-serif" fill="#222">Top view. Solid = top side, dashed = underside. 12 o\'clock = touch, 6 o\'clock = pogo.</text></svg>'
open("layout_sketch.svg", "w").write(svg)
print("written layout_sketch.svg")
