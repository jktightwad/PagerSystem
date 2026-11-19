"""Builds pager_main.kicad_pcb (layout D): 16 LEDs on top, ESP32-S3 SuperMini underneath.
Route afterwards: python3 ../carrier_s3/route_pcb.py pager_main.kicad_pcb

Design coordinates are mm with the LED ring centre at (0, 0), x right, y UP
(as in layout_study.py); P() converts to KiCad (origin top-left, y down).
"""
import json, math, os
import pcbnew
from design_main import PARTS, NETS, N_LED

# PAGER_SMD_CONN=1 builds the variant with surface-mount touch / dock connectors (DEALON XH-3PWB /
# XH-2PWB, right angle, under the board) for a JLC Standard (two-sided) assembly quote
SMD_CONN = os.environ.get("PAGER_SMD_CONN") == "1"
OUT = "pager_main_smdconn.kicad_pcb" if SMD_CONN else "pager_main.kicad_pcb"
FPLIB = "/usr/share/kicad/footprints"

# ---------------- geometry (design coords) ----------------
X0, X1, Y0, Y1 = -24.0, 30.0, -24.0, 24.0         # board 54 x 48
R_CORNER = 1.5
R_LED = 20.5
# SuperMini under the board: USB end at x = SM_X, antenna end at the right edge
SM_X, SM_L, SM_W = 6.0, 24.0, 18.0
ROW_IN, PIN_X0, PITCH = 1.375, 1.75, 2.54           # measured: rows 15.25 apart, first pin 1.75 from USB end
ANT = 5.0                                           # antenna end kept copper-free (estimate)
BHOLE_X, BHOLE_DY = 1.6, 1.83                       # B+/B- plated holes: from the USB end / either side of centre
# cut-out only where the module's underside parts are (measured from a photo, +0.5 mm clearance):
# L-shape, as (distance from the USB end, y) corners; y is + towards the module's TX/B- side
CUT_L = [(3.0, -1.6), (7.7, -1.6), (7.7, 0.9), (11.2, 0.9), (11.2, 3.9), (3.0, 3.9)]   # lower parts 10.4-12.4 from the 5V edge (measured)
# module pins as seen from the TOP of our board (module upside down under it, USB end left):
# its 5V/GND/3V3 row is at -y, its TX/RX row at +y
ROW_NEG = ["5V", "GND", "3V3", "GP13", "GP12", "GP11", "GP10", "GP9", "GP8"]
ROW_POS = ["TX", "RX", "GP1", "GP2", "GP3", "GP4", "GP5", "GP6", "GP7"]
SM_PAD_OUT, SM_PAD_IN, SM_PAD_W = 1.0, 3.0, 1.5     # castellation pad: beyond / inside the module edge

def mm(v): return pcbnew.FromMM(v)
def P(x, y): return pcbnew.VECTOR2I(mm(x - X0), mm(Y1 - y))
W, H = X1 - X0, Y1 - Y0

board = pcbnew.BOARD(); board.SetCopperLayerCount(2)
ds = board.GetDesignSettings()
ds.m_TrackMinWidth = mm(0.2); ds.m_MinClearance = mm(0.2); ds.m_ViasMinSize = mm(0.6)
ds.m_MinThroughDrill = mm(0.3); ds.m_CopperEdgeClearance = mm(0.3)
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetTrackWidth(mm(0.25)); nc.SetClearance(mm(0.2)); nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]
pin_net = {(r, p): n for n, pins in NETS.items() for r, p in pins}
for n in NETS: net(n)

def layers(*ls):
    st = pcbnew.LSET()
    for l in ls: st.AddLayer(l)
    return st

