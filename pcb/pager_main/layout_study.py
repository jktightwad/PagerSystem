"""Layout study for the combined board: 16 LEDs on top, ESP32-S3 SuperMini underneath.

Each variant is a list of parts placed in board coordinates (mm, x right, y up,
origin = LED ring centre). The checker reports overlaps:
  - bodies on the same side (top / bottom),
  - through-hole pins against anything on either side (incl. the LED ring),
  - holes (cut-out, mounting) against everything,
  - parts outside the board outline,
and draws each variant (top side solid, underside dashed) to variant_<name>.svg/.png.

Sizes are from the datasheets / footprints we chose; positions are proposals.
"""
import math, json
from shapely.geometry import Point, Polygon, box
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

R_LED, N_LED, R_CAP = 20.5, 16, 16.4
LED_FP = (6.6, 5.2)          # LED 5050 incl. pads (tangential x radial)
CAP_FP = (3.0, 1.5)          # 0603 courtyard
SM_L, SM_W, ANT = 24.0, 18.0, 5.0
ROW_IN = 1.375               # SuperMini pin row from its edge
PIN_X0, PITCH = 1.75, 2.54   # first pin from the USB end
CUT = 9.5                    # cut-out under the module's bottom parts, from 1 mm off the USB end
XH = {2: (8.4, 12.5), 3: (10.9, 12.5)}   # right-angle XH courtyard (along pins x depth)
XH_BACK = 2.8                # courtyard behind the pin row (front = depth - back)
PLUG = 8.0                   # room in front of an XH for the plug (unless it is off the board edge)
SW_BODY = (12.0, 5.7)        # SS12F44 body
MH_KEEP = 2.2                # screw head radius (copper / parts keep-out)
PIN_CLR = 0.5                # through-hole pin pad radius-ish margin


def rect(cx, cy, w, h, rot=0):
    return rotate(box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), rot, origin=(cx, cy))


def led_ring(skip_cap_angles=(), beside=False, avoid=None):
    """caps between LEDs (old) or beside each LED on the inside (beside=True); a cap that would land
    in `avoid` (e.g. the cut-out) goes into the gap after its LED instead"""
    leds, caps = [], []
    for i in range(N_LED):
        a = 11.25 + 22.5 * i
        x, y = R_LED * math.cos(math.radians(a)), R_LED * math.sin(math.radians(a))
        leds.append(rect(x, y, *LED_FP, rot=a - 90))
        if beside:
            ca, rc = a, R_LED - LED_FP[1] / 2 - CAP_FP[1] / 2 - 0.3
            g = rect(rc * math.cos(math.radians(ca)), rc * math.sin(math.radians(ca)), *CAP_FP, rot=ca - 90)
            if avoid is None or not g.intersects(avoid.buffer(0.3)):
                caps.append(g); continue
        ca = a + 11.25
        if any(abs(((ca - s + 180) % 360) - 180) < 1 for s in skip_cap_angles):
            ca = a - 11.25
        cx, cy = R_CAP * math.cos(math.radians(ca)), R_CAP * math.sin(math.radians(ca))
        caps.append(rect(cx, cy, *CAP_FP, rot=ca - 90))
    return leds, caps


