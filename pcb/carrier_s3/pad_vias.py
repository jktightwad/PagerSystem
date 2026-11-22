"""Gives cut-off pads of a net (default GND) a short stub track + via to the other layer, where it is legal.

    python3 pad_vias.py board.kicad_pcb REF.PIN [REF.PIN ...] [--net GND]

For each pad it tries directions every 15 degrees and stub lengths 0.9-3.0 mm, and keeps the shortest
candidate whose stub and via clear (by the board's 0.2 mm copper clearance + 0.02) every copper item of
another net on the layers they touch, every hole by 0.25 mm drill-to-drill, the board edge / cut-outs
by 0.5 mm, and rule areas that forbid vias or tracks. Clearance is checked with exact geometry (pad
polygons, track capsules, via circles). Saves in place; refill zones and run DRC afterwards.
"""
import math, sys
import pcbnew
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union

PCB = sys.argv[1]
args = [a for a in sys.argv[2:] if not a.startswith("--")]
NET = sys.argv[sys.argv.index("--net") + 1] if "--net" in sys.argv else "GND"
if NET in args: args.remove(NET)
CLR, VIA_D, VIA_DRILL, STUB_W, EDGE = 0.22, 0.6, 0.3, 0.25, 0.5
mm = pcbnew.ToMM; F = pcbnew.FromMM
b = pcbnew.LoadBoard(PCB)
net = b.FindNet(NET); code = net.GetNetCode()

def poly_of(sps):
    out = []
    for i in range(sps.OutlineCount()):
        o = sps.COutline(i)
        pts = [(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())]
        if len(pts) >= 3: out.append(Polygon(pts).buffer(0))
    return unary_union(out)

def foreign(layer):
    geo = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() == code and p.GetNetCode() > 0: continue
            if p.IsOnLayer(layer):
                geo.append(poly_of(p.GetEffectivePolygon()))
    for t in b.GetTracks():
        if t.GetNetCode() == code: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            geo.append(Point(mm(t.GetPosition().x), mm(t.GetPosition().y)).buffer(mm(t.GetWidth()) / 2))
        elif t.GetLayer() == layer:
            geo.append(LineString([(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]).buffer(mm(t.GetWidth()) / 2))
    return unary_union(geo)

FG = {pcbnew.F_Cu: foreign(pcbnew.F_Cu), pcbnew.B_Cu: foreign(pcbnew.B_Cu)}
holes = [Point(mm(p.GetPosition().x), mm(p.GetPosition().y)).buffer(mm(p.GetDrillSize().x) / 2)
         for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSize().x > 0]
holes += [Point(mm(t.GetPosition().x), mm(t.GetPosition().y)).buffer(mm(t.GetDrill()) / 2) for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
HOLES = unary_union(holes)
ol = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ol)
board_poly = []
for i in range(ol.OutlineCount()):
    o = ol.COutline(i); outer = Polygon([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
    hs = [[(mm(ol.CHole(i, h).CPoint(k).x), mm(ol.CHole(i, h).CPoint(k).y)) for k in range(ol.CHole(i, h).PointCount())] for h in range(ol.HoleCount(i))]
    board_poly.append(Polygon(outer.exterior.coords, hs))
BOARD = unary_union(board_poly).buffer(-EDGE)
NOVIA = unary_union([poly_of(z.Outline()) for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()])
NOTRK = {L: unary_union([poly_of(z.Outline()) for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowTracks() and z.IsOnLayer(L)])
         for L in (pcbnew.F_Cu, pcbnew.B_Cu)}

for refpin in args:
    ref, pin = refpin.split(".")
    pad = [p for f in b.GetFootprints() if f.GetReference() == ref for p in f.Pads() if p.GetNumber() == pin][0]
    L = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    O = pcbnew.B_Cu if L == pcbnew.F_Cu else pcbnew.F_Cu
    px, py = mm(pad.GetPosition().x), mm(pad.GetPosition().y)
    best = None
    for d10 in range(9, 31):
        d = d10 / 10
        for k in range(24):
            a = math.radians(15 * k); vx, vy = px + d * math.cos(a), py + d * math.sin(a)
            via = Point(vx, vy).buffer(VIA_D / 2); stub = LineString([(px, py), (vx, vy)]).buffer(STUB_W / 2)
            if not BOARD.contains(via) or not BOARD.contains(stub): continue
            if via.intersects(NOVIA) or stub.intersects(NOTRK[L]) or via.intersects(NOTRK[L]): continue
            if FG[L].distance(via) < CLR or FG[O].distance(via) < CLR or FG[L].distance(stub) < CLR: continue
            if HOLES.distance(Point(vx, vy).buffer(VIA_DRILL / 2)) < 0.25: continue
            best = (vx, vy); break
        if best: break
    if not best:
        print(f"  {refpin}: no legal stub + via within 3 mm"); continue
    t = pcbnew.PCB_TRACK(b); t.SetStart(pad.GetPosition()); t.SetEnd(pcbnew.VECTOR2I(F(best[0]), F(best[1])))
    t.SetWidth(F(STUB_W)); t.SetLayer(L); t.SetNet(net); b.Add(t)
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(F(best[0]), F(best[1]))); v.SetWidth(F(VIA_D)); v.SetDrill(F(VIA_DRILL)); v.SetNet(net); b.Add(v)
    FG_new = Point(best).buffer(VIA_D / 2)
    HOLES = HOLES.union(Point(best).buffer(VIA_DRILL / 2))
    print(f"  {refpin}: stub {math.hypot(best[0] - px, best[1] - py):.1f} mm + via")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