# ---------------- outline (+ internal cut-out) ----------------
def seg(a, b, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(layer); s.SetWidth(mm(w))
    s.SetStart(P(*a)); s.SetEnd(P(*b)); board.Add(s)
def arc(cx, cy, a0, sweep, r=R_CORNER):   # angles in design coords (CCW, y up)
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
    s.SetCenter(P(cx, cy)); s.SetStart(P(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))))
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(-sweep, pcbnew.DEGREES_T)); board.Add(s)   # KiCad y-down: negate
r = R_CORNER
seg((X0 + r, Y1), (X1 - r, Y1)); seg((X1, Y1 - r), (X1, Y0 + r)); seg((X1 - r, Y0), (X0 + r, Y0)); seg((X0, Y0 + r), (X0, Y1 - r))
arc(X1 - r, Y1 - r, 90, -90); arc(X1 - r, Y0 + r, 0, -90); arc(X0 + r, Y0 + r, 270, -90); arc(X0 + r, Y1 - r, 180, -90)
cut = [(SM_X + u, v) for u, v in CUT_L]
for a, b in zip(cut, cut[1:] + cut[:1]):
    seg(a, b)

# ---------------- helpers ----------------
def text(t, x, y, size=0.8, layer=pcbnew.F_SilkS, rot=0):
    s = pcbnew.PCB_TEXT(board); s.SetText(t); s.SetPosition(P(x, y)); s.SetLayer(layer)
    s.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); s.SetTextThickness(mm(size * 0.15))
    if rot: s.SetTextAngleDegrees(rot)
    if layer in (pcbnew.B_SilkS,): s.SetMirrored(True)
    board.Add(s)

def rule_area(poly, lays, pour=True, tracks=True, vias=True):
    for lay in lays:
        z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(pour); z.SetDoNotAllowTracks(tracks)
        z.SetDoNotAllowVias(vias); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetLayer(lay)
        ol = z.Outline(); ol.NewOutline()
        for x, y in poly: ol.Append(P(x, y))
        board.Add(z)

def lib_fp(lib, name): return pcbnew.FootprintLoad(f"{FPLIB}/{lib}.pretty", name)

def place(fp, ref, x, y, rot=0, bottom=False):
    fp.SetReference(ref); fp.SetValue(PARTS.get(ref, (ref,))[0])
    fp.SetPosition(P(x, y)); fp.SetOrientationDegrees(rot); board.Add(fp)
    if bottom: fp.Flip(P(x, y), False)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    return fp

def set_nets(fp, ref, mapping):
    for pad in fp.Pads():
        pin = mapping.get(pad.GetNumber())
        if pin is not None and (ref, pin) in pin_net: pad.SetNet(net(pin_net[(ref, pin)]))

def new_fp(ref):
    # footprint origin at the KiCad origin, so pad / shape positions given in board coordinates are absolute
    fp = pcbnew.FOOTPRINT(board); fp.SetReference(ref); fp.SetPosition(pcbnew.VECTOR2I(0, 0)); return fp

def add_pad(fp, num, x, y, size, kind="smd", drill=None, shape=pcbnew.PAD_SHAPE_RECT, side="top", oval_drill=None):
    p = pcbnew.PAD(fp); p.SetNumber(num); p.SetShape(shape)
    p.SetSize(pcbnew.VECTOR2I(mm(size[0]), mm(size[1])))
    if kind == "smd":
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        p.SetLayerSet(layers(pcbnew.F_Cu, pcbnew.F_Mask) if side == "top" else layers(pcbnew.B_Cu, pcbnew.B_Mask))
    else:
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH); p.SetLayerSet(pcbnew.PAD.PTHMask())
        if oval_drill:
            p.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG); p.SetDrillSize(pcbnew.VECTOR2I(mm(oval_drill[0]), mm(oval_drill[1])))
        else:
            p.SetDrillSize(pcbnew.VECTOR2I(mm(drill), mm(drill)))
    p.SetPos0(P(x, y)); p.SetPosition(P(x, y)); fp.Add(p); return p

def fp_rect(fp, x0, y0, x1, y1, layer, w=0.12):
    for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        s = pcbnew.FP_SHAPE(fp); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(layer); s.SetWidth(mm(w))
        s.SetStart0(P(*a)); s.SetEnd0(P(*b)); s.SetStart(P(*a)); s.SetEnd(P(*b)); fp.Add(s)

