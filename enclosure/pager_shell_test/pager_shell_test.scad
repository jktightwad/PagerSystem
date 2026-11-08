// Pool-ball pager shell test, v2 (OpenSCAD)
//
// Changes from ball_fit_test (v1), after the first prints:
//   - crown / opening / stacking recess are EGG shaped: this keys the
//     orientation (replaces the pogo keystone and the D-shaped brim)
//   - crown stands 1.5 mm proud (was 2.5); number at 80 % size
//   - pogo connector sits FLUSH in the coloured ring of the ball (flat
//     contacts) and in the base underside (spring pins), held by a clamp bar
//     over its back; no screw holes through the flange
//   - two 6 x 2.75 mm magnets per side, triangulated with the pogo connector:
//     hidden behind 0.4 mm of plastic in the ball, pressed in from the
//     underside in the base
//
// Coordinates: looking down on the pager face, +Y = 12 o'clock (narrow end
// of the egg, top of the number). Angles below are clockwise from 12 o'clock.
//
// Render: openscad -D 'part="ball"' -o ball.stl pager_shell_test.scad
//         part = "hat", "number", "ball", "base", "brim_clamp", "pogo_clamp",
//                "all" (exploded preview)

/* [Part to show / export] */
part = "all"; // [all, hat, number, ball, base, brim_clamp, pogo_clamp]

/* [Shape and size] */
white_d      = 72;     // egg's main circle (covers the 68.2 mm LED ring)
egg_small_d  = 62;     // second circle of the egg
egg_shift    = 9;      // how far it sits towards 12 o'clock
                       // -> egg is 72 wide, 76 tall (36 below centre, 40 above)
ball_od      = 104;    // coloured body
ball_face_t  = 3.0;
protrude     = 1.5;    // crown face above the ball face
crown_wall   = 1.6;
face_t       = 0.8;
crown_clear_d = 0.05;  // user's PLA sliding fit (diameter)

brim_w       = 3;      // brim around the crown, behind the ball face
brim_t       = 1.6;
brim_clear_d = 0.05;

/* [Number] */
number_text  = "2";
number_font  = "DejaVu Serif:style=Bold";
number_h     = 0.6 * white_d;   // 80 % of v1 (0.75)
number_mode  = "inlay"; // [inlay, raised, none]
raised_h     = 0.6;
number_depth = 2.4;     // inlay thickness: 0.8 through the face + 1.6 behind it,
                        // so bright LEDs can't glow through the black

/* [Body, screws and base] */
ball_wall    = 2.4;
ball_test_h  = 14;
boss_d       = 7;
screw_pilot  = 2.2;     // M2.5 self-tapping
screw_clear  = 2.9;
screw_head_d = 5.2;
screw_head_h = 2.0;
boss_r       = ball_od / 2 - ball_wall - boss_d / 2 + 0.5;
boss_angles  = [45, 135, 225, 315];

base_t         = 3.0;
recess_clear_d = 0.4;   // stacking recess is looser so pagers drop on easily
recess_d       = protrude + 0.3;

/* [Pogo connector] */
oval_l        = 13.15;
oval_w        = 4.0;
oval_hole_l   = 13.45;  // design sizes; printed ~0.1 mm smaller on this printer
oval_hole_w   = 4.3;    //   (4.5 printed 4.4; 4.3 should print ~4.2)
face_body     = 2.0;    // oval body in front of the flange
flange_l      = 19.2;
flange_w      = 4.0;
flange_t      = 1.0;
back_body     = 1.0;    // oval repeated behind the flange
flange_pocket_l = flange_l + 0.3;
flange_pocket_w = oval_hole_w;
pogo_r        = 44;     // radius of the connector centre
pogo_angle    = 180;    // 6 o'clock

/* [Pogo clamp bar] */
pclamp_l      = 28;
pclamp_w      = 6;
pclamp_t      = 2.4;
pclamp_screw_cc = 23.6;
pclamp_pilot  = 1.8;    // M2 self-tapping pilot, blind
pclamp_pilot_depth = 2.4;

