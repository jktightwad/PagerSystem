"""Independent check: every pad on pager_main.kicad_pcb is on the net design_main.py says,
and every design connection exists on the board. Also lists the parts JLCPCB will place.

    python3 check_netlist.py [board.kicad_pcb]
"""
import sys
import pcbnew
from design_main import PARTS, NETS

PCB = sys.argv[1] if len(sys.argv) > 1 else "pager_main.kicad_pcb"
b = pcbnew.LoadBoard(PCB)

# footprint pad number -> design pin name, per part type
PADMAP = {
    "Q": {"1": "G", "2": "S", "3": "D"},
    "D": {"1": "K", "2": "A"},
    "LED": {"1": "VDD", "2": "DOUT", "3": "GND", "4": "DIN"},
    "BZ": {"1": "+", "2": "-"},
    "SW": {"1": "ON", "2": "COM"},
}
def pin_name(ref, num):
    for pre in ("LED", "BZ", "SW"):
        if ref.startswith(pre): return PADMAP[pre].get(num)
    if ref[0] in "QD" and not ref.startswith("DOCK"): return PADMAP[ref[0]].get(num)
    return num

want = {(r, p): n for n, pins in NETS.items() for r, p in pins}
seen, errors = set(), []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        if not pad.GetNumber(): continue
        pin = pin_name(ref, pad.GetNumber())
        net = pad.GetNetname()
        key = (ref, pin)
        if key in want:
            seen.add(key)
            if net != want[key]:
                errors.append(f"{ref} pad {pad.GetNumber()} ({pin}) is on '{net}', design says '{want[key]}'")
        elif net and not net.startswith("SPARE_") and not (ref == "P3" and net in ("GND", "3V3", "VBAT")) and ref != "TP1":
            errors.append(f"{ref} pad {pad.GetNumber()} on '{net}' but not in the design")
missing = [k for k in want if k not in seen]
for r, p in missing:
    errors.append(f"design pin {r}.{p} ({want[(r, p)]}) has no pad on the board")
refs = {fp.GetReference() for fp in b.GetFootprints()}
for ref in PARTS:
    if ref not in refs: errors.append(f"part {ref} missing from the board")

print(f"{len(want)} design connections checked, {len(errors)} problems")
for e in errors: print("  " + e)
placed = sorted([r for r, (v, l, n) in PARTS.items() if l], key=lambda r: (r.rstrip('0123456789'), int(''.join(c for c in r if c.isdigit()) or 0)))
print(f"JLCPCB places {len(placed)} parts, {len({PARTS[r][1] for r in placed})} part types")
sys.exit(1 if errors else 0)
