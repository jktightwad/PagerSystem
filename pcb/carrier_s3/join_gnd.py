"""Joins stranded GND pour pieces to the main GND network with vias.

    python3 join_gnd.py board.kicad_pcb

Builds the GND connectivity from the filled zones (pieces per layer), GND vias and
through-hole pads (both layers) and SMD pads (the piece they sit in). For every piece
not connected to the largest group, it looks for a spot inside that piece that also
lies inside a main-group piece on the other layer, with clearance for a via, and puts
a GND via there. Repeats until nothing changes, refills, writes drc_report.txt.
"""
import math, os, sys
import pcbnew

PCB = sys.argv[1]
VIA_D, VIA_DRILL, CLR = 0.6, 0.3, 0.25

def mm(v): return pcbnew.FromMM(v)
def to_mm(v): return pcbnew.ToMM(v)

b = pcbnew.LoadBoard(PCB)
g = b.FindNet("GND").GetNetCode()
filler = pcbnew.ZONE_FILLER(b)
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)

def obstacles():
    obst = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == g and p.GetDrillSize().x == 0: continue
            obst.append(("pt", to_mm(p.GetPosition().x), to_mm(p.GetPosition().y), to_mm(math.hypot(p.GetSize().x, p.GetSize().y)) / 2 + (0.3 if p.GetDrillSize().x else 0)))
    for t in b.GetTracks():
        if t.GetNetCode() == g and t.Type() != pcbnew.PCB_VIA_T: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            obst.append(("pt", to_mm(t.GetPosition().x), to_mm(t.GetPosition().y), to_mm(t.GetWidth()) / 2 + 0.2))   # keeps drills >= 0.25 mm apart
        else:
            obst.append(("seg", to_mm(t.GetStart().x), to_mm(t.GetStart().y), to_mm(t.GetEnd().x), to_mm(t.GetEnd().y), to_mm(t.GetWidth()) / 2))
    return obst

def seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / L2))
    return math.hypot(px - x0 - t * dx, py - y0 - t * dy)

novia = [z for z in b.Zones() if z.GetIsRuleArea() and (z.GetDoNotAllowVias() or z.GetDoNotAllowCopperPour())]
outline = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline)

def via_ok(x, y, obst):
    for k in range(17):
        a = 2 * math.pi * k / 16; rr = 0 if k == 16 else 0.55
        v = pcbnew.VECTOR2I(mm(x + rr * math.cos(a)), mm(y + rr * math.sin(a)))
        if not outline.Contains(v): return False
        if any(z.Outline().Contains(v) for z in novia): return False
    need = VIA_D / 2 + CLR
    for o in obst:
        if o[0] == "pt":
            if math.hypot(x - o[1], y - o[2]) < need + o[3]: return False
        elif seg_dist(x, y, *o[1:5]) < need + o[5]: return False
    return True

def groups():
    """union-find over pieces; returns list of (layer, piece SHAPE_POLY_SET, group id), main group id"""
    pieces = []
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetCode() != g: continue
        pl = z.GetFilledPolysList(z.GetLayer())
        for i in range(pl.OutlineCount()):
            sp = pcbnew.SHAPE_POLY_SET(); sp.AddOutline(pl.COutline(i)); pieces.append((z.GetLayer(), sp))
    parent = list(range(len(pieces)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def union(i, j): parent[find(i)] = find(j)
    links = [t.GetPosition() for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == g]
    links += [p.GetPosition() for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetCode() == g and p.GetDrillSize().x]
    for pos in links:
        hit = [i for i, (_, sp) in enumerate(pieces) if sp.Contains(pos)]
        for i in hit[1:]: union(hit[0], i)
    # GND tracks join the pieces their ends sit in
    for t in b.GetTracks():
        if t.GetNetCode() == g and t.Type() != pcbnew.PCB_VIA_T:
            hit = [i for i, (ly, sp) in enumerate(pieces) if ly == t.GetLayer() and (sp.Contains(t.GetStart()) or sp.Contains(t.GetEnd()))]
            for i in hit[1:]: union(hit[0], i)
    size = {}
    for i, (_, sp) in enumerate(pieces): size[find(i)] = size.get(find(i), 0) + sp.Area()
    main = max(size, key=size.get) if size else None
    return [(ly, sp, find(i)) for i, (ly, sp) in enumerate(pieces)], main

added = 0
for rnd in range(6):
    filler.Fill(b.Zones())
    pcs, main = groups()
    stray = [(ly, sp, gid) for ly, sp, gid in pcs if gid != main]
    if not stray: break
    obst = obstacles(); done_groups = set(); fixed = 0
    mains = {ly: [sp for l2, sp, gid in pcs if gid == main and l2 == ly] for ly in LAYERS}
    for ly, sp, gid in sorted(stray, key=lambda t: -t[1].Area()):
        if gid in done_groups: continue
        other = LAYERS[1] if ly == LAYERS[0] else LAYERS[0]
        bb = sp.BBox(); found = None
        yy = to_mm(bb.GetTop())
        while yy <= to_mm(bb.GetBottom()) and not found:
            xx = to_mm(bb.GetLeft())
            while xx <= to_mm(bb.GetRight()):
                v = pcbnew.VECTOR2I(mm(xx), mm(yy))
                if sp.Contains(v) and any(m.Contains(v) for m in mains[other]) and via_ok(xx, yy, obst):
                    found = (xx, yy); break
                xx += 0.2
            yy += 0.2
        if found:
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(found[0]), mm(found[1]))); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL))
            v.SetNet(b.FindNet("GND")); b.Add(v); obst.append(("pt", found[0], found[1], VIA_D / 2 + 0.2))
            done_groups.add(gid); fixed += 1; added += 1
        else:
            c = sp.BBox().GetCenter()
            print(f"  no via spot for a stray piece on {b.GetLayerName(ly)} at x {to_mm(c.x):.2f} y {to_mm(c.y):.2f} (area {sp.Area() / 1e12:.2f} mm2)")
    print(f"round {rnd + 1}: {len(stray)} stray pieces, {fixed} joined")
    if not fixed: break
