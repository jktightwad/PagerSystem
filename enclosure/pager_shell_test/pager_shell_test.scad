// Pool-ball pager shell test, v4 (OpenSCAD)
//
// v4 changes (after review of v3):
//   - screw columns are blended into the ball wall with a radius; the hat
//     brim fills the inside of the ball (0.5 mm gap) and follows that shape,
//     so the bumps stop it rotating. The brim also holds the ball's pogo
//     connector (slot for its back + wires) and the hidden magnets.
//   - chassis clamp ring moved out to the wall, beside the columns, leaving
//     the middle free for electronics; pogo post removed
//   - egg tip reduced to 2 mm (was 4) via the new egg_tip setting
// v5: the base sits INSIDE the bottom of the ball wall, flush with its rim
//     (no seam on the side); centre wire holes removed (only pogo wires).
// Ball/chassis coordinates: z = 0 at the top of the base; the ball wall runs
// down to z = -base_t.
// Kept from v3: columns stop chassis_t short of the back rim, chassis plate
// clamped between ball and base by the 4 screws (it also clamps the base's
// pogo connector), LED ring posts, 2 mm radius on the front edge.
//
// Coordinates: looking down on the pager face, +Y = 12 o'clock (narrow end
// of the egg, top of the number). Angles are clockwise from 12 o'clock.
//
// Render: openscad -D 'part="ball"' -o ball.stl pager_shell_test.scad

/* [Part to show / export] */
part = "all"; // [all, hat, number, ball, chassis, base]

/* [Shape and size] */
white_d      = 72;     // egg's main circle (covers the 68.2 mm LED ring)
egg_small_d  = 62;     // second circle of the egg
egg_tip      = 2;      // how far the egg's narrow end sticks out past the round
                       // part (v2/v3: 4). 0 = round (no rotation key).
ball_od      = 104;    // coloured body
ball_face_t  = 3.0;
edge_r       = 2.0;    // radius on the outer front edge of the ball
protrude     = 1.5;    // crown face above the ball face
crown_wall   = 1.6;
face_t       = 0.8;
crown_clear_d = 0.05;  // user's PLA sliding fit (diameter)

brim_t       = 1.6;    // hat brim: fills the inside of the ball behind the face
brim_gap_d   = 0.5;    // brim smaller than the ball's inside by this (diameter)
column_fillet = 3;     // radius blending the screw columns into the ball wall
mag_capture_h = 0.3;   // brim recess over each magnet (magnet stands 0.15 proud)

/* [Number] */
number_text  = "2";
number_font  = "DejaVu Serif:style=Bold";
number_h     = 0.6 * white_d;
number_mode  = "inlay"; // [inlay, raised, none]
raised_h     = 0.6;
number_depth = 2.4;     // 0.8 through the face + 1.6 behind it

/* [Body, screws and base] */
body_h       = 14;      // ball depth above the base (short for the test; the real
                        // pager is deeper). The ball wall also wraps the base.
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
base_clear_d   = 0.1;   // base fits inside the bottom of the ball wall (diameter)

/* [Chassis] */
chassis_t     = 2.0;    // plate between the column ends and the base
chassis_clear = 0.2;    // radial clearance to the ball wall
led_gap       = 6;      // LED tops to the underside of the white face
ring_h        = 2.5;    // measured: ring PCB + LEDs
ring_hole_cx  = 35.24;  // ring mounting holes, centre to centre
ring_hole_cy  = 52.8;
ring_post_d   = 5;
ring_pilot    = 1.8;    // M2 self-tapping
clamp_ring_w  = 2.0;    // chassis ring pressing the brim's outer edge

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

/* [Magnets] */
mag_d         = 6.0;
mag_h         = 2.75;
mag_skin      = 0.4;    // plastic hiding the magnet on the ball face
mag_hole_ball = 6.05;   // held in by the hat brim (no glue needed)
mag_hole_base = 6.0;    // press fit
mag_r         = 44;
mag_angles    = [60, 300];

/* [Hidden] */
$fn = 128;
egg_shift = egg_tip + (white_d - egg_small_d) / 2;   // centre of the egg's small circle

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

// Inside of the ball where the columns are: circle minus columns, with the
// column/wall junctions rounded by column_fillet
module cavity_2d() {
  offset(r = column_fillet) offset(delta = -column_fillet)
    difference() { circle(d = ball_od - 2 * ball_wall); bosses_2d(); }
}

// Hat brim: the cavity shape, brim_gap_d smaller on diameter
module brim_2d() { offset(delta = -brim_gap_d / 2) cavity_2d(); }

// ================= Hat (face up, z = 0 at brim underside) ==================
module hat_upright() {
  difference() {
    union() {
      linear_extrude(brim_t) brim_2d();
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
    // slot for the ball pogo connector's back oval + wires (brim presses its flange)
    at_angle(pogo_r, pogo_angle) translate([0, 0, -1]) linear_extrude(brim_t + 2) stadium_2d(oval_hole_l, oval_hole_w);
    // shallow recesses that capture the magnets standing proud of the face back
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, brim_t - mag_capture_h]) cylinder(d = mag_d + 0.4, h = mag_capture_h + 0.01);
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
    translate([0, -base_t]) square([R, body_h - edge_r + base_t]);   // wall wraps the base
    translate([R - edge_r, body_h - edge_r]) circle(r = edge_r, $fn = 48);
    // 45-deg tangent point on the face plane
    square([R - edge_r + edge_r * (sqrt(2) - 1), body_h]);
  }
}

module ball_upright() {
  difference() {
    ball_outer();
    // below the column ends: plain circle (the chassis plate goes here)
    translate([0, 0, -base_t - 1]) cylinder(d = ball_od - 2 * ball_wall, h = base_t + chassis_t + 1);
    // above: cavity with the columns blended into the wall
    translate([0, 0, chassis_t - 0.01]) linear_extrude(face_back_z - chassis_t + 0.01) cavity_2d();
    translate([0, 0, 0]) linear_extrude(body_h + 1) egg_2d(0);                        // crown opening
    at_angle(pogo_r, pogo_angle) translate([0, 0, body_h]) pogo_cut();               // flat contacts
    for (a = mag_angles) at_angle(mag_r, a)                                          // magnets, 0.4 mm skin
      translate([0, 0, face_back_z - 1]) cylinder(d = mag_hole_ball, h = body_h - mag_skin - face_back_z + 1);
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
      // clamp ring at the wall, beside the columns, pressing the brim's edge
      linear_extrude(brim_bottom_z) difference() {
        offset(delta = -brim_gap_d / 2 - chassis_clear) cavity_2d();
        offset(delta = -brim_gap_d / 2 - chassis_clear - clamp_ring_w) cavity_2d();
      }
      // LED ring posts
      for (sx = [-1, 1], sy = [-1, 1]) translate([sx * ring_hole_cx / 2, sy * ring_hole_cy / 2, 0])
        cylinder(d = ring_post_d, h = ring_bottom_z, $fn = 32);
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
  }
}

// ================= Base (right way up; z = 0 underside) ====================
module base_upright() {
  difference() {
    cylinder(d = ball_od - 2 * ball_wall - base_clear_d, h = base_t);   // sits inside the ball wall
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
  }
}

// ================= Print orientations ======================================
module hat_print()    { translate([0, 0, hat_h]) rotate([180, 0, 0]) hat_upright(); }
module number_print() { translate([0, 0, hat_h]) rotate([180, 0, 0]) number_upright(); }
module ball_print()   { translate([0, 0, body_h]) rotate([180, 0, 0]) ball_upright(); }   // face down
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
