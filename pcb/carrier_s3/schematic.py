"""Draws schematic.svg / schematic.png from the circuit in design.py (by hand-placed sections, net labels join them)."""
import schemdraw
import schemdraw.elements as e

schemdraw.config(fontsize=11, lw=1.3)

def lab(d, txt, loc='right'):
    d += e.Label().label(txt, loc=loc, color='#1f4fbf')

def gnd(d):
    d += e.Ground()

with schemdraw.Drawing(file='schematic.svg', show=False) as d:
    d.config(unit=2)
    # ---------------- U1: SuperMini block ----------------
    U = e.Ic(pins=[e.IcPin(name='5V', side='left'), e.IcPin(name='GND', side='left'), e.IcPin(name='3V3', side='left'),
                   e.IcPin(name='B+', side='left'), e.IcPin(name='B-', side='left'),
                   e.IcPin(name='GP1', side='right'), e.IcPin(name='GP2', side='right'), e.IcPin(name='GP4', side='right'),
                   e.IcPin(name='GP5', side='right'), e.IcPin(name='GP12', side='right'), e.IcPin(name='GP13', side='right')],
             size=(3.4, 6.5), pinspacing=1.0, edgepadW=0.5).label('U1\nESP32-S3\nSuperMini', 'center')
    d += U.at((0, 0))
    for pin, net in [('5V', 'POGO5V'), ('GND', 'GND'), ('3V3', '3V3'), ('B+', 'VBAT (wire, H1)'), ('B-', 'GND (wire, H2)')]:
        d += e.Line().at(getattr(U, pin)).left(1.2)
        lab(d, net, 'left')
    for pin, net in [('GP1', 'DOCK_SENSE'), ('GP2', 'BAT_SENSE'), ('GP4', 'TOUCH'), ('GP5', 'RING_IO'), ('GP12', 'BUZ_IO'), ('GP13', 'MOT_IO')]:
        d += e.Line().at(getattr(U, pin)).right(1.2)
        lab(d, net, 'right')

    # ---------------- Power in ----------------
    d.here = (-14, 0)
    d += (J1 := e.Dot(open=True).label('J1 battery +', 'left'))
    d += e.Line().right(1)
    d += e.Switch().right().label('SW1 power')
    d += e.Line().right(0.5)
    lab(d, 'VBAT')
    d.here = (-14, -1.5)
    d += e.Dot(open=True).label('J1 battery −', 'left')
    d += e.Line().right(1)
    lab(d, 'GND')
    d.here = (-14, -3.5)
    d += e.Dot(open=True).label('J5 pogo 5V', 'left')
    d += e.Line().right(1.5)
    lab(d, 'POGO5V')
    d.here = (-14, -5)
    d += e.Dot(open=True).label('J5 pogo GND', 'left')
    d += e.Line().right(1.5)
    lab(d, 'GND')

    # ---------------- Dividers ----------------
    for i, (top, mid, rt, rb, c) in enumerate([('VBAT', 'BAT_SENSE', 'R6 100k', 'R7 100k', 'C1 100n'),
                                              ('POGO5V', 'DOCK_SENSE', 'R8 100k', 'R9 100k', 'C2 100n')]):
        x = -14 + i * 5; y = -8
        d.here = (x, y)
        d += e.Label().label(top, 'top', color='#1f4fbf')
        d += e.Resistor().down().label(rt, 'left')
        d += (m := e.Dot())
        d += e.Resistor().down().label(rb, 'left')
        gnd(d)
        d += e.Line().at(m.center).right(1.5)
        d += (n := e.Dot())
        d += e.Capacitor().down().label(c, 'right')
        gnd(d)
        d += e.Line().at(n.center).right(0.8)
        lab(d, mid)

    # ---------------- Buzzer / motor drivers (low-side N-MOSFET) ----------------
    for i, (io, rg, rp, q, load, motor) in enumerate([
            ('BUZ_IO', 'R1 100', 'R2 100k', 'Q1 AO3400A', 'BZ1 buzzer', False),
            ('MOT_IO', 'R3 100', 'R4 100k', 'Q2 AO3400A', 'J3 motor', True)]):
        x = 8 + i * 12; y = -10
        Q = e.NFet().right().at((x + 5, y)).label(q, 'right')
        d += Q
        # gate: IO -> resistor -> gate, pull-down from gate to GND
        d.here = (x, Q.gate[1])
        d += e.Label().label(io, 'left', color='#1f4fbf')
        d += e.Resistor().right().label(rg, 'top')
        d += (gd := e.Dot())
        d += e.Line().to(Q.gate)
        d += e.Resistor().at(gd.center).down().label(rp, 'left')
        gnd(d)
        # source to GND
        d += e.Line().at(Q.source).down(0.4)
        gnd(d)
        # drain -> load -> VBAT
        d += e.Line().at(Q.drain).up(0.6)
        d += (dd := e.Dot())
        if motor:
            d += e.Motor().up().label(load, 'right')
        else:
            d += e.RBox().up().label(load + ' (+ top)', 'right')
        d += (vt := e.Dot())
        d += e.Line().up(1.2)
        lab(d, 'VBAT', 'top')
        if motor:
            d += e.Line().at(dd.center).left(2)
            d += e.Diode().up().reverse().toy(vt.center).label('D1 B5819W', 'left')
            d += e.Line().to(vt.center)

    # ---------------- Ring, touch ----------------
    x, y = 8, -18
    d.here = (x, y)
    d += e.Label().label('RING_IO', 'left', color='#1f4fbf')
    d += e.Resistor().right().label('R5 330')
    d += e.Line().right(1)
    d += e.Dot(open=True).label('J2 ring DATA', 'right')
    d.here = (x, y - 1.5)
    d += e.Label().label('VBAT', 'left', color='#1f4fbf')
    d += e.Line().right(4)
    d += (vr := e.Dot())
    d += e.Line().right(1)
    d += e.Dot(open=True).label('J2 ring VCC', 'right')
    d += e.Capacitor().at(vr.center).down().label('C3, C4 2×47µ', 'right')
    gnd(d)
    d.here = (x, y - 5)
    d += e.Label().label('GND', 'left', color='#1f4fbf')
    d += e.Line().right(5)
    d += e.Dot(open=True).label('J2 ring GND', 'right')

    d.here = (x + 14, y)
    d += e.Label().label('3V3', 'left', color='#1f4fbf'); d += e.Line().right(1.5); d += e.Dot(open=True).label('J4 touch VCC', 'right')
    d.here = (x + 14, y - 1.5)
    d += e.Label().label('TOUCH', 'left', color='#1f4fbf'); d += e.Line().right(1.5); d += e.Dot(open=True).label('J4 touch OUT', 'right')
    d.here = (x + 14, y - 3)
    d += e.Label().label('GND', 'left', color='#1f4fbf'); d += e.Line().right(1.5); d += e.Dot(open=True).label('J4 touch GND', 'right')
    d.here = (x + 14, y - 5)
    d += e.Label().label('VBAT', 'left', color='#1f4fbf'); d += e.Line().right(1.5); d += e.Dot(open=True).label('J3 motor +', 'right')

    d += e.Label().at((-14, 6)).label('Pager carrier board, ESP32-S3 SuperMini (draft, not yet built). Blue labels with the same name are connected.', 'right')
