// Pool-ball pager shell test, v9 (OpenSCAD)
//
// v9: ball face 2 mm; internal_h 4 by default; light_t (Light group) sets
// ONLY the lit face thickness, growing inwards (outside height unchanged;
// led_depth now measures LED tops from the face's TOP); no chamfers on the
// crown / base ring fit; base_pogo_extra gives the base connector's flange
// 0.2 mm more room in the chassis; magnet caps and the pogo tongue resize
// automatically for the face thickness.
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

// The number's font ships with the model so every PC renders the same digit
// (a missing system font is silently replaced by another, different-sized one).
use <fonts/LiberationSans-Bold.ttf>
use <fonts/DejaVuSerif-Bold.ttf>

/* [Part to show / export] */
part = "all"; // [all, hat, number, ball, chassis, base, clip_test]

/* [Shape and size] */
white_d      = 72;     // egg's main circle (covers the 68.2 mm LED ring)
egg_small_d  = 62;
// how far the egg's narrow end sticks out (0 = round)
egg_tip      = 1; // [0:0.1:10]
ball_od      = 104;
// ball face thickness, INCLUDING the brim pocket on its back
ball_face_t  = 2.6; // [1.5:0.1:6]
edge_r       = 5.0;
protrude     = 1.5;    // crown face above the ball face
crown_wall   = 1.6;
// white face the light shines through

crown_clear_d = 0.05; // [0:0.01:1]
crown_chamfer = 0;     // bevel on the crown's top edge (0 = none)

// hat brim thickness (part sits in the face pocket, the rest hangs below)
brim_t       = 2.0; // [0.6:0.1:6]
// how much of the brim sits in the pocket in the back of the ball face
brim_sink    = 1.0; // [0:0.1:3]
// brim smaller than the ball's inside (diameter)
brim_gap_d   = 0.5; // [0:0.01:2]
column_fillet = 3;
// minimum plastic under a magnet / the pogo flange; where the brim is too
// thin, a cap / tongue is added underneath to reach this
floor_min    = 0.6; // [0.3:0.1:3]
// side wall around each magnet pocket in a cap (caps only appear if needed)
cap_wall     = 2.0; // [0.8:0.1:5]
// magnet pocket diameter in the hat brim
mag_pocket_d = 6.4; // [6:0.01:7]

/* [Light] */
// thickness of the white lit face; thicker adds material on the INSIDE,
// so the outside height stays the same
light_t      = 0.4; // [0.2:0.01:3]

/* [Number] */
number_text  = "2";
// pool-ball style bold sans (Liberation Sans Bold = Arial/Helvetica metrics);
// loaded from fonts/ (see top of file). DejaVu Serif Bold is also bundled.
number_font  = "Liberation Sans:style=Bold";
// number size as a fraction of the white circle's diameter (0.6 = 43 mm text size)
number_scale = 0.45; // [0.2:0.01:1]
// underline under the number (pool-ball style, tells 6 from 9)
underline    = "auto"; // [auto, on, off]
// "arc": curved like the pool-ball 6 / 9; "bar": straight
underline_style = "arc"; // [arc, bar]
// underline sizes as fractions of the number height (they scale with it)
underline_w     = 0.6;  // [0.2:0.01:1.5]
underline_t     = 0.1;  // [0.03:0.005:0.3]
underline_gap   = 0.025; // [0:0.005:0.3]
underline_sag   = 0.06; // [0:0.005:0.3]
// digit height / text size for the chosen font (Liberation Sans Bold 0.98,
// DejaVu Serif Bold 1.03); positions the underline under the digit
digit_h_ratio   = 0.98; // [0.6:0.01:1.4]
number_mode  = "inlay"; // [inlay, raised, none]
raised_h     = 0.6;
number_back  = 1.6;     // black number continues this far behind the lit face (so it doesn't glow)

/* [Body, screws and base] */
// FREE height for electronics under the LED ring, on top of the minimum. The ball height is calculated from this.
internal_h   = 3; // [0:0.1:60]
ball_wall    = 2.4;
boss_d       = 7;
// Shell screws: M2 x 8 mm self-tapping, head recessed fully in the base
// in the columns
screw_pilot  = 1.7; // [1:0.01:5]
// through base and chassis plate
screw_clear  = 2.3; // [1:0.01:5]
screw_head_d = 4.2;     // M2 pan head (measure yours)
screw_head_h = 1.5;     // counterbore depth (head height); leaves base_t - this under the head
boss_r       = ball_od / 2 - ball_wall - boss_d / 2 + 0.5;
boss_angles  = [45, 135, 225, 315];