# fallback: GND pads still stranded -> a short GND track from the pad to the nearest main-group GND via,
# routed with the grid router around all existing copper
filler.Fill(b.Zones())
pcs, main = groups()
stray = [(ly, sp) for ly, sp, gid in pcs if gid != main]
# GND pads that KiCad's DRC reports as unconnected (e.g. the pour never reaches them)
import re
drc_pads = set()
rep0 = os.path.join(os.path.dirname(PCB) or ".", "drc_report.txt")
pcbnew.WriteDRCReport(b, rep0, pcbnew.EDA_UNITS_MILLIMETRES, True)
txt = open(rep0).read()
for block in txt.split("[unconnected_items]")[1:]:
    for m in re.finditer(r"Pad (\S+) \[GND\] of (\S+)", block.split("\n[")[0]):
        drc_pads.add(f"{m.group(2)}.{m.group(1)}")
if stray or drc_pads:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from route_pcb import Router, G as GRID
    r = Router(b)
    for t in b.GetTracks():                    # existing copper becomes an obstacle (or own net)
        code = t.GetNetCode()
        if t.Type() == pcbnew.PCB_VIA_T:
            c = (to_mm(t.GetPosition().x), to_mm(t.GetPosition().y))
            for l in (0, 1): r.mark_track(c, c, l, to_mm(t.GetWidth()) / 2, code)
        else:
            l = 0 if t.GetLayer() == pcbnew.F_Cu else 1
            r.mark_track((to_mm(t.GetStart().x), to_mm(t.GetStart().y)), (to_mm(t.GetEnd().x), to_mm(t.GetEnd().y)), l, to_mm(t.GetWidth()) / 2, code)
    net = b.FindNet("GND")
    main_vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == g and
                 any(gid == main and sp.Contains(t.GetPosition()) for _, sp, gid in pcs)]
    targets = set()
    for v in main_vias:
        cr, cc = r.cell(to_mm(v.GetPosition().x), to_mm(v.GetPosition().y))
        for l in (0, 1): targets.add((l, cr, cc))
    for ref_pin, cells in r.netpads.get("GND", []):
        lay_cells = list(cells)
        pos = [p for fp in b.GetFootprints() for p in fp.Pads() if f"{fp.GetReference()}.{p.GetNumber()}" == ref_pin][0].GetPosition()
        in_stray = any(sp.Contains(pos) for ly, sp in stray if (ly == pcbnew.F_Cu) == any(l == 0 for l, _, _ in lay_cells))
        if not in_stray and ref_pin not in drc_pads:
            continue
        free, vok = r.free_maps(g, 0.15)
        for l, rr_, cc_ in lay_cells: free[l, rr_, cc_] = True
        for l, rr_, cc_ in targets: free[l, rr_, cc_] = True
        path = r.astar(lay_cells, targets, free, vok)
        if path:
            r.commit(path, net, 0.15); print(f"  GND track from {ref_pin} to the main GND network")
        else:
            print(f"  could not reach {ref_pin}")
filler.Fill(b.Zones())
b.Save(PCB)
rep = os.path.join(os.path.dirname(PCB) or ".", "drc_report.txt")
pcbnew.WriteDRCReport(b, rep, pcbnew.EDA_UNITS_MILLIMETRES, True)
print(f"added {added} joining vias; DRC in {rep}")
