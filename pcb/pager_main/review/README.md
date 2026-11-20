# Review package: pager board (pager_main, ESP32-S3)

Start with `design_description.md`, then `schematic.pdf`.

| File | What it is |
|---|---|
| `design_description.md` | what the board does, power path, GPIO map, expected currents, **the specific questions** |
| `schematic.pdf` / `.svg` | schematic, generated from the design data (blue labels with the same name are connected) |
| `netlist.md` | every net and every pin on it, generated from the same data |
| `parts_list.csv` | all parts, values, LCSC numbers with part-page links (datasheets are linked there), who fits them |
| `netlist_check.txt` | result of the independent check that every pad on the PCB is on the net the design says |
| `drc_report.txt` | KiCad DRC of the routed board |
| `pcb_top.png`, `pcb_bottom.png` | board renders (bottom mirrored, as seen from below) |
| `top_1to1.pdf`, `bottom_1to1_seen_from_below.pdf` | 1:1 prints of the copper / silk layers |
| `pager_main.kicad_pcb`, `pager_main.kicad_pro` | KiCad 7 board (no separate KiCad schematic: the circuit is defined in `design_main.py`) |
| `pager_main_gerbers.zip`, `bom_jlc.csv`, `cpl_jlc.csv` | the files that would be sent to JLCPCB |

Regenerate: `python3 schematic.py` (schematic + net list) and `sh make_review.sh` (this package) in `pcb/pager_main/`.