base_t         = 2.0;   // base ring = depth of the stacking recess
// base inside the ball wall (diameter)
base_clear_d   = 0.1; // [0:0.01:1]
// stacking fit (diameter): crown of the pager below in the base ring
recess_clear_d = 0.1; // [0:0.01:2]
recess_chamfer = 0;     // lead-in at the base ring opening (0 = none)

/* [Chassis] */
chassis_t     = 2.0;    // plate: ceiling of the stacking recess
chassis_clear = 0.2;
clamp_ring_w  = 2.0;
// clamp ring this much short of the face back
ring_relief   = 0.2; // [0:0.01:2]
// LED tops to the underside of the white face
// LED tops below the TOP of the white face (sets the ball height; light_t
// doesn't change it)
led_depth     = 7.8; // [1:0.1:30]
ring_h        = 2.5;    // measured LED ring thickness
ring_od       = 68.2;   // measured LED ring outside diameter
ring_hole_cx  = 35.24;
ring_hole_cy  = 52.8;
ring_post_d   = 5;
ring_pilot    = 1.7;    // LED ring screws: M2 x 6 mm self-tapping
ring_pcb_t    = 1.6;    // ring PCB only (the screw goes through this)
ring_screw_l  = 6;
post_min      = ring_screw_l - ring_pcb_t + 0.6;   // shortest post that takes the screw

/* [Component mounts] */
// GENERAL LAYOUT ONLY (not final). Each part sits in a pocket of 1.2 mm walls
// on the chassis plate; neighbouring pockets share walls. +y = 12 o'clock.
pocket_wall    = 1.2;   // [0.6:0.1:3]
pocket_h       = 5.0;   // [1:0.5:10] wall height above the plate
pocket_clear   = 0.3;   // [0:0.05:1] gap round each part
// cut the clamp ring away behind the boost and touch module
ring_open_at_parts = false;
// LED ring posts kept: [x sign, y sign] of the 4 holes (11 and 5 o'clock kept)
ring_posts     = [[-1, 1], [1, -1]];
// battery 503035 (35 x 30 x 5) at 9 o'clock, back on the clamp ring (3 walls);
// bat_y moves it along the wall (+ = towards 12 o'clock). Its inner wall is
// shared with the LOLIN32, which is placed from it automatically.
bat_w = 35; bat_l = 30; bat_gap = 0; bat_y = 4;
// LOLIN32 Lite: snug tray (lolin_clear per side); top end against the clamp
// ring at 12 o'clock, held at the pogo end by a tab. USB/JST end open.
lolin_w        = 25.7;
lolin_l        = 49.6;
lolin_clear    = 0.05;  // [0:0.01:0.5] per side
lolin_gap      = 0;     // [0:0.1:10] board top end to the clamp ring
lolin_chan_w   = 3.0;   // 1 mm channels under the long edges for the solder joints
lolin_chan_d   = 1.0;
lolin_pin_inset = 1.27;
// tray side walls stop this much short of the board's pogo-side (6 o'clock) end
lolin_tray_cut = 4;     // [0:0.5:20]
// tab at the board's pogo-side end that stops it sliding towards the pogo
lolin_tab_off  = 9.5;   // [0:0.1:25] from the battery-side (left) inside wall to the tab
lolin_tab_w    = 4;     // [1:0.5:20]
lolin_tab_h    = 4;     // [1:0.5:10]
lolin_tab_t    = 2;     // [0.8:0.1:5]
// boost board 10.5 x 11 at ~7 o'clock against the wall (angle clockwise from 12)
// parts against the chassis wall get no back wall: they sit on the clamp ring.
// *_gap moves the part in from the wall (0 = touching)
boost_w = 10.5; boost_l = 11; boost_gap = 0; boost_a = 205;
// buzzer 9.2 on the wall between the 7:30 screw column and the battery;
// one sound hole through the plate
buzzer_d = 9.2; buzzer_gap = 0; buzzer_a = 241;
sound_hole_d   = 2.0;
// touch module at ~4 o'clock, back against the wall
touch_w = 24; touch_l = 24.3; touch_gap = 0; touch_a = 114;
// vibration motor at ~3 o'clock, angled 45 deg towards the LOLIN32, one clip
motor_d        = 7.0;
motor_l        = 26;
motor_x        = 32;
motor_y        = 16;
motor_angle    = 45;    // axis rotation from 12-6 o'clock (CCW)
clip_w         = 8;     // [2:0.5:20] clip length along the motor
clip_wall      = 1.2;   // [0.6:0.1:3]
clip_h         = 5.5;
motor_clear    = 0.1;   // [0:0.05:1] added to the motor diameter in the clip
clip_open      = 0.84;  // [0.5:0.01:0.95] snap opening as a fraction of motor_d

