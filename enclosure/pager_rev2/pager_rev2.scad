// Pool-ball pager, Rev 2 (OpenSCAD)
//
// Two printed parts plus two small clamps:
//   - ball: shell + flat top, printed TOP DOWN in three colours on the AMS
//     (export ball / white / number as separate STLs, load them together as
//     one multi-part object and give each part its filament).
//     The white circle is white_t thick (0.25 first layer + one 0.2 layer)
//     over a light pocket; the black number goes number_t deep so it blocks
//     the light. The top is top_t thick elsewhere and built up in the inside
//     corner against light bleed at the rounded edge.
//   - base: flat plate (base_t) that carries every component, printed
//     BOTTOM DOWN. Same mounts as Rev 1's chassis.
//   - pogo_clamp (x2): holds each pogo connector's flange; a short piece of
//     1.75 mm filament through the fork bosses holds each end of the clamp.
// Magnets go in from the inside (mag_skin of plastic in front of them), so
// nothing sticks out of the top or the bottom.
//
// Coordinates: z = 0 at the bottom of the pager. Looking down on the top,
// +Y = 12 o'clock; angles clockwise from 12.
// Rev 1 (pager_shell_test) is unchanged and kept for reference.

use <fonts/LiberationSans-Bold.ttf>
use <fonts/DejaVuSerif-Bold.ttf>

/* [Part to show / export] */
part = "all"; // [all, ball, white, number, base, pogo_clamp, pogo_test]

/* [Ball] */
ball_od      = 104;
ball_h       = 20.8;    // overall height (kept from Rev 1)
ball_wall    = 2.4;
edge_r       = 5.0;     // rounded top edge
top_t        = 1.65;    // [1:0.05:4] top thickness
// inside corner where the top meets the wall: 45 deg build-up this tall/wide
// (stops LED light leaking through the rounded edge)
corner_build = 3.0;     // [0:0.2:8]
column_fillet = 3;
boss_d       = 7;
boss_angles  = [45, 135, 225, 315];

/* [Top: white circle, light and number] */
white_d      = 72;      // white circle (LED ring is 68.2)
white_t      = 0.45;    // [0.2:0.05:1.65] white thickness = lit face
// light pocket under the white: white_d minus this rim on each side
pocket_rim   = 1.0;     // [0:0.1:5]
number_t     = 1.2;     // [0.4:0.05:1.65] black number depth from the top

/* [Number] */
number_text  = "2";
number_font  = "Liberation Sans:style=Bold";
number_scale = 0.45;    // [0.2:0.01:1] size as a fraction of white_d
underline    = "auto";  // [auto, on, off]
underline_style = "arc"; // [arc, bar]
underline_w     = 0.6;  // [0.2:0.01:1.5]
underline_t     = 0.1;  // [0.03:0.005:0.3]
underline_gap   = 0.025; // [0:0.005:0.3]
underline_sag   = 0.06; // [0:0.005:0.3]
digit_h_ratio   = 0.98; // [0.6:0.01:1.4]

/* [Base and screws] */
base_t       = 1.65;    // [1:0.05:4]
base_clear_d = 0.1;     // [0:0.01:1] base inside the ball wall (diameter)
// M2 x 8 self-tapping from the bottom into the columns; the base is built up
// under each column so the head can be recessed
screw_pilot  = 1.7;
screw_clear  = 2.3;
screw_head_d = 4.2;
screw_head_h = 1.5;
screw_boss_h = 2.0;     // [0:0.1:5] build-up on the base under each column
// gap between the parts placed against the wall and the ball wall
wall_gap     = 0.2;     // [0:0.05:2]

/* [LED ring] */
// LED tops to the underside of the white (spacers can add to this)
led_gap      = 6.5;     // [3:0.1:12]
ring_h       = 2.5;
ring_od      = 68.2;
ring_hole_cx = 35.24;
ring_hole_cy = 52.8;
ring_post_d  = 5;
ring_pilot   = 1.7;     // M2 x 6 self-tapping
ring_posts   = [[-1, 1], [1, -1]];   // 11 and 5 o'clock

