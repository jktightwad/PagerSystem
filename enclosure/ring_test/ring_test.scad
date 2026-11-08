// LED ring light-diffusion test rig (OpenSCAD)
//
// Three parts:
//   base   - disc with a centring lip, 4 M2 nut traps underneath, cable hole
//   spacer - tube; print several heights to vary the LED-to-face gap
//   cup    - open-bottom cup with a 0.8 mm face; print FACE DOWN in white
//
// The 16-LED ring sits on 4 spacers, bolted through the base with M2 bolts
// and nuts. The cup drops over the base (its rim sits on the base, outside
// the lip). Gap from LED tops to the face underside:
//   gap = cup_inner_h - spacer_h - ring_h
//
// Render one part:  openscad -D 'part="base"' -o base.stl ring_test.scad
//                   (part = "base", "cup", "spacers", or "all" to preview)

part = "all";

// ---- Measured LED ring ----
ring_od        = 68.2;
ring_id        = 53.6;
hole_outside_x = 37.24;   // measured outside edge to outside edge
hole_outside_y = 54.8;
ring_hole_d    = 2.0;   // M2 bolt (1.9 mm measured) just passes
hole_cx = hole_outside_x - ring_hole_d;   // centre-to-centre = 35.24
hole_cy = hole_outside_y - ring_hole_d;   // centre-to-centre = 52.80
ring_h  = 2.5;   // measured: PCB + LED height

// ---- Rig ----
wall        = 2.0;
cup_od      = 82;
cup_id      = cup_od - 2 * wall;     // 78
face_t      = 0.8;                   // the white face being tested
cup_inner_h = 30;                    // base top to face underside
base_t      = 2.4;
lip_h       = 3.0;
lip_clear   = 0.3;                   // cup-to-lip clearance per side
cable_hole_d = 7;

// M2 hardware
bolt_clear_d = 2.3;
nut_af       = 4.0;                  // M2 nut across flats
nut_h        = 1.8;                  // trap depth (M2 nut is ~1.6)
nut_clear    = 0.3;

// Spacers
spacer_od      = 5.0;
spacer_id      = 2.4;
spacer_heights = [5, 10, 15, 20, 25];

$fn = 96;

module hole_positions() {
  for (sx = [-1, 1], sy = [-1, 1])
    translate([sx * hole_cx / 2, sy * hole_cy / 2, 0]) children();
}

module base() {
  lip_od = cup_id - 2 * lip_clear;
  difference() {
    union() {
      cylinder(d = cup_od, h = base_t);
      // centring lip the cup slides over
      translate([0, 0, base_t])
        difference() {
          cylinder(d = lip_od, h = lip_h);
          translate([0, 0, -1]) cylinder(d = lip_od - 2 * 1.6, h = lip_h + 2);
        }
    }
    hole_positions() {
      translate([0, 0, -1]) cylinder(d = bolt_clear_d, h = base_t + 2, $fn = 24);
      // hex nut trap from underneath
      translate([0, 0, -0.01])
        cylinder(d = (nut_af + nut_clear) / cos(30), h = nut_h, $fn = 6);
    }
    // cable hole, offset from the bolt pattern
    translate([0, -12, -1]) cylinder(d = cable_hole_d, h = base_t + 2);
  }
}

module spacer(h) {
  difference() {
    cylinder(d = spacer_od, h = h, $fn = 40);
    translate([0, 0, -1]) cylinder(d = spacer_id, h = h + 2, $fn = 24);
  }
}

module spacers() {
  for (i = [0 : len(spacer_heights) - 1])
    for (j = [0 : 3])   // 4 of each height
      translate([i * 10, j * 10, 0]) spacer(spacer_heights[i]);
}

// Modelled the right way up; print it FACE DOWN (flip in the slicer, or
// use the "cup" part, which is already flipped).
module cup_upright() {
  notch_w = 10;
  notch_h = 6;
  difference() {
    cylinder(d = cup_od, h = cup_inner_h + face_t);
    translate([0, 0, -1]) cylinder(d = cup_id, h = cup_inner_h + 1);
    // cable / USB notch in the rim
    translate([-notch_w / 2, -cup_od / 2 - 1, -1]) cube([notch_w, wall + 2, notch_h + 1]);
  }
}

module cup_print() {
  translate([0, 0, cup_inner_h + face_t]) rotate([180, 0, 0]) cup_upright();
}

// Preview: everything assembled, cup see-through
module preview() {
  sh = spacer_heights[1];
  base();
  hole_positions() translate([0, 0, base_t]) color("gray") spacer(sh);
  translate([0, 0, base_t + sh])
    color("darkgreen") difference() {
      cylinder(d = ring_od, h = ring_h);
      translate([0, 0, -1]) cylinder(d = ring_id, h = ring_h + 2);
    }
  translate([0, 0, base_t]) color("white", 0.35) cup_upright();
}

if (part == "base") base();
else if (part == "cup") cup_print();
else if (part == "spacers") spacers();
else preview();

// Gap for each spacer height (shown in the console when rendering)
for (h = spacer_heights)
  echo(str("spacer ", h, " mm -> LED-to-face gap ", cup_inner_h - h - ring_h, " mm"));