# ---------------- U1: SuperMini under the board ----------------
u1 = new_fp("U1"); u1.SetValue(PARTS["U1"][0])
used = {p for (r_, p) in pin_net if r_ == "U1"}
spares = []
for sgn, row in [(-1, ROW_NEG), (1, ROW_POS)]:
    edge = sgn * SM_W / 2
    for k, name in enumerate(row):
        x = SM_X + PIN_X0 + k * PITCH
        y = edge + sgn * (SM_PAD_OUT - SM_PAD_IN) / 2           # pad centre (from SM_PAD_IN inside to SM_PAD_OUT outside)
        add_pad(u1, name, x, y, (SM_PAD_W, SM_PAD_OUT + SM_PAD_IN), side="bottom", shape=pcbnew.PAD_SHAPE_ROUNDRECT)
        if name not in used: spares.append(name)
for name, dy in [("B+", -BHOLE_DY), ("B-", BHOLE_DY)]:     # B+ on the 5V-row side (seen from the top)
    # as big as the 2 x 2 mm module pad allows: oval 1.1 x 1.6 mm hole, 1.5 x 2.0 mm copper
    add_pad(u1, name, SM_X + BHOLE_X, dy, (1.5, 2.0), kind="pth", shape=pcbnew.PAD_SHAPE_OVAL, oval_drill=(1.1, 1.6))
fp_rect(u1, SM_X, -SM_W / 2, SM_X + SM_L, SM_W / 2, pcbnew.B_SilkS)
board.Add(u1)
for pad in u1.Pads():
    nm = pad.GetNumber()
    pad.SetNet(net(pin_net[("U1", nm)]) if ("U1", nm) in pin_net else net("SPARE_" + nm))
u1.Reference().SetVisible(False); u1.Value().SetVisible(False)
text("ESP32-S3 SuperMini (under)", SM_X + 12, 0, 0.8, pcbnew.B_SilkS)
text("B+", SM_X + BHOLE_X, -BHOLE_DY - 1.6, 0.8); text("B-", SM_X + BHOLE_X, BHOLE_DY + 1.6, 0.8)

# no bottom tracks under the module body (between the castellation pads); GND pour + stitching vias are
# allowed there (covered by solder mask), so the LEDs / caps above the module can reach ground
inner = SM_W / 2 - SM_PAD_IN - 0.3
rule_area([(SM_X, inner), (SM_X + SM_L + 1, inner), (SM_X + SM_L + 1, -inner), (SM_X, -inner)], [pcbnew.B_Cu],
          pour=False, tracks=True, vias=False)
# antenna end: no tracks / vias / pour on the top over it, none between the pads on the bottom
ax = SM_X + SM_L - ANT
rule_area([(ax, SM_W / 2), (X1 + 1, SM_W / 2), (X1 + 1, -SM_W / 2), (ax, -SM_W / 2)], [pcbnew.F_Cu])
rule_area([(ax - 1, SM_W / 2 + 3), (X1 + 1, SM_W / 2 + 3), (X1 + 1, -SM_W / 2 - 3), (ax - 1, -SM_W / 2 - 3)],
          [pcbnew.F_Cu, pcbnew.B_Cu], pour=True, tracks=False, vias=False)          # no pour near the antenna

# ---------------- LEDs + their capacitors (top) ----------------
LED = ("LED_SMD", "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm")      # pins 1 VDD, 2 DOUT, 3 GND, 4 DIN
C0603 = ("Capacitor_SMD", "C_0603_1608Metric")
# ring turned so every LED's capacitor clears the cut-out (spacing stays 22.5 deg; offset 19.75 deg found by search,
# copper about 0.4 mm from the cut-out edge)
a_first = 19.75 + 22.5 * 12                                   # LED1 (bottom right), chain runs clockwise
for i in range(1, N_LED + 1):
    a = a_first - (i - 1) * 22.5
    x, y = R_LED * math.cos(math.radians(a)), R_LED * math.sin(math.radians(a))
    fp = place(lib_fp(*LED), f"LED{i}", x, y, rot=90 + a)
    set_nets(fp, f"LED{i}", {"1": "VDD", "2": "DOUT", "3": "GND", "4": "DIN"})
    # capacitor beside its LED on the inside; if that is in the cut-out, in the gap away from the module axis
    rc = R_LED - 2.6 - 0.75 - 0.3
    cx, cy = rc * math.cos(math.radians(a)), rc * math.sin(math.radians(a))
    ca = a
    cp = place(lib_fp(*C0603), f"CL{i}", cx, cy, rot=90 + ca)
    set_nets(cp, f"CL{i}", {"1": "1", "2": "2"})