/* [Magnets] */
mag_d        = 6.0;
mag_h        = 2.75;
mag_skin     = 0.45;    // plastic in front of each magnet
mag_hole_ball = 6.05;   // press fit
mag_hole_base = 6.0;
mag_wall     = 1.2;
// magnet bosses flare out to the root like a hill (45 deg) so they don't shear off
mag_flare    = true;
mag_r        = 43;
// Two magnets; with the pogo connector (180 deg) they form the triangle that
// aligns the stack. The battery may sit over the 300 deg one.
mag_angles   = [60, 300];

/* [Pogo connector] */
oval_hole_l   = 13.15;
oval_hole_w   = 3.9;
face_body     = 1.9;    // oval body in front of the flange (flush with the outside)
flange_t      = 0.9;
flange_pocket_l = 19.2;
flange_pocket_w = 3.9;
base_pogo_extra = 0.2;  // spring-pin connector flange room
pogo_r        = 44;
pogo_angle    = 180;
pogo_wall     = 1.2;    // wall round the flange
// flange pocket walls stop this short so the clamp presses the flange, not the walls
pogo_press    = 0.2;    // [0:0.05:0.6]
clamp_t       = 1.6;    // [0.8:0.1:4]
clamp_w       = 7.0;    // [4:0.1:12] (radial); 1.25 mm rails beside the wire hole
clamp_end     = 5.0;    // [3:0.5:10] clamp length past each flange end
clamp_hole_add = 0.6;   // oval hole in the clamp: oval + this (back body + wires)
// One clamp end hooks under a latch bar (insert, then lever the clamp down).
// The other end is forked round a single post; a 1.75 mm filament pin through
// the post, across the fork's tines, holds it. Latch on the 7 o'clock side,
// post on the 5 o'clock side (pin pushed in from the centre).
latch_leg_t   = 1.6;    // [1:0.1:4]
latch_bar_t   = 1.6;    // [0.8:0.1:4]
latch_clear   = 0.1;    // [0:0.05:0.5] room for the clamp end under the latch bar
fork_clear    = 0.3;    // clamp end to latch leg / fork to post
post_t        = 3.5;    // [3.5:0.1:6] pin post, along the connector
post_w        = 3.5;    // [3.5:0.1:6] pin post, across (= pin hole length)
tine_w        = 2.0;    // [1:0.1:4] each fork tine beside the post
pin_hole_d    = 1.8;    // 1.75 filament
pin_floor     = 1.2;    // plastic beyond the pin hole
// smoothing (strength): rounded clamp corners, fillets on its inside corners,
// rounded post / leg edges and a 45 deg flare where they join the part
clamp_round   = 0.8;    // [0:0.1:2] outside corners of the clamp
clamp_fillet  = 1.0;    // [0:0.1:2] inside corners of the clamp (fork root, step)
post_round    = 1.2;    // [0:0.1:1.7] vertical edges of the pin post
leg_round     = 0.6;    // [0:0.1:0.8] vertical edges of the latch legs
root_flare    = 0.9;    // [0:0.1:1.1] 45 deg flare at the post / leg roots

/* [Component mounts] */
pocket_wall    = 1.2;
pocket_h       = 5.0;
pocket_clear   = 0.3;
bat_w = 35; bat_l = 30; bat_gap = 0; bat_y = 4;
bat_wall_keep = 9;
lolin_w        = 25.7;
lolin_l        = 49.6;
lolin_clear    = 0.05;
lolin_w_adj    = -0.12;
lolin_len_adj  = 0.9;
lolin_gap      = 0;
lolin_chan_w   = 3.0;
lolin_chan_d   = 1.0;
lolin_pin_inset = 1.27;
lolin_tray_cut = 4;
lolin_tab_off  = 9.5;
lolin_tab_w    = 4;
lolin_tab_h    = 4;
lolin_tab_t    = 2;
boost_w = 10.5; boost_l = 11; boost_gap = 0; boost_a = 210.5;
buzzer_d = 9.2; buzzer_gap = 0;
buzzer_a = -1;          // -1 = auto: beside the LOLIN32's 12 o'clock end, away from the battery
sound_hole_d   = 2.0;
touch_w = 24; touch_l = 24.3; touch_gap = 0; touch_a = 111;
motor_d        = 7.0;
motor_l        = 26;
motor_x        = 29;   // clear of the 60 deg magnet
motor_y        = 13;
motor_angle    = 45;
clip_w         = 8;
clip_wall      = 1.6;
clip_h         = 5.5;
motor_clear    = 0.1;
clip_open      = 0.84;