/* [Power switch] */
// slide switch, upside down: slider pokes down through a slot in the plate
switch_w       = 8.75;  // [1:0.01:30] along the slider travel
switch_d       = 5.0;   // [1:0.01:20]
switch_h       = 4.5;   // [1:0.01:20] body height (sets the clip hook height)
switch_clear   = 0;     // [0:0.01:0.5] per side
switch_extra_w = 0.2;   // [0:0.01:2] added to the length along the travel
switch_slider_l = 4.35; // [0:0.01:10] slider length out of the body
// slider tip ends level with: 0 = bottom of the chassis plate, base_t = bottom of the base
switch_tip_below = 0.6; // [0:0.1:5]
switch_slot_l  = 5.75;  // [1:0.01:20] slot along the travel
switch_slot_w  = 2.2;   // [0.5:0.05:6] slot width (MEASURE the slider)
switch_pad_w   = 1.5;   // [0.5:0.1:5] riser pads under each end
switch_clip_t  = 1.2;   // [0.6:0.1:4] clip arm thickness (flex direction)
// gap between each riser pad and its clip (0 = pad fused to the arm, which
// shortens the flexing length and concentrates the bend at the pad top)
switch_pad_gap = 0.6;   // [0:0.1:1.4]
switch_clip_w  = 5;     // [1:0.5:10] clip width (across the switch)
switch_hook    = 0.6;   // [0.2:0.05:2] hook overhang onto the switch top
switch_hook_t  = 0.6;   // [0:0.05:3] flat lip thickness at the hook tip (was 0: a knife edge)
switch_base_slot = true; // cut the slot through the base too
// wall along the switch's pogo-side (-y) face so it can't slide that way
switch_wall    = true;   // clip_test only (the chassis uses the boost wall)
switch_wall_gap  = 0.6; // [0:0.1:3] gap between the clips and the wall so they can flex
// against the front wall of the boost pocket; switch_dx slides it along that wall
switch_dx = 0;          // [-10:0.1:10]

/* [Clip test plate] */
test_motor_clears = [0.1, 0.2, 0.3];
// switch mounts on the test plate, one per clip arm thickness
test_switch_clip_ts = [1.2, 1.6, 2.4];

/* [Pogo connector] */
// hole for the oval body through the face (connector 13.15)
oval_hole_l   = 13.15; // [5:0.01:30]
// (connector 4.0; this printer prints holes ~0.1 small)
oval_hole_w   = 3.9; // [1:0.01:10]
// oval body in front of the flange
face_body     = 1.9; // [0.4:0.01:6]
flange_l      = 19.2;
flange_t      = 0.9; // [0.2:0.01:5]
back_body     = 1.0;
// pocket for the flange (flange 19.2 long)
flange_pocket_l = 19.2; // [5:0.01:40]
// pocket width (flange 4.0 wide)
flange_pocket_w = 3.9; // [1:0.01:10]
// extra room for the BASE connector's flange in the chassis pocket
base_pogo_extra = 0.2; // [0:0.05:1]
pogo_r        = 44;
pogo_angle    = 180;
tongue_w      = 6.6;    // brim tongue over the ball pogo flange

/* [Magnets] */
mag_d         = 6.0;
mag_h         = 2.75;
mag_skin      = 0.4;
mag_hole_ball = 6.05; // [4:0.01:10]
// press fit
mag_hole_base = 6.0; // [4:0.01:10]
mag_r         = 43;
mag_angles    = [60, 300];

