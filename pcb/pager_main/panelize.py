"""3 x 2 panel of the finished pager board, joined by small tabs, each copy labelled "Pager N".

    python3 panelize.py [pager_main.kicad_pcb] [pager_panel.kicad_pcb]

Takes the routed, DRC-clean single board and copies everything (footprints, tracks, vias,
zones, rule areas, drawings) six times. References get a suffix (LED1 -> LED1_3 on copy 3) so
the JLCPCB BOM / CPL designators stay unique; nets get a "P3/" prefix so DRC does not ask
for the copies to be connected to each other. The single board's outer outline is replaced by
one panel outline: the six boards, GAP mm apart, joined by TAB_W mm tabs (3 per shared edge);
inner cut-outs (the L under the module) are kept on every copy.
"""
import sys
import pcbnew
from shapely.geometry import box
from shapely.ops import unary_union

SRC = sys.argv[1] if len(sys.argv) > 1 else "pager_main.kicad_pcb"
OUT = sys.argv[2] if len(sys.argv) > 2 else "pager_panel.kicad_pcb"
COLS, ROWS = 3, 2
GAP = 2.0          # routed gap between boards, mm
TAB_W = 2.5        # tab width along the edge, mm
CORNER_R = 1.5     # board corner radius (as the single board)
# tab centres along each shared edge, measured from the board's own corner (mm)
TABS_X = (8.0, 27.0, 46.0)      # along the 54 mm edges (horizontal gap)
TABS_Y = (6.0, 24.0, 42.0)      # along the 48 mm edges (vertical gap)
LABEL_AT, LABEL_ROT, LABEL_H = (50.6, 24.0), 90, 1.6   # "Pager N": top silk, beside the antenna (no parts there)

def mm(v): return pcbnew.FromMM(v)
def to_mm(v): return pcbnew.ToMM(v)

src0 = pcbnew.LoadBoard(SRC)
bb = src0.GetBoardEdgesBoundingBox()
X0, Y0 = to_mm(bb.GetLeft()) + 0.05, to_mm(bb.GetTop()) + 0.05     # minus half the edge line
W, H = to_mm(bb.GetWidth()) - 0.1, to_mm(bb.GetHeight()) - 0.1
print(f"board {W:.2f} x {H:.2f} mm")

panel = pcbnew.LoadBoard(SRC)          # keeps the stackup, design rules and net classes of the source
for it in list(panel.GetFootprints()) + list(panel.GetTracks()) + list(panel.GetDrawings()) + list(panel.Zones()):
    panel.Delete(it)

def on_outline(s):
    """True for the single board's outer outline (lines / corner arcs on the bounding box)"""
    pts = [s.GetStart(), s.GetEnd()]
    near = lambda p: min(abs(to_mm(p.x) - X0), abs(to_mm(p.x) - X0 - W), abs(to_mm(p.y) - Y0), abs(to_mm(p.y) - Y0 - H)) < CORNER_R + 0.01
    return all(near(p) for p in pts)

for k in range(COLS * ROWS):
    c, r = k % COLS, k // COLS
    dx, dy = c * (W + GAP), r * (H + GAP)
    off = pcbnew.VECTOR2I(mm(dx), mm(dy))
    src = pcbnew.LoadBoard(SRC)
    netmap = {}
    def net(n):
        name = n.GetNetname()
        if not name: return None
        if name not in netmap:
            ni = pcbnew.NETINFO_ITEM(panel, f"P{k + 1}/{name}"); panel.Add(ni); netmap[name] = ni
        return netmap[name]
    for fp in src.GetFootprints():
        n = pcbnew.FOOTPRINT(fp)
        n.SetReference(f"{fp.GetReference()}_{k + 1}")
        n.Move(off); panel.Add(n)
        for p in n.Pads():
            m = net(p.GetNet())
            if m: p.SetNet(m)
    for t in src.GetTracks():
        n = t.Duplicate().Cast(); n.Move(off); panel.Add(n)
        m = net(t.GetNet())
        if m: n.SetNet(m)
    for z in src.Zones():
        n = z.Duplicate().Cast(); n.Move(off); panel.Add(n)
        if not z.GetIsRuleArea():
            m = net(z.GetNet())
            if m: n.SetNet(m)
    for d in src.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and isinstance(d, pcbnew.PCB_SHAPE) and on_outline(d):
            continue
        n = d.Duplicate().Cast(); n.Move(off); panel.Add(n)
    t = pcbnew.PCB_TEXT(panel); t.SetText(f"Pager {k + 1}"); t.SetLayer(pcbnew.F_SilkS)
    t.SetPosition(pcbnew.VECTOR2I(mm(X0 + dx + LABEL_AT[0]), mm(Y0 + dy + LABEL_AT[1])))
    t.SetTextAngleDegrees(LABEL_ROT); t.SetTextSize(pcbnew.VECTOR2I(mm(LABEL_H), mm(LABEL_H)))
    t.SetTextThickness(mm(0.22)); panel.Add(t)

# panel outline: rounded boards + tabs across the gaps
shapes = []
for k in range(COLS * ROWS):
    c, r = k % COLS, k // COLS
    x, y = X0 + c * (W + GAP), Y0 + r * (H + GAP)
    shapes.append(box(x, y, x + W, y + H).buffer(-CORNER_R).buffer(CORNER_R, quad_segs=8))
    if c < COLS - 1:      # vertical gap to the right
        for ty in TABS_Y: shapes.append(box(x + W - 0.5, y + ty - TAB_W / 2, x + W + GAP + 0.5, y + ty + TAB_W / 2))
    if r < ROWS - 1:      # horizontal gap below
        for tx in TABS_X: shapes.append(box(x + tx - TAB_W / 2, y + H - 0.5, x + tx + TAB_W / 2, y + H + GAP + 0.5))
outline = unary_union(shapes)
assert outline.geom_type == "Polygon", outline.geom_type
rings = [outline.exterior] + list(outline.interiors)
for ring in rings:
    pts = list(ring.coords)
    for a, b in zip(pts, pts[1:]):
        s = pcbnew.PCB_SHAPE(panel); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1]))); s.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
        s.SetWidth(mm(0.1)); panel.Add(s)

pcbnew.ZONE_FILLER(panel).Fill(panel.Zones())
panel.Save(OUT)
pw, ph = COLS * W + (COLS - 1) * GAP, ROWS * H + (ROWS - 1) * GAP
print(f"{OUT}: {COLS} x {ROWS} boards, panel {pw:.1f} x {ph:.1f} mm, {len(panel.GetFootprints())} footprints, "
      f"{len(outline.interiors)} inner openings in the outline")
