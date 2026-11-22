# Combined pager board (16 LEDs + ESP32-S3 SuperMini) — draft

**Status: placed, routed, GND stitched; DRC has no clearance or unconnected errors
(remaining: silkscreen overlaps/clipping and 1 single-spoke thermal). Not ordered, not tested.**

| Top | Bottom (seen from below) |
|---|---|
| ![top](pcb_top.png) | ![bottom](pcb_bottom.png) |

54 x 48 mm, 2 layers, M2 holes in all 4 corners (layout D from `layout_study.py`).

- **Top:** 16 × TUOZHAN TZ-5050S2RGB-5V-I4-H1 (LCSC C26167850, allowed in JLC Economic PCBA; the XINGLIGHT part was Standard-only), evenly spaced (22.5°) on a 20.5 mm radius,
  ring turned 19.75° so every LED keeps its own 100 nF cap beside it, clear of the cut-out.
  Passive SMD buzzer XHXDZ SMD8530-16R (C49246948, 8.5 x 8.5 x 3.0 mm, 16 Ω, 2.7 kHz, PWM tone on GP12;
  four pads, + and − on the right, the two left pads are mechanical dummies) and
  the small parts inside the ring; all JLC-assembled.
- **Under:** SuperMini flat on castellated pads, antenna end at the right edge (no copper
  there); B+/B− soldered from the top through 1.1 × 1.6 mm plated oval holes; an
  L-shaped cut-out only where the module's underside parts are (measured: 3.0–11.2 mm
  from the USB end, incl. 0.5 mm clearance). GND pour (no tracks) allowed under the module. Touch (XH-3) and dock
  (XH-2) right-angle connectors, plugs in from the left edge. SS12F44 switch (slider
  down; end-leg spacing 11.2 mm is an ESTIMATE, slotted). Battery and motor wire pads.
- **Spare pins** on an arc outside the LED ring: top-left TX RX 3 6 7 3V3 GND,
  bottom-left 11 10 9 8 VBAT 3V3 GND (labels on both sides where they fit).
- Connectors: pin 1 = GND (square), power last.

Pins: dock GP1, battery GP2, touch GP4, LEDs GP5 (via 330 Ω), buzzer GP12, motor GP13.

## Rebuild
```
python3 build_main.py
ROUTE_OPTIONAL=GND ROUTE_FIRST=U1 ROUTE_MARGIN=0.08 \
  ROUTE_WIDTHS='{"VBAT": 0.3, "BAT+": 0.4, "POGO5V": 0.3, "MOT_-": 0.3, "GND": 0.25}' \
  python3 ../carrier_s3/route_pcb.py pager_main.kicad_pcb
python3 ../carrier_s3/stitch_gnd.py pager_main.kicad_pcb 2.0
python3 ../carrier_s3/join_gnd.py pager_main.kicad_pcb
python3 ../carrier_s3/remove_dangling.py pager_main.kicad_pcb
python3 fix_anchors.py pager_main.kicad_pcb && python3 check_netlist.py
sh export_fab.sh && sh render.sh pcb_top.png pcb_bottom.png
```
Routing takes a while (randomised retries; `ROUTE_SEED` picks the sequence). GND gets tracks
where they fit (routed last, best effort), plus pours on both layers, ~200 stitching vias and
`join_gnd.py` for any piece left over; `remove_dangling.py` drops stitch vias left in pour
islands. The current board is seed 3 with the transistor / divider block ripped up and
re-routed (`../carrier_s3/reroute_area.py`, box 14,19-30,31, GND fan-out vias for R2, R7, Q2,
C1), because those four GND pads were walled in by tracks.

## Assembly
Single-sided JLC Economic PCBA (top side): LEDs, caps, resistors, MOSFETs, diode, buzzer. Hand-soldered:
SuperMini, switch and the two through-hole JST-XH connectors (under the board).
A two-sided variant with SMD connectors (DEALON XH-3PWB / XH-2PWB) can still be built with
`PAGER_SMD_CONN=1 python3 build_main.py` and exported with `sh export_fab.sh smdconn` (Standard PCBA);
its files were removed to avoid uploading the wrong set.

## Current board (v4)
Placement from `build_main.py` (VBAT ring + U2 links pre-drawn). Routed in EasyEDA Pro (autorouter, GND
ignored) and imported with `../carrier_s3/import_dsn_wiring.py`; then: 3V3 link and a 0.4 mm module-B+ feed
(`add_links.py`), GND stubs + vias for boxed-in pads (`pad_vias.py`, local re-route of the nets around R4 / Q1),
ground pours + stitching (`stitch_gnd.py`, `join_gnd.py`, `remove_dangling.py`). Unrouted versions for an
external router are in `for_autorouter/`.

## Panel (3 x 2), not used
`panelize.py` can copy the finished board six times with tabs (`sh export_fab.sh panel` for its JLC
files). Not used: it saved about 4 % on the quote, so the panel files were removed to avoid
uploading the wrong set.

## Review package
`sh make_review.sh` builds `review/` and `review/pager_main_review.zip` for an independent check:
schematic (from `schematic.py`, drawn from `design_main.py`), net list, parts list, design
description with the specific questions, DRC, renders, KiCad and JLC files.

## JLCPCB
`fab/pager_main_gerbers.zip`, `fab/bom_jlc.csv`, `fab/cpl_jlc.csv` (top-side assembly:
LEDs, caps, resistors, MOSFETs, diode). Hand-soldered: SuperMini, switch, buzzer, XH
connectors. **Check LED orientation in JLC's placement preview** (XINGLIGHT package
drawing is an image only; same 5050 4-pin WS2812B pinout).

## Checking before ordering
- `python3 check_netlist.py` compares every pad's net with `design_main.py` (independent of
  the generator).
- `print/top_1to1.pdf` and `print/bottom_1to1_seen_from_below.pdf`: print at 100 % (no
  "fit to page"), check the board outline measures 54 x 48 mm, then lay the real SuperMini,
  switch and XH connectors on them (pin rows, B+/B- holes, cut-out, switch legs).
- In JLC's placement preview: LED pin 1, buzzer +/-, diode stripes, MOSFETs.

## Still to confirm
1. Switch end-leg spacing (11.2 mm assumed).
2. Antenna length (5 mm kept copper-free).
3. Base/ball redesign to fit this board (holes, slider slot, connector access).