/* [Hidden] */
$fn = 128;
number_h   = number_scale * white_d;
// Ball height follows from: base + plate + shortest LED post + internal_h +
// LED ring + LED-to-face gap, up to the white face (minus how far it protrudes)
ball_h     = base_t + chassis_t + post_min + internal_h + ring_h + led_depth - protrude;
egg_shift  = egg_tip + (white_d - egg_small_d) / 2;
face_back  = ball_h - ball_face_t;            // back of the face (brim underside)
col_start  = base_t + chassis_t;              // columns start here
hat_h      = ball_face_t + protrude;           // hat z = 0 is the face back plane
brim_top   = brim_sink;                         // brim top (in the face pocket)
brim_bot   = brim_sink - brim_t;                // brim bottom (below the face back if < 0)
face_under = ball_h + protrude - light_t;     // underside of the white face
ring_bottom = ball_h + protrude - led_depth - ring_h;
number_depth = light_t + number_back;
mag_bottom  = ball_h - mag_skin - mag_h;      // magnet bottom (below face_back)
// Connector depth vs the plastic it sits in. Positive = the flange's back is
// short of the surface that should press it, so a presser is added.
pogo_depth   = face_body + flange_t;          // face to back of flange
ball_flange_gap = ball_face_t - pogo_depth;   // ball: face back plane vs flange back
// magnets stand proud of the face back by this much
mag_proud  = max(0, mag_skin + mag_h - ball_face_t);
mag_pocket_bot = -mag_proud - 0.1;                  // magnet pocket floor (hat z)
mag_floor_bot  = mag_pocket_bot - floor_min;        // plastic needed down to here
pogo_floor_bot = ball_flange_gap - floor_min;       // under the flange (hat z)
cap_bot    = min(brim_bot, mag_floor_bot);          // cap reaches here (= brim_bot: no cap)
tongue_bot = min(brim_bot, pogo_floor_bot);
hat_low    = min(cap_bot, tongue_bot);              // lowest point of the hat
base_flange_gap = base_t - pogo_depth;        // base: base top vs flange back

// ================= Helpers =================================================
module at_angle(r, a) { translate([r * sin(a), r * cos(a), 0]) rotate([0, 0, -a]) children(); }
module egg_2d(grow = 0) {
  offset(delta = grow) hull() { circle(d = white_d); translate([0, egg_shift]) circle(d = egg_small_d); }
}
module stadium_2d(l, w) { hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0]) circle(d = w); }
module underline_2d() {
  w = number_h * underline_w;
  t = number_h * underline_t;
  if (underline_style == "arc") {
    // smile-shaped stroke with round ends: lowest in the middle
    sag = number_h * underline_sag;
    steps = 24;
    for (i = [0 : steps - 1]) hull() for (j = [i, i + 1]) {
      x = -w / 2 + t / 2 + j * (w - t) / steps;
      u = x / ((w - t) / 2);
      translate([x, sag * u * u]) circle(d = t, $fn = 32);
    }
  } else {
    offset(r = t / 2 - 0.01) square([w - t, 0.02], center = true);
  }
}
module number_2d() {
  ul = underline == "on" || (underline == "auto" && (number_text == "6" || number_text == "9"));
  glyph_h = number_h * digit_h_ratio;
  gap = number_h * underline_gap;
  t = number_h * underline_t;
  sag = underline_style == "arc" ? number_h * underline_sag : 0;
  ul_h = t + sag;                                   // height of the underline shape
  shift = ul ? (gap + ul_h) / 2 : 0;                // keep number + underline centred
  translate([0, shift]) {
    text(number_text, size = number_h, font = number_font, halign = "center", valign = "center");
    // underline's top (its ends, for an arc) sits gap below the digit
    if (ul) translate([0, -glyph_h / 2 - gap - t / 2 - sag]) underline_2d();
  }
}

