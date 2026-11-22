# Pager PCB: design brief (requirements only)

Please lay out and route this circuit. Placement, board shape and routing strategy are open: only the
requirements below are fixed. The circuit is in `schematic.pdf`, `netlist.md` (every net and pin) and
`parts.csv`. If something can't be met, say which requirement and what the smallest compromise would be.

**Questions:**
- Can every requirement be met on **2 layers**?
- How much easier is it on **4 layers**?

## What the board is
- A table-queue pager.
- It has a ring of 16 addressable RGB LEDs, a passive buzzer, a vibration motor and a touch sensor.
- An ESP32-S3 module provides Wi-Fi.
- It runs on a 1S LiPo and charges through spring contacts (pogo pins) when docked.
- It goes inside a round enclosure, which will be made to fit the board.

## Requirements
1. **Size:** as small as practical. Current reference: 54 x 48 mm; smaller is better.
2. **LEDs:**
   - 16 LEDs in an **even ring**, with equal angular spacing.
   - Each LED has **its own 100 nF capacitor right beside it**.
   - The LEDs are daisy-chained (DOUT to the next DIN).
   - Ring diameter is open. The current enclosure is designed around about 41 mm between LED centres.
3. **ESP32-S3 SuperMini module (U1):**
   - placed so its **antenna is not blocked**: no copper near or under the antenna end on any layer, and nothing
     metal over it;
   - its **B+ / B- battery pads stay reachable** for soldering;
   - the module side, orientation and how it mounts (castellated pads, headers, etc.) are open.
   - Module facts are below.
4. **Connectors and wire pads on the bottom** (hand-soldered):
   - touch sensor connector J1 (3-pin JST-XH 2.5 mm, right angle): GND, OUT, 3V3;
   - dock connector J2 (2-pin JST-XH 2.5 mm, right angle): GND, 5V;
   - battery wire pads P1: GND, BAT+;
   - motor wire pads P2: MOT-, VBAT;
   - power slide switch SW1: SS12F44 through-hole, 3 pins at 2.5 mm, plus 2 slotted mounting legs.
5. **Access to pins from the top:**
   - the module's spare GPIOs (TX, RX, GPIO 3, 6, 7, 8, 9, 10, 11) plus 3V3, GND and VBAT as through-holes for
     adding wires later;
   - test points for the GPIOs in use (GP1, GP2, GP4, GP5, GP12, GP13).
6. **Mounting:** at least 2 M2 holes, roughly opposite each other.
7. **Assembly:** JLCPCB Economic PCBA, which allows **SMD parts on the top side only** and 2 layers only. All
   JLC-fitted parts (the ones with an LCSC number in `parts.csv`) go on top. Hand-soldered parts can go on
   either side. A 4-layer board would need JLC Standard PCBA, so for comparison please also say what 4 layers
   would gain.
8. **Power integrity:**
   - VBAT feeds:
     - the 16 LEDs, up to about 60 mA each at full white;
     - the module's B+, with Wi-Fi peaks of a few hundred mA;
     - the buzzer (up to about 100 mA, PWM) and the motor.
   - The worst case is about 1.3 A total.
   - Keep VBAT resistance low to every LED and to the module. For reference, the current attempt achieves
     about 10 mOhm to the module and under 50 mOhm to the worst LED.
   - Ground should be solid, with a good return path.
   - BAT+ (battery to the Q3 switch) carries the full current.
9. **Design rules (JLC standard):**

   | Rule | Value |
   |---|---|
   | Copper clearance | 0.2 mm |
   | Track | 0.25 mm minimum (power wider) |
   | Via | 0.6 mm pad / 0.3 mm drill |
   | Hole to hole | 0.25 mm |
   | Copper to board edge | 0.5 mm |

## Module facts (ESP32-S3 SuperMini, measured)
- **Size:** 24 x 18 mm PCB. The USB-C connector sits at one short end and sticks out about 1.45 mm. The antenna
  is at the other short end; an estimated 5 mm of the module length is antenna area.
- **Pins:** two rows of 9 along the long edges, 2.54 mm pitch, rows 15.25 mm apart, first pin 1.75 mm from the USB
  end. The module edges are castellated, so it can sit flat on pads or take headers.
  - Row A, from the USB end: 5V, GND, 3V3, GP13, GP12, GP11, GP10, GP9, GP8
  - Row B, from the USB end: TX, RX, GP1, GP2, GP3, GP4, GP5, GP6, GP7
- **B+ / B- pads:** 2 mm pads on the module's back, 1-3 mm from the USB end,
  centres about 1.83 mm either side of the module's centre line. B+ is on the row A side.
- **Parts on the module's back:** about 5 components between 3 and about 12.4 mm from the USB end, near the
  centre line. If the module sits flat on the board with its back down, they need a cut-out or clearance.
  The antenna chip is about 2.1 mm thick.

## Files in this package
| File | Content |
|---|---|
| `ROUTING_BRIEF.md` | this document |
| `schematic.pdf` | schematic (generated from the design data) |
| `netlist.md` | every net and every pin on it |
| `parts.csv` | parts, values, LCSC numbers and JLC part links (datasheets linked there), hand-fit or JLC-fit |
