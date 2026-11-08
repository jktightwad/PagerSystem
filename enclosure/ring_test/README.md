# LED ring diffusion test rig

Tests how far the 16-LED ring (68.2 mm OD) should sit below a 0.8 mm white
face for an even glow. Source: `ring_test.scad` (OpenSCAD, parametric).

![Assembly preview](preview.png)

## Parts
| File | Print | Notes |
|---|---|---|
| `ring_test_cup.stl` | 1, **white**, already oriented **face down** | The 0.8 mm face is the first 4 layers at 0.2 mm. Wall notch for the cable |
| `ring_test_base.stl` | 1, any colour | M2 nut traps underneath, centring lip on top, cable hole |
| `ring_test_spacers.stl` | 1 plate: 4 each of 5, 10, 15, 20, 25 mm | Tubes for M2 bolts |

## LED-to-face gap per spacer
Assumes ring PCB 1.6 mm and LEDs 1.6 mm tall (measure yours and change
`pcb_t` / `led_h` in the .scad if different).

| Spacer | Gap | M2 bolt length (approx.) |
|---|---|---|
| 5 mm | 21.8 mm | 10 mm |
| 10 mm | 16.8 mm | 14-16 mm |
| 15 mm | 11.8 mm | 20 mm |
| 20 mm | 6.8 mm | 25 mm |
| 25 mm | 1.8 mm | 30 mm |

Bolt length = ring PCB + spacer + base (2.4 mm) + nut (~1.6 mm).

## Assembly
1. Drop 4 M2 nuts into the traps under the base.
2. Bolt down through the ring's holes, the spacers and the base into the nuts.
   LEDs face **up**.
3. Feed the 3 wires (DI, 5V, GND) through the base cable hole.
4. Drop the cup over the base; the wall notch can line up with the cable.
5. Run `pager_alert_test` (`t`, then `a`) and compare gaps.

## Check before printing
- **The ring's holes are 1.8 mm, smaller than an M2 bolt (2.0 mm).** Either
  drill them to 2.0-2.1 mm (check there are no traces right at the hole
  edge), or use M1.6 bolts and nuts (then set `nut_af = 3.2` and
  `bolt_clear_d = 1.9`).
- Hole spacing was entered as **outside edge to outside edge** (37.24 x
  54.8 mm), giving centres 35.44 x 53.0 mm. If you measured centre to
  centre, set `hole_cx = 37.24; hole_cy = 54.8;` and re-export.

## Re-exporting STLs
```
openscad -D 'part="base"' -o ring_test_base.stl ring_test.scad
openscad -D 'part="cup"' -o ring_test_cup.stl ring_test.scad
openscad -D 'part="spacers"' -o ring_test_spacers.stl ring_test.scad
```
