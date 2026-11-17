"""Builds carrier_s3.kicad_pcb from design.py: outline, footprints, placement, nets.
Routing is done afterwards by route_pcb.py. Run with the system python (KiCad's pcbnew).

Coordinates in mm, KiCad style: x right, y DOWN, origin = board top-left.

The SuperMini lies sideways along the top: USB-C end flush with the left edge,
antenna end flush with the right edge of that band. All its pins are on the
board. No copper pour, tracks or vias under the antenna end or just below it;
the board is full width (27 mm) only further down, clear of the antenna.
"""
import json, math
import pcbnew
from design import PARTS, NETS

FPLIB = "/usr/share/kicad/footprints"
OUT = "carrier_s3.kicad_pcb"

# ---------------- SuperMini geometry (measure and adjust) ----------------
SM_L, SM_W = 24.0, 18.0          # length (USB to antenna end, longest reported) x width
ANT_LEN = 5.0                    # antenna end kept free of copper (ESTIMATE: measure)
ROW_INSET = 1.25                 # pin row centre from the long edge (assumed; pads tolerate +-1.5)
PIN_PITCH = 2.54
PIN_U0 = (SM_L - 8 * PIN_PITCH) / 2       # first pin from the USB end (pins centred)
# rows as seen from the top with the USB end LEFT
TOP_ROW = ["5V", "GND", "3V3", "GP13", "GP12", "GP11", "GP10", "GP9", "GP8"]
BOT_ROW = ["TX", "RX", "GP1", "GP2", "GP3", "GP4", "GP5", "GP6", "GP7"]
SM_PAD = (1.5, 3.4)              # pad (x, y): long across the edge, covers row-spacing error
SPARE_HOLE_D = 0.9

# ---------------- board ----------------
BOARD_W = 24.0                   # = SuperMini length: plain rectangle
BAND_W = SM_L                    # antenna end flush with the right edge
SM_X0 = 0.0                      # USB end flush with the left edge
MH_C = 2.1                       # corner mounting holes: centre this far from both edges
SM_YC = 15.35                    # SuperMini centre line (corner holes, then the top spare holes)
ROW_TOP_Y = SM_YC - SM_W / 2 + ROW_INSET
ROW_BOT_Y = SM_YC + SM_W / 2 - ROW_INSET
SPARE_DY = SM_PAD[1] / 2 + 0.9   # spare hole distance from the pad row
NOTCH_Y = ROW_BOT_Y + SPARE_DY + 1.0   # parts area starts below the bottom spare holes
ANT_X = SM_L - ANT_LEN           # antenna zone starts here
ANT_CLEAR_Y = NOTCH_Y + 2.5      # no copper right of ANT_X - 2 down to here
BOARD_L = 60.4
R = 1.5                          # corner radius

def mm(v): return pcbnew.FromMM(v)
def layers(*ls):
    st = pcbnew.LSET()
    for l in ls: st.AddLayer(l)
    return st
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

board = pcbnew.BOARD()
board.SetCopperLayerCount(2)
ds = board.GetDesignSettings()
ds.m_TrackMinWidth = mm(0.2)
ds.m_MinClearance = mm(0.2)
ds.m_ViasMinSize = mm(0.6)
ds.m_MinThroughDrill = mm(0.3)
ds.m_CopperEdgeClearance = mm(0.3)
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetTrackWidth(mm(0.3)); nc.SetClearance(mm(0.2)); nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

nets = {}
for name in NETS:
    n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
pin_net = {(r, p): n for n, pins in NETS.items() for r, p in pins}

# ---------------- outline: band under the SuperMini, full width below ----------------
def edge_seg(a, b):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(*a)); s.SetEnd(pt(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
def edge_arc(cx, cy, a0, sweep, r=R):
    a = pcbnew.PCB_SHAPE(board); a.SetShape(pcbnew.SHAPE_T_ARC); a.SetLayer(pcbnew.Edge_Cuts); a.SetWidth(mm(0.1))
    a.SetCenter(pt(cx, cy)); a.SetStart(pt(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))))
    a.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(sweep, pcbnew.DEGREES_T)); board.Add(a)
W, L, N = BOARD_W, BOARD_L, NOTCH_Y
edge_seg((R, 0), (W - R, 0)); edge_arc(W - R, R, 270, 90)
edge_seg((W, R), (W, L - R)); edge_arc(W - R, L - R, 0, 90)
edge_seg((W - R, L), (R, L)); edge_arc(R, L - R, 90, 90)
edge_seg((0, L - R), (0, R)); edge_arc(R, R, 180, 90)
OUTLINE = [(0, 0), (W, 0), (W, L), (0, L)]

def silk_text(txt, x, y, size=0.8, layer=pcbnew.F_SilkS, mirror=False, rot=0):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(pt(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * 0.15))
    if mirror: t.SetMirrored(True)
    if rot: t.SetTextAngleDegrees(rot)
    board.Add(t)

