// Pool-ball pager: "top hat" number insert fit test (OpenSCAD)
//
// Parts:
//   hat    - the swappable number insert: a hollow white crown with a 0.8 mm
//            face and the number, and a keyed brim at the bottom. The crown
//            passes through the ball's face opening and stands proud of it;
//            the brim sits in a keyed pocket behind the ball face.
//   number - the number as a separate inlay (print in black with the hat as
//            a multi-material object), when number_mode = "inlay"
//   ball   - the coloured body, SHORTENED for this test (real one is deeper).
//            Prints face down. Screw bosses at the back.
//   base   - screws to the ball with recessed (counterbored) screws and has
//            the stacking recess underneath (which the crown of the pager
//            below keys into; touch sensor goes here). Prints recess up.
//   clamp  - loose ring between base and brim that holds the hat in place.
//
// Fit testing: hats are exported in three clearance variants (notches on
// the brim edge = variant number) against one ball opening.
//
// Render:  openscad -D 'part="hat"' -D 'hat_variant=1' -o hat_1.stl ball_fit_test.scad
//          part = "hat", "number", "ball", "base", "clamp", "all" (preview)
// The hat prints face down; its brim overhangs 4 mm, so enable supports
// (build plate only) under the brim.

part        = "all";
hat_variant = 0;          // 0, 1, 2 -> crown_clears_d values below

// ---- Main sizes ----
white_od     = 72;        // crown (white section) outside diameter; ring is 68.2
ball_od      = 100;       // outer diameter of the coloured body
ball_face_t  = 3.0;       // thickness of the ball's front face
protrude     = 2.5;       // crown face stands this far above the ball face
crown_wall   = 1.6;
face_t       = 0.8;       // the white face the light shines through
// Diameter clearances (crown smaller than the opening by this much).
// 0.05 mm is the user's usual PLA fit; the others are looser in case a part
// this large shrinks/warps differently.
crown_clears_d = [0.05, 0.10, 0.20];
ball_hole_d  = white_od;            // the ball opening

// Brim (keyed, sits behind the ball face)
brim_w       = 4;         // brim extends this far beyond the crown
brim_t       = 1.6;
brim_flat    = 3;         // D-flat depth at 6 o'clock: sets number orientation
brim_clear_d = 0.05;      // brim pocket clearance (diameter)

// Number
number_text  = "2";
number_font  = "DejaVu Serif:style=Bold";
number_h     = 0.75 * white_od;     // digit height
number_mode  = "inlay";   // "inlay": separate black part, full face depth
                          // "raised": raised 0.6 mm on the face (filament swap)
                          // "none"
raised_h     = 0.6;

// Ball test body
ball_wall    = 2.4;
ball_test_h  = 14;        // shortened body depth for the fit test
boss_d       = 7;
screw_pilot  = 2.2;       // M2.5 self-tapping into plastic (or M2 machine + nut)
screw_clear  = 2.9;
screw_head_d = 5.2;       // counterbore for the screw head
screw_head_h = 2.2;
boss_r       = ball_od / 2 - ball_wall - boss_d / 2 + 0.5;

// Base
base_t       = 4.5;
recess_clear_d = 0.4;     // stacking recess: deliberately looser so pagers drop on easily
recess_d     = protrude + 0.3;

$fn = 128;

brim_od = white_od + 2 * brim_w;
hat_h   = brim_t + ball_face_t + protrude;

module d_shape(d, flat, h) {
  // circle with a flat at -Y (6 o'clock)
  intersection() {
    cylinder(d = d, h = h);
    translate([-d, -d / 2 + flat, -1]) cube([2 * d, 2 * d, h + 2]);
  }
}

module number_2d() {
  text(number_text, size = number_h, font = number_font,
       halign = "center", valign = "center");
}

// Hat, modelled face UP (z = 0 at brim underside)
module hat_upright(clear_d) {
  crown_od = ball_hole_d - clear_d;
  difference() {
    union() {
      d_shape(brim_od, brim_flat, brim_t);
      cylinder(d = crown_od, h = hat_h);
      if (number_mode == "raised")
        translate([0, 0, hat_h]) linear_extrude(raised_h) number_2d();
    }
    // hollow crown: light from the ring reaches the 0.8 mm face
    translate([0, 0, -1]) cylinder(d = crown_od - 2 * crown_wall, h = hat_h - face_t + 1);
    // inlay pocket through the face
    if (number_mode == "inlay")
      translate([0, 0, hat_h - face_t - 0.01]) linear_extrude(face_t + 0.02) number_2d();
    // variant notches on the brim edge (at 12 o'clock)
    for (i = [0 : hat_variant])
      rotate([0, 0, 90 + (i - hat_variant / 2) * 4])
        translate([brim_od / 2, 0, -1]) cylinder(d = 1.6, h = brim_t + 2, $fn = 16);
  }
}

