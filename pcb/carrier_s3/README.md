# Pager carrier board (ESP32-S3 SuperMini) — draft

**Status: schematic draft only. Not laid out, not ordered, not tested.**

![Schematic](schematic.png)

- `design.py`: the parts and every connection (single source for the
  schematic and, later, the board generator).
- `schematic.py` → `schematic.svg` / `schematic.png`.
- `bom_draft.csv`: parts list. LCSC part numbers are for JLCPCB assembly and
  are from memory: **verify each one on lcsc.com before ordering.**

## Circuit
- Battery (J1) → power switch SW1 → **VBAT**: SuperMini B+ (short wire up
  through the board), LED ring, buzzer, motor, battery divider.
- Pogo (J5, from the pogo tower) **5 V** → SuperMini 5V pin (its charger
  charges the battery) and the dock divider.
- SuperMini **3V3** → touch module only.
- Buzzer and motor: low-side AO3400A MOSFETs, 100 Ω gate resistor, 100 kΩ
  pull-down; Schottky across the motor.
- Pins: dock GP1, battery GP2, touch GP4, ring GP5, buzzer GP6, motor GP7.

## Needed before layout (measurements)
1. SuperMini: row-to-row pin spacing, board size, B+/B− pad positions.
2. Buzzer pin spacing and polarity.
3. Slide switch: pin count, spacing, mounting tabs.
4. Battery plug type (JST-PH 2.0 assumed).
5. Board target: fit the Rev 2 ball, or smallest possible.
