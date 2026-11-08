// Pool-ball pager shell test, v3 (OpenSCAD)
//
// v3 changes (after the v2 prints):
//   - hat brim has 4 TABS that hug the 4 screw columns: no rotation in the ball
//   - columns stop CHASSIS_T short of the ball's back; the new CHASSIS has a
//     plate that sits there, clamped between ball and base by the same 4
//     screws. The chassis carries: the brim clamp ring, a post that presses
//     the ball's pogo connector, a pocket that clamps the base's pogo
//     connector, LED ring posts, and room for the electronics.
//   - 2 mm radius on the ball's outer front edge (starts at 45 deg so it
//     prints face down without supports)
//   - separate pogo clamp bars and their screw pilots removed
//
// Coordinates: looking down on the pager face, +Y = 12 o'clock (narrow end
// of the egg, top of the number). Angles are clockwise from 12 o'clock.
// Ball/chassis z = 0 at the back rim of the ball (where it meets the base).
//
// Render: openscad -D 'part="ball"' -o ball.stl pager_shell_test.scad

/* [Part to show / export] */
part = "all"; // [all, hat, number, ball, chassis, base]

/* [Shape and size] */
white_d      = 72;     // egg's main circle (covers the 68.2 mm LED ring)
egg_small_d  = 62;     // second circle of the egg
egg_shift    = 9;      // how far it sits towards 12 o'clock
ball_od      = 104;    // coloured body
ball_face_t  = 3.0;
edge_r       = 2.0;    // radius on the outer front edge of the ball
protrude     = 1.5;    // crown face above the ball face
crown_wall   = 1.6;
face_t       = 0.8;
crown_clear_d = 0.05;  // user's PLA sliding fit (diameter)

brim_w       = 3;      // brim around the crown, behind the ball face
brim_t       = 1.6;
brim_clear_d = 0.05;
tab_w        = 12;     // brim tabs reaching the screw columns (fork ~2.4 mm each side)
tab_clear_d  = 0.1;    // clearance around the columns in the tab notches

/* [Number] */
number_text  = "2";
number_font  = "DejaVu Serif:style=Bold";
number_h     = 0.6 * white_d;
number_mode  = "inlay"; // [inlay, raised, none]
raised_h     = 0.6;
number_depth = 2.4;     // 0.8 through the face + 1.6 behind it

/* [Body, screws and base] */
body_h       = 14;      // ball depth (short for the test; the real pager is deeper)
ball_wall    = 2.4;
boss_d       = 7;
screw_pilot  = 2.2;     // M2.5 self-tapping
screw_clear  = 2.9;
screw_head_d = 5.2;
screw_head_h = 2.0;
boss_r       = ball_od / 2 - ball_wall - boss_d / 2 + 0.5;
boss_angles  = [45, 135, 225, 315];

base_t         = 3.0;
recess_clear_d = 0.2;   // stacking fit (diameter)
recess_d       = protrude + 0.3;
recess_chamfer = 0.8;
crown_chamfer  = 0.4;
wire_hole_d    = 6;     // base/chassis hole for the touch-sensor wires

/* [Chassis] */
chassis_t     = 2.0;    // plate between the column ends and the base
chassis_clear = 0.2;    // radial clearance to the ball wall
led_gap       = 6;      // LED tops to the underside of the white face
ring_h        = 2.5;    // measured: ring PCB + LEDs
ring_hole_cx  = 35.24;  // ring mounting holes, centre to centre
ring_hole_cy  = 52.8;
ring_post_d   = 5;
ring_pilot    = 1.8;    // M2 self-tapping
pogo_post_extra = 0.0;  // make the pogo post this much longer to add clamp pressure

/* [Pogo connector] */
oval_hole_l   = 13.45;  // design sizes; printed ~0.1 mm smaller on this printer
oval_hole_w   = 4.3;
face_body     = 2.0;    // oval body in front of the flange
flange_l      = 19.2;
flange_t      = 1.0;
back_body     = 1.0;    // oval repeated behind the flange
flange_pocket_l = flange_l + 0.3;
pogo_r        = 44;
pogo_angle    = 180;    // 6 o'clock
pogo_post_l   = 28;
pogo_post_w   = 6;

/* [Magnets] */
mag_d         = 6.0;
mag_h         = 2.75;
mag_skin      = 0.4;
mag_hole_ball = 6.05;   // slide in + glue
mag_hole_base = 6.0;    // press fit
mag_r         = 44;
mag_angles    = [60, 300];

/* [Hidden] */
$fn = 128;

face_back_z   = body_h - ball_face_t;                 // underside of the ball face
brim_bottom_z = face_back_z - brim_t;
hat_h         = brim_t + ball_face_t + protrude;
face_under_z  = body_h + protrude - face_t;           // underside of the white face
ring_bottom_z = face_under_z - led_gap - ring_h;

// ================= Helpers =================================================
module at_angle(r, a) { translate([r * sin(a), r * cos(a), 0]) rotate([0, 0, -a]) children(); }

