"""Builds carrier_s3.kicad_pcb from design.py: outline, footprints, placement, nets.
Routing is done afterwards by route_pcb.py. Run with the system python (KiCad's pcbnew).

Coordinates in mm, KiCad style: x right, y DOWN, origin = board top-left.
The SuperMini sits at the top, USB-C at the top edge, components underneath it.
"""
import math
import pcbnew
from design import PARTS, NETS

FPLIB = "/usr/share/kicad/footprints"
OUT = "carrier_s3.kicad_pcb"

# ---------------- board and SuperMini geometry (measure and adjust) ----------------
BOARD_W = 27.0
BOARD_L = 47.2
SM_W, SM_L = 18.0, 24.0          # SuperMini board (longest reported); USB end at y = SM_Y0
SM_X0, SM_Y0 = (BOARD_W - SM_W) / 2, 0.6
ROW_INSET = 1.25                 # pin row centre from the SuperMini's long edge (assumed; pads tolerate +-1.5)
PIN_PITCH = 2.54
PIN_Y0 = SM_Y0 + (SM_L - 8 * PIN_PITCH) / 2      # first pin (USB end), pins centred on the board
# rows as seen from the top with USB at the top edge
LEFT_ROW = ["TX", "RX", "GP1", "GP2", "GP3", "GP4", "GP5", "GP6", "GP7"]
RIGHT_ROW = ["5V", "GND", "3V3", "GP13", "GP12", "GP11", "GP10", "GP9", "GP8"]
SM_PAD = (3.4, 1.5)              # long pad across the edge: covers row-spacing uncertainty
SPARE_HOLE_D = 0.9               # solder hole for unused pins, outside the SuperMini outline

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

# ---------------- nets ----------------
nets = {}
for name in NETS:
    n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
pin_net = {(r, p): n for n, pins in NETS.items() for r, p in pins}
spare_nets = {}

# ---------------- outline ----------------
def edge_line(a, b):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(*a)); s.SetEnd(pt(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
R = 1.5
corners = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_L), (0, BOARD_L)]
edge_line((R, 0), (BOARD_W - R, 0)); edge_line((BOARD_W, R), (BOARD_W, BOARD_L - R))
edge_line((BOARD_W - R, BOARD_L), (R, BOARD_L)); edge_line((0, BOARD_L - R), (0, R))
for cx, cy, sa in [(R, R, 180), (BOARD_W - R, R, 270), (BOARD_W - R, BOARD_L - R, 0), (R, BOARD_L - R, 90)]:
    a = pcbnew.PCB_SHAPE(board); a.SetShape(pcbnew.SHAPE_T_ARC); a.SetLayer(pcbnew.Edge_Cuts); a.SetWidth(mm(0.1))
    a.SetCenter(pt(cx, cy)); import math
    a.SetStart(pt(cx + R * math.cos(math.radians(sa)), cy + R * math.sin(math.radians(sa))))
    a.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T)); board.Add(a)

def silk_text(txt, x, y, size=0.8, layer=pcbnew.F_SilkS, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(pt(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * 0.15))
    if mirror: t.SetMirrored(True)
    board.Add(t)

def silk_rect(x0, y0, x1, y1, layer=pcbnew.F_SilkS):
    for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(pt(*a)); s.SetEnd(pt(*b))
        s.SetLayer(layer); s.SetWidth(mm(0.12)); board.Add(s)

# ---------------- footprints ----------------
def lib_fp(lib, name):
    return pcbnew.FootprintLoad(f"{FPLIB}/{lib}.pretty", name)

def add_fp(fp, ref, value, x, y, rot=0, layer_bottom=False):
    fp.SetReference(ref); fp.SetValue(value)
    fp.SetPosition(pt(x, y)); fp.SetOrientationDegrees(rot)
    board.Add(fp)
    if layer_bottom: fp.Flip(pt(x, y), False)
    return fp

def set_pad_nets(fp, ref, mapping):
    """mapping: pad number -> design pin name"""
    for pad in fp.Pads():
        pin = mapping.get(pad.GetNumber())
        if pin is not None and (ref, pin) in pin_net:
            pad.SetNet(nets[pin_net[(ref, pin)]])

def new_fp(ref):
    fp = pcbnew.FOOTPRINT(board); fp.SetReference(ref)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False); return fp

