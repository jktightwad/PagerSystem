"""fab/pos_front.csv (kicad-cli) + design.py -> JLCPCB assembly BOM and CPL.
Only parts with an LCSC number are listed (the rest are hand-soldered)."""
import csv
from collections import defaultdict
from design import PARTS

FOOT = {"0603": "0603", "1206": "1206", "SOT-23": "SOT-23", "SOD-123": "SOD-123"}
groups = defaultdict(list)
for ref, (val, fp, lcsc, note) in PARTS.items():
    if lcsc: groups[(val, fp, lcsc)].append(ref)
with open("fab/bom_jlc.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fp, lcsc), refs in sorted(groups.items(), key=lambda g: g[1][0]):
        w.writerow([val, ",".join(sorted(refs, key=lambda r: (r[0], int(r[1:])))), FOOT.get(fp, fp), lcsc])
with open("fab/pos_front.csv") as f, open("fab/cpl_jlc.csv", "w", newline="") as o:
    w = csv.writer(o); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for row in csv.DictReader(f):
        ref = row["Ref"]
        if ref in PARTS and PARTS[ref][2]:
            w.writerow([ref, row["PosX"] + "mm", row["PosY"] + "mm", "Top", row["Rot"]])
print("fab/bom_jlc.csv, fab/cpl_jlc.csv written")