module number_inlay_upright() {
  translate([0, 0, hat_h - face_t]) linear_extrude(face_t) number_2d();
}

// Ball, modelled face UP (z = 0 at the back, face at z = ball_test_h)
module ball_upright() {
  difference() {
    union() {
      difference() {
        cylinder(d = ball_od, h = ball_test_h);
        translate([0, 0, -1]) cylinder(d = ball_od - 2 * ball_wall, h = ball_test_h - ball_face_t + 1);
      }
      for (a = [45, 135, 225, 315]) rotate([0, 0, a])
        translate([boss_r, 0, 0]) cylinder(d = boss_d, h = ball_test_h);
    }
    // face opening for the crown
    translate([0, 0, -1]) cylinder(d = ball_hole_d, h = ball_test_h + 2);
    // keyed brim pocket behind the face
    translate([0, 0, ball_test_h - ball_face_t - brim_t])
      d_shape(brim_od + brim_clear_d, brim_flat - brim_clear_d / 2, brim_t + 0.01);
    // screw pilots
    for (a = [45, 135, 225, 315]) rotate([0, 0, a])
      translate([boss_r, 0, -1]) cylinder(d = screw_pilot, h = ball_test_h - ball_face_t - 0.5, $fn = 24);
  }
}

// Base, modelled right way up (z = 0 underside). Same OD as the ball; the
// ball sits on top of it and the screws go up through it into the bosses.
module base_upright() {
  difference() {
    cylinder(d = ball_od, h = base_t);
    // stacking recess underneath (crown of the pager below keys in here;
    // touch sensor mounts in this recess)
    translate([0, 0, -0.01]) cylinder(d = ball_hole_d + recess_clear_d, h = recess_d);
    // screw clearance + counterbore from underneath
    for (a = [45, 135, 225, 315]) rotate([0, 0, a]) translate([boss_r, 0, 0]) {
      translate([0, 0, -1]) cylinder(d = screw_clear, h = base_t + 2, $fn = 24);
      translate([0, 0, -0.01]) cylinder(d = screw_head_d, h = screw_head_h, $fn = 32);
    }
  }
}

// Clamp ring: loose part between base and brim, pressing the brim into its
// pocket (in the real pager the LED-ring mount can do this job).
clamp_h = ball_test_h - ball_face_t - brim_t;
module clamp_upright() {
  difference() {
    cylinder(d = brim_od - 1, h = clamp_h);
    translate([0, 0, -1]) cylinder(d = brim_od - 1 - 4, h = clamp_h + 2);
  }
}

// ---- Print orientations ----
module hat_print()    { translate([0, 0, hat_h]) rotate([180, 0, 0]) hat_upright(crown_clears_d[hat_variant]); }
module number_print() { translate([0, 0, hat_h]) rotate([180, 0, 0]) number_inlay_upright(); }
module ball_print()   { translate([0, 0, ball_test_h]) rotate([180, 0, 0]) ball_upright(); }
module base_print()   { translate([0, 0, base_t]) rotate([180, 0, 0]) base_upright(); }  // recess up
module clamp_print()  { clamp_upright(); }

module preview() {
  color("royalblue") translate([0, 0, 20]) ball_upright();
  color("white") translate([0, 0, 20 + ball_test_h - ball_face_t - brim_t + 25]) hat_upright(crown_clears_d[0]);
  if (number_mode == "inlay")
    color("black") translate([0, 0, 20 + ball_test_h - ball_face_t - brim_t + 25.01]) number_inlay_upright();
  color("gray") translate([0, 0, -15]) base_upright();
  color("darkgray") translate([0, 0, -15 + base_t + 8]) clamp_upright();
}

if (part == "hat") hat_print();
else if (part == "number") number_print();
else if (part == "ball") ball_print();
else if (part == "base") base_print();
else if (part == "clamp") clamp_print();
else preview();

echo(str("Ball opening ", ball_hole_d, " mm; crown OD variants: ",
         [for (c = crown_clears_d) ball_hole_d - c]));
echo(str("Brim ", brim_od, " mm; hat height ", hat_h, " mm; crown stands ",
         protrude, " mm proud"));