/* [Power switch] */
switch_w       = 8.75;
switch_d       = 5.0;
switch_h       = 4.5;
switch_clear   = 0;
switch_extra_w = 0.2;
switch_slider_l = 4.35;
// slider tip this far up from the bottom of the base (0 = flush)
switch_tip_recess = 0.5; // [0:0.1:3]
switch_slot_l  = 5.75;
switch_slot_w  = 2.2;
switch_pad_w   = 1.5;
switch_clip_t  = 1.6;
switch_cove_r  = 1.0;
switch_pad_gap = 0.4;
switch_clip_w  = 5;
switch_hook    = 0.6;
switch_hook_t  = 0.6;
switch_wall_gap = 0.6;
switch_dx      = 0;

/* [Hidden] */
$fn = 128;
number_h    = number_scale * white_d;
top_under   = ball_h - top_t;               // underside of the top
white_under = ball_h - white_t;             // underside of the white (pocket ceiling)
pocket_d    = white_d - 2 * pocket_rim;
col_start   = base_t + screw_boss_h;        // columns start here
ring_bottom = white_under - led_gap - ring_h;
inner_r     = (ball_od - 2 * ball_wall) / 2;
inside_r    = inner_r - wall_gap;           // parts placed against the wall touch here
// pogo z levels
top_flange_back  = ball_h - face_body - flange_t;              // clamp's top face (ball)
base_flange_back = face_body + flange_t + base_pogo_extra;     // clamp's bottom face (base)
switch_pad_h = switch_slider_l - base_t + switch_tip_recess;

