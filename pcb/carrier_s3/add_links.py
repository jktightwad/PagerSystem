"""Adds extra copper paths between two pads of the same net on a routed board (e.g. closing a
power ring into a loop, or a direct feed so a load is not at the end of a daisy chain).

    LINKS='[["VBAT", "LED2.1", "LED3.1", 0.6], ["VBAT", "Q3.3", "U1.B+", 0.6]]' python3 add_links.py board.kicad_pcb

Each link is routed with the grid router around all existing copper (same clearances as
route_pcb.py). A link that finds no path is reported and skipped. Saves in place, refills zones.
"""
import json, os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route_pcb import Router, to_mm

PCB = sys.argv[1]
LINKS = json.loads(os.environ["LINKS"])
b = pcbnew.LoadBoard(PCB)

def build_router():
    r = Router(b)
    for t in b.GetTracks():
        code = t.GetNetCode()
        if t.Type() == pcbnew.PCB_VIA_T:
            c = (to_mm(t.GetPosition().x), to_mm(t.GetPosition().y))
            for l in (0, 1): r.mark_track(c, c, l, to_mm(t.GetWidth()) / 2, code)
            r.holes[r.cell(*c)] = True
        else:
            l = 0 if t.GetLayer() == pcbnew.F_Cu else 1
            r.mark_track((to_mm(t.GetStart().x), to_mm(t.GetStart().y)), (to_mm(t.GetEnd().x), to_mm(t.GetEnd().y)),
                         l, to_mm(t.GetWidth()) / 2, code)
    return r

ok = 0
for netname, a, c, width in LINKS:
    r = build_router()
    net = b.FindNet(netname); code = net.GetNetCode(); hw = width / 2
    pads = dict(r.netpads.get(netname, []))
    if a not in pads or c not in pads:
        print(f"  {netname}: pad {a if a not in pads else c} not found"); continue
    free, vok = r.free_maps(code, hw)
    for l, rr, cc in pads[a] | pads[c]: free[l, rr, cc] = True
    path = r.astar(pads[a], pads[c], free, vok)
    if path:
        r.commit(path, net, hw); ok += 1
        print(f"  {netname}: link {a} - {c} added ({len(path)} cells, {width} mm)")
    else:
        print(f"  {netname}: no path for {a} - {c} at {width} mm")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print(f"{ok} of {len(LINKS)} links added")