class Layout:
    def __init__(self, name, board, note=""):
        self.name, self.board, self.note = name, board, note
        self.items = []          # (label, side, geom, kind)  side: top/bottom/both ; kind: body/pins/hole/pads
        self.extra = []          # drawing only (off-board battery etc.)

    def add(self, label, side, geom, kind="body"):
        self.items.append((label, side, geom, kind)); return self

    # ---- parts ----
    def leds(self, skip_cap_angles=(0,), beside=False, avoid=None):
        leds, caps = led_ring(skip_cap_angles, beside, avoid)
        for k, g in enumerate(leds): self.add(f"LED{k+1}", "top", g)
        for k, g in enumerate(caps): self.add("cap", "top", g)
        return self

    def supermini(self, usb_x, axis="+x", cut_from=1.0):
        """module under the board along +x: USB end at usb_x, antenna end at usb_x + 24"""
        assert axis == "+x"
        x0 = usb_x
        self.add("ESP32 (under)", "bottom", box(x0, -SM_W / 2, x0 + SM_L, SM_W / 2))
        self.add("cut-out", "both", box(x0 + cut_from, -CUT / 2, x0 + 1 + CUT, CUT / 2), "hole")
        if cut_from > 1.0:   # B+ / B- soldered through plated holes over solid board
            self.add("B+/B- holes", "both", unary_union([Point(x0 + 2.0, d).buffer(0.8) for d in (-1.83, 1.83)]), "pins")
        self.add("antenna", "both", box(x0 + SM_L - ANT, -SM_W / 2, x0 + SM_L, SM_W / 2), "antenna")
        self.mod = (x0, x0 + SM_L)
        return self

    def buzzer(self, x, y, rot=0):
        self.add("buzzer (top)", "top", Point(x, y).buffer(4.7))
        dx, dy = 2.5 * math.cos(math.radians(rot)), 2.5 * math.sin(math.radians(rot))
        self.add("buzzer pins", "both", unary_union([Point(x - dx, y - dy).buffer(0.9), Point(x + dx, y + dy).buffer(0.9)]), "pins")
        return self

    def xh(self, label, pins, x, y, facing):
        """right-angle XH under the board; (x, y) = middle of the pin row; facing = direction the plug comes from"""
        w, d = XH[pins]
        ang = {"+y": 0, "-x": 90, "-y": 180, "+x": 270}[facing]
        body = rect(0, (d / 2 - XH_BACK), w, d)
        plug = rect(0, d - XH_BACK + PLUG / 2, w, PLUG)
        pinrow = unary_union([Point((k - (pins - 1) / 2) * 2.5, 0).buffer(1.0) for k in range(pins)])
        for g, side, kind, lab in [(body, "bottom", "body", label), (plug, "bottom", "plug", label + " plug"), (pinrow, "both", "pins", label + " pins")]:
            g = translate(rotate(g, ang, origin=(0, 0)), x, y)
            self.add(lab, side, g, kind)
        return self

    def switch(self, x, y, rot=0):
        body = rect(0, 0, *SW_BODY)
        pins = unary_union([Point(px, 0).buffer(0.8) for px in (-2.5, 0, 2.5, -5.4, 5.4)])
        for g, side, kind, lab in [(body, "bottom", "body", "switch (under)"), (pins, "both", "pins", "switch pins")]:
            self.add(lab, side, translate(rotate(g, rot, origin=(0, 0)), x, y), kind)
        return self

    def pads(self, label, x, y, n=2, pitch=2.54, rot=0, tht=True):
        g = unary_union([Point((k - (n - 1) / 2) * pitch, 0).buffer(0.9) for k in range(n)])
        g = translate(rotate(g, rot, origin=(0, 0)), x, y)
        return self.add(label, "both" if tht else "bottom", g, "pins" if tht else "pads")

    def hole(self, x, y):
        return self.add("M2", "both", Point(x, y).buffer(MH_KEEP), "hole")

    def smd_block(self, x, y, w, h):
        return self.add("small parts (top)", "top", rect(x, y, w, h))

    # ---- checks ----
    def check(self):
        bad = []
        outline = self.board
        for i, (la, sa, ga, ka) in enumerate(self.items):
            if ka == "plug":                       # plug may hang off the board edge, but not into parts
                pass
            elif not outline.buffer(0.01).contains(ga) and not (self.name == "B" and la in ("TOUCH", "DOCK")):
                bad.append(f"{la} outside the board")
            for j in range(i + 1, len(self.items)):
                lb, sb, gb, kb = self.items[j]
                if la.split()[0] == lb.split()[0] and (ka in ("pins", "plug") or kb in ("pins", "plug")):
                    continue                       # a part's own pins / plug space
                if {ka, kb} == {"antenna", "body"} and "ESP32" in (la + lb):
                    continue
                if "ESP32" in la + lb and "B+/B-" in la + lb:
                    continue                       # the plated holes sit under the module's pads on purpose
                same_side = sa == sb or "both" in (sa, sb)
                if not same_side:
                    continue
                if {ka, kb} <= {"body"} or "pins" in (ka, kb) or "hole" in (ka, kb) or "plug" in (ka, kb) or "pads" in (ka, kb):
                    if "ESP32" in la + lb and ("cut-out" in la + lb):
                        continue                   # the module covers its own cut-out
                    if "antenna" in (ka, kb) and ("ESP32" in la + lb):
                        continue
                    if ga.intersects(gb) and ga.intersection(gb).area > 0.05:
                        bad.append(f"{la} x {lb}")
                if "antenna" in (ka, kb):
                    other = gb if ka == "antenna" else ga
                    lab = lb if ka == "antenna" else la
                    if "ESP32" not in lab and other.distance(ga if ka == "antenna" else gb) < 1.5:
                        bad.append(f"{lab} within 1.5 mm of the antenna")
        return bad

    # ---- drawing ----
    def svg(self, path, S=8.0, pad=14):
        minx, miny, maxx, maxy = unary_union([self.board] + [g for _, _, g, _ in self.items] + [g for _, g, _ in self.extra]).bounds
        W, H = (maxx - minx + 2 * pad) * S, (maxy - miny + 2 * pad) * S + 40
        def P(x, y): return ((x - minx + pad) * S, (maxy - y + pad) * S + 40)
        def path_of(g):
            polys = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", [g]))
            d = ""
            for p in polys:
                pts = list(p.exterior.coords)
                d += "M" + " L".join("%.1f %.1f" % P(*c) for c in pts) + " Z "
            return d
        col = {"ESP32": "#1565c0", "LED": "#e65100", "cap": "#bf8040", "buzzer": "#00695c", "switch": "#4e342e",
               "TOUCH": "#37474f", "DOCK": "#37474f", "MOTOR": "#6d4c41", "BAT": "#6a1b9a", "SPARE": "#455a64",
               "M2": "#000", "cut-out": "#000", "antenna": "#1565c0", "small": "#2e7d32", "battery": "#6a1b9a"}
        el = [f'<path d="{path_of(self.board)}" fill="#2e7d32" fill-opacity="0.10" stroke="#2e7d32" stroke-width="2"/>']
        for lab, g, style in self.extra:
            el.append(f'<path d="{path_of(g)}" fill="#e1bee7" fill-opacity="0.35" stroke="#6a1b9a" stroke-width="1.5" stroke-dasharray="6 3"/>')
            cx, cy = g.centroid.coords[0]; X, Y = P(cx, cy)
            el.append(f'<text x="{X:.0f}" y="{Y:.0f}" font-size="12" text-anchor="middle" font-family="sans-serif" fill="#6a1b9a">{lab}</text>')
        labelled = set()
        for lab, side, g, kind in self.items:
            key = next((k for k in col if lab.startswith(k) or k in lab), "small")
            c = col[key]
            dash = ' stroke-dasharray="6 3"' if side == "bottom" else ""
            fill_op = {"pins": 0.9, "pads": 0.6, "hole": 0.0, "plug": 0.04, "antenna": 0.25}.get(kind, 0.25)
            if kind == "plug": dash = ' stroke-dasharray="2 3"'
            el.append(f'<path d="{path_of(g)}" fill="{c}" fill-opacity="{fill_op}" stroke="{c}" stroke-width="1.3"{dash}/>')
            base = lab.split(" pins")[0].split(" plug")[0]
            if kind in ("body", "hole", "pads") and not lab.startswith(("LED", "cap")) and base not in labelled or lab.startswith(("MOTOR", "BAT", "SPARE")) and base not in labelled:
                labelled.add(base)
                cx, cy = g.centroid.coords[0]; X, Y = P(cx, cy)
                el.append(f'<text x="{X:.0f}" y="{Y + 4:.0f}" font-size="11" text-anchor="middle" font-family="sans-serif" fill="{c}">{base}</text>')
        bx0, by0, bx1, by1 = self.board.bounds
        bad = self.check()
        title = f"{self.name}: board {bx1 - bx0:.1f} x {by1 - by0:.1f} mm  -  {'no collisions' if not bad else str(len(bad)) + ' collisions'}"
        el.append(f'<text x="10" y="20" font-size="15" font-family="sans-serif" fill="#222">{title}</text>')
        el.append(f'<text x="10" y="36" font-size="11" font-family="sans-serif" fill="#555">{self.note}  (solid = top, dashed = underside, dotted = plug space, filled dots = through-hole pins)</text>')
        open(path, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}"><rect width="100%" height="100%" fill="#fff"/>' + "".join(el) + "</svg>")
        return bad