// ================= Helpers =================================================
module at_angle(r, a) { translate([r * sin(a), r * cos(a), 0]) rotate([0, 0, -a]) children(); }
module stadium_2d(l, w) { hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0]) circle(d = w); }
module cove_2d(r) { difference() { square([r, r]); translate([r, r]) circle(r = r, $fn = 32); } }
// horizontal hole along local y with a 45 deg point towards +z (prints without support)
module teardrop_y(d, len) {
  rotate([90, 0, 0]) linear_extrude(len, center = true)
    hull() { circle(d = d, $fn = 24); translate([0, d / 2 / cos(45) - 0.01]) square(0.02, center = true); }
}
module underline_2d() {
  w = number_h * underline_w;
  t = number_h * underline_t;
  if (underline_style == "arc") {
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
  ul_h = t + sag;
  shift = ul ? (gap + ul_h) / 2 : 0;
  intersection() {
    translate([0, shift]) {
      text(number_text, size = number_h, font = number_font, halign = "center", valign = "center");
      if (ul) translate([0, -glyph_h / 2 - gap - t / 2 - sag]) underline_2d();
    }
    circle(d = white_d - 0.8);
  }
}
// magnet boss: h tall, root at z = 0 (dir = +1, rises) or at z = h (dir = -1, hangs)
module mag_boss(hole, h, dir) {
  d_top = hole + 2 * mag_wall; d_root = d_top + (mag_flare ? 2 * h : 0);
  if (dir > 0) cylinder(d1 = d_root, d2 = d_top, h = h);
  else cylinder(d1 = d_top, d2 = d_root, h = h);
}
module bosses_2d() { for (a = boss_angles) at_angle(boss_r, a) circle(d = boss_d); }
boss_r = ball_od / 2 - ball_wall - boss_d / 2 + 0.5;
module cavity_2d(grow = 0) {
  offset(delta = grow) offset(r = column_fillet) offset(delta = -column_fillet)
    difference() { circle(d = ball_od - 2 * ball_wall); bosses_2d(); }
}
// where base components may go: inside the ball wall and the columns
module base_inside_2d() { cavity_2d(-wall_gap); }

// ================= Ball (upright; colour body / white / number) ============
module ball_outer() {
  R = ball_od / 2;
  rotate_extrude() hull() {
    square([R, ball_h - edge_r]);
    translate([R - edge_r, ball_h - edge_r]) circle(r = edge_r, $fn = 48);
    square([R - edge_r + edge_r * (sqrt(2) - 1), ball_h]);   // 45 deg start: prints top down
  }
}
module ball_cavity() {
  // base + screw build-ups: plain circle up to col_start
  translate([0, 0, -1]) cylinder(d = ball_od - 2 * ball_wall, h = col_start + 1);
  // main cavity with columns, up to where the corner build-up starts
  h0 = top_under - corner_build;
  translate([0, 0, col_start - 0.01]) linear_extrude(h0 - col_start + 0.02) cavity_2d();
  // 45 deg corner build-up in 0.2 mm steps
  steps = max(1, round(corner_build / 0.2));
  for (k = [0 : steps - 1]) translate([0, 0, h0 + k * corner_build / steps])
    linear_extrude(corner_build / steps + 0.01) cavity_2d(-(k + 1) * corner_build / steps);
}
module white_vol()  { translate([0, 0, white_under]) linear_extrude(white_t + 0.01) circle(d = white_d); }
module number_vol() { translate([0, 0, ball_h - number_t]) linear_extrude(number_t + 0.01) number_2d(); }
module ball_shell() {
  difference() {
    union() {
      difference() { ball_outer(); ball_cavity(); }
      // magnet bosses under the top
      for (a = mag_angles) at_angle(mag_r, a)
        translate([0, 0, ball_h - mag_skin - mag_h]) mag_boss(mag_hole_ball, mag_h + mag_skin - top_t + 0.01, -1);
      // pogo: flange walls + ledge, and the clamp forks
      at_angle(pogo_r, pogo_angle) {
        translate([0, 0, top_flange_back + pogo_press])
          linear_extrude(top_under - top_flange_back - pogo_press + 0.01)
            stadium_2d(flange_pocket_l + 2 * pogo_wall, flange_pocket_w + 2 * pogo_wall);
        pogo_forks(top_flange_back - clamp_t, top_under, -1);
      }
    }
    // light pocket under the white
    translate([0, 0, top_under - 1]) cylinder(d = pocket_d, h = white_under - top_under + 1);
    // magnet pockets (from the inside)
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, ball_h - mag_skin - mag_h - 1]) cylinder(d = mag_hole_ball, h = mag_h + 1);
    // pogo: oval through the top, flange pocket behind it
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, ball_h - face_body - 0.01]) linear_extrude(face_body + 1) stadium_2d(oval_hole_l, oval_hole_w);
      translate([0, 0, top_flange_back - 3]) linear_extrude(ball_h - face_body - top_flange_back + 3)
        stadium_2d(flange_pocket_l, flange_pocket_w);
    }
    // column screw pilots
    for (a = boss_angles) at_angle(boss_r, a)
      translate([0, 0, col_start - 1]) cylinder(d = screw_pilot, h = top_under - col_start, $fn = 24);
  }
}
module ball_body() { difference() { ball_shell(); white_vol(); number_vol(); } }
module white_body() { difference() { white_vol(); number_vol(); } }

