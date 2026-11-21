"""Imports the routed wiring (tracks + vias) from a Specctra .dsn written by another tool (e.g. EasyEDA
Pro's "Auto Router (DSN)" export) onto our placed KiCad board.

    python3 import_dsn_wiring.py placed.kicad_pcb routed.dsn out.kicad_pcb [--skip-gnd-vias]

Coordinates: the .dsn uses its own units ("resolution") with y up from the board's bottom-left corner;
our board has its outline from (0,0) to (W,H) mm with y down, so x_k = x * unit, y_k = H - y * unit.
All tracks already on the placed board are removed first (the .dsn contains them again). GND vias are
dropped with --skip-gnd-vias (stitching vias are redone by stitch_gnd.py).
"""
import re, sys
import pcbnew

src, dsn, out = sys.argv[1:4]
skip_gnd_vias = "--skip-gnd-vias" in sys.argv
s = open(dsn).read()
m = re.search(r"\(resolution\s+(\w+)\s+([\d.]+)\)", s)
unit = {"mil": 0.0254, "um": 0.001, "mm": 1.0, "inch": 25.4}[m.group(1)]
b = pcbnew.LoadBoard(src)
bb = b.GetBoardEdgesBoundingBox()
H = pcbnew.ToMM(bb.GetBottom()) - 0.05            # outline bottom (edge line half width)
def P(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(float(x) * unit), pcbnew.FromMM(H - float(y) * unit))
for t in list(b.GetTracks()): b.Delete(t)
LAY = {"TopLayer": pcbnew.F_Cu, "BottomLayer": pcbnew.B_Cu, "F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
w = s[s.index("(wiring"):]
nt = nv = sk = 0
for lay, wid, pts, net in re.findall(r'\(wire\s*\(path\s+(\S+)\s+([-\d.]+)\s+([-\d.\s]+?)\)\s*\(net\s+"?([^)"]+)"?\)', w):
    xy = pts.split(); n = b.FindNet(net)
    if n is None: print("unknown net", net); continue
    for i in range(0, len(xy) - 2, 2):
        a, c = P(xy[i], xy[i + 1]), P(xy[i + 2], xy[i + 3])
        if a == c: continue
        t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c); t.SetWidth(pcbnew.FromMM(float(wid) * unit))
        t.SetLayer(LAY[lay]); t.SetNet(n); b.Add(t); nt += 1
for name, x, y, net in re.findall(r'\(via\s+(\S+)\s+([-\d.]+)\s+([-\d.]+)\s*\(net\s+"?([^)"]+)"?\)', w):
    if skip_gnd_vias and net == "GND": sk += 1; continue
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(pcbnew.FromMM(0.6)); v.SetDrill(pcbnew.FromMM(0.3))
    v.SetNet(b.FindNet(net)); b.Add(v); nv += 1
b.Save(out)
print(f"{nt} track segments, {nv} vias imported ({sk} GND vias skipped) -> {out}")