module egg_2d(grow = 0) {
  offset(delta = grow) hull() {
    circle(d = white_d);
    translate([0, egg_shift]) circle(d = egg_small_d);
  }
}

module stadium_2d(l, w) { hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0]) circle(d = w); }

module number_2d() {
  text(number_text, size = number_h, font = number_font, halign = "center", valign = "center");
}

module bosses_2d(grow = 0) { for (a = boss_angles) at_angle(boss_r, a) circle(d = boss_d + 2 * grow); }

// Brim outline: egg + brim, plus 4 tabs reaching the columns, minus the columns
module brim_2d(grow = 0) {
  difference() {
    union() {
      egg_2d(brim_w + grow);
      for (a = boss_angles) hull() {
        circle(d = tab_w + 2 * grow);
        at_angle(boss_r, a) circle(d = tab_w + 2 * grow);
      }
    }
    bosses_2d(tab_clear_d / 2 - grow);
  }
}

// ================= Hat (face up, z = 0 at brim underside) ==================
module hat_upright() {
  difference() {
    union() {
      linear_extrude(brim_t) brim_2d(-brim_clear_d / 2);
      linear_extrude(hat_h - crown_chamfer) egg_2d(-crown_clear_d / 2);
      hull() {
        translate([0, 0, hat_h - crown_chamfer]) linear_extrude(0.01) egg_2d(-crown_clear_d / 2);
        translate([0, 0, hat_h - 0.01]) linear_extrude(0.01) egg_2d(-crown_clear_d / 2 - crown_chamfer);
      }
      if (number_mode == "raised") translate([0, 0, hat_h]) linear_extrude(raised_h) number_2d();
    }
    // hollow: light from the ring reaches the face; the hub of the brim is
    // removed too so the LED ring and brim clamp have room
    translate([0, 0, -1]) linear_extrude(hat_h - face_t + 1) egg_2d(-crown_clear_d / 2 - crown_wall);
    if (number_mode == "inlay")
      translate([0, 0, hat_h - number_depth - 0.01]) linear_extrude(number_depth + 0.02) number_2d();
  }
}
module number_upright() { translate([0, 0, hat_h - number_depth]) linear_extrude(number_depth) number_2d(); }

// ================= Pogo connector cut-out ==================================
// Outer face of the connector at z = 0 pointing +Z, flush with the surface;
// face_body of plastic, then a flange_t pocket open to the back.
module pogo_cut() {
  translate([0, 0, -face_body - 0.01]) linear_extrude(face_body + 1) stadium_2d(oval_hole_l, oval_hole_w);
  translate([0, 0, -face_body - flange_t - 5]) linear_extrude(flange_t + 5.01) stadium_2d(flange_pocket_l, oval_hole_w);
}

// ================= Ball (face up) ==========================================
// Outer profile with a rounded front edge that starts at 45 deg (prints
// face down without supports): flat face out to the 45-deg tangent, then
// the edge_r arc, then the vertical side.
module ball_outer() {
  R = ball_od / 2;
  rotate_extrude() hull() {
    square([R, body_h - edge_r]);
    translate([R - edge_r, body_h - edge_r]) circle(r = edge_r, $fn = 48);
    // 45-deg tangent point on the face plane
    square([R - edge_r + edge_r * (sqrt(2) - 1), body_h]);
  }
}

module ball_upright() {
  difference() {
    union() {
      difference() {
        ball_outer();
        translate([0, 0, -1]) cylinder(d = ball_od - 2 * ball_wall, h = face_back_z + 1);
      }
      // columns stop chassis_t above the back rim
      for (a = boss_angles) at_angle(boss_r, a)
        translate([0, 0, chassis_t]) cylinder(d = boss_d, h = body_h - chassis_t);
      // pads behind the face for the hidden magnet pockets
      for (a = mag_angles) at_angle(mag_r, a)
        translate([0, 0, body_h - (mag_h + mag_skin + 0.05)]) cylinder(d = mag_d + 3, h = mag_h + mag_skin + 0.05);
    }
    translate([0, 0, -1]) linear_extrude(body_h + 2) egg_2d(0);                       // crown opening
    translate([0, 0, brim_bottom_z]) linear_extrude(brim_t + 0.01) brim_2d(brim_clear_d / 2);  // brim seat
    at_angle(pogo_r, pogo_angle) translate([0, 0, body_h]) pogo_cut();               // flat contacts
    for (a = mag_angles) at_angle(mag_r, a)                                          // hidden magnets
      translate([0, 0, body_h - mag_skin - mag_h - 0.05 - 1]) cylinder(d = mag_hole_ball, h = mag_h + 0.05 + 1);
    for (a = boss_angles) at_angle(boss_r, a)                                        // screw pilots
      translate([0, 0, chassis_t - 1]) cylinder(d = screw_pilot, h = face_back_z - chassis_t + 0.5, $fn = 24);
  }
}