text("1", *[(R_LED + 3.3) * f(math.radians(a_first)) for f in (math.cos, math.sin)], 0.8)

# ---------------- buzzer (top, SMD, JLC-assembled) ----------------
# S&S SMD-0955-05-27 active buzzer: 9 x 9 mm body, two 2 mm-wide terminals on opposite sides,
# 11.4 mm tip to tip, 5.4 mm between them (datasheet). Terminals along x here; + on the left.
BZX, BZY = -2.5, 8.0
bz = new_fp("BZ1"); bz.SetValue(PARTS["BZ1"][0])
for num, sx in [("1", -1), ("2", 1)]:
    add_pad(bz, num, BZX + sx * 4.2, BZY, (3.4, 2.4), side="top", shape=pcbnew.PAD_SHAPE_ROUNDRECT)
fp_rect(bz, BZX - 4.5, BZY - 4.5, BZX + 4.5, BZY + 4.5, pcbnew.F_SilkS)
fp_rect(bz, BZX - 6.0, BZY - 4.8, BZX + 6.0, BZY + 4.8, pcbnew.F_CrtYd, w=0.05)
board.Add(bz); set_nets(bz, "BZ1", {"1": "+", "2": "-"})
bz.Reference().SetVisible(False); bz.Value().SetVisible(False)
text("+", BZX - 4.2, BZY + 2.1, 0.8)

# ---------------- switch SS12F44 (under): 3 pins 2.5 mm, end legs slotted ----------------
SWX, SWY, SW_LEG = -2.0, -11.5, 5.6          # leg spacing 11.2 mm is an ESTIMATE - measure
sw = new_fp("SW1"); sw.SetValue(PARTS["SW1"][0])
for num, dx in [("1", -2.5), ("2", 0.0), ("3", 2.5)]:
    add_pad(sw, num, SWX + dx, SWY, (1.7, 1.7), kind="pth", drill=1.1, shape=pcbnew.PAD_SHAPE_CIRCLE if num != "1" else pcbnew.PAD_SHAPE_RECT)
for num, dx in [("4", -SW_LEG), ("5", SW_LEG)]:
    add_pad(sw, num, SWX + dx, SWY, (1.6, 2.8), kind="pth", shape=pcbnew.PAD_SHAPE_OVAL, oval_drill=(1.0, 2.2))
fp_rect(sw, SWX - 6.0, SWY - 2.85, SWX + 6.0, SWY + 2.85, pcbnew.B_SilkS)
board.Add(sw); set_nets(sw, "SW1", {"1": "ON", "2": "COM"})
sw.Reference().SetVisible(False); sw.Value().SetVisible(False)
text("SWITCH (under)", SWX, SWY - 4.0, 0.8, pcbnew.B_SilkS)

# ---------------- XH right-angle connectors (under), plug from the left edge ----------------
def xh(ref, pins, x, y, mapping, label):
    name = f"JST_XH_S{pins}B-XH-A_1x0{pins}_P2.50mm_Horizontal"
    fp = lib_fp("Connector_JST", name)
    # pins along y, body towards -x: try orientations until the body sits left of the pins
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot); fp.SetPosition(P(0, 0))
        bb = fp.GetBoundingBox(False, False); p1 = [p for p in fp.Pads() if p.GetNumber() == "1"][0].GetPosition()
        pins_x = sum(p.GetPosition().x for p in fp.Pads()) / pins
        if bb.GetCenter().x < pins_x - mm(2) and p1.y < [p for p in fp.Pads() if p.GetNumber() == str(pins)][0].GetPosition().y:
            break
    fp = place(fp, ref, 0, 0, rot=rot)
    # move so the middle of the pin row is at (x, y), then put it under the board
    pads = list(fp.Pads()); mx = sum(p.GetPosition().x for p in pads) / len(pads); my = sum(p.GetPosition().y for p in pads) / len(pads)
    fp.Move(pcbnew.VECTOR2I(int(P(x, y).x - mx), int(P(x, y).y - my)))
    fp.Flip(P(x, y), False)
    set_nets(fp, ref, mapping)
    text(label, x - 6.0, y, 0.8, pcbnew.B_SilkS, rot=90)
    return fp