// ================= Pogo clamp holders ======================================
// Local +x end (world 7 o'clock side): latch = two thin legs and a bar; hook
// the clamp end under the bar, then lever the clamp down. Local -x end: one
// post with a pin hole; the clamp's forked end goes round the post and the
// filament pin through the post lies across the tines.
// clamp_face = z of the clamp face away from the flange; z_root = where the
// holders join the part; dir = -1 for the ball (they hang down), +1 for the base.
function fork_x() = flange_pocket_l / 2 + 1 + clamp_end / 2;
clamp_fork_w = post_w + 2 * fork_clear + 2 * tine_w;   // clamp width at the forked end
// rounded rectangle centred on [cx, cy]
module rrect_2d(w, l, r) { offset(r = r) square([max(0.01, w - 2 * r), max(0.01, l - 2 * r)], center = true); }
// extrude a 2D profile from z_root to z_tip, flaring 45 deg (root_flare) at the root
module flared(z_root, z_tip) {
  dir = z_tip > z_root ? 1 : -1;
  h = abs(z_tip - z_root); f = min(root_flare, h);
  steps = max(1, round(f / 0.15));
  translate([0, 0, min(z_root, z_tip) - (dir < 0 ? 0 : 0.01)]) linear_extrude(h + 0.01) children();
  for (k = [0 : steps - 1]) {
    g = f * (1 - (k + 0.5) / steps);             // grow at this slice
    z = z_root + dir * k * f / steps;
    translate([0, 0, dir > 0 ? z - 0.01 : z - f / steps]) linear_extrude(f / steps + 0.01) offset(delta = g) children();
  }
}
module pogo_forks(clamp_face, z_root, dir) {
  pin_z  = clamp_face + dir * (pin_hole_d / 2);          // pin touches the clamp face
  tip_pin   = pin_z + dir * (pin_hole_d / 2 + pin_floor);
  tip_latch = clamp_face + dir * (latch_clear + latch_bar_t);
  // latch (+x)
  translate([fork_x(), 0, 0]) {
    for (sy = [-1, 1]) flared(z_root, tip_latch)
      translate([0, sy * (clamp_w / 2 + fork_clear + latch_leg_t / 2)]) rrect_2d(clamp_end, latch_leg_t, leg_round);
    translate([-clamp_end / 2, -(clamp_w / 2 + fork_clear), min(clamp_face + dir * latch_clear, tip_latch)])
      cube([clamp_end, clamp_w + 2 * fork_clear, latch_bar_t]);   // a short bridge in the print
  }
  // pin post (-x)
  translate([-fork_x(), 0, 0]) difference() {
    flared(z_root, tip_pin) rrect_2d(post_t, post_w, post_round);
    // teardrop points up in the print (ball prints top down: up = -z)
    translate([0, 0, pin_z]) mirror([0, 0, dir < 0 ? 1 : 0]) teardrop_y(pin_hole_d, post_w + 2 * root_flare + 2);
  }
}
module pogo_clamp_2d() {
  L = flange_pocket_l + 2 + 2 * clamp_end;
  slot_r = post_w / 2 + fork_clear;
  slot_cx = -fork_x() + fork_clear;                    // round end of the slot, just past the post centre
  difference() {
  // fillet inside corners, then round outside corners (outline + slot only)
  offset(r = -clamp_fillet) offset(delta = clamp_fillet)
  offset(r = clamp_round) offset(delta = -clamp_round)
  difference() {
    union() {
      square([L, clamp_w], center = true);
      // wider forked end, tapering 45 deg into the body
      hull() {
        translate([-L / 2, -clamp_fork_w / 2]) square([clamp_end, clamp_fork_w]);
        translate([-L / 2, -clamp_w / 2]) square([clamp_end + (clamp_fork_w - clamp_w) / 2, clamp_w]);
      }
    }
    // slot with a round end round the post
    translate([-L / 2 - 1, -slot_r]) square([slot_cx + L / 2 + 1, 2 * slot_r]);
    translate([slot_cx, 0]) circle(r = slot_r, $fn = 48);
  }
  stadium_2d(oval_hole_l + clamp_hole_add, oval_hole_w + clamp_hole_add);
  }
}
module pogo_clamp() { linear_extrude(clamp_t) pogo_clamp_2d(); }

