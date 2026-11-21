# Unrouted pager board for an external autorouter (EasyEDA, Freerouting)

| File | What |
|---|---|
| `pager_unrouted_spares_right.kicad_pcb` / `.dsn` | spare-pin through-holes in the two right corners (beside the module pins) |
| `pager_unrouted_spares_left.kicad_pcb` / `.dsn` | spare-pin through-holes in the two left corners (earlier layout) |

`.kicad_pcb` is the KiCad 7 board (for EasyEDA Pro import or KiCad); `.dsn` is the Specctra file for Freerouting.

## Already on the board, keep it
- **VBAT ring:** 1.0 mm copper circle inside the LEDs, with stubs to every LED VDD and capacitor.
- **U2 links:** pin 3 -> 4 -> 6 (MOD5V) and pin 5 -> 2 (GND).

## Keep-outs (check they survived the import; redraw if not)
- **Antenna end:** no copper (tracks, vias, pour) near the module's antenna end on either layer, at the right edge.
- **Under the module:** no bottom-layer tracks between the module's two pin rows (ground pour and vias are allowed).
- **Mounting holes:** small copper keep-outs round the holes.

## Rules
| Item | Value |
|---|---|
| Clearance | 0.2 mm |
| Track | 0.25 mm |
| Via | 0.6 / 0.3 mm |
| Hole to hole | 0.25 mm |
| Copper to edge | 0.5 mm |
| Wider nets | BAT+ 0.6, VBAT 0.5, MOD5V / POGO5V / MOT_- 0.3 mm |

GND: tracks only where needed; then add ground fill on both layers, plus stitching vias.
