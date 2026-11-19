"""Local rip-up and re-route on a routed board.

    REROUTE_BOX="x0,y0,x1,y1" REROUTE_FANOUT="R2,R7,Q2,C1" python3 reroute_area.py board.kicad_pcb

Every net with a track or via inside the box (KiCad mm) loses all its tracks and vias; the GND
pads named in REROUTE_FANOUT get a short stub + via to the bottom pour first (gnd_fanout from
route_pcb.py); then the ripped nets are routed again around everything that was kept. Retries
with a shuffled order (up to 60). GND stays best effort (the pours finish it). Saves in place
and refills the zones; run stitch_gnd / join_gnd / DRC afterwards as usual.
"""
import os, random, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_pcb
from route_pcb import Router, gnd_fanout, to_mm

PCB = sys.argv[1]
x0, y0, x1, y1 = map(float, os.environ["REROUTE_BOX"].split(","))
FAN = os.environ.get("REROUTE_FANOUT", "")
route_pcb.OPTIONAL.add("GND")
random.seed(int(os.environ.get("ROUTE_SEED", "1")))

def inside(p): return x0 <= to_mm(p.x) <= x1 and y0 <= to_mm(p.y) <= y1

b0 = pcbnew.LoadBoard(PCB)
rip = sorted({t.GetNetname() for t in b0.GetTracks() if inside(t.GetStart()) or inside(t.GetEnd())})
print("ripping up:", " ".join(rip))

def attempt(order):
    b = pcbnew.LoadBoard(PCB)
    for t in [t for t in b.GetTracks() if t.GetNetname() in rip]: b.Delete(t)
    rt = Router(b)
    for t in b.GetTracks():                       # kept copper is an obstacle (or own net)
        code = t.GetNetCode()
        if t.Type() == pcbnew.PCB_VIA_T:
            c = (to_mm(t.GetPosition().x), to_mm(t.GetPosition().y))
            for l in (0, 1): rt.mark_track(c, c, l, to_mm(t.GetWidth()) / 2, code)
            rt.holes[rt.cell(*c)] = True
        else:
            l = 0 if t.GetLayer() == pcbnew.F_Cu else 1
            rt.mark_track((to_mm(t.GetStart().x), to_mm(t.GetStart().y)), (to_mm(t.GetEnd().x), to_mm(t.GetEnd().y)),
                          l, to_mm(t.GetWidth()) / 2, code)
    if FAN: gnd_fanout(rt, FAN)
    failed = [n for n in order if not rt.route_net(n)]
    return b, failed

order = [n for n in rip if n != "GND"] + (["GND"] if "GND" in rip else [])
for k in range(60):
    print(f"attempt {k + 1}: {' '.join(order)}")
    b, failed = attempt(order)
    if not failed: break
    rest = [n for n in order if n not in failed and n != "GND"]; random.shuffle(rest)
    order = failed + rest + (["GND"] if "GND" in rip else [])
else:
    print("could not re-route:", failed); sys.exit(1)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("re-routed and saved", PCB)
