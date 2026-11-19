"""Combined pager board: 16 LEDs on top + ESP32-S3 SuperMini underneath (layout D).

Parts and every connection; single source for build_main.py.
Pin 1 of every connector = GND (left / square pad), power last, signal in the middle.
"""
N_LED = 16

# ref: (value, LCSC part for JLCPCB assembly or None = hand-soldered / not fitted, note)
PARTS = {
    "U1":  ("ESP32-S3 SuperMini", None, "under the board, castellated edges; B+/B- through plated holes"),
    "SW1": ("SS12F44-G3 slide switch", None, "under the board; breaks battery +"),
    "BZ1": ("MLT-8540H", "C95298", "SMD 8.5 mm magnetic buzzer, passive: drive 2.7 kHz square wave (PWM) on GP12; JLC-assembled"),
    "Q1":  ("AO3400A", "C20917", "buzzer driver"),
    "Q2":  ("AO3400A", "C20917", "motor driver"),
    "R1":  ("330R", "C23138", "Q1 gate"),
    "R2":  ("100k", "C25803", "Q1 gate pull-down"),
    "R3":  ("330R", "C23138", "Q2 gate"),
    "R4":  ("100k", "C25803", "Q2 gate pull-down"),
    "R5":  ("330R", "C23138", "LED data"),
    "R6":  ("100k", "C25803", "battery divider top"),
    "R7":  ("100k", "C25803", "battery divider bottom"),
    "R8":  ("100k", "C25803", "dock divider top"),
    "R9":  ("100k", "C25803", "dock divider bottom"),
    "C1":  ("100nF", None, "battery divider filter: NOT FITTED"),
    "C2":  ("100nF", None, "dock divider filter: NOT FITTED"),
    "C3":  ("47uF 10V", None, "LED bulk: NOT FITTED (1206 pads)"),
    "D1":  ("B5819W", "C8598", "motor flyback"),
    "D2":  ("B5819W", "C8598", "buzzer coil flyback"),
    "J1":  ("Touch", None, "JST-XH 3 right angle, under: GND, OUT, 3V3"),
    "J2":  ("Dock (pogo)", None, "JST-XH 2 right angle, under: GND, 5V"),
    "P1":  ("Battery pads", None, "under: GND, BAT+"),
    "P2":  ("Motor pads", None, "under: MOT-, VBAT"),
}
NO_CAP = ()           # every LED has its own capacitor
for i in range(1, N_LED + 1):
    PARTS[f"LED{i}"] = ("TZ-5050S2RGB-5V-I4-H1", "C26167850", "TUOZHAN TZ2812, WS2812-compatible; JLC Economic + Standard PCBA")
    if i not in NO_CAP:
        PARTS[f"CL{i}"] = ("100nF", "C14663", f"LED{i} decoupling")

NETS = {
    "GND":    [("U1", "GND"), ("U1", "B-"), ("J1", "1"), ("J2", "1"), ("P1", "1"),
               ("Q1", "S"), ("Q2", "S"), ("R2", "2"), ("R4", "2"), ("R7", "2"), ("R9", "2"),
               ("C1", "2"), ("C2", "2"), ("C3", "2")],
    "BAT+":   [("P1", "2"), ("SW1", "COM")],
    "VBAT":   [("SW1", "ON"), ("U1", "B+"), ("BZ1", "+"), ("P2", "2"), ("D1", "K"), ("D2", "K"),
               ("R6", "1"), ("C3", "1")],
    "POGO5V": [("J2", "2"), ("U1", "5V"), ("R8", "1")],
    "3V3":    [("U1", "3V3"), ("J1", "3")],
    "DOCK_SENSE": [("R8", "2"), ("R9", "1"), ("C2", "1"), ("U1", "GP1")],
    "BAT_SENSE":  [("R6", "2"), ("R7", "1"), ("C1", "1"), ("U1", "GP2")],
    "TOUCH":      [("J1", "2"), ("U1", "GP4")],
    "RING_IO":    [("U1", "GP5"), ("R5", "1")],
    "LED_DIN":    [("R5", "2"), ("LED1", "DIN")],
    "BUZ_IO":     [("U1", "GP12"), ("R1", "1")],
    "BUZ_G":      [("R1", "2"), ("R2", "1"), ("Q1", "G")],
    "BUZ_-":      [("Q1", "D"), ("BZ1", "-"), ("D2", "A")],
    "MOT_IO":     [("U1", "GP13"), ("R3", "1")],
    "MOT_G":      [("R3", "2"), ("R4", "1"), ("Q2", "G")],
    "MOT_-":      [("Q2", "D"), ("P2", "1"), ("D1", "A")],
}
for i in range(1, N_LED + 1):
    NETS["VBAT"].append((f"LED{i}", "VDD"))
    NETS["GND"].append((f"LED{i}", "GND"))
    if i not in NO_CAP:
        NETS["VBAT"].append((f"CL{i}", "1"))
        NETS["GND"].append((f"CL{i}", "2"))
    if i < N_LED:
        NETS[f"LED_D{i}"] = [(f"LED{i}", "DOUT"), (f"LED{i+1}", "DIN")]

if __name__ == "__main__":
    used = [(r, p) for pins in NETS.values() for r, p in pins]
    assert len(used) == len(set(used)), "pin on two nets"
    print(len(PARTS), "parts,", len(NETS), "nets")