/* [Magnets] */
mag_d         = 6.0;
mag_h         = 2.75;
mag_skin      = 0.4;    // plastic hiding the magnet in the ball face
mag_hole_ball = 6.05;   // slide in + glue
mag_hole_base = 6.0;    // press fit (prints ~5.9)
mag_r         = 44;
mag_angles    = [60, 300];  // with the pogo at 180: an equilateral triangle

/* [Hidden] */
$fn = 128;

module at_angle(r, a) {   // a: clockwise from 12 o'clock
  translate([r * sin(a), r * cos(a), 0]) rotate([0, 0, -a]) children();
}

module egg_2d(grow = 0) {
  offset(delta = grow) hull() {
    circle(d = white_d);
    translate([0, egg_shift]) circle(d = egg_small_d);
  }
}

module stadium_2d(l, w) {
  hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0]) circle(d = w);
}

module number_2d() {
  text(number_text, size = number_h, font = number_font, halign = "center", valign = "center");
}

// ================= Hat (modelled face up, z = 0 at brim underside) =========
hat_h = brim_t + ball_face_t + protrude;

module hat_upright() {
  difference() {
    union() {
      linear_extrude(brim_t) egg_2d(brim_w - crown_clear_d / 2);
      linear_extrude(hat_h) egg_2d(-crown_clear_d / 2);
      if (number_mode == "raised")
        translate([0, 0, hat_h]) linear_extrude(raised_h) number_2d();
    }
    translate([0, 0, -1]) linear_extrude(hat_h - face_t + 1) egg_2d(-crown_clear_d / 2 - crown_wall);
    if (number_mode == "inlay")
      translate([0, 0, hat_h - number_depth - 0.01]) linear_extrude(number_depth + 0.02) number_2d();
  }
}
module number_upright() { translate([0, 0, hat_h - number_depth]) linear_extrude(number_depth) number_2d(); }

// ================= Pogo connector cut-outs =================================
// Outer face of the connector at z = 0 pointing +Z, flush with the surface.
// Plastic is face_body thick over the flange, then a flange_t pocket from
// the back; the back oval sticks out of the back for the clamp bar.
module pogo_cut() {
  translate([0, 0, -face_body - 0.01]) linear_extrude(face_body + 1) stadium_2d(oval_hole_l, oval_hole_w);
  translate([0, 0, -face_body - flange_t - 5]) linear_extrude(flange_t + 5.01) stadium_2d(flange_pocket_l, flange_pocket_w);
  // blind pilots for the clamp bar screws, from the back
  for (s = [-1, 1]) translate([s * pclamp_screw_cc / 2, 0, -face_body - flange_t - 5])
    cylinder(d = pclamp_pilot, h = 5 + pclamp_pilot_depth, $fn = 20);
}

module pogo_clamp() {
  difference() {
    linear_extrude(pclamp_t) stadium_2d(pclamp_l, pclamp_w);
    // pocket for the 1 mm back oval
    translate([0, 0, -0.01]) linear_extrude(back_body + 0.05) stadium_2d(oval_hole_l, oval_hole_w);
    // wire slot through the middle
    translate([0, 0, -1]) linear_extrude(pclamp_t + 2) stadium_2d(8, 2.5);
    for (s = [-1, 1]) translate([s * pclamp_screw_cc / 2, 0, -1]) cylinder(d = 2.3, h = pclamp_t + 2, $fn = 20);
  }
}