// ================= Component mounts (base top at z = base_t) ===============
function wall_r(w, l, gap) = sqrt(pow(inside_r - gap, 2) - pow(w / 2 + pocket_clear, 2)) - l / 2 - pocket_clear;
module pocket_rect(w, l, open_bottom = false, open_back = false, clear = pocket_clear) {
  iw = w + 2 * clear; il = l + 2 * clear;
  ext = 20;
  linear_extrude(pocket_h) difference() {
    translate([-iw / 2 - pocket_wall, -il / 2 - pocket_wall])
      square([iw + 2 * pocket_wall, il + 2 * pocket_wall + (open_back ? ext : 0)]);
    translate([-iw / 2, -il / 2]) square([iw, il + (open_back ? 2 * ext : 0)]);
    if (open_bottom) translate([0, -il / 2]) square([iw, 2 * pocket_wall + 1], center = true);
  }
}
module pocket_round(d) {
  linear_extrude(pocket_h) difference() { circle(d = d + 2 * pocket_clear + 2 * pocket_wall); circle(d = d + 2 * pocket_clear); }
}
bat_ytop = max(abs(bat_y + bat_w / 2 + pocket_clear), abs(bat_y - bat_w / 2 - pocket_clear));
bat_cx   = -sqrt(pow(inside_r - bat_gap, 2) - pow(bat_ytop, 2)) + pocket_clear + bat_l / 2;
lolin_x  = bat_cx + bat_l / 2 + pocket_clear + pocket_wall + lolin_clear + (lolin_w + lolin_w_adj) / 2;
lolin_xmax = max(abs(lolin_x - lolin_w / 2 - lolin_clear), abs(lolin_x + lolin_w / 2 + lolin_clear));
lolin_y  = sqrt(pow(inside_r - lolin_gap, 2) - pow(lolin_xmax, 2)) - lolin_clear - lolin_l / 2;
buzzer_r = inside_r - buzzer_gap - pocket_clear - buzzer_d / 2;
lolin_right_wall = lolin_x + (lolin_w + lolin_w_adj) / 2 + lolin_clear + pocket_wall;
buzzer_ang = buzzer_a >= 0 ? buzzer_a : asin((lolin_right_wall + pocket_clear + buzzer_d / 2) / buzzer_r);
module motor_clip(clear = motor_clear) {
  bd = motor_d + clear;
  difference() {
    translate([-bd / 2 - clip_wall, -clip_w / 2, 0]) cube([bd + 2 * clip_wall, clip_w, clip_h]);
    // bore 0.1 above the plate so it doesn't touch it along a line (non-manifold)
    translate([0, clip_w / 2 + 0.01, bd / 2 + 0.1]) rotate([90, 0, 0]) cylinder(d = bd, h = clip_w + 0.02, $fn = 64);
    translate([-motor_d * clip_open / 2, -clip_w, bd / 2 + 0.7]) cube([motor_d * clip_open, clip_w * 3, 10]);
  }
}
module switch_mount(ct = switch_clip_t) {
  sw = switch_w + switch_extra_w + 2 * switch_clear; sd = switch_d + 2 * switch_clear;
  top = switch_pad_h + switch_h + switch_clear;
  cw = min(switch_clip_w, sd - switch_wall_gap);
  for (sx = [-1, 1]) {
    translate([sx > 0 ? sw / 2 - switch_pad_w : -sw / 2 + switch_pad_gap, -switch_d / 2, -0.01])
      cube([switch_pad_w - switch_pad_gap, switch_d, switch_pad_h + 0.01]);
    translate([sx * (sw / 2 + ct / 2), sd / 2 - cw / 2, 0]) mirror([sx < 0 ? 1 : 0, 0, 0]) {
      translate([-ct / 2, -cw / 2, -0.01]) cube([ct, cw, top + 0.01]);
      ri = min(switch_cove_r, switch_pad_gap - 0.1);
      translate([0, cw / 2, 0]) rotate([90, 0, 0]) linear_extrude(cw) {
        translate([ct / 2, 0]) cove_2d(switch_cove_r);
        if (ri > 0) translate([-ct / 2, 0]) mirror([1, 0]) cove_2d(ri);
      }
      translate([-ct / 2, cw / 2, top]) rotate([90, 0, 0])
        linear_extrude(cw) polygon([[0, 0], [-switch_hook, 0], [-switch_hook, switch_hook_t],
                                    [0, switch_hook_t + switch_hook * 2], [ct, switch_hook_t + switch_hook * 2], [ct, 0]]);
    }
  }
}
module switch_place() {
  at_angle(wall_r(boost_w, boost_l, boost_gap), boost_a)
    translate([switch_dx, -(boost_l / 2 + pocket_clear) - pocket_wall - (switch_d / 2 + switch_clear)])
      rotate([0, 0, 180]) children();
}
module switch_slot(h) { translate([-switch_slot_l / 2, -switch_slot_w / 2, 0]) cube([switch_slot_l, switch_slot_w, h]); }

