"""16-LED ring board (48 mm OD, 30 mm ID) with XINGLIGHT XL-5050RGBC-2812B LEDs.
Builds led_ring16.kicad_pcb (placement + nets); route with ../carrier_s3/route_pcb.py.

Coordinates in mm, y down; ring centre at (CX, CY). Wire pads on a tab on the
inside edge at 6 o'clock: GND, DATA, VDD (same order as the carrier's ring
connector). Data runs clockwise (seen from the LED side) from LED 1.
"""
import math, pcbnew

OUT = "led_ring16.kicad_pcb"
OD, ID = 48.0, 30.0
N = 16
R_LED = 20.5                 # LED centres
R_CAP = 16.4                 # capacitors on an inner circle, between the LEDs (no room beside them)
CX = CY = OD / 2 + 0.05
TAB_W, TAB_IN = 9.0, 6.0     # inner tab: width, how far it reaches in from the ID
LED_FP = ("LED_SMD", "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm")   # pins 1 VDD, 2 DOUT, 3 GND, 4 DIN
CAP_FP = ("Capacitor_SMD", "C_0603_1608Metric")
FPLIB = "/usr/share/kicad/footprints"

def mm(v): return pcbnew.FromMM(v)
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))
def polar(r, deg): a = math.radians(deg); return CX + r * math.cos(a), CY + r * math.sin(a)

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

def edge_poly(points):
    for a, b in zip(points, points[1:] + points[:1]):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1)); s.SetStart(pt(*a)); s.SetEnd(pt(*b)); board.Add(s)

# outer circle
c = pcbnew.PCB_SHAPE(board); c.SetShape(pcbnew.SHAPE_T_CIRCLE); c.SetLayer(pcbnew.Edge_Cuts); c.SetWidth(mm(0.1))
c.SetCenter(pt(CX, CY)); c.SetEnd(pt(CX + OD / 2, CY)); board.Add(c)
# inner hole with the pad tab at 6 o'clock (90 deg, y down)
r_in = ID / 2
half = math.degrees(math.asin((TAB_W / 2) / r_in))
steps = 160
y_tab = CY + r_in - TAB_IN
# arc from just left of the tab (90+half) clockwise round to just right of it (450-half),
# then the tab's right and left inner corners back to the start
arc = [polar(r_in, 90 + half + (360 - 2 * half) * k / steps) for k in range(steps + 1)]
tab = [(CX + TAB_W / 2, y_tab), (CX - TAB_W / 2, y_tab)]
edge_poly(arc + tab)

def lib_fp(lib, name): return pcbnew.FootprintLoad(f"{FPLIB}/{lib}.pretty", name)
def text(t, x, y, size=0.8, layer=pcbnew.F_SilkS, rot=0, mirror=False):
    s = pcbnew.PCB_TEXT(board); s.SetText(t); s.SetPosition(pt(x, y)); s.SetLayer(layer)
    s.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); s.SetTextThickness(mm(size * 0.15))
    if rot: s.SetTextAngleDegrees(rot)
    if mirror: s.SetMirrored(True)
    board.Add(s)

# LEDs: data clockwise; local -x points to the next LED, local -y points inward (VDD inside)
th0 = 90 + 360 / N / 2       # first LED just clockwise of the tab
for i in range(N):
    th = th0 + i * 360 / N
    x, y = polar(R_LED, th)
    fp = lib_fp(*LED_FP); fp.SetReference(f"D{i+1}"); fp.SetValue("XL-5050RGBC-2812B")
    fp.SetPosition(pt(x, y)); fp.SetOrientationDegrees(90 - th); board.Add(fp)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    din = "DIN" if i == 0 else f"D{i}"
    dout = f"D{i+1}" if i < N - 1 else "DOUT"
    for p in fp.Pads():
        p.SetNet(net({"1": "VDD", "2": dout, "3": "GND", "4": din}[p.GetNumber()]))
    # 100 nF on the inner circle, between this LED and the next (tangential)
    cth = th + 360 / N / 2
    if abs(((cth - 90) % 360)) < 1e-6:      # this gap is over the wire tab: put that cap on the far side of D1
        cth = th0 + 360 / N * 0.0 - 0.0
    cx_, cy_ = polar(R_CAP, cth)
    cp = lib_fp(*CAP_FP); cp.SetReference(f"C{i+1}"); cp.SetValue("100nF")
    cp.SetPosition(pt(cx_, cy_)); cp.SetOrientationDegrees(90 - cth); board.Add(cp)
    cp.Reference().SetVisible(False); cp.Value().SetVisible(False)
    for p in cp.Pads(): p.SetNet(net("VDD" if p.GetNumber() == "1" else "GND"))
    text(str(i + 1), *polar(R_LED, th), 0.8, pcbnew.B_SilkS, mirror=True)

# wire pads on the tab: GND, DATA, VDD (left to right, LED side up)
w = pcbnew.FOOTPRINT(board); w.SetReference("J1"); w.SetValue("Ring wires"); w.SetPosition(pt(0, 0))
for k, (num, n) in enumerate([("1", "GND"), ("2", "DIN"), ("3", "VDD")]):
    p = pcbnew.PAD(w); p.SetNumber(num); p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(pcbnew.PAD_SHAPE_RECT if k == 0 else pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(mm(1.7), mm(1.7))); p.SetDrillSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
    px, py = CX + (k - 1) * 2.54, y_tab + 1.6
    p.SetPos0(pt(px, py)); p.SetPosition(pt(px, py)); p.SetLayerSet(pcbnew.PAD.PTHMask()); p.SetNet(net(n)); w.Add(p)
w.Reference().SetVisible(False); w.Value().SetVisible(False); board.Add(w)
for k, t in enumerate("GDV"):
    text(t, CX + (k - 1) * 2.54, y_tab + 3.3, 0.8)
text("RING 16 XL-5050", CX, CY - r_in - 1.0 + 0.0, 0.8, pcbnew.B_SilkS, mirror=True) if False else None

board.Save(OUT)
print("saved", OUT, f"OD {OD} ID {ID}, {N} LEDs at r {R_LED}")
