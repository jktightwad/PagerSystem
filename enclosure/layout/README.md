# Chassis layout sketch

`layout_sketch.scad` / `layout_sketch.png`: top view of the chassis plate
with component outlines, to check fit before designing mounts. Not a part.

![Layout](layout_sketch.png)

Space (pager_shell_test defaults, ball 20.8 mm, LED ring at its original
height): plate ~98.8 mm across; **9 mm under the LED ring** (68 mm circle in
the middle), 13.8 mm outside it up to the brim. LED ring posts at
(+-17.6, +-26.4).

**Current layout (general only, not final)** is modelled directly in the
chassis (`pager_shell_test.scad`, "Component mounts" group); every position
and angle is a Customizer setting. `layout_sketch.png` above is the older
outline sketch.

![Chassis layout](chassis_layout.png)

Pockets: 1.2 mm walls (`pocket_wall`), 5 mm high (`pocket_h`), 0.3 mm
clearance round each part (`pocket_clear`); neighbours share walls. LED ring
posts at 1 and 7 o'clock removed (`ring_posts`), 11 and 5 o'clock kept.
Angles are clockwise from 12 o'clock.

| Part | Size (mm) | Placement |
|---|---|---|
| Battery (white stand-in) | 30 x 35 | Left, centre (-25.5, 2); shares its right wall with the LOLIN32 |
| LOLIN32 Lite | 49.6 x 25.7 | Centre (4.15, 16.9), shifted right so the shared wall clears; USB-C / JST end (6 o'clock side) open; 1 mm channels under the long edges |
| Boost (3-pin) | 10.5 x 11 | 205 deg (~7 o'clock), back on the clamp-ring wall (no pocket back wall; `boost_gap` moves it in) |
| Buzzer | 9.2 dia | 190 deg (~6:30), r 28, just inside the LED ring; one sound hole through chassis plate and base |
| Touch module | 24 x 24.3 | 117 deg (~4 o'clock), back on the clamp-ring wall (no pocket back wall; `touch_gap`), facing the centre |
| Vibration motor | 7 x 26 | Centre (32, 16), axis turned 45 deg towards the LOLIN32, two U-clips |

All heights fit under the LED ring (9 mm): LOLIN32 ~6, battery ~5, boost
~4, buzzer 5.8.