// rectangular pocket frame (inner = part + clearance), optional open end at -y
// open_back: no wall on the local +y side (radially outward when placed with
// at_angle); side walls run on out to the chassis wall and are trimmed there
// open_left: same on the local -x side (walls run on out to the chassis wall)
module pocket_rect(w, l, open_bottom = false, open_back = false, open_left = false, clear = pocket_clear) {
  iw = w + 2 * clear; il = l + 2 * clear;
  ext = 20;   // how far open sides' walls run on (trimmed at the chassis wall)
  linear_extrude(pocket_h) difference() {
    translate([-iw / 2 - pocket_wall - (open_left ? ext : 0), -il / 2 - pocket_wall])
      square([iw + 2 * pocket_wall + (open_left ? ext : 0), il + 2 * pocket_wall + (open_back ? ext : 0)]);
    translate([-iw / 2 - (open_left ? 2 * ext : 0), -il / 2])
      square([iw + (open_left ? 2 * ext : 0), il + (open_back ? 2 * ext : 0)]);
    if (open_bottom) translate([0, -il / 2]) square([iw, 2 * pocket_wall + 1], center = true);
  }
}
// inside of the clamp ring / columns (pockets are trimmed to this)
module chassis_inside_2d() { offset(delta = -brim_gap_d / 2 - chassis_clear - clamp_ring_w) cavity_2d(); }
inside_r = (ball_od - 2 * ball_wall) / 2 - brim_gap_d / 2 - chassis_clear - clamp_ring_w;
// radius that puts a w x l part's back corners on the inside wall
function wall_r(w, l, gap) = sqrt(pow(inside_r - gap, 2) - pow(w / 2 + pocket_clear, 2)) - l / 2 - pocket_clear;
module pocket_round(d) {
  linear_extrude(pocket_h) difference() { circle(d = d + 2 * pocket_clear + 2 * pocket_wall); circle(d = d + 2 * pocket_clear); }
}
// battery / LOLIN32 placement (computed from the clamp ring)
bat_ytop = max(abs(bat_y + bat_w / 2 + pocket_clear), abs(bat_y - bat_w / 2 - pocket_clear));
bat_cx   = -sqrt(pow(inside_r - bat_gap, 2) - pow(bat_ytop, 2)) + pocket_clear + bat_l / 2;
lolin_x  = bat_cx + bat_l / 2 + pocket_clear + pocket_wall + lolin_clear + lolin_w / 2;
lolin_xmax = max(abs(lolin_x - lolin_w / 2 - lolin_clear), abs(lolin_x + lolin_w / 2 + lolin_clear));
lolin_y  = sqrt(pow(inside_r - lolin_gap, 2) - pow(lolin_xmax, 2)) - lolin_clear - lolin_l / 2;
buzzer_r = inside_r - buzzer_gap - pocket_clear - buzzer_d / 2;
switch_pad_h = switch_slider_l - chassis_t - switch_tip_below;
// motor clip, plate top at z = 0, motor axis along y
module motor_clip(clear = motor_clear) {
  bd = motor_d + clear;
  difference() {
    translate([-bd / 2 - clip_wall, -clip_w / 2, 0]) cube([bd + 2 * clip_wall, clip_w, clip_h]);
    translate([0, clip_w, bd / 2]) rotate([90, 0, 0]) cylinder(d = bd, h = clip_w * 3, $fn = 64);
    translate([-motor_d * clip_open / 2, -clip_w, bd / 2 + 0.6]) cube([motor_d * clip_open, clip_w * 3, 10]);
  }
}
// switch mount (pads + end clips), plate top at z = 0; travel along x
// The -y side faces a wall (in the chassis: the boost pocket's front wall).
// Clips stop switch_wall_gap short of that wall so they can flex.
module switch_mount(own_wall = false, ct = switch_clip_t) {
  sw = switch_w + switch_extra_w + 2 * switch_clear; sd = switch_d + 2 * switch_clear;
  top = switch_pad_h + switch_h + switch_clear;
  cw = min(switch_clip_w, sd - switch_wall_gap);
  if (own_wall) translate([-sw / 2 - ct - 2, -sd / 2 - pocket_wall, -0.01])
    cube([sw + 2 * ct + 4, pocket_wall, pocket_h + 0.01]);
  for (sx = [-1, 1]) {
    // riser pad under each end, kept switch_pad_gap clear of the clip so the
    // clip flexes from the plate, not from the pad top
    translate([sx > 0 ? sw / 2 - switch_pad_w : -sw / 2 + switch_pad_gap, -switch_d / 2, -0.01])
      cube([switch_pad_w - switch_pad_gap, switch_d, switch_pad_h + 0.01]);
    // clip: arm outside the end, hook over the switch top (flat lip + sloped lead-in)
    translate([sx * (sw / 2 + ct / 2), sd / 2 - cw / 2, 0]) mirror([sx < 0 ? 1 : 0, 0, 0]) {
      translate([-ct / 2, -cw / 2, -0.01]) cube([ct, cw, top + 0.01]);
      translate([-ct / 2, cw / 2, top]) rotate([90, 0, 0])
        linear_extrude(cw) polygon([[0, 0], [-switch_hook, 0], [-switch_hook, switch_hook_t],
                                    [0, switch_hook_t + switch_hook * 2], [ct, switch_hook_t + switch_hook * 2], [ct, 0]]);
    }
  }
}
// switch frame: against the boost pocket's front (centre-side) wall, rotated so
// the switch's -y side faces that wall
module switch_place() {
  at_angle(wall_r(boost_w, boost_l, boost_gap), boost_a)
    translate([switch_dx, -(boost_l / 2 + pocket_clear) - pocket_wall - (switch_d / 2 + switch_clear)])
      rotate([0, 0, 180]) children();
}
module switch_slot(h) { translate([-switch_slot_l / 2, -switch_slot_w / 2, 0]) cube([switch_slot_l, switch_slot_w, h]); }
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
      translate([0, 0, brim_bot]) linear_extrude(brim_t) brim_2d();
      translate([0, 0, brim_bot]) linear_extrude(hat_h - brim_bot - crown_chamfer) egg_2d(-crown_clear_d / 2);
      if (crown_chamfer > 0) hull() {
        translate([0, 0, hat_h - crown_chamfer]) linear_extrude(0.01) egg_2d(-crown_clear_d / 2);
        translate([0, 0, hat_h - 0.01]) linear_extrude(0.01) egg_2d(-crown_clear_d / 2 - crown_chamfer);
      }
      // only where the brim is too thin: tongue under the pogo flange, caps under the magnets
      if (tongue_bot < brim_bot)
        translate([0, 0, tongue_bot]) linear_extrude(brim_bot - tongue_bot + 0.01) tongue_2d();
      if (cap_bot < brim_bot)
        for (a = mag_angles) at_angle(mag_r, a)
          translate([0, 0, cap_bot]) cylinder(d = mag_pocket_d + 2 * cap_wall, h = brim_bot - cap_bot + 0.01);
      if (number_mode == "raised") translate([0, 0, hat_h]) linear_extrude(raised_h) number_2d();
    }
    translate([0, 0, hat_low - 1]) linear_extrude(hat_h - light_t - hat_low + 1) egg_2d(-crown_clear_d / 2 - crown_wall);
    if (number_mode == "inlay")
      translate([0, 0, hat_h - number_depth - 0.01]) linear_extrude(number_depth + 0.02) number_2d();
    // pogo: pocket from the brim top down to the flange's back; back oval + wires right through
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, ball_flange_gap]) linear_extrude(brim_top - ball_flange_gap + 1) stadium_2d(flange_pocket_l, flange_pocket_w);
      translate([0, 0, hat_low - 1]) linear_extrude(brim_top - hat_low + 2) stadium_2d(oval_hole_l, oval_hole_w);
    }
    // magnets: pocket from the brim top down to just past the magnet
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, mag_pocket_bot]) cylinder(d = mag_pocket_d, h = brim_top - mag_pocket_bot + 1);
  }
}
module number_upright() { translate([0, 0, hat_h - number_depth]) linear_extrude(number_depth) number_2d(); }