// ================= Chassis (right way up, z = 0 on the base) ===============
module chassis() {
  plate_d = ball_od - 2 * ball_wall - 2 * chassis_clear;
  difference() {
    union() {
      cylinder(d = plate_d, h = chassis_t);
      // brim clamp ring: from the plate up to the brim, following the egg
      linear_extrude(brim_bottom_z) difference() { egg_2d(brim_w - 0.5); egg_2d(brim_w - 2.5); }
      // post pressing the ball's pogo connector (its back oval)
      at_angle(pogo_r, pogo_angle)
        linear_extrude(face_back_z + pogo_post_extra) stadium_2d(pogo_post_l, pogo_post_w);
      // LED ring posts
      for (sx = [-1, 1], sy = [-1, 1]) translate([sx * ring_hole_cx / 2, sy * ring_hole_cy / 2, 0])
        cylinder(d = ring_post_d, h = ring_bottom_z, $fn = 32);
    }
    // ball pogo: pocket for its 1 mm back oval at the top of the post + wire slot
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, face_back_z + pogo_post_extra - back_body - 0.05])
        linear_extrude(back_body + 1) stadium_2d(oval_hole_l, oval_hole_w);
      translate([0, 0, chassis_t]) linear_extrude(50) stadium_2d(8, 2.5);
    }
    // base pogo: pocket underneath the plate for its 1 mm back oval + wire slot
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, -0.01]) linear_extrude(back_body + 0.05) stadium_2d(oval_hole_l, oval_hole_w);
      translate([0, 0, -1]) linear_extrude(chassis_t + 2) stadium_2d(8, 2.5);
    }
    // screws pass through the plate into the columns
    for (a = boss_angles) at_angle(boss_r, a) translate([0, 0, -1]) cylinder(d = screw_clear, h = chassis_t + 2, $fn = 24);
    // LED ring post pilots
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx * ring_hole_cx / 2, sy * ring_hole_cy / 2, chassis_t])
      cylinder(d = ring_pilot, h = 50, $fn = 20);
    // wires to the touch sensor in the base recess
    translate([0, 0, -1]) cylinder(d = wire_hole_d, h = chassis_t + 2);
    // keep clear of the magnet pockets in the base (press-fit magnets stand proud if long)
    for (a = mag_angles) at_angle(mag_r, a) translate([0, 0, -1]) cylinder(d = mag_d + 1, h = 1.5);
  }
}

// ================= Base (right way up; z = 0 underside) ====================
module base_upright() {
  difference() {
    cylinder(d = ball_od, h = base_t);
    translate([0, 0, -0.01]) linear_extrude(recess_d) egg_2d(recess_clear_d / 2);
    hull() {
      translate([0, 0, -0.01]) linear_extrude(0.01) egg_2d(recess_clear_d / 2 + recess_chamfer);
      translate([0, 0, recess_chamfer]) linear_extrude(0.01) egg_2d(recess_clear_d / 2);
    }
    at_angle(pogo_r, pogo_angle) mirror([0, 0, 1]) pogo_cut();                      // spring pins
    for (a = mag_angles) at_angle(mag_r, a) translate([0, 0, -0.01]) cylinder(d = mag_hole_base, h = mag_h + 0.01);
    for (a = boss_angles) at_angle(boss_r, a) {
      translate([0, 0, -1]) cylinder(d = screw_clear, h = base_t + 2, $fn = 24);
      translate([0, 0, -0.01]) cylinder(d = screw_head_d, h = screw_head_h, $fn = 32);
    }
    translate([0, 0, -1]) cylinder(d = wire_hole_d, h = base_t + 2);
  }
}

// ================= Print orientations ======================================
module hat_print()    { translate([0, 0, hat_h]) rotate([180, 0, 0]) hat_upright(); }
module number_print() { translate([0, 0, hat_h]) rotate([180, 0, 0]) number_upright(); }
module ball_print()   { translate([0, 0, body_h]) rotate([180, 0, 0]) ball_upright(); }
module base_print()   { translate([0, 0, base_t]) rotate([180, 0, 0]) base_upright(); }

module preview() {
  e = 18;   // explode distance
  color("gray") translate([0, 0, -base_t - e]) base_upright();
  color("darkgray") chassis();
  color("royalblue") translate([0, 0, e]) ball_upright();
  color("white") translate([0, 0, 2 * e + brim_bottom_z]) hat_upright();
  if (number_mode == "inlay") color("black") translate([0, 0, 2 * e + brim_bottom_z + 0.01]) number_upright();
}

if (part == "hat") hat_print();
else if (part == "number") number_print();
else if (part == "ball") ball_print();
else if (part == "chassis") chassis();
else if (part == "base") base_print();
else preview();

echo(str("Body ", body_h, " mm; face underside at ", face_under_z, "; LED ring bottom at ",
         ring_bottom_z, " (posts ", ring_bottom_z - chassis_t, " mm above the plate)"));
assert(ring_bottom_z > chassis_t + 1, "led_gap too large for body_h: no room for the LED ring posts");
