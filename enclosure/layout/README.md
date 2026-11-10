# Chassis layout sketch

`layout_sketch.scad` / `layout_sketch.png`: top view of the chassis plate
with component outlines, to check fit before designing mounts. Not a part.

![Layout](layout_sketch.png)

Space (pager_shell_test defaults, ball 20.8 mm, LED ring at its original
height): plate ~98.8 mm across; **9 mm under the LED ring** (68 mm circle in
the middle), 13.8 mm outside it up to the brim. LED ring posts at
(+-17.6, +-26.4).

| Part | Size (mm) | Placement (x, y from the centre; +y = 12 o'clock) |
|---|---|---|
| LOLIN32 Lite | 49.6 x 25.7 | Middle, flat on the plate, (0.15, 19.2): spans y -5.6 to +44, as far from the pogo as fits. USB-C / JST end towards 6 o'clock. 1 mm channels under both long edges for the solder joints (in the chassis model) |
| Battery 500 mAh | 30 x 35 x ~5 | Left, (-28, 0) |
| Boost (3-pin) | 10.5 x 11 | Lower left, (-31, -24) |
| Buzzer | 9.2 x 5.8 | Lower left, (-22, -36); sound hole through chassis plate + base (in the model) |
| Vibration motor | 7 x 26 | Right, (39.5, 0), in two U-clips (in the model) |
| TTP223 touch | 11 x 14 | Right, (22, -12), over the stacking recess |

All heights fit under the LED ring (9 mm): LOLIN32 ~6, battery ~5, boost
~4, buzzer 5.8.