def battery(cx, cy, w=35, h=30):
    return ("battery 35x30 (off board)", rect(cx, cy, w, h), None)


# ---------------- variants ----------------
V = []

# A: 54 x 50. ESP32 under, antenna right. Touch / dock XH in the left corners facing inward (plug room
#    under the left half, which is free because the battery sits beside the board). Switch along the
#    top edge, holes in the two right corners. Battery / motor / spare-pin wires on underside pads.
A = Layout("A", box(-24, -25, 30, 25), "XH left corners facing in; switch top edge; holes right corners")
A.leds().supermini(6)
A.xh("TOUCH", 3, -17.0, 22.1, "-y").xh("DOCK", 2, -17.5, -22.1, "+y")
A.switch(19.0, 22.1)
A.hole(27.8, 22.8).hole(27.8, -22.8)
A.buzzer(-6.0, 2.0)
A.smd_block(-3.0, -8.0, 10, 6)
A.pads("BAT +- (under)", -22.6, 1.9, rot=90, tht=False).pads("MOTOR +- (under)", -22.6, -2.6, rot=90, tht=False)
A.pads("SPARE 9 (under)", 13.0, -21.8, n=9, pitch=1.9, tht=False)
A.extra.append(battery(-41.5, 0))
V.append(A)

# B: same 54 x 50, but the XH face outward off the left edge (plug from outside, housings overhang
#    the edge by about 7 mm); holes in three corners.
B = Layout("B", box(-24, -25, 30, 25), "XH at the left edge facing out (housing overhangs the edge); holes in 3 corners")
B.leds().supermini(6)
B.xh("TOUCH", 3, -21.4, 15.0, "-x").xh("DOCK", 2, -21.4, -15.5, "-x")
B.switch(19.0, 22.1)
B.hole(-21.8, 22.8).hole(27.8, 22.8).hole(27.8, -22.8)
B.buzzer(-6.0, 2.0)
B.smd_block(-3.0, -8.0, 10, 6)
B.pads("BAT +- (under)", -14.0, -2.0, rot=90, tht=False).pads("MOTOR +- (under)", -14.0, 4.5, rot=90, tht=False)
B.pads("SPARE 9 (under)", 13.0, -21.8, n=9, pitch=1.9, tht=False)
B.extra.append(battery(-47.5, 0))
V.append(B)

