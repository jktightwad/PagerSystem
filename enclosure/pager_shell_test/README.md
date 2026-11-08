# Pager shell test (v2)

Second iteration of the pool-ball pager shell, after the first fit prints.
Source: `pager_shell_test.scad` (OpenSCAD, everything is a parameter).
Replaces `ball_fit_test` (v1) and the pogo keystone coupons.

![Preview](preview.png)

## What changed from v1
| | v1 | v2 |
|---|---|---|
| Crown / opening / stacking recess | round | **egg** (72 wide, 76 tall, narrow end at 12 o'clock): keys orientation |
| Crown above the ball face | 2.5 mm | **1.5 mm** |
| Number height | 0.75 x 72 mm | **0.6 x 72 = 43 mm** (80 %) |
| Brim | D-shaped (orientation) | egg-shaped (follows the crown) |
| Hat fit | 3 variants | **0.05 mm on diameter** (confirmed) |
| Pogo connector | on a separate keystone | **flush in the coloured ring**, 6 o'clock |
| Connector retention | screws through the flange | **clamp bar** over the back, 2 blind M2 pilots |
| Alignment / holding | keystone | **2 magnets** (6 x 2.75 mm) at 2 and 10 o'clock, triangle with the pogo |

## Parts
| File | Print | Notes |
|---|---|---|
| `hat.stl` | white, face down, slicer supports under the brim | Egg crown 0.05 mm under the opening |
| `number.stl` | black, second part of the hat (multi-material) | Full-depth inlay |
| `ball.stl` | ball colour, face down | 104 mm OD, shortened to 14 mm deep for the test |
| `base.stl` | any, underside up (as exported) | Egg stacking recess, pogo (spring pins), press-in magnets, counterbored screws |
| `pogo_clamp.stl` | x2 (ball + base) | Pocket for the 1 mm back oval, wire slot, 2 screw holes |
| `brim_clamp.stl` | any | Loose ring between base and brim |

## Pogo connector
Measured: 2 mm oval face body, 1 mm flange, 1 mm oval back body (4 mm total).
- Faces sit **flush**: 2 mm of plastic in front of the flange, then a **1 mm
  flange pocket from the back**; the 1 mm back oval sticks out of the back.
- Oval hole 13.45 x **4.3** mm in the model (this printer prints holes about
  0.1 mm small: 4.5 printed 4.4, so 4.3 should print ~4.2).
- **Clamp bar** (2.4 mm thick) fits over the back oval and presses the flange
  into its pocket; two M2 self-tapping screws into blind pilots (0.6 mm
  short of the face). Wire slot through the middle of the bar.
- Ball = flat contacts (top of the pager), base = spring pins (underside).
  When stacked both faces are flush, so the gap is ~0 and the pins compress
  flush.

## Magnets (6 x 2.75 mm)
- **Ball:** pockets from the back with **0.4 mm** of plastic hiding the
  magnet on the face (a small pad behind the face gives the depth). Slide in
  and glue (hole 6.05 mm).
- **Base:** **pressed in** from the underside, flush (hole 6.0 mm, prints
  ~5.9 for a press fit).
- **Polarity:** install **every magnet with the same pole facing the top of
  the pager** (e.g. mark the north pole and always put it up). Then each
  pager's base magnets attract the ball magnets of the pager below.

## Check
1. Hat in the egg opening: only goes in one way, number upright.
2. Crown 1.5 mm proud; number size; more lit white area.
3. Pogo faces flush in ball and base; slot fit at ~4.2 mm printed.
4. Clamp bar holds the connector; wires fit through.
5. Two assemblies stack: egg drops in, magnets pull it down, pogo contact
   on both pins (meter).

## Re-exporting
```
for p in hat number ball base brim_clamp pogo_clamp; do
  openscad -D "part=\"$p\"" -o $p.stl pager_shell_test.scad
done
```
