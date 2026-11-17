#!/bin/sh
# Fabrication files for JLCPCB / PCBWay from carrier_s3.kicad_pcb.
# Writes fab/gerbers/*.g?? + drill, fab/carrier_s3_gerbers.zip, fab/bom_jlc.csv, fab/cpl_jlc.csv
set -e
cd "$(dirname "$0")"
rm -rf fab; mkdir -p fab/gerbers
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask -o fab/gerbers/ carrier_s3.kicad_pcb
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th \
  --excellon-oval-format route -o fab/gerbers/ carrier_s3.kicad_pcb
kicad-cli pcb export pos --format csv --units mm --side front --smd-only -o fab/pos_front.csv carrier_s3.kicad_pcb
python3 make_jlc.py
(cd fab/gerbers && zip -q ../carrier_s3_gerbers.zip *)
ls fab fab/gerbers
