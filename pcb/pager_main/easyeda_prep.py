"""Final step before importing the routed board into EasyEDA Pro (run after every refill):

    python3 easyeda_prep.py pager_main.kicad_pcb

- removes rule areas that only forbid tracks / vias (routing guides, e.g. under the module): EasyEDA
  imports every rule area as a "Prohibited Region" for all copper, so the ground pour there showed as overlaps
- cuts the stored ground fill back 0.3 mm from the remaining pour keep-outs (mounting holes, antenna):
  KiCad fills right up to their edge, which EasyEDA's DRC reports as an overlap
Saves without refilling (a KiCad refill would bring the fill back to the keep-out edge).
(The two steps run in separate processes: the KiCad API's zone list breaks after removing a zone.)
"""
import subprocess, sys
import pcbnew

PCB = sys.argv[1]
def zones(b): return [b.GetArea(i) for i in range(b.GetAreaCount())]

if "--trim" not in sys.argv:
    b = pcbnew.LoadBoard(PCB)
    rm = [z for z in zones(b) if z.GetIsRuleArea() and not z.GetDoNotAllowCopperPour()]
    for z in rm: b.Remove(z)
    b.Save(PCB)
    print(f"removed {len(rm)} routing-only rule areas")
    sys.exit(subprocess.call([sys.executable, __file__, PCB, "--trim"]))

GAP = pcbnew.FromMM(0.3)
b = pcbnew.LoadBoard(PCB)
keep = {}
for z in zones(b):
    if z.GetIsRuleArea() and z.GetDoNotAllowCopperPour():
        for lay in z.GetLayerSet().Seq():
            p = z.Outline().CloneDropTriangulation(); p.Inflate(GAP, 16)
            keep.setdefault(lay, pcbnew.SHAPE_POLY_SET()).BooleanAdd(p, pcbnew.SHAPE_POLY_SET.PM_FAST)
for z in zones(b):
    if z.GetIsRuleArea(): continue
    for lay in z.GetLayerSet().Seq():
        if lay not in keep or not z.HasFilledPolysForLayer(lay): continue
        fp = z.GetFilledPolysList(lay).CloneDropTriangulation()
        before = fp.Area()
        fp.BooleanSubtract(keep[lay], pcbnew.SHAPE_POLY_SET.PM_STRICTLY_SIMPLE)
        fp.Fracture(pcbnew.SHAPE_POLY_SET.PM_STRICTLY_SIMPLE)
        z.SetFilledPolysList(lay, fp)
        print(f"  {z.GetNetname()} {b.GetLayerName(lay)}: fill {before / 1e12:.1f} -> {fp.Area() / 1e12:.1f} mm2")
b.Save(PCB)
