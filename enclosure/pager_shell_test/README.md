# Pager shell test (v3)

Pool-ball pager shell, third iteration. Source: `pager_shell_test.scad`
(OpenSCAD, everything is a parameter; open the Customizer for dropdowns).

![Preview](preview.png)

## v3 changes
- **Hat can't rotate:** the brim has 4 ears with holes that slide over the 4
  screw columns (the egg still sets which way it goes in).
- **Chassis:** the columns stop 2 mm short of the ball's back rim; the
  chassis plate sits there, clamped between ball and base by the same 4
  screws. It carries the **brim clamp ring**, a **post pressing the ball's
  pogo connector**, a **pocket under the plate clamping the base's pogo
  connector**, **4 LED ring posts** (`led_gap` sets LEDs-to-face distance,
  default 6 mm) and room for electronics.
- **2 mm radius** on the ball's outer front edge; it starts at 45 deg so the
  ball still prints face down without supports.
- Separate pogo clamp bars and brim clamp ring are gone (now in the chassis).

## Assembly (from the back of the ball)
1. Pogo connector (flat contacts) into the ball face, flange into its pocket.
2. Magnets into the ball's hidden pockets (same pole towards the face), glue.
3. Hat in from the back: egg through the opening, ear holes over the columns.
4. LED ring onto the chassis posts (M2 self-tapping), wired.
5. Chassis in: plate under the column ends; its post presses the ball's
   pogo connector, its ring presses the brim.
6. Base: pogo connector (spring pins) in from the top, magnets pressed in
   from the underside; then 4 M2.5 x 10 mm screws up through base and
   chassis plate into the columns.

## Parts
| File | Print | Notes |
|---|---|---|
| `hat.stl` | white, face down, slicer supports under the brim | |
| `number.stl` | black, second part of the hat | 2.4 mm deep inlay |
| `ball.stl` | ball colour, face down | 104 mm OD, 14 mm deep test body (`body_h`) |
| `chassis.stl` | any, plate down (as exported) | |
| `base.stl` | any, underside up (as exported) | |

## Pogo connector
Measured: 2 mm oval face body, 1 mm flange, 1 mm oval back body (4 mm total).
- Faces sit **flush**: 2 mm of plastic in front of the flange, then a **1 mm
  flange pocket from the back**; the 1 mm back oval sticks out of the back.
- Oval hole 13.45 x **4.3** mm in the model (this printer prints holes about
  0.1 mm small: 4.5 printed 4.4, so 4.3 should print ~4.2).
- Held by the **chassis**: a post presses the ball connector's back oval; a
  pocket under the chassis plate presses the base connector's back oval.
  `pogo_post_extra` adds clamp pressure if the ball connector is loose.
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

## Tuning the stacking fit
- `recess_clear_d` (default 0.2 mm on diameter): how much bigger the base
  recess is than the crown below. Smaller = snugger, better rotation lock.
- `egg_shift` / `egg_small_d`: how pronounced the egg is. A subtler egg
  needs a tighter `recess_clear_d` to still lock the orientation.
- `recess_chamfer` (0.8) and `crown_chamfer` (0.4): lead-ins that guide a
  tight fit together. Only `base` and `hat` change when these change.

## Re-exporting
```
for p in hat number ball base brim_clamp pogo_clamp; do
  openscad -D "part=\"$p\"" -o $p.stl pager_shell_test.scad
done
```
