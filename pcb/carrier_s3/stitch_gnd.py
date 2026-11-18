"""Adds GND stitching vias to a routed board so the top and bottom GND pours join up,
refills the zones and rewrites drc_report.txt next to the board.

    python3 stitch_gnd.py board.kicad_pcb [pitch_mm]

A via goes on a grid point only where it keeps clearance (0.2 mm + margin) from every
non-GND pad, track and via on both layers, from holes and the board edge, and outside
rule areas that forbid vias.
"""
import math, os, sys
import pcbnew

PCB = sys.argv[1]
PITCH = float(sys.argv[2]) if len(sys.argv) > 2 else 1.6
VIA_D, VIA_DRILL, CLR, EDGE = 0.6, 0.3, 0.25, 0.5

def mm(v): return pcbnew.FromMM(v)
def to_mm(v): return pcbnew.ToMM(v)

b = pcbnew.LoadBoard(PCB)
gnd = b.FindNet("GND")
outline = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline)
bb = b.GetBoardEdgesBoundingBox()

obst = []          # (kind, geometry...) of non-GND copper and holes
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetCode() == gnd.GetNetCode() and p.GetDrillSize().x == 0:
            continue
        r = max(p.GetSize().x, p.GetSize().y) / 2
        obst.append(("pt", to_mm(p.GetPosition().x), to_mm(p.GetPosition().y), to_mm(r) + (0.3 if p.GetDrillSize().x else 0)))
for t in b.GetTracks():
    if t.GetNetCode() == gnd.GetNetCode():
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        obst.append(("pt", to_mm(t.GetPosition().x), to_mm(t.GetPosition().y), to_mm(t.GetWidth()) / 2 + 0.2))
    else:
        obst.append(("seg", to_mm(t.GetStart().x), to_mm(t.GetStart().y), to_mm(t.GetEnd().x), to_mm(t.GetEnd().y), to_mm(t.GetWidth()) / 2))
noviazones = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]

def seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / L2))
    return math.hypot(px - x0 - t * dx, py - y0 - t * dy)

def ok(x, y):
    v = pcbnew.VECTOR2I(mm(x), mm(y))
    if not outline.Contains(v): return False
    # distance to the board edge (incl. internal cut-outs)
    for k in range(16):
        a = 2 * math.pi * k / 16
        if not outline.Contains(pcbnew.VECTOR2I(mm(x + EDGE * math.cos(a)), mm(y + EDGE * math.sin(a)))): return False
    for z in noviazones:                       # the whole via, not just its centre
        for k in range(9):
            a = 2 * math.pi * k / 8
            rr = 0 if k == 8 else VIA_D / 2 + 0.1
            if z.Outline().Contains(pcbnew.VECTOR2I(mm(x + rr * math.cos(a)), mm(y + rr * math.sin(a)))): return False
    need = VIA_D / 2 + CLR
    for o in obst:
        if o[0] == "pt":
            if math.hypot(x - o[1], y - o[2]) < need + o[3]: return False
        elif seg_dist(x, y, *o[1:5]) < need + o[5]:
            return False
    return True

added = 0
added_extra = []
x0, y0, x1, y1 = to_mm(bb.GetLeft()), to_mm(bb.GetTop()), to_mm(bb.GetRight()), to_mm(bb.GetBottom())
y = y0 + PITCH / 2
while y < y1:
    x = x0 + PITCH / 2
    while x < x1:
        if ok(x, y):
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL))
            v.SetNet(gnd); b.Add(v); added += 1
            obst.append(("pt", x, y, VIA_D / 2))       # keep vias apart from each other
        x += PITCH
    y += PITCH
def add_via(x, y):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL))
    v.SetNet(gnd); b.Add(v); obst.append(("pt", x, y, VIA_D / 2))

# fill, then give every GND fill piece that has no via / through-hole GND pad in it a via of its own
filler = pcbnew.ZONE_FILLER(b)
for rnd in range(3):
    filler.Fill(b.Zones())
    anchors = [t.GetPosition() for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gnd.GetNetCode()]
    anchors += [p.GetPosition() for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetCode() == gnd.GetNetCode() and p.GetDrillSize().x]
    fixed = 0
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetCode() != gnd.GetNetCode(): continue
        polys = z.GetFilledPolysList(z.GetLayer())
        for i in range(polys.OutlineCount()):
            piece = pcbnew.SHAPE_POLY_SET(); piece.AddOutline(polys.COutline(i))
            if any(piece.Contains(a) for a in anchors): continue
            pb = polys.COutline(i).BBox()
            done = False
            yy = to_mm(pb.GetTop())
            while yy <= to_mm(pb.GetBottom()) and not done:
                xx = to_mm(pb.GetLeft())
                while xx <= to_mm(pb.GetRight()):
                    if piece.Contains(pcbnew.VECTOR2I(mm(xx), mm(yy))) and ok(xx, yy):
                        add_via(xx, yy); fixed += 1; added_extra.append((xx, yy)); done = True; break
                    xx += 0.25
                yy += 0.25
    print(f"round {rnd + 1}: {fixed} vias added to isolated GND pieces")
    if not fixed: break
b.Save(PCB)
rep = os.path.join(os.path.dirname(PCB) or ".", "drc_report.txt")
pcbnew.WriteDRCReport(b, rep, pcbnew.EDA_UNITS_MILLIMETRES, True)
print(f"added {added} GND vias, zones refilled, DRC in {rep}")
