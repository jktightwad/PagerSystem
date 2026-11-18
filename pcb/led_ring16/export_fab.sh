#!/bin/sh
# JLCPCB files for the 16-LED ring: Gerbers + drill zip, BOM and CPL (top side).
set -e
cd "$(dirname "$0")"
rm -rf fab; mkdir -p fab/gerbers
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask -o fab/gerbers/ led_ring16.kicad_pcb >/dev/null
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th \
  --excellon-oval-format route -o fab/gerbers/ led_ring16.kicad_pcb >/dev/null
kicad-cli pcb export pos --format csv --units mm --side front --smd-only -o fab/pos_front.csv led_ring16.kicad_pcb >/dev/null
python3 - <<'PY'
import csv
rows = list(csv.DictReader(open("fab/pos_front.csv")))
leds = sorted([r["Ref"] for r in rows if r["Ref"].startswith("D")], key=lambda r: int(r[1:]))
caps = sorted([r["Ref"] for r in rows if r["Ref"].startswith("C")], key=lambda r: int(r[1:]))
with open("fab/bom_jlc.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    w.writerow(["XL-5050RGBC-2812B", ",".join(leds), "5050", "C2843785"])
    w.writerow(["100nF", ",".join(caps), "0603", "C14663"])
with open("fab/cpl_jlc.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for r in rows:
        w.writerow([r["Ref"], f'{float(r["PosX"]):.4f}', f'{float(r["PosY"]):.4f}', "Top", f'{float(r["Rot"]) % 360:.2f}'])
print(len(leds), "LEDs,", len(caps), "caps")
PY
(cd fab/gerbers && zip -q ../led_ring16_gerbers.zip *)