def smd_pad(fp, num, x, y, w, h, shape=pcbnew.PAD_SHAPE_ROUNDRECT):
    p = pcbnew.PAD(fp); p.SetNumber(num); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(shape)
    p.SetSize(pcbnew.VECTOR2I(mm(w), mm(h))); p.SetPos0(pt(x, y)); p.SetPosition(pt(x, y))
    p.SetLayerSet(layers(pcbnew.F_Cu, pcbnew.F_Paste, pcbnew.F_Mask))
    if shape == pcbnew.PAD_SHAPE_ROUNDRECT: p.SetRoundRectRadiusRatio(0.25)
    fp.Add(p); return p

def tht_pad(fp, num, x, y, d, drill, shape=pcbnew.PAD_SHAPE_CIRCLE):
    p = pcbnew.PAD(fp); p.SetNumber(num); p.SetAttribute(pcbnew.PAD_ATTRIB_PTH); p.SetShape(shape)
    p.SetSize(pcbnew.VECTOR2I(mm(d), mm(d))); p.SetDrillSize(pcbnew.VECTOR2I(mm(drill), mm(drill)))
    p.SetPos0(pt(x, y)); p.SetPosition(pt(x, y)); p.SetLayerSet(pcbnew.PAD.PTHMask()); fp.Add(p); return p

# U1: SuperMini (castellated edges soldered flat onto long pads); unused pins get an
# extra solder hole just outside the SuperMini outline.
u1 = new_fp("U1"); u1.SetValue("ESP32-S3 SuperMini"); u1.SetPosition(pt(0, 0))
used = {p for (r, p) in pin_net if r == "U1"}
for side, row in [(-1, LEFT_ROW), (1, RIGHT_ROW)]:
    xr = SM_X0 + ROW_INSET if side < 0 else SM_X0 + SM_W - ROW_INSET
    for i, name in enumerate(row):
        y = PIN_Y0 + i * PIN_PITCH
        p = smd_pad(u1, name, xr, y, SM_PAD[0], SM_PAD[1])
        if name not in used:
            hx = xr + side * (SM_PAD[0] / 2 + 0.9)
            tht_pad(u1, name, hx, y, 1.5, SPARE_HOLE_D)
u1.Reference().SetPosition(pt(BOARD_W / 2, SM_Y0 + SM_L - 3)); u1.Value().SetVisible(False)
board.Add(u1)
for pad in u1.Pads():
    name = pad.GetNumber()
    if ("U1", name) in pin_net: pad.SetNet(nets[pin_net[("U1", name)]])
    else:
        if name not in spare_nets:
            n = pcbnew.NETINFO_ITEM(board, "SPARE_" + name); board.Add(n); spare_nets[name] = n
        pad.SetNet(spare_nets[name])
silk_rect(SM_X0, SM_Y0, SM_X0 + SM_W, SM_Y0 + SM_L)
slot_ref_hide = True
for side, row in [(-1, LEFT_ROW), (1, RIGHT_ROW)]:
    for i, name in enumerate(row):
        if name in used: continue
        xr = (SM_X0 + ROW_INSET if side < 0 else SM_X0 + SM_W - ROW_INSET) + side * (SM_PAD[0] / 2 + 0.9)
        silk_text(name.replace("GP", ""), xr + side * 1.6, PIN_Y0 + i * PIN_PITCH, 0.8)