def silk_poly(points, layer=pcbnew.F_SilkS, w=0.12):
    for a, b in zip(points, points[1:]):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(pt(*a)); s.SetEnd(pt(*b))
        s.SetLayer(layer); s.SetWidth(mm(w)); board.Add(s)

def rule_area(poly, lays, pour=True, tracks=True, vias=True):
    for lay in lays:
        z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(pour)
        z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias); z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False); z.SetLayer(lay)
        ol = z.Outline(); ol.NewOutline()
        for x, y in poly: ol.Append(mm(x), mm(y))
        board.Add(z)

# ---------------- footprints ----------------
def lib_fp(lib, name): return pcbnew.FootprintLoad(f"{FPLIB}/{lib}.pretty", name)

def add_fp(fp, ref, value, x, y, rot=0):
    fp.SetReference(ref); fp.SetValue(value)
    fp.SetPosition(pt(x, y)); fp.SetOrientationDegrees(rot); board.Add(fp); return fp

def set_pad_nets(fp, ref, mapping):
    for pad in fp.Pads():
        pin = mapping.get(pad.GetNumber())
        if pin is not None and (ref, pin) in pin_net: pad.SetNet(nets[pin_net[(ref, pin)]])

def new_fp(ref):
    fp = pcbnew.FOOTPRINT(board); fp.SetReference(ref)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False); return fp

def smd_pad(fp, num, x, y, w, h):
    p = pcbnew.PAD(fp); p.SetNumber(num); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
    p.SetSize(pcbnew.VECTOR2I(mm(w), mm(h))); p.SetPos0(pt(x, y)); p.SetPosition(pt(x, y))
    p.SetLayerSet(layers(pcbnew.F_Cu, pcbnew.F_Paste, pcbnew.F_Mask)); p.SetRoundRectRadiusRatio(0.25)
    fp.Add(p); return p

def tht_pad(fp, num, x, y, d, drill, shape=pcbnew.PAD_SHAPE_CIRCLE):
    p = pcbnew.PAD(fp); p.SetNumber(num); p.SetAttribute(pcbnew.PAD_ATTRIB_PTH); p.SetShape(shape)
    p.SetSize(pcbnew.VECTOR2I(mm(d), mm(d))); p.SetDrillSize(pcbnew.VECTOR2I(mm(drill), mm(drill)))
    p.SetPos0(pt(x, y)); p.SetPosition(pt(x, y)); p.SetLayerSet(pcbnew.PAD.PTHMask()); fp.Add(p); return p

# U1: SuperMini soldered flat by its castellated edges; unused pins get a solder hole outside the rows
u1 = new_fp("U1"); u1.SetValue("ESP32-S3 SuperMini"); u1.SetPosition(pt(0, 0))
used = {p for (r, p) in pin_net if r == "U1"}
spares = []
for side, row, yr in [(-1, TOP_ROW, ROW_TOP_Y), (1, BOT_ROW, ROW_BOT_Y)]:
    for i, name in enumerate(row):
        x = SM_X0 + PIN_U0 + i * PIN_PITCH
        smd_pad(u1, name, x, yr, *SM_PAD)
        if name not in used:
            hy = yr + side * SPARE_DY
            tht_pad(u1, name, x, hy, 1.5, SPARE_HOLE_D); spares.append((name, x, hy, side))
board.Add(u1)
for pad in u1.Pads():
    name = pad.GetNumber()
    if ("U1", name) in pin_net: pad.SetNet(nets[pin_net[("U1", name)]])
    else:
        n = board.FindNet("SPARE_" + name)
        if n is None: n = pcbnew.NETINFO_ITEM(board, "SPARE_" + name); board.Add(n)
        pad.SetNet(n)
i_ = 0.3   # outline drawn just inside the board edge
silk_poly([(SM_X0 + i_, SM_YC - SM_W / 2), (SM_L - i_, SM_YC - SM_W / 2), (SM_L - i_, SM_YC + SM_W / 2),
           (SM_X0 + i_, SM_YC + SM_W / 2), (SM_X0 + i_, SM_YC - SM_W / 2)])
silk_text("USB", SM_X0 + 1.6, SM_YC, 0.8, rot=90)
# spare pin labels on the bottom silk, just inside the holes (the top is under the SuperMini)
for name, x, hy, side in spares:
    silk_text(name.replace("GP", ""), x, hy - side * 2.9, 0.8, pcbnew.B_SilkS, True)
silk_text("SPARE PINS", 14.0, SM_YC, 0.8, pcbnew.B_SilkS, True)