// ================= Ball (modelled face up; z = 0 back, face top at ball_test_h)
module ball_upright() {
  top = ball_test_h;
  difference() {
    union() {
      difference() {
        cylinder(d = ball_od, h = top);
        translate([0, 0, -1]) cylinder(d = ball_od - 2 * ball_wall, h = top - ball_face_t + 1);
      }
      for (a = boss_angles) at_angle(boss_r, a) cylinder(d = boss_d, h = top);
      // pads behind the face so the magnet pockets keep 0.4 mm skin
      for (a = mag_angles) at_angle(mag_r, a)
        translate([0, 0, top - (mag_h + mag_skin + 0.05)]) cylinder(d = mag_d + 3, h = mag_h + mag_skin + 0.05);
    }
    // egg opening for the crown
    translate([0, 0, -1]) linear_extrude(top + 2) egg_2d(0);
    // brim pocket behind the face
    translate([0, 0, top - ball_face_t - brim_t]) linear_extrude(brim_t + 0.01) egg_2d(brim_w + brim_clear_d / 2);
    // pogo connector, flush with the face, flat contacts
    at_angle(pogo_r, pogo_angle) translate([0, 0, top]) pogo_cut();
    // hidden magnet pockets from the back
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, top - mag_skin - mag_h - 0.05 - 1]) cylinder(d = mag_hole_ball, h = mag_h + 0.05 + 1);
    // screw pilots in the bosses
    for (a = boss_angles) at_angle(boss_r, a)
      translate([0, 0, -1]) cylinder(d = screw_pilot, h = top - ball_face_t - 0.5, $fn = 24);
  }
}

// ================= Base (modelled right way up; z = 0 underside) ===========
module base_upright() {
  difference() {
    cylinder(d = ball_od, h = base_t);
    // egg stacking recess (crown of the pager below); touch sensor goes here
    translate([0, 0, -0.01]) linear_extrude(recess_d) egg_2d(recess_clear_d / 2);
    // pogo connector, flush with the underside, spring pins pointing down
    at_angle(pogo_r, pogo_angle) mirror([0, 0, 1]) pogo_cut();
    // magnets pressed in from the underside
    for (a = mag_angles) at_angle(mag_r, a) translate([0, 0, -0.01]) cylinder(d = mag_hole_base, h = mag_h + 0.01);
    // counterbored screws up into the ball bosses
    for (a = boss_angles) at_angle(boss_r, a) {
      translate([0, 0, -1]) cylinder(d = screw_clear, h = base_t + 2, $fn = 24);
      translate([0, 0, -0.01]) cylinder(d = screw_head_d, h = screw_head_h, $fn = 32);
    }
  }
}

// Loose ring between base and brim (the LED ring mount can do this later)
brim_clamp_h = ball_test_h - ball_face_t - brim_t;
module brim_clamp_upright() {
  difference() {
    linear_extrude(brim_clamp_h) egg_2d(brim_w - 0.5);
    translate([0, 0, -1]) linear_extrude(brim_clamp_h + 2) egg_2d(brim_w - 2.5);
  }
}

// ================= Print orientations ======================================
module hat_print()    { translate([0, 0, hat_h]) rotate([180, 0, 0]) hat_upright(); }       // face down
module number_print() { translate([0, 0, hat_h]) rotate([180, 0, 0]) number_upright(); }
module ball_print()   { translate([0, 0, ball_test_h]) rotate([180, 0, 0]) ball_upright(); } // face down
module base_print()   { translate([0, 0, base_t]) rotate([180, 0, 0]) base_upright(); }      // underside up

module preview() {
  color("royalblue") translate([0, 0, 25]) ball_upright();
  color("white") translate([0, 0, 25 + ball_test_h - ball_face_t - brim_t + 20]) hat_upright();
  if (number_mode == "inlay")
    color("black") translate([0, 0, 25 + ball_test_h - ball_face_t - brim_t + 20.01]) number_upright();
  color("gray") translate([0, 0, -10]) base_upright();
  color("dimgray") translate([0, 0, -10 + base_t + 6]) brim_clamp_upright();
}

if (part == "hat") hat_print();
else if (part == "number") number_print();
else if (part == "ball") ball_print();
else if (part == "base") base_print();
else if (part == "brim_clamp") brim_clamp_upright();
else if (part == "pogo_clamp") pogo_clamp();
else preview();

echo(str("Hat height ", hat_h, " mm, crown ", protrude, " mm proud; number height ~", number_h, " mm"));
echo(str("Pogo: oval hole ", oval_hole_l, " x ", oval_hole_w, ", flange pocket ", flange_t,
         " mm from the back, ", face_body, " mm plastic over the flange (faces flush)"));