// ================= Base (upright = print orientation) ======================
module base_part(parts = true) {
  difference() {
    intersection() {
    // everything stays inside the ball wall
    cylinder(d = ball_od - 2 * ball_wall - base_clear_d, h = ball_h);
    union() {
      cylinder(d = ball_od - 2 * ball_wall - base_clear_d, h = base_t);
      // build-up under each column for the screw head
      for (a = boss_angles) at_angle(boss_r, a) cylinder(d = boss_d, h = col_start);
      // LED ring posts
      for (p = ring_posts) translate([p[0] * ring_hole_cx / 2, p[1] * ring_hole_cy / 2, base_t - 0.01])
        cylinder(d = ring_post_d, h = ring_bottom - base_t + 0.01, $fn = 32);
      // magnet bosses
      for (a = mag_angles) at_angle(mag_r, a)
        translate([0, 0, base_t - 0.01]) mag_boss(mag_hole_base, mag_skin + mag_h - base_t + 0.01, 1);
      // pogo: flange walls + ledge, and the clamp forks
      at_angle(pogo_r, pogo_angle) {
        linear_extrude(base_flange_back - pogo_press)
          stadium_2d(flange_pocket_l + 2 * pogo_wall, flange_pocket_w + 2 * pogo_wall);
        pogo_forks(base_flange_back + clamp_t, base_t - 0.01, 1);
      }
      // component pockets
      if (parts) translate([0, 0, base_t - 0.01]) intersection() {
        union() {
          translate([lolin_x, lolin_y + lolin_tray_cut / 2])
            pocket_rect(lolin_w + lolin_w_adj, lolin_l - lolin_tray_cut, open_bottom = true, open_back = true, clear = lolin_clear);
          intersection() {
            translate([bat_cx, bat_y]) rotate([0, 0, 90]) pocket_rect(bat_w, bat_l, open_back = true);
            translate([bat_cx + bat_l / 2 + pocket_clear - bat_wall_keep, -100, -1]) cube([200, 200, pocket_h + 2]);
          }
          at_angle(buzzer_r, buzzer_ang) pocket_round(buzzer_d);
          at_angle(wall_r(boost_w, boost_l, boost_gap), boost_a) pocket_rect(boost_w, boost_l, open_back = true);
          at_angle(wall_r(touch_w, touch_l, touch_gap), touch_a) pocket_rect(touch_w, touch_l, open_back = true);
        }
        translate([0, 0, -1]) linear_extrude(pocket_h + 2) base_inside_2d();
      }
      if (parts) translate([lolin_x - (lolin_w + lolin_w_adj) / 2 - lolin_clear + lolin_tab_off,
                 lolin_y - lolin_l / 2 - lolin_clear - lolin_tab_t + lolin_len_adj, base_t - 0.01])
        cube([lolin_tab_w, lolin_tab_t, lolin_tab_h + 0.01]);
      if (parts) translate([motor_x, motor_y, base_t]) rotate([0, 0, motor_angle]) motor_clip();
      if (parts) switch_place() translate([0, 0, base_t]) switch_mount();
    }
    }
    // pogo: oval through the bottom, flange pocket above it
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, -1]) linear_extrude(face_body + 1.01) stadium_2d(oval_hole_l, oval_hole_w);
      translate([0, 0, face_body]) linear_extrude(base_flange_back - face_body + 3) stadium_2d(flange_pocket_l, flange_pocket_w);
    }
    // magnet pockets (from the inside)
    for (a = mag_angles) at_angle(mag_r, a) translate([0, 0, mag_skin]) cylinder(d = mag_hole_base, h = mag_h + 1);
    // screws: clearance + head recess from the bottom
    for (a = boss_angles) at_angle(boss_r, a) {
      translate([0, 0, -1]) cylinder(d = screw_clear, h = col_start + 2, $fn = 24);
      translate([0, 0, -0.01]) cylinder(d = screw_head_d, h = screw_head_h, $fn = 32);
    }
    for (p = ring_posts) translate([p[0] * ring_hole_cx / 2, p[1] * ring_hole_cy / 2, base_t])
      cylinder(d = ring_pilot, h = 50, $fn = 20);
    // LOLIN32 solder-joint channels
    for (sx = [-1, 1]) translate([lolin_x + sx * (lolin_w / 2 - lolin_pin_inset), lolin_y, base_t - lolin_chan_d])
      translate([-lolin_chan_w / 2, -lolin_l / 2 - 0.5, 0]) cube([lolin_chan_w, lolin_l + 1, lolin_chan_d + 0.01]);
    at_angle(buzzer_r, buzzer_ang) translate([0, 0, -1]) cylinder(d = sound_hole_d, h = base_t + 2, $fn = 24);
    switch_place() translate([0, 0, -1]) switch_slot(base_t + 2);
  }
}

