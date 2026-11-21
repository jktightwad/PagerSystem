# Pager PCB: routing brief for an independent look

**Question:** can this board meet every goal below on **2 layers** with no compromise? If not, what is the
smallest change that gets there? Separately, how much easier is it on **4 layers**?

All files referred to are in this package. The circuit is fixed (`../netlist.md`, `../schematic.pdf`,
`../parts_list.csv`). Placement and routing are open for suggestions, within the constraints below.

## The board
- **Size:** 54 x 48 mm rectangle, 1.5 mm corner radius, 2 layers. A 4-layer version may be priced as an
  alternative.
- **Assembly:** JLCPCB Economic PCBA, which allows SMD parts on the **top side only** and 2 layers only. Everything
  JLC fits is on top. Through-hole parts and the module are hand-soldered from below. (A 4-layer board would
  need Standard PCBA instead.)
- **LED ring (top):** 16 x 5050 addressable LEDs (WS2812 pinout: 1 VDD, 2 DOUT, 3 GND, 4 DIN) on a circle of
  r = 20.5 mm centred at design (0, 0), every 22.5 degrees, rotated tangentially. Each LED's inner pad row (VDD,
  DIN) sits at r = 19.0 and its outer row (DOUT, GND) at r = 22.3. Each LED has its own 100 nF 0603 capacitor
  just inside it (r = 16.25). **The spacing must stay equal and each LED must keep its own capacitor.**
- **ESP32-S3 SuperMini module (U1):** 24 x 18 mm, mounted **under** the board. Its USB end faces the board
  centre (x = 6) and its antenna end is at the right board edge (x = 30).
  - Its castellated pins are on two rows at y = +-9 (pads on the bottom layer).
  - Its B+/B- battery pads are reached through plated oval holes.
  - The bottom layer allows **no tracks under the module body** (a rule area). Ground pour and vias are allowed there.
  - There is **no copper of any kind near the antenna end** (rule areas on both layers).
  - An **L-shaped cut-out** through the board clears components on the module's back (see `placement.md` / the
    board file).
- **Bottom-side, hand-soldered parts:**
  - JST-XH right-angle connectors J1 (touch, 3 pins) and J2 (dock 5 V, 2 pins) on the left.
  - Slide switch SW1 (3 pins plus 2 slotted legs).
  - Battery pads P1 and motor pads P2 near the bottom edge.
  - 6 GPIO test pads (TP1).
- **4 M2 mounting holes,** one in each corner.
- **Spare GPIO breakouts (P3):** 9 spare module pins (TX, RX, GPIO 3, 6, 7, 8, 9, 10, 11) plus 3V3/GND/VBAT
  as 0.9 mm through-holes on two arcs (r = 26) in the two left corners. **This is the part that currently does not
  fit.**

## Power integrity goals
- **Supply:** a 1S LiPo (3.0-4.2 V) feeds VBAT through a P-MOSFET switch Q3. VBAT feeds the 16 LEDs (up to about
  60 mA each at full white), the module's B+ (Wi-Fi peaks of a few hundred mA), the buzzer (30 mA) and the motor.
  The design worst case is about 1.3 A.
- **VBAT ring (current approach):**
  - a pre-drawn 1.0 mm top-copper ring at r = 17.65, between the LED capacitors and the LEDs' inner pad row;
  - a 0.6 mm stub to every LED VDD pad and capacitor;
  - open for about 17 degrees where it passes the module cut-out (edge clearance).
  - The data line (DOUT on the outer row to the next LED's DIN on the inner row) stays outside the ring.
- **Results with that ring** (routed board in this package, spares left out):

  | From Q3 to | Resistance |
  |---|---|
  | Module B+ | 9.6 mOhm |
  | Motor | 12 mOhm |
  | Worst LED | 47 mOhm |

  The earlier layout was a daisy chain of 0.3 mm track at up to 193 mOhm, with the module at the far end.
- **Ground:** pours on both layers, about 2 mm via stitching.
- **Dock 5 V:** the pogo connector goes through an LM66100 ideal diode (U2) to the module's 5 V pin. It blocks
  backfeed and reverse polarity, with CE tied to VOUT. Its CE-VOUT and ST-GND links are pre-drawn.

## Design rules (JLC standard, as set on the board)
| Rule | Value |
|---|---|
| Copper clearance | 0.2 mm |
| Signal track | 0.25 mm |
| Power tracks | VBAT 0.5, BAT+ 0.6, MOD5V / POGO5V / MOT- 0.3 mm |
| Via | 0.6 mm pad / 0.3 mm drill |
| Hole to hole | 0.25 mm |
| Copper to board edge (and cut-out) | 0.5 mm |
| Zone clearance | 0.25 mm |

## What has been tried (own grid A* router, sequential, randomised retries)
| Attempt | Result |
|---|---|
| Earlier layout: 0.3 mm VBAT daisy chain, all nets | routes (once), but VBAT is weak (see above) |
| VBAT and BAT+ as 0.6 / 0.8 mm routed tracks | fails (3 seeds x 80 attempts) |
| Pre-drawn VBAT ring + all nets | fails: spare GPIOs, BAT+, BUZ_IO, MOT_IO, LED data hops alternate as the failures |
| Pre-drawn ring, **spare GPIO nets left out** | **routes in 14-75 attempts** (all 3 seeds) |

**Why it is tight:**
- Every route from inside the ring to outside it must use the bottom layer at some point.
- The bottom is blocked under the module and crowded around J1/J2/SW1/P1/P2.
- The spare-GPIO routes run from the module pins on the right to the arcs on the far left, crossing everything.

## Options already identified (to check, compare, or beat)
1. Drop the 9 spare breakouts. This works now.
2. Put the spares as bare bottom pads right beside the module's pin rows (short bottom traces). Not yet tried.
3. Keep only some spares (e.g. TX/RX).
4. Narrow the VBAT ring to about 0.7 mm.
5. Move parts, or grow the board slightly.
6. **4 layers:** for example In1 = GND plane, In2 = VBAT plane, with every VBAT/GND pad dropping to its plane through
   a via. The top and bottom then carry signals only, and the ring becomes unnecessary. Cost: Standard PCBA
   instead of Economic, plus the 4-layer board price.

## Files in this package
| File | Content |
|---|---|
| `ROUTING_BRIEF.md` | this document |
| `placement.md` | every part's position, rotation and side |
| `pager_main_unrouted_with_ring.kicad_pcb` (+ `.kicad_pro`) | KiCad 7 board: parts placed, VBAT ring and U2 links pre-drawn, nothing else routed |
| `pager_main_routed_no_spares.kicad_pcb` + `drc_routed_no_spares.txt` | the route that worked with the spare nets left out (unconnected items in its DRC = the 9 spares + 1 GND pad) |
| `../schematic.pdf`, `../netlist.md`, `../parts_list.csv`, `../design_description.md` | circuit, connections, parts, design notes |