# C: 58 x 48: the board grows 4 mm on the right so the switch and both holes fit beside the antenna
#    end; XH as in A; plain 48 mm height.
C = Layout("C", box(-24, -24, 34, 24), "48 tall: switch upright at the right edge beside the antenna end")
C.leds().supermini(6)
C.add("antenna clear", "both", box(30, -9, 34, 9), "antenna")
C.xh("TOUCH", 3, -17.0, 21.1, "-y").xh("DOCK", 2, -17.5, -21.1, "+y")
C.switch(31.4, 0.0, rot=90)
C.hole(31.8, 21.8).hole(31.8, -21.8)
C.buzzer(-6.0, 2.0)
C.smd_block(-3.0, -8.0, 10, 6)
C.pads("BAT +- (under)", -22.3, 1.3, rot=90, tht=False).pads("MOTOR +- (under)", -22.3, -5.0, rot=90, tht=False)
C.pads("SPARE 9 (under)", 13.0, -21.3, n=9, pitch=1.9, tht=False)
C.extra.append(battery(-41.5, 0))
V.append(C)

# A2: as A, holes in opposite corners (top-right, bottom-left); dock connector moved right of the hole.
A2 = Layout("A2", box(-24, -25, 30, 25), "as A, holes in opposite corners (top-right / bottom-left)")
A2.leds().supermini(6)
A2.xh("TOUCH", 3, -17.0, 22.1, "-y").xh("DOCK", 2, -12.3, -22.1, "+y")
A2.switch(19.0, 22.1)
A2.hole(27.8, 22.8).hole(-21.8, -22.8)
A2.buzzer(-6.0, 2.0)
A2.smd_block(-3.0, -8.0, 10, 6)
A2.pads("BAT +- (under)", -22.6, 1.9, rot=90, tht=False).pads("MOTOR +- (under)", -22.6, -2.6, rot=90, tht=False)
A2.pads("SPARE 9 (under)", 13.0, -21.8, n=9, pitch=1.9, tht=False)
A2.extra.append(battery(-41.5, 0))
V.append(A2)

# D: 54 x 48. Connectors and switch under the board inside the LED circle (pins come up inside the
#    circle, soldered on top); XH face the left edge so plugs go in from outside; holes in all 4
#    corners; caps beside their LEDs; B+/B- through plated holes.
D = Layout("D", box(-24, -24, 30, 24), "connectors + switch under, pins inside the LED circle; holes in 4 corners")
D.supermini(6, cut_from=3.3)
D.leds(beside=True, avoid=D.items[1][2])
D.xh("TOUCH", 3, -11.5, 8.0, "-x").xh("DOCK", 2, -11.5, -8.0, "-x")
D.switch(0.0, -11.5)
D.hole(-21.8, 21.8).hole(27.8, 21.8).hole(-21.8, -21.8).hole(27.8, -21.8)
D.buzzer(-2.5, 7.5)
D.smd_block(0.5, -3.0, 9, 5)
D.pads("BAT +- (under)", -6.0, -21.5, tht=False).pads("MOTOR +- (under)", 0.5, -21.5, tht=False)
D.pads("SPARE 9 (under)", 13.0, -21.3, n=9, pitch=1.9, tht=False)
D.extra.append(battery(-45.0, 0))
V.append(D)

if __name__ == "__main__":
    import subprocess, os
    rows = []
    for v in V:
        bad = v.svg(f"variant_{v.name}.svg")
        bx0, by0, bx1, by1 = v.board.bounds
        rows.append((v.name, f"{bx1-bx0:.1f} x {by1-by0:.1f}", v.note, bad))
        print(f"{v.name}: {bx1-bx0:.1f} x {by1-by0:.1f} mm, {len(bad)} collisions")
        for b_ in bad: print("   ", b_)