// ================= Print orientations ======================================
module flip() { translate([0, 0, ball_h]) rotate([180, 0, 0]) children(); }   // top down
module preview() {
  e = 12;
  color("royalblue") translate([0, 0, e]) ball_body();
  color("white") translate([0, 0, e]) white_body();
  color("black") translate([0, 0, e]) number_vol();
  color("gray") base_part();
  color("orange") at_angle(pogo_r, pogo_angle) translate([0, 0, base_flange_back]) pogo_clamp();
  color("orange") translate([0, 0, e]) at_angle(pogo_r, pogo_angle) translate([0, 0, top_flange_back - clamp_t]) pogo_clamp();
}

// test print: the pogo corner of the ball (as printed, top down) and of the
// base, cut out of the real parts, plus two clamps
module pogo_test() {
  cx = fork_x() + clamp_end / 2 + root_flare + 1; r0 = 36; r1 = ball_od / 2 + 1;
  // ball piece: after flip() the pogo is at +y
  translate([0, -pogo_r, 0]) intersection() {
    flip() ball_shell();
    translate([-cx, r0, -1]) cube([2 * cx, r1 - r0, top_t + face_body + flange_t + clamp_t + 6]);
  }
  // base piece
  translate([0, pogo_r - 22, 0]) intersection() {
    base_part(parts = false);
    translate([-cx, -r1, -1]) cube([2 * cx, r1 - r0, 20]);
  }
  for (k = [0, 1]) translate([0, -38 - k * 10, 0]) pogo_clamp();
}

if (part == "ball") flip() ball_body();
else if (part == "white") flip() white_body();
else if (part == "number") flip() number_vol();
else if (part == "base") base_part();
else if (part == "pogo_clamp") pogo_clamp();
else if (part == "pogo_test") pogo_test();
else preview();

echo(str("Rev 2: ball ", ball_h, " mm; LED tops to underside of the white ", led_gap,
         " mm; LED posts ", ring_bottom - base_t, " mm tall; free height under the LED ring ", ring_bottom - base_t, " mm"));
echo(str("Switch riser pads ", switch_pad_h, " mm (slider tip ", switch_tip_recess, " mm up from the bottom)"));
assert(white_t < number_t, "number_t must be deeper than white_t");
assert(number_t <= top_t, "number_t deeper than the top");
assert(screw_head_h < col_start - 0.3, "screw head recess leaves under 0.3 mm");
assert(switch_pad_h > 0, "switch riser pads <= 0");
assert(top_flange_back - clamp_t - pin_hole_d - pin_floor > col_start, "top pogo forks reach the base");