def xh_smd(ref, pins, x, y, label):
    """DEALON XH-nPWB SMD right angle under the board (datasheet land pattern): signal pads 1.3 x 5.0 on
    2.5 mm pitch along y, centred on x; mounting pads 1.5 x 3.8, 2.8 mm beyond the signal pads towards -x
    (the plug opening, at the left edge) and 2.9 mm outboard of the end pins. Pin 1 at +y."""
    fp = new_fp(ref); fp.SetValue(PARTS[ref][0])
    span = (pins - 1) * 2.5
    for k in range(pins):
        add_pad(fp, str(k + 1), x, y + span / 2 - k * 2.5, (5.0, 1.3), side="bottom", shape=pcbnew.PAD_SHAPE_ROUNDRECT)
    mx = x - 2.5 - 2.8 - 1.9
    for k, sy in enumerate((1, -1)):
        add_pad(fp, f"MP{k+1}", mx, y + sy * (span / 2 + 2.9), (3.8, 1.5), side="bottom", shape=pcbnew.PAD_SHAPE_ROUNDRECT)
    w = span + 7.5                                   # housing width (DIM C)
    fp_rect(fp, x - 9.7, y - w / 2, x + 2.6, y + w / 2, pcbnew.B_SilkS)
    fp_rect(fp, x - 10.0, y - w / 2 - 0.3, x + 2.9, y + w / 2 + 0.3, pcbnew.B_CrtYd, w=0.05)
    board.Add(fp); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    set_nets(fp, ref, {str(k + 1): str(k + 1) for k in range(pins)})
    text(label, x - 6.0, y, 0.8, pcbnew.B_SilkS, rot=90)
    return fp
if SMD_CONN:
    xh_smd("J1", 3, -11.5, 7.0, "TOUCH G O V")
    xh_smd("J2", 2, -11.5, -7.0, "DOCK G +")
else:
    xh("J1", 3, -11.5, 7.0, {"1": "1", "2": "2", "3": "3"}, "TOUCH G O V")
    xh("J2", 2, -11.5, -7.0, {"1": "1", "2": "2"}, "DOCK G +")

# ---------------- small parts (top, inside the ring) ----------------
R0603 = ("Resistor_SMD", "R_0603_1608Metric")
C1206 = ("Capacitor_SMD", "C_1206_3216Metric")
SOT23 = ("Package_TO_SOT_SMD", "SOT-23")
SOD123 = ("Diode_SMD", "D_SOD-123")
ya, yb, yc = 1.0, -3.0, -6.8
small = {
    "R6": (R0603, -7.5, ya, 90), "R7": (R0603, -5.8, ya, 90), "C1": (C0603, -4.1, ya, 90),
    "R8": (R0603, -1.6, ya, 90), "R9": (R0603, 0.1, ya, 90), "C2": (C0603, 1.8, ya, 90),
    "Q1": (SOT23, -6.5, yb, 0), "R1": (R0603, -3.8, yb, 90), "R2": (R0603, -2.2, yb, 90),
    "Q2": (SOT23, 1.0, yb, 0), "R3": (R0603, 3.7, yb, 90), "R4": (R0603, 5.3, yb, 90),
    "R5": (R0603, -6.0, yc, 0), "C3": (C1206, -1.5, yc, 0), "D1": (SOD123, 3.5, yc, 180),
}
pinmap = {"R": {"1": "1", "2": "2"}, "C": {"1": "1", "2": "2"}, "Q": {"1": "G", "2": "S", "3": "D"}, "D": {"1": "K", "2": "A"}}
for ref, (lf, x, y, rot) in small.items():
    fp = place(lib_fp(*lf), ref, x, y, rot)
    set_nets(fp, ref, pinmap[ref[0]])

# ---------------- wire pads (under) ----------------
def wire_pads(ref, x, y, labels, pitch=2.8, size=(1.8, 2.6)):
    fp = new_fp(ref); fp.SetValue(PARTS.get(ref, (ref,))[0])
    for k in range(len(labels)):
        add_pad(fp, str(k + 1), x + (k - (len(labels) - 1) / 2) * pitch, y, size, side="bottom", shape=pcbnew.PAD_SHAPE_ROUNDRECT)
    board.Add(fp); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); return fp
