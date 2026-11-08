# Pager shell test (v4)

Pool-ball pager shell. Source: `pager_shell_test.scad` (OpenSCAD; open the
Customizer for grouped settings and dropdowns).

![Preview](preview.png)

## v4 changes
- **Screw columns blended into the ball wall** (`column_fillet`, 3 mm).
- **Hat brim fills the inside of the ball**, `brim_gap_d` (0.5 mm on
  diameter) smaller, following the column bumps, so the hat can't rotate.
  The brim also **holds the ball's pogo connector** (slot for its back oval
  and wires; the brim presses the flange) and **captures the magnets**
  (0.3 mm recesses; magnets stand 0.15 mm proud of the face back).
- **Chassis clamp ring moved out to the wall**, next to the columns; the
  middle of the chassis is free for electronics. Pogo post removed.
- **`egg_tip` replaces `egg_shift`:** how far the egg's narrow end sticks out
  past the round part. Now **2 mm** (v2/v3 had 4). With the old setting,
  `egg_shift = 5` would have made the egg perfectly round.
- Kept: chassis plate under the shortened columns (clamps the base's pogo
  connector), LED ring posts, 2 mm front-edge radius, magnets in the base.

## Assembly (from the back of the ball)
1. Pogo connector (flat contacts) into the ball face, flange into its pocket.
2. Magnets into the ball's pockets, same pole towards the face.
3. Hat in from the back: egg through the opening, brim around the columns.
   The brim now holds the connector and magnets.
4. LED ring onto the chassis posts (M2 self-tapping), wired.
5. Chassis in: plate under the column ends, ring pressing the brim's edge.
6. Base: pogo connector (spring pins) in from the top, magnets pressed in
   from the underside; 4 M2.5 x 10 mm screws up through base and chassis
   plate into the columns.

## Parts
| File | Print | Notes |
|---|---|---|
| `hat.stl` | white, face down, slicer supports under the brim | Brim fills the ball interior |
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
- Ball connector held by the **hat brim** (slot for its back oval); base
  connector held by a pocket under the **chassis plate**.
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
