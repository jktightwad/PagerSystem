"""Removes GND vias that KiCad's DRC reports as dangling (left in a pour island that island
removal deleted), and for each hole_near_hole pair the via that no track ends on (a stitch
via next to a fan-out / routed via). Edits the .kicad_pcb text (removing vias through the
Python API has crashed), then refills the zones and rewrites drc_report.txt.

    python3 remove_dangling.py board.kicad_pcb
"""
import os, re, sys
import pcbnew

PCB = sys.argv[1]
REP = os.path.join(os.path.dirname(PCB) or ".", "drc_report.txt")

def report():
    b = pcbnew.LoadBoard(PCB); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(PCB)
    pcbnew.WriteDRCReport(b, REP, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return b, open(REP).read()

def blocks(txt, kind):
    out = []
    for blk in txt.split("\n[")[1:]:
        if blk.startswith(kind):
            out.append([(float(x), float(y), rest) for x, y, rest in re.findall(r"@\(([-\d.]+) mm, ([-\d.]+) mm\): (.*)", blk)])
    return out

for rnd in range(3):
    b, txt = report()
    track_ends = {(round(pcbnew.ToMM(p.x), 3), round(pcbnew.ToMM(p.y), 3)) for t in b.GetTracks()
                  if t.Type() != pcbnew.PCB_VIA_T for p in (t.GetStart(), t.GetEnd())}
    kill = set()
    for items in blocks(txt, "via_dangling"):
        for x, y, what in items:
            if what.startswith("Via [GND]"): kill.add((round(x, 3), round(y, 3)))
    for items in blocks(txt, "hole_near_hole"):
        vias = [(round(x, 3), round(y, 3)) for x, y, what in items if what.startswith("Via [GND]")]
        loose = [v for v in vias if v not in track_ends]
        if len(vias) == 2 and loose: kill.add(loose[0])
    if not kill: break
    s = open(PCB).read()
    n0 = s.count("(via ")
    def drop(m):
        x, y = round(float(m.group(1)), 3), round(float(m.group(2)), 3)
        return "" if (x, y) in kill else m.group(0)
    s = re.sub(r"\n\s*\(via \(at ([-\d.]+) ([-\d.]+)\)[^\n]*", drop, s)
    open(PCB, "w").write(s)
    print(f"round {rnd + 1}: removed {n0 - s.count('(via ')} vias")
b, txt = report()
print("DRC in", REP)