# B+/B- pass-through: slot under the SuperMini's battery pads (USB end, centre),
# wires go down through it to the B+/B- pads on the bottom.
slot = new_fp("H1"); slot.SetValue("B+/B- wires"); slot.SetPosition(pt(0, 0))
sp = pcbnew.PAD(slot); sp.SetNumber(""); sp.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); sp.SetShape(pcbnew.PAD_SHAPE_OVAL)
sp.SetSize(pcbnew.VECTOR2I(mm(7), mm(2.6))); sp.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
sp.SetDrillSize(pcbnew.VECTOR2I(mm(7), mm(2.6))); sp.SetPos0(pt(BOARD_W / 2, SM_Y0 + 4.5)); sp.SetPosition(pt(BOARD_W / 2, SM_Y0 + 4.5))
sp.SetLayerSet(layers(pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask)); slot.Add(sp)
board.Add(slot)

# bottom pads for the B+/B- wires (and battery / switch wires)
def wire_pads(ref, label, x, y, pins, pitch=2.54, nets_for=None, vertical=False):
    fp = new_fp(ref); fp.SetValue(label); fp.SetPosition(pt(0, 0))
    for i, (num, pin) in enumerate(pins):
        px, py = (x, y + i * pitch) if vertical else (x + i * pitch, y)
        p = tht_pad(fp, num, px, py, 1.7, 1.0, pcbnew.PAD_SHAPE_CIRCLE if i else pcbnew.PAD_SHAPE_RECT)
    board.Add(fp)
    return fp

# ---------------- placement (below the SuperMini) ----------------
y_top = SM_Y0 + SM_L + 0.6          # first row under the SuperMini

# U1 B+/B- wire pads (through holes so the wires can be soldered from either side)
hb = wire_pads("J6", "SuperMini B+/B-", BOARD_W / 2 - 1.27, SM_Y0 + 7.4, [("1", "B+"), ("2", "B-")])
for pad in hb.Pads():
    pad.SetNet(nets["VBAT"] if pad.GetNumber() == "1" else nets["GND"])
silk_text("B+  B-", BOARD_W / 2, SM_Y0 + 9.0, 0.8)

