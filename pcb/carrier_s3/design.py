"""Pager carrier board (ESP32-S3 SuperMini): parts and connections.

Single source of truth for the schematic drawing and the PCB generator.
Net names are what the schematic labels show.

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
    "BZ1": ("TDB05 5V buzzer", "WIRE2", None, "in its base pocket, wired to two pads"),
    "Q1":  ("AO3400A", "SOT-23", "C20917", "buzzer driver"),
    "Q2":  ("AO3400A", "SOT-23", "C20917", "motor driver"),
    "R1":  ("100R", "0603", "C22775", "Q1 gate"),
    "R2":  ("100k", "0603", "C25803", "Q1 gate pull-down"),
    "R3":  ("100R", "0603", "C22775", "Q2 gate"),
    "R4":  ("100k", "0603", "C25803", "Q2 gate pull-down"),
    "R5":  ("330R", "0603", "C23138", "ring data"),
    "R6":  ("100k", "0603", "C25803", "battery divider top"),
    "R7":  ("100k", "0603", "C25803", "battery divider bottom"),
    "R8":  ("100k", "0603", "C25803", "dock divider top"),
    "R9":  ("100k", "0603", "C25803", "dock divider bottom"),
    "C1":  ("100nF", "0603", "C14663", "battery divider filter"),
    "C2":  ("100nF", "0603", "C14663", "dock divider filter"),
    "C3":  ("47uF 10V", "1206", "C96123", "ring bulk"),
    "C4":  ("47uF 10V", "1206", "C96123", "ring bulk"),
    "D1":  ("B5819W", "SOD-123", "C8598", "motor flyback"),
    "J1":  ("Battery", "PH2", None, "JST-PH 2"),
    "J2":  ("LED ring", "PH3", None, "JST-PH 3: VBAT, DATA, GND"),
    "J3":  ("Motor", "PH2", None, "JST-PH 2"),
    "J4":  ("Touch", "PH3", None, "JST-PH 3: 3V3, OUT, GND"),
    "J5":  ("Pogo (tower)", "PH2", None, "JST-PH 2: 5V, GND"),
}

# net: [(ref, pin), ...]   SuperMini pins by label
NETS = {
    "GND":    [("U1", "GND"), ("U1", "B-"), ("J1", "2"), ("J2", "3"), ("J4", "3"), ("J5", "2"),
               ("Q1", "S"), ("Q2", "S"), ("R2", "2"), ("R4", "2"), ("R7", "2"), ("R9", "2"),
               ("C1", "2"), ("C2", "2"), ("C3", "2"), ("C4", "2")],
    "BAT+":   [("J1", "1"), ("SW1", "COM")],
    "VBAT":   [("SW1", "ON"), ("U1", "B+"), ("J2", "1"), ("BZ1", "+"), ("J3", "1"), ("D1", "K"),
               ("R6", "1"), ("C3", "1"), ("C4", "1")],
    "POGO5V": [("J5", "1"), ("U1", "5V"), ("R8", "1")],
    "3V3":    [("U1", "3V3"), ("J4", "1")],
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
    "MOT_-":      [("Q2", "D"), ("J3", "2"), ("D1", "A")],
}

if __name__ == "__main__":
    used = {(r, p) for pins in NETS.values() for r, p in pins}
    dup = [x for x in used if sum(x in v for v in NETS.values()) > 1]
    assert not dup, dup
    print(len(PARTS), "parts,", len(NETS), "nets")
