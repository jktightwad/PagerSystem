// Pool-ball pager shell test, v6 (OpenSCAD)
//
// v6 (after the v5 assembly):
//   - hat brim 1 mm, SUNK into a 1 mm pocket in the back of the ball face:
//     face + brim = ball_face_t (3 mm) instead of 4.6 mm. The brim still
//     follows the column bumps (no rotation). Under the brim: a tongue that
//     presses the ball's pogo flange, and caps that hold the magnets.
//   - base is now a RING: the egg stacking recess goes right through it and
//     the chassis plate is the recess ceiling. Base 2 mm + plate 2 mm (was
//     3 + 2). The plate's underside holds the base's pogo flange and magnets.
//   - clamp ring is ring_relief (0.2 mm) short so print variation no longer
//     pushes the base out of the ball (v5 stuck out ~0.5 mm)
//   - magnets moved in to r = 43 so their caps clear the clamp ring
// Earlier decisions kept: egg-shaped crown/opening/recess, columns blended
// into the wall, base flush inside the ball wall, 2 mm front-edge radius,
// chassis plate under the column ends, LED ring posts.
//
// Coordinates: z = 0 at the bottom rim of the ball (underside of the base).
// Looking down on the face, +Y = 12 o'clock; angles clockwise from 12.
//
// Export one part: choose `part`, press F6, wait for "Rendering finished",
// then F7 (export uses the LAST F6 render).

/* [Part to show / export] */
part = "all"; // [all, hat, number, ball, chassis, base]

/* [Shape and size] */
white_d      = 72;     // egg's main circle (covers the 68.2 mm LED ring)
egg_small_d  = 62;
egg_tip      = 2;      // how far the egg's narrow end sticks out (0 = round)
ball_od      = 104;
ball_h       = 17;     // overall ball height (test value; real pager deeper)
ball_face_t  = 3.0;    // face, INCLUDING the 1 mm brim pocket on its back
edge_r       = 2.0;
protrude     = 1.5;    // crown face above the ball face
crown_wall   = 1.6;
face_t       = 0.8;    // white face the light shines through
crown_clear_d = 0.05;
crown_chamfer = 0.4;

brim_t       = 1.0;    // hat brim, sunk into the back of the ball face
brim_gap_d   = 0.5;    // brim smaller than the ball's inside (diameter)
column_fillet = 3;
pad_t        = 1.0;    // tongue under the brim pressing the pogo flange
cap_t        = 0.8;    // caps under the brim holding the magnets
cap_recess   = 0.25;   // magnets stand 0.15 proud of the face back

/* [Number] */
number_text  = "2";
number_font  = "DejaVu Serif:style=Bold";
number_h     = 0.6 * white_d;
number_mode  = "inlay"; // [inlay, raised, none]
raised_h     = 0.6;
number_depth = 2.4;     // face_t through the face + 1.6 behind it

/* [Body, screws and base] */
ball_wall    = 2.4;
boss_d       = 7;
screw_pilot  = 2.2;     // M2.5 self-tapping
screw_clear  = 2.9;
screw_head_d = 4.8;
screw_head_h = 1.2;     // counterbore in the 2 mm base
boss_r       = ball_od / 2 - ball_wall - boss_d / 2 + 0.5;
boss_angles  = [45, 135, 225, 315];

base_t         = 2.0;   // base ring = depth of the stacking recess
base_clear_d   = 0.1;   // base inside the ball wall (diameter)
recess_clear_d = 0.2;   // stacking fit (diameter)
recess_chamfer = 0.8;

/* [Chassis] */
chassis_t     = 2.0;    // plate: ceiling of the stacking recess
chassis_clear = 0.2;
clamp_ring_w  = 2.0;
ring_relief   = 0.2;    // clamp ring this much short of the face back
led_gap       = 6;      // LED tops to the underside of the white face
ring_h        = 2.5;    // measured LED ring thickness
ring_hole_cx  = 35.24;
ring_hole_cy  = 52.8;
ring_post_d   = 5;
ring_pilot    = 1.8;

/* [Pogo connector] */
oval_hole_l   = 13.45;
oval_hole_w   = 4.3;
face_body     = 2.0;    // oval body in front of the flange
flange_l      = 19.2;
flange_t      = 1.0;
back_body     = 1.0;
flange_pocket_l = flange_l + 0.3;
pogo_r        = 44;
pogo_angle    = 180;
tongue_w      = 6.6;    // brim tongue over the ball pogo flange

/* [Magnets] */
mag_d         = 6.0;
mag_h         = 2.75;
mag_skin      = 0.4;
mag_hole_ball = 6.05;
mag_hole_base = 6.0;    // press fit
mag_r         = 43;
mag_angles    = [60, 300];