# connectors: JST-PH vertical, two rows along the bottom. Their holes also take wires directly.
PH2 = ("Connector_JST", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical")
PH3 = ("Connector_JST", "JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical")
ROW1, ROW2 = BOARD_L - 9.4, BOARD_L - 3.6
conn = {
    # ref: (lib, x, y of pad 1, name, pin labels) -- labels go on the bottom silk
    "J1": (PH2, 2.6, ROW1, "BAT", "+-"),
    "J5": (PH2, 9.6, ROW1, "DOCK", "5G"),
    "J3": (PH2, 16.6, ROW1, "MOTOR", "+-"),
    "J2": (PH3, 2.6, ROW2, "RING", "VDG"),
    "J4": (PH3, 11.6, ROW2, "TOUCH", "VOG"),
}
for ref, (lf, x, y, label, pins) in conn.items():
    fp = add_fp(lib_fp(*lf), ref, PARTS[ref][0], x, y)
    set_pad_nets(fp, ref, {"1": "1", "2": "2", "3": "3"})
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    npin = 3 if lf is PH3 else 2
    for k, ch in enumerate(pins):
        silk_text(ch, x + 2 * k, y + 1.4, 0.8, pcbnew.B_SilkS, True)
    silk_text(label, x + (npin - 1), y + 2.55, 0.8, pcbnew.B_SilkS, True)
silk_text("+", 0.75, ROW1 - 2.65, 0.8)          # battery + next to J1 pin 1 (top side)

# power switch: two wire pads (switch stays in its printed mount)
sw = wire_pads("SW1", "Switch", 23.4, ROW1 - 1.4, [("1", "COM"), ("2", "ON")], vertical=True)
for pad in sw.Pads(): pad.SetNet(nets[pin_net[("SW1", "COM" if pad.GetNumber() == "1" else "ON")]])
silk_text("SW", 25.4, ROW1 - 0.1, 0.8)

# buzzer: 9.2 mm round, pins 5 mm apart (pins equal, either way round)
bz = new_fp("BZ1"); bz.SetValue("TDB05"); bz.SetPosition(pt(0, 0))
bx, by = 21.7, y_top + 4.8
tht_pad(bz, "1", bx - 2.5, by, 1.8, 0.9); tht_pad(bz, "2", bx + 2.5, by, 1.8, 0.9)
c = pcbnew.FP_SHAPE(bz); c.SetShape(pcbnew.SHAPE_T_CIRCLE); c.SetStart0(pt(bx, by)); c.SetEnd0(pt(bx + 4.6, by)); c.SetCenter(pt(bx, by)); c.SetEnd(pt(bx + 4.6, by))
c.SetLayer(pcbnew.F_SilkS); c.SetWidth(mm(0.12)); bz.Add(c)
board.Add(bz)
for pad in bz.Pads(): pad.SetNet(nets[pin_net[("BZ1", "+" if pad.GetNumber() == "1" else "-")]])
silk_text("BZ", bx, by - 2.6, 0.8)

# small parts (JLCPCB assembly, top side)
R0603 = ("Resistor_SMD", "R_0603_1608Metric")
C0603 = ("Capacitor_SMD", "C_0603_1608Metric")
C1206 = ("Capacitor_SMD", "C_1206_3216Metric")
SOT23 = ("Package_TO_SOT_SMD", "SOT-23")
SOD123 = ("Diode_SMD", "D_SOD-123")
r1, r2, r3 = y_top + 1.7, y_top + 5.6, y_top + 9.2
small = {
    # dividers: battery (R6 R7 C1), dock (R8 R9 C2)
    "R6": (R0603, 1.3, r1, 90), "R7": (R0603, 3.0, r1, 90), "C1": (C0603, 4.7, r1, 90),
    "R8": (R0603, 6.9, r1, 90), "R9": (R0603, 8.6, r1, 90), "C2": (C0603, 10.3, r1, 90),
    "C3": (C1206, 14.0, r1, 0),
    # drivers: buzzer (Q1 R1 R2), motor (Q2 R3 R4 D1)
    "Q1": (SOT23, 2.6, r2, 0), "R1": (R0603, 5.4, r2, 90), "R2": (R0603, 7.1, r2, 90),
    "Q2": (SOT23, 10.4, r2, 0), "R3": (R0603, 13.2, r2, 90), "R4": (R0603, 14.9, r2, 90),
    # ring
    "R5": (R0603, 2.2, r3, 0), "C4": (C1206, 6.6, r3, 0), "D1": (SOD123, 12.2, r3, 180),
}
pinmap = {
    "R": {"1": "1", "2": "2"}, "C": {"1": "1", "2": "2"},
    "Q": {"1": "G", "2": "S", "3": "D"}, "D": {"1": "K", "2": "A"},
}
for ref, (lf, x, y, rot) in small.items():
    fp = add_fp(lib_fp(*lf), ref, PARTS[ref][0], x, y, rot)
    set_pad_nets(fp, ref, pinmap[ref[0]])
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    silk_text(ref, x, y, 0.5, pcbnew.F_Fab)

# mounting holes for M2 self-tapping screws; copper is kept 2 mm from the centre (screw head)
MH_KEEP = 2.0
mh_pos = [(BOARD_W - 1.9, 5.0), (1.9, 19.6), (BOARD_W - 3.4, ROW2 + 0.2)]
for i, (x, y) in enumerate(mh_pos):
    mfp = add_fp(lib_fp("MountingHole", "MountingHole_2.2mm_M2"), f"MH{i+1}", "M2", x, y)
    mfp.Reference().SetVisible(False); mfp.Value().SetVisible(False)
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False); z.SetLayer(lay)
        ol = z.Outline(); ol.NewOutline()
        for k in range(16):
            a = 2 * math.pi * k / 16
            ol.Append(mm(x + MH_KEEP * math.cos(a)), mm(y + MH_KEEP * math.sin(a)))
        board.Add(z)

silk_text("POOL PAGER S3", BOARD_W / 2, 12.0, 0.8, pcbnew.B_SilkS, True)
board.Save(OUT)
print("saved", OUT, f"{BOARD_W} x {BOARD_L} mm")
