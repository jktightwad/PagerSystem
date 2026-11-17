"""Pager carrier board (ESP32-S3 SuperMini): parts and connections.

Single source of truth for the schematic drawing and the PCB generator.
Net names are what the schematic labels show.

Connectors all the same way round: pin 1 (left, square pad) = GND, last pin
(right) = power, signal in the middle.

Power:
  BAT+ (battery connector) -> SW1 -> VBAT -> SuperMini B+ (wire through the
  board), LED ring, buzzer, motor, battery divider.
  POGO5V (dock) -> SuperMini 5V pin (its charger charges the battery) and
  the dock divider. 3V3 (SuperMini regulator) -> touch module only.
"""

# ref: (value, footprint, LCSC part for assembly or None = hand-soldered, note)
PARTS = {
    "U1":  ("ESP32-S3 SuperMini", "SUPERMINI", None, "hand-soldered; B+/B- wired through H1/H2"),
    "SW1": ("Slide switch", "SWITCH", None, "power: breaks battery +"),
    "BZ1": ("TDB05 5V buzzer", "BUZZER", None, "9 mm, 5 mm pin spacing, hand-soldered on the board"),
    "Q1":  ("AO3400A", "SOT-23", "C20917", "buzzer driver"),
    "Q2":  ("AO3400A", "SOT-23", "C20917", "motor driver"),
    "R1":  ("330R", "0603", "C23138", "Q1 gate (same part as R5)"),
    "R2":  ("100k", "0603", "C25803", "Q1 gate pull-down"),
    "R3":  ("330R", "0603", "C23138", "Q2 gate (same part as R5)"),
    "R4":  ("100k", "0603", "C25803", "Q2 gate pull-down"),
    "R5":  ("330R", "0603", "C23138", "ring data"),
    "R6":  ("100k", "0603", "C25803", "battery divider top"),
    "R7":  ("100k", "0603", "C25803", "battery divider bottom"),
    "R8":  ("100k", "0603", "C25803", "dock divider top"),
    "R9":  ("100k", "0603", "C25803", "dock divider bottom"),
    "C1":  ("100nF", "0603", None, "battery divider filter: NOT FITTED (pads kept; was C14663)"),
    "C2":  ("100nF", "0603", None, "dock divider filter: NOT FITTED (pads kept; was C14663)"),
    "C3":  ("47uF 10V", "1206", None, "ring bulk: NOT FITTED (pads left for hand-soldering if the ring needs it; was C96123)"),
    "D1":  ("B5819W", "SOD-123", "C8598", "motor flyback"),
    "J1":  ("Battery", "PH2", None, "JST-PH 2: pin 1 = GND, pin 2 = + (right, tab up), to match the battery plug"),
    "J2":  ("LED ring", "PH3", None, "JST-PH 3: GND, DATA, VBAT (pins 1-3)"),
    "J3":  ("Motor", "PH2", None, "JST-PH 2: pin 1 = motor -, pin 2 = + (VBAT)"),
    "J4":  ("Touch", "PH3", None, "JST-PH 3: GND, OUT, 3V3 (pins 1-3)"),
    "J5":  ("Pogo (tower)", "PH2", None, "JST-PH 2: GND, 5V (pins 1-2)"),
}

# net: [(ref, pin), ...]   SuperMini pins by label
NETS = {
    "GND":    [("U1", "GND"), ("U1", "B-"), ("J1", "1"), ("J2", "1"), ("J4", "1"), ("J5", "1"),
               ("Q1", "S"), ("Q2", "S"), ("R2", "2"), ("R4", "2"), ("R7", "2"), ("R9", "2"),
               ("C1", "2"), ("C2", "2"), ("C3", "2")],
    "BAT+":   [("J1", "2"), ("SW1", "COM")],
    "VBAT":   [("SW1", "ON"), ("U1", "B+"), ("J2", "3"), ("BZ1", "+"), ("J3", "2"), ("D1", "K"),
               ("R6", "1"), ("C3", "1")],
    "POGO5V": [("J5", "2"), ("U1", "5V"), ("R8", "1")],
    "3V3":    [("U1", "3V3"), ("J4", "3")],
    "DOCK_SENSE": [("R8", "2"), ("R9", "1"), ("C2", "1"), ("U1", "GP1")],
    "BAT_SENSE":  [("R6", "2"), ("R7", "1"), ("C1", "1"), ("U1", "GP2")],
    "TOUCH":      [("J4", "2"), ("U1", "GP4")],
    "RING_IO":    [("U1", "GP5"), ("R5", "1")],
    "RING_DATA":  [("R5", "2"), ("J2", "2")],
    "BUZ_IO":     [("U1", "GP12"), ("R1", "1")],
    "BUZ_G":      [("R1", "2"), ("R2", "1"), ("Q1", "G")],
    "BUZ_-":      [("Q1", "D"), ("BZ1", "-")],
    "MOT_IO":     [("U1", "GP13"), ("R3", "1")],
    "MOT_G":      [("R3", "2"), ("R4", "1"), ("Q2", "G")],
    "MOT_-":      [("Q2", "D"), ("J3", "1"), ("D1", "A")],
}

if __name__ == "__main__":
    used = {(r, p) for pins in NETS.values() for r, p in pins}
    dup = [x for x in used if sum(x in v for v in NETS.values()) > 1]
    assert not dup, dup
    print(len(PARTS), "parts,", len(NETS), "nets")