# no top copper under the middle of the SuperMini body
inner_top, inner_bot = ROW_TOP_Y + SM_PAD[1] / 2 + 0.2, ROW_BOT_Y - SM_PAD[1] / 2 - 0.2
# (a 2 mm strip inside each pad row stays open so the pins can get out)
rule_area([(0.3, inner_top + 2), (BAND_W, inner_top + 2), (BAND_W, inner_bot - 2), (0.3, inner_bot - 2)],
          [pcbnew.F_Cu], tracks=True, vias=False)
# antenna: nothing on either layer under its end (between the rows) or just below the band
rule_area([(ANT_X, inner_top), (BAND_W + 0.5, inner_top), (BAND_W + 0.5, inner_bot), (ANT_X, inner_bot)],
          [pcbnew.F_Cu, pcbnew.B_Cu])
top_hole_y = ROW_TOP_Y - SPARE_DY                    # top spare holes
rule_area([(ANT_X - 2, -0.5), (W + 0.5, -0.5), (W + 0.5, top_hole_y - 1.0), (ANT_X - 2, top_hole_y - 1.0)],
          [pcbnew.F_Cu, pcbnew.B_Cu])                    # strip above the antenna end
rule_area([(ANT_X - 2, NOTCH_Y - 0.3), (W + 0.5, NOTCH_Y - 0.3), (W + 0.5, ANT_CLEAR_Y), (ANT_X - 2, ANT_CLEAR_Y)],
          [pcbnew.F_Cu, pcbnew.B_Cu])

# B+/B- pass-through: slot under the SuperMini's battery pads (USB end, centre)
slot = new_fp("H1"); slot.SetValue("B+/B- wires"); slot.SetPosition(pt(0, 0))
sp = pcbnew.PAD(slot); sp.SetNumber(""); sp.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); sp.SetShape(pcbnew.PAD_SHAPE_OVAL)
sp.SetSize(pcbnew.VECTOR2I(mm(2.6), mm(7))); sp.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
sp.SetDrillSize(pcbnew.VECTOR2I(mm(2.6), mm(7))); sp.SetPos0(pt(SM_X0 + 4.5, SM_YC)); sp.SetPosition(pt(SM_X0 + 4.5, SM_YC))
sp.SetLayerSet(layers(pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask)); slot.Add(sp)
board.Add(slot)

def wire_pads(ref, label, x, y, pins, pitch=2.54, vertical=False):
    fp = new_fp(ref); fp.SetValue(label); fp.SetPosition(pt(0, 0))
    for i, (num, pin) in enumerate(pins):
        px, py = (x, y + i * pitch) if vertical else (x + i * pitch, y)
        tht_pad(fp, num, px, py, 1.7, 1.0, pcbnew.PAD_SHAPE_CIRCLE if i else pcbnew.PAD_SHAPE_RECT)
    board.Add(fp); return fp

hb = wire_pads("J6", "SuperMini B+/B-", SM_X0 + 7.4, SM_YC - 1.27, [("1", "B+"), ("2", "B-")], vertical=True)
for pad in hb.Pads(): pad.SetNet(nets["VBAT"] if pad.GetNumber() == "1" else nets["GND"])
silk_text("B+", SM_X0 + 9.1, SM_YC - 1.27, 0.8, pcbnew.B_SilkS, True)
silk_text("B-", SM_X0 + 9.1, SM_YC + 1.27, 0.8, pcbnew.B_SilkS, True)

# ---------------- lower area ----------------
y0 = NOTCH_Y
ya, yb, yc, yd = y0 + 1.7, y0 + 5.9, y0 + 9.7, y0 + 13.3     # SMD rows
ROW1 = y0 + 18.4                  # connector rows (pad 1 y); two label lines above each
ROW2 = ROW1 + 7.4

