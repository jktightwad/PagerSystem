#!/bin/sh
# JLCPCB files: Gerbers + drill zip, BOM and CPL.
#   sh export_fab.sh                      -> main board (Economic PCBA, top side only)   -> fab/
#   sh export_fab.sh panel                -> 3 x 2 panel from panelize.py (Economic, top side only) -> fab_panel/
#   sh export_fab.sh smdconn              -> SMD-connector variant (Standard PCBA, both sides,
#                                            JLC also fits the connectors + switch) -> fab_smdconn/
set -e
cd "$(dirname "$0")"
if [ "$1" = "smdconn" ]; then BOARD=pager_main_smdconn.kicad_pcb; OUTD=fab_smdconn; VARIANT=smdconn
elif [ "$1" = "panel" ]; then BOARD=pager_panel.kicad_pcb; OUTD=fab_panel; VARIANT=panel
else BOARD=pager_main.kicad_pcb; OUTD=fab; VARIANT=main; fi
rm -rf $OUTD; mkdir -p $OUTD/gerbers
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask -o $OUTD/gerbers/ $BOARD >/dev/null
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th \
  --excellon-oval-format route -o $OUTD/gerbers/ $BOARD >/dev/null
kicad-cli pcb export pos --format csv --units mm --side both -o $OUTD/pos_all.csv $BOARD >/dev/null
OUTD=$OUTD VARIANT=$VARIANT python3 - <<'PY'
import csv, os, re
from collections import defaultdict
from design_main import PARTS
outd, variant = os.environ["OUTD"], os.environ["VARIANT"]
parts = {r: (v, l) for r, (v, l, n) in PARTS.items()}
if variant == "smdconn":   # JLC also fits these (Standard PCBA, both sides)
    parts["J1"] = ("XH-3PWB SMD right angle (DEALON)", "C2905025")
    parts["J2"] = ("XH-2PWB SMD right angle (DEALON)", "C2905024")
    parts["SW1"] = ("SS12F44G4 slide switch (through-hole)", "C2887261")
BOTTOM = {"J1", "J2", "SW1"}   # parts that sit under the board
FOOT = {"R": "0603", "C": "0603", "Q": "SOT-23", "D": "SOD-123", "L": "5050", "B": "SMD 9x9", "J": "XH SMD", "S": "THT", "U": "SC-70-6"}
# panel copies are LED1_3 etc.: the part data comes from the base reference
base = (lambda r: r.rsplit("_", 1)[0]) if variant == "panel" else (lambda r: r)
with open(f"{outd}/pos_all.csv") as f:
    refs_on_board = [row["Ref"] for row in csv.DictReader(f)]
groups = defaultdict(list)
for ref in refs_on_board:
    val, lcsc = parts.get(base(ref), (None, None))
    if lcsc: groups[(val, lcsc)].append(ref)
key = lambda r: (re.sub(r"[\d_]", "", r), [int(x) for x in re.findall(r"\d+", r)])
with open(f"{outd}/bom_jlc.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, lcsc), refs in sorted(groups.items()):
        refs.sort(key=key)
        foot = {"C3": "1206", "C4": "1206"}.get(base(refs[0]), FOOT.get(refs[0][0], ""))
        w.writerow([val, ",".join(refs), foot, lcsc])
with open(f"{outd}/pos_all.csv") as f, open(f"{outd}/cpl_jlc.csv", "w", newline="") as o:
    w = csv.writer(o); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for row in csv.DictReader(f):
        ref = row["Ref"]
        if base(ref) in parts and parts[base(ref)][1]:
            side = "Bottom" if row["Side"].lower().startswith("b") else "Top"
            # hand-built footprints mounted under the board (pads on B.Cu / body below) are recorded by
            # KiCad as top-side footprints: list them as Bottom for JLC
            if base(ref) in BOTTOM: side = "Bottom"
            w.writerow([ref, f'{float(row["PosX"]):.4f}', f'{float(row["PosY"]):.4f}', side, f'{float(row["Rot"]) % 360:.2f}'])
print(f"{outd}/bom_jlc.csv, {outd}/cpl_jlc.csv written")
PY
(cd $OUTD/gerbers && zip -q ../$(basename $BOARD .kicad_pcb)_gerbers.zip *)