/* [Hidden] */
$fn = 128;
egg_shift  = egg_tip + (white_d - egg_small_d) / 2;
face_back  = ball_h - ball_face_t;            // back of the face (brim underside)
col_start  = base_t + chassis_t;              // columns start here
hat_h      = brim_t + (ball_face_t - brim_t) + protrude;
face_under = ball_h + protrude - face_t;      // underside of the white face
ring_bottom = face_under - led_gap - ring_h;
mag_bottom  = ball_h - mag_skin - mag_h;      // magnet bottom (below face_back)

// ================= Helpers =================================================
module at_angle(r, a) { translate([r * sin(a), r * cos(a), 0]) rotate([0, 0, -a]) children(); }
module egg_2d(grow = 0) {
  offset(delta = grow) hull() { circle(d = white_d); translate([0, egg_shift]) circle(d = egg_small_d); }
}
module stadium_2d(l, w) { hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0]) circle(d = w); }
module number_2d() { text(number_text, size = number_h, font = number_font, halign = "center", valign = "center"); }
module bosses_2d() { for (a = boss_angles) at_angle(boss_r, a) circle(d = boss_d); }
module cavity_2d() {
  offset(r = column_fillet) offset(delta = -column_fillet)
    difference() { circle(d = ball_od - 2 * ball_wall); bosses_2d(); }
}
module brim_2d() { offset(delta = -brim_gap_d / 2) cavity_2d(); }
module tongue_2d() { at_angle(pogo_r, pogo_angle) stadium_2d(flange_pocket_l + 4, tongue_w); }

// ================= Hat (face up; z = 0 at the face back plane) =============
module hat_upright() {
  difference() {
    union() {
      linear_extrude(brim_t) brim_2d();
      linear_extrude(hat_h - crown_chamfer) egg_2d(-crown_clear_d / 2);
      hull() {
        translate([0, 0, hat_h - crown_chamfer]) linear_extrude(0.01) egg_2d(-crown_clear_d / 2);
        translate([0, 0, hat_h - 0.01]) linear_extrude(0.01) egg_2d(-crown_clear_d / 2 - crown_chamfer);
      }
      // tongue under the brim pressing the ball pogo flange
      translate([0, 0, -pad_t]) linear_extrude(pad_t + 0.01) tongue_2d();
      // caps under the brim holding the magnets
      for (a = mag_angles) at_angle(mag_r, a) translate([0, 0, -cap_t]) cylinder(d = mag_d + 1.2, h = cap_t + 0.01);
      if (number_mode == "raised") translate([0, 0, hat_h]) linear_extrude(raised_h) number_2d();
    }
    translate([0, 0, -pad_t - 1]) linear_extrude(hat_h - face_t + pad_t + 1) egg_2d(-crown_clear_d / 2 - crown_wall);
    if (number_mode == "inlay")
      translate([0, 0, hat_h - number_depth - 0.01]) linear_extrude(number_depth + 0.02) number_2d();
    // pogo: flange sits in the brim layer (cut-out); back oval + wires through the tongue
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, -0.01]) linear_extrude(brim_t + 1) stadium_2d(flange_pocket_l, oval_hole_w);
      translate([0, 0, -pad_t - 1]) linear_extrude(pad_t + brim_t + 2) stadium_2d(oval_hole_l, oval_hole_w);
    }
    // magnets pass through the brim; caps have a shallow recess for the 0.15 mm overhang
    for (a = mag_angles) at_angle(mag_r, a) {
      translate([0, 0, -0.01]) cylinder(d = mag_d + 0.4, h = brim_t + 1);
      translate([0, 0, -cap_recess]) cylinder(d = mag_d + 0.4, h = cap_recess + 0.02);
    }
  }
}
module number_upright() { translate([0, 0, hat_h - number_depth]) linear_extrude(number_depth) number_2d(); }

// ================= Pogo cut (outer face at z = 0, pointing +Z) =============
module pogo_cut() {
  translate([0, 0, -face_body - 0.01]) linear_extrude(face_body + 1) stadium_2d(oval_hole_l, oval_hole_w);
  translate([0, 0, -face_body - flange_t - 5]) linear_extrude(flange_t + 5.01) stadium_2d(flange_pocket_l, oval_hole_w);
}

// ================= Ball (face up) ==========================================
module ball_outer() {
  R = ball_od / 2;
  rotate_extrude() hull() {
    square([R, ball_h - edge_r]);
    translate([R - edge_r, ball_h - edge_r]) circle(r = edge_r, $fn = 48);
    square([R - edge_r + edge_r * (sqrt(2) - 1), ball_h]);   // 45-deg start: prints face down
  }
}

module ball_upright() {
  difference() {
    ball_outer();
    translate([0, 0, -1]) cylinder(d = ball_od - 2 * ball_wall, h = col_start + 1);          // base + plate
    translate([0, 0, col_start - 0.01]) linear_extrude(face_back + brim_t - col_start + 0.01) cavity_2d();  // + brim pocket
    translate([0, 0, -1]) linear_extrude(ball_h + 2) egg_2d(0);                              // crown opening
    at_angle(pogo_r, pogo_angle) translate([0, 0, ball_h]) pogo_cut();                       // flat contacts
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, face_back - 1]) cylinder(d = mag_hole_ball, h = ball_h - mag_skin - face_back + 1);
    for (a = boss_angles) at_angle(boss_r, a)
      translate([0, 0, col_start - 1]) cylinder(d = screw_pilot, h = face_back - col_start + 0.5, $fn = 24);
  }
}