# connectors: JST-PH vertical; their holes also take wires directly.
# Labels on top: pin names over the pins, connector name above them.
PH2 = ("Connector_JST", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical")
PH3 = ("Connector_JST", "JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical")
conn = {
    # ref: (lib, x, y of pad 1, name, pin labels)
    "J1": (PH2, 2.6, ROW1, "BAT", "+-"),
    "J5": (PH2, 9.6, ROW1, "DOCK", "+-"),
    "J3": (PH2, 16.6, ROW1, "MOTOR", "+-"),
    "J2": (PH3, 2.6, ROW2, "RING", "VDG"),
    "J4": (PH3, 17.0, ROW2, "TOUCH", "VOG"),
}
for ref, (lf, x, y, label, pins) in conn.items():
    fp = add_fp(lib_fp(*lf), ref, PARTS[ref][0], x, y)
    set_pad_nets(fp, ref, {"1": "1", "2": "2", "3": "3"})
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    npin = 3 if lf is PH3 else 2
    for k, ch in enumerate(pins):
        silk_text(ch, x + 2 * k, y - 2.45, 0.8)
    silk_text(label, x + (npin - 1), y - 3.55, 0.8)

# power switch: two wire pads (the switch stays in its printed mount)
sw = wire_pads("SW1", "Switch", 22.6, ROW1 - 0.6, [("1", "COM"), ("2", "ON")], vertical=True)
for pad in sw.Pads(): pad.SetNet(nets[pin_net[("SW1", "COM" if pad.GetNumber() == "1" else "ON")]])
silk_text("SW", 22.6, ROW1 - 2.45, 0.8)

# buzzer on the board: 9 mm round, pins 5 mm apart (either way round)
BZ_D = 9.0
bz = new_fp("BZ1"); bz.SetValue("Buzzer 9 mm"); bz.SetPosition(pt(0, 0))
bx, by = 18.8, y0 + 9.4
tht_pad(bz, "1", bx - 2.5, by, 1.8, 0.9, pcbnew.PAD_SHAPE_RECT); tht_pad(bz, "2", bx + 2.5, by, 1.8, 0.9)
for lay, d in [(pcbnew.F_SilkS, BZ_D + 0.3), (pcbnew.F_CrtYd, BZ_D + 0.6)]:
    c = pcbnew.FP_SHAPE(bz); c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetStart0(pt(bx, by)); c.SetEnd0(pt(bx + d / 2, by)); c.SetCenter(pt(bx, by)); c.SetEnd(pt(bx + d / 2, by))
    c.SetLayer(lay); c.SetWidth(mm(0.12 if lay == pcbnew.F_SilkS else 0.05)); bz.Add(c)
board.Add(bz)
for pad in bz.Pads(): pad.SetNet(nets[pin_net[("BZ1", "+" if pad.GetNumber() == "1" else "-")]])
silk_text("BZ", bx, by - 2.4, 0.8)

# small parts (JLCPCB assembly, top side)
R0603 = ("Resistor_SMD", "R_0603_1608Metric")
C0603 = ("Capacitor_SMD", "C_0603_1608Metric")
C1206 = ("Capacitor_SMD", "C_1206_3216Metric")
SOT23 = ("Package_TO_SOT_SMD", "SOT-23")
SOD123 = ("Diode_SMD", "D_SOD-123")
small = {
    # dividers: battery (R6 R7 C1), dock (R8 R9 C2); C1 C2 not fitted
    "R6": (R0603, 5.2, ya, 90), "R7": (R0603, 6.9, ya, 90), "C1": (C0603, 8.6, ya, 90),
    "R8": (R0603, 10.8, ya, 90), "R9": (R0603, 12.5, ya, 90), "C2": (C0603, 14.2, ya, 90),
    # buzzer driver (Q1 R1 R2) and motor flyback D1
    "Q1": (SOT23, 6.2, yb, 0), "R1": (R0603, 8.9, yb, 90), "R2": (R0603, 10.5, yb, 90),
    "D1": (SOD123, 12.9, yb, 90),
    # motor driver (Q2 R3 R4)
    "Q2": (SOT23, 6.2, yc, 0), "R3": (R0603, 9.0, yc, 90), "R4": (R0603, 10.7, yc, 90),
    # ring data resistor, optional bulk cap (not fitted)
    "R5": (R0603, 5.6, yd, 0), "C3": (C1206, 9.8, yd, 0),
}
pinmap = {"R": {"1": "1", "2": "2"}, "C": {"1": "1", "2": "2"},
          "Q": {"1": "G", "2": "S", "3": "D"}, "D": {"1": "K", "2": "A"}}
for ref, (lf, x, y, rot) in small.items():
    fp = add_fp(lib_fp(*lf), ref, PARTS[ref][0], x, y, rot)
    set_pad_nets(fp, ref, pinmap[ref[0]])
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    silk_text(ref, x, y, 0.5, pcbnew.F_Fab)

# mounting holes for M2 self-tapping screws; copper kept 2 mm from the centre (screw head)
MH_KEEP = 2.0
mh_pos = [(MH_C, MH_C), (W - MH_C, MH_C), (MH_C, L - MH_C), (W - MH_C, L - MH_C)]   # 4 corners
for i, (x, y) in enumerate(mh_pos):
    mfp = add_fp(lib_fp("MountingHole", "MountingHole_2.2mm_M2"), f"MH{i+1}", "M2", x, y)
    mfp.Reference().SetVisible(False); mfp.Value().SetVisible(False)
    rule_area([(x + MH_KEEP * math.cos(2 * math.pi * k / 16), y + MH_KEEP * math.sin(2 * math.pi * k / 16))
               for k in range(16)], [pcbnew.F_Cu, pcbnew.B_Cu])

silk_text("POOL PAGER S3", 12.0, y0 + 12.6, 0.8, pcbnew.B_SilkS, True)

board.Save(OUT)
json.dump({"outline": OUTLINE, "corner_r": R}, open("board_geom.json", "w"))
print("saved", OUT, f"{BOARD_W} x {BOARD_L} mm rectangle")