p1 = wire_pads("P1", -6.0, -19.5, ["-", "+"]); set_nets(p1, "P1", {"1": "1", "2": "2"})
text("BAT - +", -6.0, -22.0, 0.8, pcbnew.B_SilkS)
p2 = wire_pads("P2", 1.0, -19.5, ["-", "+"]); set_nets(p2, "P2", {"1": "1", "2": "2"})
text("MOT - +", 1.0, -22.0, 0.8, pcbnew.B_SilkS)
# spare pins + power: through-holes on an arc just outside the LED ring, in the two left corners.
# Each corner takes the spares from the module row on its side (the 5V/GND/3V3 row faces -y),
# plus 3V3 and GND (and VBAT at the bottom) for future additions.
R_SPARE, PITCH_ARC = 26.0, 2.0      # last hole clear of the connector plugs
STEP = math.degrees(PITCH_ARC / R_SPARE)
top_names = [n for n in ROW_POS if n in spares] + ["3V3", "GND"]
bot_names = [n for n in ROW_NEG if n in spares] + ["VBAT", "3V3", "GND"]
def arc_holes(names, a0, direction):
    return [(n, a0 + direction * k * STEP) for k, n in enumerate(names)]
holes = arc_holes(top_names, 120.1, +1) + arc_holes(bot_names, 239.9, -1)
sp = new_fp("P3"); sp.SetValue("spare pins / power")
for k, (name, a) in enumerate(holes):
    px, py = R_SPARE * math.cos(math.radians(a)), R_SPARE * math.sin(math.radians(a))
    pd = add_pad(sp, str(k + 1), px, py, (1.5, 1.5), kind="pth", drill=0.9,
                 shape=pcbnew.PAD_SHAPE_RECT if name == "GND" else pcbnew.PAD_SHAPE_CIRCLE)
    lab = name.replace("GP", "")
    # top label just outside the hole where it fits on the board, underside label just inside it
    lx, ly = (R_SPARE + 1.8) * math.cos(math.radians(a)), (R_SPARE + 1.8) * math.sin(math.radians(a))
    if X0 + 1.2 < lx < X1 - 1.2 and Y0 + 1.2 < ly < Y1 - 1.2:
        text(lab, lx, ly, 0.8, rot=a + 90)
    bx, by = (R_SPARE - 2.0) * math.cos(math.radians(a)), (R_SPARE - 2.0) * math.sin(math.radians(a))
    text(lab, bx, by, 0.8, pcbnew.B_SilkS, rot=a + 90)
board.Add(sp); sp.Reference().SetVisible(False); sp.Value().SetVisible(False)
for k, pad in enumerate(sorted(sp.Pads(), key=lambda p: int(p.GetNumber()))):
    name = holes[k][0]
    pad.SetNet(net(name if name in ("3V3", "GND", "VBAT") else "SPARE_" + name))

# ---------------- mounting holes (4 corners) ----------------
for k, (x, y) in enumerate([(X0 + 2.2, Y1 - 2.2), (X1 - 2.2, Y1 - 2.2), (X0 + 2.2, Y0 + 2.2), (X1 - 2.2, Y0 + 2.2)]):
    fp = place(lib_fp("MountingHole", "MountingHole_2.2mm_M2"), f"MH{k+1}", x, y)
    rule_area([(x + 2.0 * math.cos(2 * math.pi * j / 16), y + 2.0 * math.sin(2 * math.pi * j / 16)) for j in range(16)],
              [pcbnew.F_Cu, pcbnew.B_Cu])

text("POOL PAGER", -17.0, 0.0, 0.8, pcbnew.B_SilkS, rot=90)
from fix_anchors import center_anchors
center_anchors(board)                # JLC places parts at the footprint anchor: centre the hand-built ones
board.Save(OUT)
if not SMD_CONN: json.dump({"spares": spares}, open("spares.json", "w"))
print("saved", OUT, f"{W:.0f} x {H:.0f} mm;", len(list(board.GetFootprints())), "footprints;", len(nets), "nets")
