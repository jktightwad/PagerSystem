#!/bin/sh
# JLCPCB files for the combined pager board: Gerbers + drill zip, BOM and CPL (top-side assembly).
set -e
cd "$(dirname "$0")"
rm -rf fab; mkdir -p fab/gerbers
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask -o fab/gerbers/ pager_main.kicad_pcb >/dev/null
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th \
  --excellon-oval-format route -o fab/gerbers/ pager_main.kicad_pcb >/dev/null
kicad-cli pcb export pos --format csv --units mm --side front --smd-only -o fab/pos_front.csv pager_main.kicad_pcb >/dev/null
python3 - <<'PY'
import csv, re
from collections import defaultdict
from design_main import PARTS
FOOT = {"R": "0603", "C": "0603", "Q": "SOT-23", "D": "SOD-123", "L": "5050"}
groups = defaultdict(list)
for ref, (val, lcsc, note) in PARTS.items():
    if lcsc: groups[(val, lcsc)].append(ref)
key = lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0))
with open("fab/bom_jlc.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, lcsc), refs in sorted(groups.items()):
        refs.sort(key=key); w.writerow([val, ",".join(refs), FOOT.get(refs[0][0], ""), lcsc])
with open("fab/pos_front.csv") as f, open("fab/cpl_jlc.csv", "w", newline="") as o:
    w = csv.writer(o); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for row in csv.DictReader(f):
        if row["Ref"] in PARTS and PARTS[row["Ref"]][1]:
            w.writerow([row["Ref"], f'{float(row["PosX"]):.4f}', f'{float(row["PosY"]):.4f}', "Top", f'{float(row["Rot"]) % 360:.2f}'])
print("fab/bom_jlc.csv, fab/cpl_jlc.csv written")
PY
(cd fab/gerbers && zip -q ../pager_main_gerbers.zip *)
