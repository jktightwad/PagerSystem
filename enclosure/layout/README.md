# Chassis layout sketch

`layout_sketch.scad` / `layout_sketch.png`: top view of the chassis plate
with component outlines, to check fit before designing mounts. Not a part.

![Layout](layout_sketch.png)

Space (pager_shell_test defaults, ball 20.8 mm): plate ~98.8 mm across;
**under the LED ring 13.2 mm** (`internal_h` 8.2 + 5 mm minimum post), with
the LED ring raised to 1.8 mm under the lit face (`led_depth` 2.6) so the
ball height doesn't change; outside the ring, up to the brim, 13.8 mm. LED
ring posts at (+-17.6, +-26.4).

| Part | Size (mm) | Placement |
|---|---|---|
| LOLIN32 Lite | 49.6 x 25.7 (+1.5 round the edges) | Centre, long axis 12-6 o'clock, between the LED posts (~0.75 mm clear each side); USB-C / JST end towards the pogo connector at 6 o'clock |
| Boost (3-pin, no enable) | 10.5 x 11 | Right side strip |
| TTP223 touch | 11 x 14 | Left, over the stacking recess (senses through the 2 mm plate) |
| Buzzer | 9.2 dia x 5.8 | Left, over the recess; sound hole through the plate into the recess |
| Vibration motor | 7 x 26 | Outer band at 9 o'clock, clamped to the chassis |
| Battery 500 mAh | 30 x 35 x ? (thickness to confirm, ~5) | On the plate under the LOLIN32 (stack: battery ~5 + gap 0.5 + LOLIN solder 1.5 + board 1.6 + tallest part ~4-5 = ~13) |
