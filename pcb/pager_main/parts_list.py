"""Writes review/parts_list.csv from design_main.PARTS."""
import csv, re
from design_main import PARTS
rows = {}
for ref, (v, l, n) in PARTS.items():
    rows.setdefault((v, l, re.sub(r"LED\d+ decoupling", "LED decoupling", n)), []).append(ref)
k = lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0))
with open("review/parts_list.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Refs", "Qty", "Value / part", "LCSC", "Part page (datasheet linked there)", "Fitted by", "Note"])
    for (v, l, n), refs in sorted(rows.items(), key=lambda t: k(sorted(t[1], key=k)[0])):
        refs = sorted(refs, key=k)
        w.writerow([" ".join(refs) if len(refs) < 5 else f"{refs[0]}-{refs[-1]}", len(refs), v, l or "",
                    f"https://jlcpcb.com/partdetail/{l}" if l else "", "JLC (top side)" if l else "hand", n])
print("review/parts_list.csv")
