"""Schematic of the pager board, drawn from design_main.py (parts, values and net names come from
there; blue net labels with the same name are connected).

    python3 schematic.py          -> review/schematic.svg (+ review/netlist.md, generated from the same data)

Every pin drawn is looked up in design_main.NETS, so a pin that is not in the design raises an
error instead of being drawn on a wrong net.
"""
import os
import schemdraw
import schemdraw.elements as e
from design_main import PARTS, NETS, N_LED, led_cap

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review")
os.makedirs(OUT, exist_ok=True)
PIN_NET = {(r, p): n for n, pins in NETS.items() for r, p in pins}
drawn = set()

def net(ref, pin):
    drawn.add((ref, pin))
    return PIN_NET[(ref, pin)]          # KeyError = pin not in the design

def val(ref): return PARTS[ref][0]
def lab(d, txt, loc="right"): d += e.Label().label(txt, loc=loc, color="#1f4fbf")

schemdraw.config(fontsize=11, lw=1.3)
with schemdraw.Drawing(file=os.path.join(OUT, "schematic.svg"), show=False) as d:
    d.config(unit=2)
    d += e.Label().at((-16, 9)).label(
        "Pager board (pager_main): ESP32-S3 SuperMini + 16 addressable LEDs. Generated from design_main.py. "
        "Blue labels with the same name are connected.", loc="right", fontsize=13)

    # ---------------- U1 ----------------
    left = ["5V", "GND", "3V3", "B+", "B-"]
    right = ["GP1", "GP2", "GP4", "GP5", "GP12", "GP13"]
    U = e.Ic(pins=[e.IcPin(name=p, side="left") for p in left] + [e.IcPin(name=p, side="right") for p in right],
             size=(5.5, 6.5), pinspacing=1.0, edgepadW=0.5).label("U1\nESP32-S3\nSuperMini\n(module,\nhand-soldered)", "center")
    d += U.at((2, 0))
    for p in left:
        d += e.Line().at(getattr(U, p)).left(1.2)
        lab(d, net("U1", p), "left")
    for p in right:
        d += e.Line().at(getattr(U, p)).right(1.2)
        lab(d, net("U1", p), "right")

    # ---------------- Battery, P-MOSFET power switch, bulk caps ----------------
    x0, y0 = -16, 6
    Q3 = e.Ic(pins=[e.IcPin(name="S", pin="2", side="left"), e.IcPin(name="D", pin="3", side="right"),
                    e.IcPin(name="G", pin="1", side="bottom")],
              size=(2.6, 1.6), pinspacing=1.0).label(f"Q3 {val('Q3')}\nP-MOSFET (power switch)", "top", fontsize=10)
    d += Q3.anchor("S").at((x0 + 4.0, y0))
    net("Q3", "S"); net("Q3", "D"); net("Q3", "G")
    d.here = (x0, y0)
    d += e.Dot(open=True).label("P1.2 battery +", "left")
    d += e.Line().right(1.5)
    d += (bp := e.Dot()); net("P1", "2")
    d += e.Label().at((bp.center[0], bp.center[1] + 0.35)).label(net("P1", "2"), "top", color="#1f4fbf")
    d += e.Line().at(bp.center).to(Q3.S)
    d += e.Line().at(Q3.D).right(1.2); lab(d, net("Q3", "D"))
    d += (r10 := e.Resistor().at(bp.center).down(3.0)); net("R10", "1"); net("R10", "2")
    d += e.Label().at((r10.center[0] - 0.5, r10.center[1])).label(f"R10\n{val('R10')}", "left", fontsize=11)
    d += (gn := e.Dot())
    d += e.Line().at(gn.center).tox(Q3.G[0]); d += e.Line().toy(Q3.G[1])
    d += e.Label().at((Q3.G[0] + 0.2, gn.center[1] + 0.35)).label(net("Q3", "G"), "right", color="#1f4fbf")
    d += e.Line().at(gn.center).down(0.6)
    d += (swe := e.Switch().down())
    d += e.Label().at((swe.center[0] + 0.7, swe.center[1])).label(f"SW1 {val('SW1')}\nCOM (top) - ON (bottom)\non = gate low = Q3 on", "center", fontsize=11, halign="left")
    net("SW1", "COM"); net("SW1", "ON")
    d += e.Ground()
    d.here = (x0, y0 - 8.5)
    d += e.Dot(open=True).label("P1.1 battery -", "left")
    d += e.Line().right(1); lab(d, net("P1", "1"))
    for k, c in enumerate(("C3", "C4")):
        d.here = (x0 + 7.5 + 3.6 * k, y0 - 4.0)
        lab(d, net(c, "1"), "top")
        d += e.Line().down(1.6)
        d += (cc := e.Capacitor(polar=False).down())
        d += e.Label().at((cc.center[0] + 0.9, cc.center[1])).label(f"{c}\n{val(c)}", "right", fontsize=10)
        d += e.Ground(); net(c, "2")

    # ---------------- Dock J2, ideal diode U2, divider ----------------
    x0, y0 = -16, -5.5
    d.here = (x0, y0)
    d += e.Dot(open=True).label("J2.2 pogo 5V", "left"); d += e.Line().right(1.5)
    d += (pj := e.Dot()); lab(d, net("J2", "2"), "top")
    U2 = e.Ic(pins=[e.IcPin(name="VIN", pin="1", side="left"), e.IcPin(name="CE", pin="3", side="right", slot="1/2"),
                    e.IcPin(name="VOUT", pin="6", side="right", slot="2/2"), e.IcPin(name="GND", pin="2", side="bottom", slot="1/3"),
                    e.IcPin(name="N/C", pin="4", side="bottom", slot="2/3"), e.IcPin(name="ST", pin="5", side="bottom", slot="3/3")],
              size=(4.2, 2.6), pinspacing=0.9).label(f"U2 {val('U2')}\nideal diode", "top", fontsize=10)
    d += U2.anchor("VIN").at((pj.center[0] + 1.2, pj.center[1]))
    d += e.Line().at(pj.center).to(U2.VIN)
    for pn in ("1", "2", "3", "4", "5", "6"): net("U2", pn)
    d += e.Line().at(U2.VOUT).right(1.0); d += (vo := e.Dot()); lab(d, net("U2", "6"))
    d += e.Line().at(U2.CE).right(0.5); d += e.Line().toy(vo.center[1]); d += e.Line().tox(vo.center[0])
    for pn in ("GND", "N/C", "ST"):
        d += e.Line().at(getattr(U2, pn.replace("/", ""), None) or U2.absanchors[pn]).down(0.5); d += e.Ground(scale=0.6)
    d += e.Label().at((x0 - 1.0, U2.VIN[1] - 3.4)).label("CE tied to VOUT: off when VOUT > VIN (backfeed); VIN -6 V abs. max (reversed dock)", "center", fontsize=9, halign="left")
    d.here = (x0, y0 - 1.5)
    d += e.Dot(open=True).label("J2.1 pogo GND", "left"); d += e.Line().right(1.5); lab(d, net("J2", "1"))

    def divider(x, y, rt, rb, c, label):
        global d
        d.here = (x, y)
        d += e.Label().label(net(rt, "1"), "top", color="#1f4fbf")
        d += e.Resistor().down().label(f"{rt} {val(rt)}", "left")
        d += (m := e.Dot()); net(rt, "2"); net(rb, "1")
        d += e.Resistor().down().label(f"{rb} {val(rb)}", "left")
        d += e.Ground(); net(rb, "2")
        d += e.Line().at(m.center).right(1.5)
        d += (n := e.Dot())
        d += e.Capacitor().at(n.center).down().label(f"{c} {val(c)}", "right"); d += e.Ground(); net(c, "1"); net(c, "2")
        d += e.Line().at(n.center).right(1.2); lab(d, net(rt, "2"))
        d += e.Label().at((x - 0.5, y + 1.2)).label(label, "right", fontsize=10)
    divider(-16, -12.5, "R8", "R9", "C2", "dock sense (pogo 5V/2 -> GP1)")
    divider(-9.5, -12.5, "R6", "R7", "C1", "battery sense (VBAT/2 -> GP2)")

    # ---------------- Touch J1 ----------------
    x0, y0 = 22, 7
    for k, pin in enumerate(["1", "2", "3"]):
        d.here = (x0, y0 - 1.2 * k)
        d += e.Dot(open=True).label(f"J1.{pin} touch {['GND', 'OUT', 'VCC'][k]}", "right")
        d += e.Line().left(1.5); lab(d, net("J1", pin), "left")

    # ---------------- Drivers (buzzer, motor) ----------------
    def driver(x, y, rg, rpd, q, load_txt, load_top, load_bot, diode=None):
        global d
        d.here = (x, y)
        d += e.Label().label(net(rg, "1"), "left", color="#1f4fbf")
        d += e.Resistor().right().label(f"{rg} {val(rg)}", "top")
        d += (g := e.Dot()); net(rg, "2"); net(rpd, "1")
        d += e.Resistor().at(g.center).down().label(f"{rpd} {val(rpd)}", "left"); d += e.Ground(); net(rpd, "2")
        d += e.Line().at(g.center).right(2.5)
        d += (Q := e.NFet(anchor="gate").label(f"{q} {val(q)}\nN-MOSFET", "right"))
        net(q, "G"); net(q, "S"); net(q, "D")
        d += e.Ground().at(Q.source)
        d += e.Line().at(Q.drain).up(0.8)
        d += (dn := e.Dot())
        d += e.Line().at(dn.center).up(0.5)
        if "motor" in load_txt: d += e.Motor().up().label(load_txt, "right")
        else: d += e.ResistorIEC().up().label(load_txt, "right")    # buzzer: two-terminal load (box)
        d += e.Line().up(1.0)
        d += (tp := e.Dot()); d += e.Line().up(0.6); lab(d, load_top, "top")
        if diode:
            d += e.Line().at(dn.center).left(1.6)
            d += e.Diode().up(3.5).label(f"{diode}\n{val(diode)}", "left")
            d += e.Line().right(1.6)
            net(diode, "A"); net(diode, "K")
        return dn
    dn = driver(10, -5, "R1", "R2", "Q1", f"BZ1 {val('BZ1')}\nactive buzzer (+ top)", net("BZ1", "+"), net("BZ1", "-"), diode="D3")
    net("BZ1", "-")
    dn = driver(19, -5, "R3", "R4", "Q2", "P2 vibration motor pads\n(P2.2 +, P2.1 -)", net("P2", "2"), net("P2", "1"), diode="D1")
    net("P2", "1")

    # ---------------- LED chain ----------------
    x0, y0 = -16, -22
    d.here = (x0, y0 + 2.5)
    d += e.Label().label(net("R5", "1"), "left", color="#1f4fbf")
    d += e.Resistor().right().label(f"R5 {val('R5')}", "top")
    d += e.Line().right(0.5); lab(d, net("R5", "2"))
    per_row, DX, DY = 4, 10.5, 7.0
    for i in range(1, N_LED + 1):
        ref = f"LED{i}"; row, col = divmod(i - 1, per_row)
        X, Y = x0 + col * DX, y0 - 3 - row * DY
        L = e.Ic(pins=[e.IcPin(name="DIN", side="left"), e.IcPin(name="DOUT", side="right"),
                       e.IcPin(name="VDD", side="top"), e.IcPin(name="GND", side="bottom")],
                 size=(2.6, 2.0), pinspacing=1.0)
        d += L.at((X, Y))
        d += e.Label().at((L.VDD[0] - 1.9, L.VDD[1] + 0.35)).label(ref, "right", fontsize=11)
        d += e.Line().at(L.VDD).up(0.8); d += (v := e.Dot()); d += e.Line().up(0.4); lab(d, net(ref, "VDD"), "top")
        d += e.Line().at(L.GND).down(0.6); d += (gd := e.Dot()); d += e.Ground(); net(ref, "GND")
        # its decoupling cap between the LED's VDD and GND, drawn beside it
        c = led_cap(i)
        d += e.Line().at(v.center).right(5.2)
        d += e.Capacitor().down(v.center[1] - gd.center[1]).label(f"{c}\n{val(c)}", "right", fontsize=9)
        d += e.Line().left(5.2); net(c, "1"); net(c, "2")
        d += e.Line().at(L.DIN).left(0.6); lab(d, net(ref, "DIN"), "left")
        if i < N_LED:
            d += e.Line().at(L.DOUT).right(0.4); lab(d, net(ref, "DOUT"))
        else:
            d += e.Line().at(L.DOUT).right(0.4); d += e.Label().label("n.c.", "right", fontsize=9)
    d += e.Label().at((x0, y0 - 3 - (N_LED + per_row - 1) // per_row * DY + 2)).label(
        f"LED1-16: {PARTS['LED1'][0]} (WS2812-compatible; VDD = VBAT 3.0-4.2 V, data 3.3 V). "
        "Each LED's DIN is the previous LED's DOUT (net LED_Dn = LEDn.DOUT -> LEDn+1.DIN); LED16 DOUT not connected.",
        "right", fontsize=10)

missing = sorted(set(PIN_NET) - drawn)
assert not missing, f"design pins not drawn: {missing}"
print("schematic.svg: every design pin drawn,", len(drawn), "pins")

# ---------------- net list, from the same data ----------------
with open(os.path.join(OUT, "netlist.md"), "w") as f:
    f.write("# Net list (generated from design_main.py)\n\nEvery connection on the board. Pin names: MOSFET G/S/D, "
            "diode A/K, LED VDD/DOUT/GND/DIN, buzzer +/-, two-pin parts 1/2, U1 module pin names.\n\n| Net | Pins |\n|---|---|\n")
    for n in sorted(NETS, key=lambda s: (s.startswith("LED_D"), s)):
        f.write(f"| {n} | {', '.join(f'{r}.{p}' for r, p in NETS[n])} |\n")
print("netlist.md written")