// ================= Pogo cut (outer face at z = 0, pointing +Z) =============
module pogo_cut() {
  translate([0, 0, -face_body - 0.01]) linear_extrude(face_body + 1) stadium_2d(oval_hole_l, oval_hole_w);
  translate([0, 0, -face_body - flange_t - 5]) linear_extrude(flange_t + 5.01) stadium_2d(flange_pocket_l, flange_pocket_w);
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
    translate([0, 0, col_start - 0.01]) linear_extrude(face_back + brim_sink - col_start + 0.01) cavity_2d();  // + brim pocket
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
  ring_top = face_back + brim_bot - ring_relief;   // meets the brim's bottom
  difference() {
    union() {
      translate([0, 0, base_t]) cylinder(d = plate_d, h = chassis_t);
      // clamp ring at the wall, pressing the brim's outer edge (notched at the tongue)
      translate([0, 0, col_start - 0.01]) linear_extrude(ring_top - col_start + 0.01) difference() {
        offset(delta = -brim_gap_d / 2 - chassis_clear) cavity_2d();
        offset(delta = -brim_gap_d / 2 - chassis_clear - clamp_ring_w) cavity_2d();
        offset(delta = 0.3) tongue_2d();
        // clamp ring cut away behind the wall-side parts
        if (ring_open_at_parts) {
          at_angle(wall_r(boost_w, boost_l, boost_gap), boost_a)
            translate([-boost_w / 2 - pocket_clear, 0]) square([boost_w + 2 * pocket_clear, 30]);
          at_angle(wall_r(touch_w, touch_l, touch_gap), touch_a)
            translate([-touch_w / 2 - pocket_clear, 0]) square([touch_w + 2 * pocket_clear, 30]);
        }
        // notches for the magnet caps (only when the brim needs them)
        if (cap_bot < brim_bot)
          for (a = mag_angles) at_angle(mag_r, a) circle(d = mag_pocket_d + 2 * cap_wall + 0.6);
      }
      for (p = ring_posts) translate([p[0] * ring_hole_cx / 2, p[1] * ring_hole_cy / 2, base_t])
        cylinder(d = ring_post_d, h = ring_bottom - base_t, $fn = 32);
      // component pockets (layout)
      translate([0, 0, col_start - 0.01]) {
        intersection() {
          union() {
            translate([lolin_x, lolin_y + lolin_tray_cut / 2]) pocket_rect(lolin_w, lolin_l - lolin_tray_cut, open_bottom = true, open_back = true, clear = lolin_clear);
          }
          translate([0, 0, -1]) linear_extrude(pocket_h + 2) chassis_inside_2d();
        }
        intersection() {
          union() {
            translate([bat_cx, bat_y]) rotate([0, 0, 90]) pocket_rect(bat_w, bat_l, open_back = true);
            at_angle(buzzer_r, buzzer_a) pocket_round(buzzer_d);
            at_angle(wall_r(boost_w, boost_l, boost_gap), boost_a) pocket_rect(boost_w, boost_l, open_back = true);
            at_angle(wall_r(touch_w, touch_l, touch_gap), touch_a) pocket_rect(touch_w, touch_l, open_back = true);
          }
          translate([0, 0, -1]) linear_extrude(pocket_h + 2) chassis_inside_2d();
        }
      }
      // LOLIN32 stop tab, against the board's pogo-side end
      translate([lolin_x - lolin_w / 2 - lolin_clear + lolin_tab_off,
                 lolin_y - lolin_l / 2 - lolin_clear - lolin_tab_t, col_start - 0.01])
        cube([lolin_tab_w, lolin_tab_t, lolin_tab_h + 0.01]);
      // motor U-clips (open at the top; the motor snaps in)
      translate([motor_x, motor_y, col_start]) rotate([0, 0, motor_angle]) motor_clip();
      // power switch
      switch_place() translate([0, 0, col_start]) switch_mount();
      // flange ends inside the base: presser reaches down to it
      if (base_flange_gap > base_pogo_extra)
        at_angle(pogo_r, pogo_angle) translate([0, 0, pogo_depth + base_pogo_extra]) linear_extrude(base_flange_gap - base_pogo_extra + 0.01)
          stadium_2d(flange_pocket_l - 0.3, flange_pocket_w - 0.2);
    }
    // base pogo: flange pocket + back oval + wires, from the plate underside
    at_angle(pogo_r, pogo_angle) {
      if (base_flange_gap < base_pogo_extra)   // flange reaches above the base: pocket up to its back (+ extra)
        translate([0, 0, base_t - 0.01]) linear_extrude(-base_flange_gap + base_pogo_extra + 0.01) stadium_2d(flange_pocket_l, flange_pocket_w);
      translate([0, 0, base_t - 1]) linear_extrude(chassis_t + 2) stadium_2d(oval_hole_l, oval_hole_w);
    }
    // LOLIN32 solder-joint channels along both long edges
    for (sx = [-1, 1]) translate([lolin_x + sx * (lolin_w / 2 - lolin_pin_inset), lolin_y, col_start - lolin_chan_d])
      translate([-lolin_chan_w / 2, -lolin_l / 2 - 0.5, 0]) cube([lolin_chan_w, lolin_l + 1, lolin_chan_d + 0.01]);
    // buzzer sound hole
    at_angle(buzzer_r, buzzer_a) translate([0, 0, base_t - 1]) cylinder(d = sound_hole_d, h = chassis_t + 2, $fn = 24);
    switch_place() translate([0, 0, base_t - 1]) switch_slot(chassis_t + 2);
    // base magnets stick up 0.75 mm into the plate
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, base_t - 0.01]) cylinder(d = mag_d + 0.4, h = mag_h - base_t + 0.1);
    for (a = boss_angles) at_angle(boss_r, a) translate([0, 0, base_t - 1]) cylinder(d = screw_clear, h = chassis_t + 2, $fn = 24);
    for (p = ring_posts) translate([p[0] * ring_hole_cx / 2, p[1] * ring_hole_cy / 2, col_start])
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
    if (recess_chamfer > 0) hull() {
      translate([0, 0, -0.01]) linear_extrude(0.01) egg_2d(recess_clear_d / 2 + recess_chamfer);
      translate([0, 0, recess_chamfer]) linear_extrude(0.01) egg_2d(recess_clear_d / 2);
    }
    at_angle(pogo_r, pogo_angle) mirror([0, 0, 1]) pogo_cut();                      // spring pins
    for (a = mag_angles) at_angle(mag_r, a) translate([0, 0, -1]) cylinder(d = mag_hole_base, h = base_t + 2);
    if (switch_base_slot) switch_place() translate([0, 0, -1]) switch_slot(base_t + 2);
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

