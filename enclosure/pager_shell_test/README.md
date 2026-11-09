# Pager shell test (v8)

Pool-ball pager shell. Source: `pager_shell_test.scad` (OpenSCAD; open the
Customizer for grouped settings and dropdowns). To export one part: choose
`part`, press **F6**, wait for "Rendering finished", then **F7** (export
uses the last F6 render).

![Preview](preview.png)

## v6 changes (more room inside, base no longer proud)
- **Hat brim 1 mm, sunk into a 1 mm pocket** in the back of the 3 mm ball
  face: face + brim = 3 mm (was 4.6). Still follows the column bumps.
  - The ball pogo flange shares that layer: the brim has a cut-out round it
    and a **tongue underneath** that presses the flange (slot for the back
    oval and wires).
  - The magnets pass through the brim; **caps underneath** hold them in.
- **Base is a 2 mm ring**: the egg stacking recess goes right through it and
  the **chassis plate is the recess ceiling**. Base 2 + plate 2 = 4 mm
  (was 5). The plate's underside holds the base's pogo flange and magnets.
- **Clamp ring 0.2 mm short** (`ring_relief`) so print variation (e.g. the
  supported brim underside) no longer pushes the base ~0.5 mm out.
- **Magnets at r = 43** (was 44) so their caps clear the clamp ring.
- **Counterbore 4.8 x 1.2 mm** (fits the 2 mm base).
- Result: inside height plate top -> face back = **10 mm** (was ~7.4) in
  the same 17 mm ball.

## v7 changes
- `egg_tip` **1 mm**; stacking fit `recess_clear_d` **0.1 mm** (was 0.2).
- Shell screws **M2 x 8 mm self-tapping**: pilot 1.7, clearance 2.3,
  counterbore 4.2 x 1.5 mm so the head sits fully below the base surface
  (0.5 mm of base under the head; measure your screw head and set
  `screw_head_d` / `screw_head_h`).
- LED ring screws **M2 x 6 mm self-tapping**; shortest post that takes them
  is `post_min` (= 6 - 1.6 PCB + 0.6 = 5 mm).
- **`internal_h`** (Body group): the FREE height for electronics under the
  LED ring, beyond the minimum. The ball height is now calculated:
  `ball_h = base_t + chassis_t + post_min + internal_h + ring_h + led_gap - protrude + face_t`
  At `internal_h = 0` the ball is 16.8 mm. Add to `internal_h` and the ball
  grows by the same amount. The console prints the result after F5/F6.

## v8 changes
- **Connector sizes from the fit test:** body hole 13.15 x 3.9, flange
  pocket 19.2 x 3.9, face body 1.9, flange 0.9, so the connector face sits
  flush. The flange now ends 0.2 mm short of the face back, so the hat's
  brim gets a 0.2 mm presser there (automatic); the chassis pocket follows
  the base connector's depth the same way.
- **`export_all.bat` (Windows) / `export_all.sh`**: export all five parts as
  separate STLs in one go, using the values saved in the .scad.
- The hat stays **one piece** (crown + brim + number inlay).

## Printing the hat and number together
`hat.stl` and `number.stl` share the same origin. In the slicer, add both
**in one step** (select both files) and answer **yes** to "load as a single
object with multiple parts"; then set the number's filament to black.

## Assembly (from the back of the ball)
1. Pogo connector (flat contacts) into the ball face.
2. Magnets into the ball's pockets, same pole towards the face.
3. Hat in from the back: egg through the opening, brim into its pocket
   (tongue over the pogo flange, caps over the magnets).
4. LED ring onto the chassis posts.
5. Base: pogo connector (spring pins) and magnets pressed in from the
   underside.
6. Chassis plate onto the base (its pockets take the base pogo flange and
   magnet tops), then both into the ball; 4 M2 x 8 mm self-tapping screws up
   through base and plate into the columns.

## Parts
| File | Print | Notes |
|---|---|---|
| `hat.stl` | white, face down, slicer supports under the brim | Tongue + caps print on top of the brim |
| `number.stl` | black, second part of the hat | 2.4 mm deep inlay |
| `ball.stl` | ball colour, face down | 104 mm OD, 16.8 mm tall at `internal_h` = 0 |
| `chassis.stl` | any, plate on the bed | Plate underside is visible in the stacking recess |
| `base.stl` | any, underside on the bed | 2 mm ring |

## Pogo connector
Measured: 2 mm oval face body, 1 mm flange, 1 mm oval back body (4 mm total).
- Faces sit **flush**: 2 mm of plastic in front of the flange, then a **1 mm
  flange pocket from the back**; the 1 mm back oval sticks out of the back.
- Oval hole 13.45 x **4.3** mm in the model (this printer prints holes about
  0.1 mm small: 4.5 printed 4.4, so 4.3 should print ~4.2).
- Ball connector: flange in the brim layer, pressed by the **brim tongue**.
  Base connector: flange pressed by a pocket under the **chassis plate**.
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
