# Pogo connector + keystone fit test

Two small coupons that stack like two pagers, to check the magnetic pogo
connector fit, its protrusion, and the keystone that sets orientation.
Source: `pogo_key_test.scad` (OpenSCAD, every dimension is a parameter).

![Preview](preview.png)

| File | What it stands in for | Contents |
|---|---|---|
| `pogo_key_top.stl` | Top of a pager (and the dock) | Raised trapezoid **keystone** with the **flat-contact** half; flange recessed from underneath; wire groove |
| `pogo_key_cal.stl` | Calibration chip | Four connector slots with different plastic thickness over the flange |
| `pogo_key_bottom.stl` | Underside of the pager above | Matching keystone **recess** with the **spring-pin** half (protected inside the recess); flange recessed from the inside; wire groove |

Both STLs are oriented to print with the flange side on the bed (no
supports). The trapezoid only mates one way round.

## Proposed arrangement
- **Spring pins** on the pager **underside**, inside the recess (protected
  when the pager is set down on a desk).
- **Flat contacts** on the **keystone on top** of every pager and on the dock.
- In the real pager the keystone sits **off-centre in the coloured border**,
  so it also sets the rotation of the whole pager.

## Calibration first: `pogo_key_cal.stl`
The first coupons left a gap of over 1 mm: the recess was 0.8 mm deeper
than the keystone, and the connector faces sat below their surfaces. Now:
- recess depth = keystone height + `seat_clear` (0.15 mm)
- connector faces are meant to be **flush**, so the seated face gap is about
  0.15 mm (target: 0.4 mm or less; the pins have ~0.8 mm of travel).

Where a face ends up depends on the plastic over its flange (`cover_t`),
which depends on the connector's real body height. The chip has four slots
with **1.20 / 1.35 / 1.50 / 1.65 mm** cover (1-4 notches on the edge; print
flat as exported). Push a connector half into each slot from underneath and
find the one where the face is **flush** with the top surface. Set
`cover_t_flat` and `cover_t_pins` to that value (and `body_depth` to the
same number), then re-export the coupons. Check both halves: they may
differ.

## Parameters to tune (top of the .scad)
| Parameter | Default | Notes |
|---|---|---|
| `oval_l`, `oval_w` | 13.15, 4.0 | Measured |
| `oval_clear` | 0.25 | Hole clearance per side |
| `body_depth` | 1.5 | Body height above the flange: **estimate** from the first print |
| `flange_l`, `flange_w`, `flange_t` | 19.2, 4.0, 1.0 | Measured |
| `cover_t_flat`, `cover_t_pins` | 1.5 | Plastic over the flange; set from the calibration chip |
| `seat_clear` | 0.15 | Recess depth beyond keystone height = designed face gap when flush |
| `key_long`, `key_short`, `key_depth`, `key_h` | 28, 22, 12, 3 | Keystone shape |
| `key_clear` | 0.3 | Recess clearance per side |

The OpenSCAD console prints the designed face gap; keep it between 0 and 0.4.

Screw pilots stop 0.5 mm short of the outer surface; with ~1.5 mm of
plastic over the flange they only give ~1 mm of grip, so expect to glue or
clamp the connectors (see the clamp-bar option discussed in chat).

## Re-exporting
```
openscad -D 'part="top"' -o pogo_key_top.stl pogo_key_test.scad
openscad -D 'part="bottom"' -o pogo_key_bottom.stl pogo_key_test.scad
openscad -D 'part="cal"' -o pogo_key_cal.stl pogo_key_test.scad
```

> **Superseded:** the keystone was dropped; the pogo connector now sits flush in the ball/base (`enclosure/pager_shell_test`). The calibration chip is still useful for checking connector depth.
