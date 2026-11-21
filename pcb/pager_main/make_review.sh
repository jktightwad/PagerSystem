#!/bin/sh
# Builds review/ (schematic, net list, description, parts list, board files) and review/pager_main_review.zip
set -e
cd "$(dirname "$0")"
python3 schematic.py
python3 parts_list.py
NODE_PATH=$(npm root -g) node ../carrier_s3/svg2pdf.js review/schematic.svg review/schematic.pdf
python3 check_netlist.py > review/netlist_check.txt
cp drc_report.txt pcb_top.png pcb_bottom.png pager_main.kicad_pcb pager_main.kicad_pro review/
cp print/top_1to1.pdf print/bottom_1to1_seen_from_below.pdf review/
cp fab/pager_main_gerbers.zip fab/bom_jlc.csv fab/cpl_jlc.csv review/
rm -f review/pager_main_review.zip
(cd review && zip -q pager_main_review.zip README.md design_description.md schematic.pdf schematic.svg netlist.md \
  parts_list.csv netlist_check.txt drc_report.txt pcb_top.png pcb_bottom.png top_1to1.pdf \
  bottom_1to1_seen_from_below.pdf pager_main.kicad_pcb pager_main.kicad_pro pager_main_gerbers.zip bom_jlc.csv cpl_jlc.csv)
echo "review/pager_main_review.zip"
