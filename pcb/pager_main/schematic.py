"""Schematic of the pager board, drawn from design_main.py (parts, values and net names come from
there; blue net labels with the same name are connected).

    python3 schematic.py          -> review/schematic.svg (+ review/netlist.md, generated from the same data)

Every pin drawn is looked up in design_main.NETS, so a pin that is not in the design raises an
error instead of being drawn on a wrong net.
"""
import os
import schemdraw
import schemdraw.elements as e
from design_main import PARTS, NETS, N_LED

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

    # ---------------- Battery, switch, bulk cap ----------------
    x0, y0 = -16, 4
    d.here = (x0, y0)
    d += e.Dot(open=True).label(f"P1.2 battery + ({net('P1', '2')})", "left")
    d += e.Line().right(1)
    d += e.Switch().right().label(f"SW1 {val('SW1')}\nCOM ({net('SW1', 'COM')}) - ON ({net('SW1', 'ON')})", "top")
    d += e.Line().right(0.5); lab(d, net("SW1", "ON"))
    d.here = (x0, y0 - 1.5)
    d += e.Dot(open=True).label("P1.1 battery -", "left")
    d += e.Line().right(1); lab(d, net("P1", "1"))
    d.here = (x0 + 1, y0 - 3)
    lab(d, net("C3", "1"), "top")
    d += e.Line().down(0.8)
    d += e.Capacitor(polar=False).down().label(f"C3 {val('C3')}\nbulk (1206)", "right")
    d += e.Ground(); net("C3", "2")

    # ---------------- Dock J2 + divider ----------------
    x0, y0 = -16, -4
    d.here = (x0, y0)
    d += e.Dot(open=True).label("J2.2 pogo 5V", "left"); d += e.Line().right(1.5); lab(d, net("J2", "2"))
    d.here = (x0, y0 - 1.2)
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
    divider(-16, -7.5, "R8", "R9", "C2", "dock sense (5V/2 -> GP1)")
    divider(-9.5, -7.5, "R6", "R7", "C1", "battery sense (VBAT/2 -> GP2)")

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
    dn = driver(10, -5, "R1", "R2", "Q1", f"BZ1 {val('BZ1')}\nactive buzzer (+ top)", net("BZ1", "+"), net("BZ1", "-"))
    net("BZ1", "-")
    dn = driver(19, -5, "R3", "R4", "Q2", "P2 vibration motor pads\n(P2.2 +, P2.1 -)", net("P2", "2"), net("P2", "1"), diode="D1")
    net("P2", "1")

    # ---------------- LED chain ----------------
    x0, y0 = -16, -17
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
        c = f"CL{i}"
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