// test plate: switch mount + motor clips at several clearances (labels in hundredths)
module clip_test() {
  ns = len(test_switch_clip_ts); sp = switch_w + 2 * max(test_switch_clip_ts) + 10;
  n = len(test_motor_clears); pitch = motor_d + 2 * clip_wall + 7;
  L = ns * sp + n * pitch + 4; W = max(clip_w, switch_d + 4) + 14;
  difference() {
    translate([0, -W / 2, 0]) cube([L, W, chassis_t]);
    for (k = [0 : ns - 1]) {
      translate([sp * k + sp / 2, 0, -1]) switch_slot(chassis_t + 2);
      translate([sp * k + sp / 2, -W / 2 + 1.5, chassis_t - 0.6]) linear_extrude(1)
        text(str(test_switch_clip_ts[k]), size = 3.5, font = "Liberation Sans:style=Bold", halign = "center");
    }
    for (i = [0 : n - 1]) translate([ns * sp + i * pitch + pitch / 2, -W / 2 + 1.5, chassis_t - 0.6])
      linear_extrude(1) text(str("+", round(test_motor_clears[i] * 100)), size = 3.5,
                             font = "Liberation Sans:style=Bold", halign = "center");
  }
  for (k = [0 : ns - 1]) translate([sp * k + sp / 2, 0, chassis_t]) switch_mount(own_wall = switch_wall, ct = test_switch_clip_ts[k]);
  for (i = [0 : n - 1]) translate([ns * sp + i * pitch + pitch / 2, 2, chassis_t]) motor_clip(test_motor_clears[i]);
}