// ================= Chassis (absolute z; plate from base_t) =================
module chassis_abs() {
  plate_d = ball_od - 2 * ball_wall - 2 * chassis_clear;
  ring_top = face_back - ring_relief;
  difference() {
    union() {
      translate([0, 0, base_t]) cylinder(d = plate_d, h = chassis_t);
      // clamp ring at the wall, pressing the brim's outer edge (notched at the tongue)
      translate([0, 0, col_start - 0.01]) linear_extrude(ring_top - col_start + 0.01) difference() {
        offset(delta = -brim_gap_d / 2 - chassis_clear) cavity_2d();
        offset(delta = -brim_gap_d / 2 - chassis_clear - clamp_ring_w) cavity_2d();
        offset(delta = 0.3) tongue_2d();
      }
      for (sx = [-1, 1], sy = [-1, 1]) translate([sx * ring_hole_cx / 2, sy * ring_hole_cy / 2, base_t])
        cylinder(d = ring_post_d, h = ring_bottom - base_t, $fn = 32);
    }
    // base pogo: flange pocket + back oval + wires, from the plate underside
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, base_t - 0.01]) linear_extrude(flange_t + 0.01) stadium_2d(flange_pocket_l, oval_hole_w);
      translate([0, 0, base_t - 1]) linear_extrude(chassis_t + 2) stadium_2d(oval_hole_l, oval_hole_w);
    }
    // base magnets stick up 0.75 mm into the plate
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, base_t - 0.01]) cylinder(d = mag_d + 0.4, h = mag_h - base_t + 0.1);
    for (a = boss_angles) at_angle(boss_r, a) translate([0, 0, base_t - 1]) cylinder(d = screw_clear, h = chassis_t + 2, $fn = 24);
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx * ring_hole_cx / 2, sy * ring_hole_cy / 2, col_start])
      cylinder(d = ring_pilot, h = 50, $fn = 20);
  }
}
module chassis() { translate([0, 0, -base_t]) chassis_abs(); }   // plate on the bed

// ================= Base ring (z 0 .. base_t) ===============================
module base_upright() {
  difference() {
    cylinder(d = ball_od - 2 * ball_wall - base_clear_d, h = base_t);
    // egg stacking recess goes right through; lead-in chamfer at the bottom
    translate([0, 0, -1]) linear_extrude(base_t + 2) egg_2d(recess_clear_d / 2);
    hull() {
      translate([0, 0, -0.01]) linear_extrude(0.01) egg_2d(recess_clear_d / 2 + recess_chamfer);
      translate([0, 0, recess_chamfer]) linear_extrude(0.01) egg_2d(recess_clear_d / 2);
    }
    at_angle(pogo_r, pogo_angle) mirror([0, 0, 1]) pogo_cut();                      // spring pins
    for (a = mag_angles) at_angle(mag_r, a) translate([0, 0, -1]) cylinder(d = mag_hole_base, h = base_t + 2);
    for (a = boss_angles) at_angle(boss_r, a) {
      translate([0, 0, -1]) cylinder(d = screw_clear, h = base_t + 2, $fn = 24);
      translate([0, 0, -0.01]) cylinder(d = screw_head_d, h = screw_head_h, $fn = 32);
    }
  }
}

// ================= Print orientations ======================================
module hat_print()    { translate([0, 0, hat_h]) rotate([180, 0, 0]) hat_upright(); }       // face down
module number_print() { translate([0, 0, hat_h]) rotate([180, 0, 0]) number_upright(); }
module ball_print()   { translate([0, 0, ball_h]) rotate([180, 0, 0]) ball_upright(); }     // face down
module base_print()   { base_upright(); }                                                    // underside on the bed

module preview() {
  e = 15;
  color("gray") translate([0, 0, -2 * e]) base_upright();
  color("darkgray") translate([0, 0, -e]) chassis_abs();
  color("royalblue") ball_upright();
  color("white") translate([0, 0, face_back + e]) hat_upright();
  if (number_mode == "inlay") color("black") translate([0, 0, face_back + e + 0.01]) number_upright();
}

if (part == "hat") hat_print();
else if (part == "number") number_print();
else if (part == "ball") ball_print();
else if (part == "chassis") chassis();
else if (part == "base") base_print();
else preview();

echo(str("Inside height: plate top ", col_start, " to face back ", face_back, " = ",
         face_back - col_start, " mm. LED ring bottom at ", ring_bottom, " mm (posts ",
         ring_bottom - col_start, " mm above the plate)"));
assert(base_t >= protrude + 0.3, "base_t must be at least protrude + 0.3 (stacking recess depth)");
assert(ring_bottom > col_start + 1, "led_gap too large for ball_h: no room for the LED ring posts");
