#!/bin/sh
# render top / bottom views of the board to PNG (needs node + playwright)
S=${S:-/tmp}
kicad-cli pcb export svg --layers F.Cu,F.SilkS,F.Mask,Edge.Cuts,B.SilkS --page-size-mode 2 --exclude-drawing-sheet -o $S/pcb_top.svg pager_main.kicad_pcb >/dev/null
kicad-cli pcb export svg --layers B.Cu,B.SilkS,Edge.Cuts --mirror --page-size-mode 2 --exclude-drawing-sheet -o $S/pcb_bot.svg pager_main.kicad_pcb >/dev/null
NODE_PATH=$(npm root -g) node ../carrier_s3/svg2png.js $S/pcb_top.svg ${1:-pcb_top.png} 4
NODE_PATH=$(npm root -g) node ../carrier_s3/svg2png.js $S/pcb_bot.svg ${2:-pcb_bottom.png} 4