if (part == "hat") hat_print();
else if (part == "number") number_print();
else if (part == "ball") ball_print();
else if (part == "chassis") chassis();
else if (part == "base") base_print();
else if (part == "clip_test") clip_test();
else preview();

echo(str("Ball height ", ball_h, " mm. Free height under the LED ring (internal_h) ", internal_h,
         " mm; LED posts ", ring_bottom - col_start, " mm (minimum ", post_min, "); LED tops to the underside of the lit face ",
         led_depth - light_t, " mm; inside height plate top to brim bottom ", face_back + brim_bot - col_start, " mm"));
echo(str("Brim ", brim_t, " mm (", brim_sink, " in the face, ", -brim_bot, " below). Magnet pocket ",
         brim_top - mag_pocket_bot, " deep", cap_bot < brim_bot ? str(", cap ", brim_bot - cap_bot, " mm") : ", no cap",
         "; pogo pocket ", brim_top - ball_flange_gap, " deep", tongue_bot < brim_bot ? str(", tongue ", brim_bot - tongue_bot, " mm") : ", no tongue"));
assert(mag_r + mag_pocket_d / 2 + cap_wall < ball_od / 2 - ball_wall - 0.2,
       "magnet caps too wide: they would hit the ball wall (reduce cap_wall or move the magnets in)");
assert(brim_sink < ball_face_t - 0.5, "brim_sink leaves less than 0.5 mm of face in front of the brim");
crown_inner_min = white_d - crown_clear_d - 2 * crown_wall;   // narrowest inside of the crown
assert(ring_bottom + ring_h <= face_back + brim_bot || crown_inner_min >= ring_od + 0.6,
       "LED ring is inside the crown hollow but the crown is too narrow for it (reduce crown_wall or lower the ring)");
assert(base_t >= protrude + 0.3, "base_t must be at least protrude + 0.3 (stacking recess depth)");
assert(screw_head_h < base_t - 0.3, "counterbore too deep for the base: less than 0.3 mm left under the screw head");
