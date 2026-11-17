// Pool-ball pager, Rev 2 (OpenSCAD)
//
// Two printed parts plus a pogo tower:
//   - ball: shell + flat top, printed TOP DOWN in three colours on the AMS
//     (export ball / white / number as separate STLs, load them together as
//     one multi-part object and give each part its filament).
//     The white circle is white_t thick (0.25 first layer + one 0.2 layer)
//     over a light pocket; the black number goes number_t deep so it blocks
//     the light. The top is top_t thick elsewhere and built up in the inside
//     corner against light bleed at the rounded edge.
//   - base: flat plate (base_t) that carries every component, printed
//     BOTTOM DOWN. Same mounts as Rev 1's chassis.
//   - pogo_tower: oval tube holding both pogo connectors (top and bottom),
//     clamped between the ball top and the base by the two screws either
//     side of it. The connectors' 1.9 mm fronts stick through the top / base.
// Magnets go in from the inside (mag_skin of plastic in front of them), so
// nothing sticks out of the top or the bottom.
//
// Coordinates: z = 0 at the bottom of the pager. Looking down on the top,
// +Y = 12 o'clock; angles clockwise from 12.
// Rev 1 (pager_shell_test) is unchanged and kept for reference.

use <fonts/LiberationSans-Bold.ttf>
use <fonts/DejaVuSerif-Bold.ttf>

/* [Part to show / export] */
part = "all"; // [all, ball, white, number, touch_mark, base, pogo_tower, pogo_test, pogo_section]

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
// screw columns: 45 / 315 stay; the other two flank the pogo tower (see Hidden)

/* [Top: white circle, light and number] */
white_d      = 72;      // white circle (LED ring is 68.2)
white_t      = 0.45;    // [0.2:0.05:1.65] white thickness = lit face
// light pocket under the white: white_d minus this rim on each side
pocket_rim   = 1.0;     // [0:0.1:5]
number_t     = 1.2;     // [0.4:0.05:1.65] black number depth from the top

/* [Touch sensor] */
// touch module 14.6 x 11 under the top at 12 o'clock (opposite the pogo),
// long side along the edge; its 11 mm touch area is 1 mm in from one end
tsens_l       = 14.6;   // [5:0.1:30]
tsens_w       = 11.0;   // [5:0.1:20]
tsens_area_d  = 11.0;   // [3:0.1:20]
tsens_area_in = 1.0;    // [0:0.1:5] touch area's edge from the sensor's end
tsens_clear   = 0.2;    // [0:0.05:1] round the sensor in its pocket
tsens_wall_h  = 2.0;    // [0.5:0.1:6] locating walls (3 sides; wire end open)
tsens_angle   = 0;      // [0:1:359]
// circle printed on the top over the touch area (its own part: touch_mark)
// ring fills the flat between the white circle and the start of the rounded
// edge; full top thickness so the ball colour doesn't show through
mark_od       = 11.0;   // [4:0.1:14] (11 = white circle to edge curve)
mark_w        = 0.8;    // [0.4:0.1:3] line width
mark_t        = 1.65;   // [0.2:0.05:1.65] depth from the top (= top_t)
mark_gap      = -0.1;   // [-0.5:0.05:5] between the white circle and the mark (slight overlap: just touching makes a non-manifold edge)

/* [Base support] */
// the base's screw build-ups stand this much proud and key into pockets in
// the column ends (stops the base rotating)
key_h         = 1.0;    // [0:0.1:3]
key_clear     = 0.15;   // [0:0.05:0.5] round the key in the column pocket
// support ring: a ledge all round the ball wall at the column ends
// (col_start), and a matching rim round the base's edge up to it, so the base
// is supported all round, not only at the screws. Parts placed "against the
// wall" now sit against the base's rim.
rim_w         = 2.0;    // [1:0.1:5] ledge / rim width
// the ledge and rim are cut away round the pogo tower (this much clearance)
pogo_notch_clear = 1.3; // [0:0.1:3] (collar 1.0 + 0.3)

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

/* [Pogo tower] */
tower_wall    = 1.6;    // [1:0.1:3] tube size = flange pocket + this all round
// flanges stand this proud of their pockets, so the tower ends press them
flange_proud  = 0.1;    // [0:0.05:0.4]
// extra depth in each flange pocket (base and ball): 0.9 = printed test needed
// about 1 mm more for the connectors to sit flush
pogo_pocket_extra = 0.9; // [0:0.05:2]
tower_slot_w  = 4.0;    // [2:0.5:8] wire exit slot (centre side), width
tower_slot_h  = 5.0;    // [2:0.5:10] and height
// snap fit: a collar on the base pad and on the ball pad holds each tower end;
// a bead inside the collar clicks into a groove round the tower
tower_socket_h = 1.6;   // [0.8:0.1:3] collar height
tower_socket_t = 0.9;   // [0.6:0.1:2] collar wall
tower_fit      = 0.1;   // [0:0.05:0.4] clearance tower to collar, per side
snap_bead      = 0.25;  // [0:0.05:0.5] bead depth (0 = plain socket)
// gap from each tower end to the column beside it
col_gap       = 1.6;    // [0.5:0.1:5] (collar 1.0 + 0.6)

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
// no 5 V boost any more (ring and buzzer on 3.3 V). These only place the
// power switch, where the boost pocket's front wall used to be.
boost_w = 10.5; boost_l = 11; boost_gap = 0; boost_a = 210.5;
buzzer_d = 9.2; buzzer_gap = 0;
buzzer_a = -1;          // -1 = auto: beside the LOLIN32's 12 o'clock end, away from the battery
sound_hole_d   = 2.0;
// old touch module pocket, now a spot for the GND / 3.3 V / 5 V rails
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
// slider tip this far up from the bottom of the base (0 = flush, negative = sticks out)
switch_tip_recess = -0.5; // [-2:0.1:3] negative = slider sticks out below the bottom by that much
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
inside_r    = inner_r - base_clear_d / 2 - rim_w - wall_gap;   // parts placed against the wall (the base rim) touch here
// pogo flanges sit in pockets in the base and ball pads (printed open side up,
// no overhangs); the tower is a plain tube clamping them from between
base_pocket_d = flange_t + base_pogo_extra + pogo_pocket_extra - flange_proud;
top_pocket_d  = flange_t + pogo_pocket_extra - flange_proud;
tower_L   = flange_pocket_l + 2 * tower_wall;
tower_W   = flange_pocket_w + 2 * tower_wall;
tower_z0  = face_body + base_pocket_d;            // base pad top
tower_z1  = ball_h - face_body - top_pocket_d;    // ball pad underside
boss_r    = ball_od / 2 - ball_wall - boss_d / 2 + 0.5;
col_da    = asin((tower_L / 2 + col_gap + boss_d / 2) / boss_r);   // column angle either side of the pogo
boss_angles = [45, pogo_angle - col_da, pogo_angle + col_da, 315];
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
    circle(d = pocket_d - 0.8);   // number stays inside the light pocket, so the ball part is the same for every number
  }
}
// magnet boss: h tall, root at z = 0 (dir = +1, rises) or at z = h (dir = -1, hangs)
module mag_boss(hole, h, dir) {
  d_top = hole + 2 * mag_wall; d_root = d_top + (mag_flare ? 2 * h : 0);
  if (dir > 0) cylinder(d1 = d_root, d2 = d_top, h = h);
  else cylinder(d1 = d_top, d2 = d_root, h = h);
}
module bosses_2d() { for (a = boss_angles) at_angle(boss_r, a) circle(d = boss_d); }
module cavity_2d(grow = 0) {
  offset(delta = grow) offset(r = column_fillet) offset(delta = -column_fillet)
    difference() { circle(d = ball_od - 2 * ball_wall); bosses_2d(); }
}
// where base components may go: inside the ball wall and the columns
module base_inside_2d() { cavity_2d(-(base_clear_d / 2 + rim_w + wall_gap)); }

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
      difference() {
        ball_outer(); ball_cavity();
        // touch sensor seat under the top (cuts the corner build-up where needed)
        at_angle(mark_r, tsens_angle) translate([tsens_dx, 0, top_under - tsens_wall_h - 2])
          linear_extrude(tsens_wall_h + 2 + 0.001) square([tsens_l + 2 * tsens_clear, tsens_w + 2 * tsens_clear], center = true);
        // room for the tower in the corner build-up (not into the wall)
        at_angle(pogo_r, pogo_angle) translate([0, 0, col_start])
          linear_extrude(tower_z1 - col_start) offset(delta = pogo_notch_clear) stadium_2d(tower_L, tower_W);
      }
      // touch sensor locating walls (open at the end away from the touch area, for the wires)
      at_angle(mark_r, tsens_angle) translate([tsens_dx, 0, top_under - tsens_wall_h])
        linear_extrude(tsens_wall_h + 0.01) difference() {
          square([tsens_l + 2 * tsens_clear + 2 * pocket_wall, tsens_w + 2 * tsens_clear + 2 * pocket_wall], center = true);
          square([tsens_l + 2 * tsens_clear, tsens_w + 2 * tsens_clear], center = true);
          translate([tsens_l / 2, 0]) square([4 * pocket_wall, tsens_w + 2 * tsens_clear], center = true);
        }
      support_ledge();
      // magnet bosses under the top
      for (a = mag_angles) at_angle(mag_r, a)
        translate([0, 0, ball_h - mag_skin - mag_h]) mag_boss(mag_hole_ball, mag_h + mag_skin - top_t + 0.01, -1);
      // pogo: pad round the hole for the tower's top end to bear on
      at_angle(pogo_r, pogo_angle) translate([0, 0, tower_z1])
        linear_extrude(top_under - tower_z1 + 0.01) offset(delta = 1) stadium_2d(tower_L, tower_W);
      // snap collar hanging down from the pad
      at_angle(pogo_r, pogo_angle) translate([0, 0, tower_z1 + 0.01]) mirror([0, 0, 1]) tower_collar();
    }
    // light pocket under the white
    translate([0, 0, top_under - 1]) cylinder(d = pocket_d, h = white_under - top_under + 1);
    // magnet pockets (from the inside)
    for (a = mag_angles) at_angle(mag_r, a)
      translate([0, 0, ball_h - mag_skin - mag_h - 1]) cylinder(d = mag_hole_ball, h = mag_h + 1);
    // pogo: oval through the top
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, ball_h - face_body - 0.01]) linear_extrude(face_body + 1) stadium_2d(oval_hole_l, oval_hole_w);
      translate([0, 0, tower_z1 - 1]) linear_extrude(top_pocket_d + 1) stadium_2d(flange_pocket_l, flange_pocket_w);
    }
    // pockets in the column ends for the base's keys
    for (a = boss_angles) at_angle(boss_r, a) translate([0, 0, col_start - 0.01]) cylinder(d = boss_d + 2 * key_clear, h = key_h + key_clear + 0.01);
    // column screw pilots
    for (a = boss_angles) at_angle(boss_r, a)
      translate([0, 0, col_start - 1]) cylinder(d = screw_pilot, h = top_under - col_start, $fn = 24);
  }
}
// ledge all round the wall: flat underside at the column ends, 45 deg above
module support_ledge() {
  difference() {
    rotate_extrude($fn = 128)
      polygon([[inner_r - rim_w, col_start], [inner_r + 0.5, col_start], [inner_r + 0.5, col_start + rim_w + 0.5]]);
    pogo_notch();
  }
}
// clearance round the pogo tower, cut out of the ledge / rim
module pogo_notch() {
  at_angle(pogo_r, pogo_angle) translate([0, 0, -1])
    linear_extrude(ball_h) offset(delta = pogo_notch_clear) stadium_2d(tower_L, tower_W + 30);
}
// touch area / mark centre, and the sensor's centre along the edge
mark_r  = white_d / 2 + mark_gap + mark_od / 2;
tsens_dx = tsens_l / 2 - tsens_area_in - tsens_area_d / 2;
module mark_vol() {
  at_angle(mark_r, tsens_angle) translate([0, 0, ball_h - mark_t])
    linear_extrude(mark_t + 0.01) difference() { circle(d = mark_od, $fn = 64); circle(d = mark_od - 2 * mark_w, $fn = 64); }
}
module ball_body() { difference() { ball_shell(); white_vol(); mark_vol(); } }   // same for every number
module white_body() { difference() { white_vol(); number_vol(); mark_vol(); } }

// ================= Pogo tower =============================================
// bead / groove centre height above the pad (in the collar's own frame)
function snap_z() = tower_socket_h - snap_bead - 0.3;
// triangular (45 deg) ring centred at z = 0, depth d at the middle: on the
// tower outline (outside = true, a groove cutter) or inside the collar (a bead)
module snap_ring(d, outside = false) {
  n = 8;
  for (k = [0 : n - 1]) {
    z0 = -d + 2 * d * k / n; zm = z0 + d / n;
    dd = d - abs(zm);
    o0 = outside ? 1 : tower_fit + 0.01;      // outer offset of the ring
    o1 = outside ? -dd : tower_fit - dd;      // inner offset
    translate([0, 0, z0]) linear_extrude(2 * d / n + 0.001) difference() {
      offset(delta = o0) stadium_2d(tower_L, tower_W);
      offset(delta = o1) stadium_2d(tower_L, tower_W);
    }
  }
}
// collar standing on a pad (z = 0 at the pad, growing +z); flip for the ball
module tower_collar() {
  linear_extrude(tower_socket_h) difference() {
    offset(delta = tower_fit + tower_socket_t) stadium_2d(tower_L, tower_W);
    offset(delta = tower_fit) stadium_2d(tower_L, tower_W);
  }
  if (snap_bead > 0) translate([0, 0, snap_z()]) snap_ring(snap_bead);
}
// Upright (print orientation = as fitted). Bottom connector's flange in the
// bottom pocket, top connector's in the top pocket; wires inside, the lead
// to the board out through the slot on the centre side.
module pogo_tower() {
  H = tower_z1 - tower_z0;
  difference() {
    linear_extrude(H) stadium_2d(tower_L, tower_W);
    // through channel for the back bodies and wires
    translate([0, 0, -1]) linear_extrude(H + 2) stadium_2d(oval_hole_l + 0.6, oval_hole_w + 0.6);
    // wire exit, centre side (local -y)
    translate([-tower_slot_w / 2, -tower_W, H / 2 - tower_slot_h / 2]) cube([tower_slot_w, tower_W, tower_slot_h]);
    // snap grooves round both ends (45 deg faces, prints without support)
    if (snap_bead > 0) for (z = [snap_z(), H - snap_z()])
      translate([0, 0, z]) snap_ring(snap_bead + 0.1, outside = true);
  }
}

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
  // back wall (was the boost pocket's front wall)
  translate([-sw / 2 - ct - 2, -sd / 2 - pocket_wall, -0.01]) cube([sw + 2 * ct + 4, pocket_wall, pocket_h + 0.01]);
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
      // rim round the edge up to the ball's support ledge
      difference() {
        cylinder(d = ball_od - 2 * ball_wall - base_clear_d, h = col_start);
        translate([0, 0, -1]) cylinder(r = inner_r - base_clear_d / 2 - rim_w, h = col_start + 2);
        pogo_notch();
      }
      // build-up under each column for the screw head
      for (a = boss_angles) at_angle(boss_r, a) cylinder(d = boss_d, h = col_start + key_h);   // + key into the column
      // LED ring posts
      for (p = ring_posts) translate([p[0] * ring_hole_cx / 2, p[1] * ring_hole_cy / 2, base_t - 0.01])
        cylinder(d = ring_post_d, h = ring_bottom - base_t + 0.01, $fn = 32);
      // magnet bosses
      for (a = mag_angles) at_angle(mag_r, a)
        translate([0, 0, base_t - 0.01]) mag_boss(mag_hole_base, mag_skin + mag_h - base_t + 0.01, 1);
      // pogo: pad round the hole for the tower's bottom end to stand on
      at_angle(pogo_r, pogo_angle) linear_extrude(tower_z0) offset(delta = 1) stadium_2d(tower_L, tower_W);
      // snap collar standing on the pad
      at_angle(pogo_r, pogo_angle) translate([0, 0, tower_z0 - 0.01]) tower_collar();
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
          at_angle(wall_r(touch_w, touch_l, touch_gap), touch_a) pocket_rect(touch_w, touch_l, open_back = true);
        }
        translate([0, 0, -1]) linear_extrude(pocket_h + 2) base_inside_2d();
      }
      if (parts) translate([lolin_x - (lolin_w + lolin_w_adj) / 2 - lolin_clear + lolin_tab_off,
                 lolin_y - lolin_l / 2 - lolin_clear - lolin_tab_t + lolin_len_adj, base_t - 0.01])
        cube([lolin_tab_w, lolin_tab_t, lolin_tab_h + 0.01]);
      if (parts) translate([motor_x, motor_y, base_t - 0.01]) rotate([0, 0, motor_angle]) motor_clip();
      if (parts) switch_place() translate([0, 0, base_t]) switch_mount();
    }
    }
    // pogo: oval through the bottom
    at_angle(pogo_r, pogo_angle) {
      translate([0, 0, -1]) linear_extrude(face_body + 1.01) stadium_2d(oval_hole_l, oval_hole_w);
      translate([0, 0, face_body]) linear_extrude(base_pocket_d + 1) stadium_2d(flange_pocket_l, flange_pocket_w);
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
  color("black") translate([0, 0, e]) mark_vol();
  color("gray") base_part();
  color("orange") translate([0, 0, e / 2]) at_angle(pogo_r, pogo_angle) translate([0, 0, tower_z0]) pogo_tower();
}

// test print: the pogo end of the ball (top down, with the two columns either
// side, full height) and of the base, cut out of the real parts, plus the tower
module pogo_test() {
  cx = boss_r * sin(col_da) + boss_d / 2 + 3; r0 = 36; r1 = ball_od / 2 + 1;
  translate([0, -pogo_r, 0]) intersection() {
    flip() ball_shell();
    translate([-cx, r0, -1]) cube([2 * cx, r1 - r0, ball_h + 2]);
  }
  translate([0, pogo_r - 24, 0]) intersection() {
    base_part(parts = false);
    translate([-cx, -r1, -1]) cube([2 * cx, r1 - r0, 20]);
  }
  translate([0, -55, 0]) pogo_tower();
}

if (part == "ball") flip() ball_body();
else if (part == "white") flip() white_body();
else if (part == "number") flip() number_vol();
else if (part == "base") base_part();
else if (part == "pogo_tower") pogo_tower();
else if (part == "pogo_test") pogo_test();
else if (part == "pogo_section") intersection() {   // assembled, cut through the tower (view only)
  union() {
    color("royalblue") ball_shell(); color("gray") base_part(parts = false);
    color("orange") at_angle(pogo_r, pogo_angle) translate([0, 0, tower_z0]) pogo_tower();
  }
  at_angle(pogo_r, pogo_angle) translate([-30, 0, -1]) cube([60, 20, ball_h + 2]);
}
else if (part == "touch_mark") flip() mark_vol();
else preview();

echo(str("Rev 2: ball ", ball_h, " mm; LED tops to underside of the white ", led_gap,
         " mm; LED posts ", ring_bottom - base_t, " mm tall; free height under the LED ring ", ring_bottom - base_t, " mm"));
echo(str("Switch riser pads ", switch_pad_h, " mm (slider tip ", -switch_tip_recess, " mm below the bottom)"));
assert(white_t < number_t, "number_t must be deeper than white_t");
assert(number_t <= top_t, "number_t deeper than the top");
assert(screw_head_h < col_start - 0.3, "screw head recess leaves under 0.3 mm");
assert(switch_pad_h > 0, "switch riser pads <= 0");
echo(str("Pogo tower ", tower_L, " x ", tower_W, " x ", tower_z1 - tower_z0, " mm (plain tube); flange pockets base ", base_pocket_d, " / ball ", top_pocket_d, " mm deep; columns at ", boss_angles, " deg"));
echo(str("Touch sensor: centre ", mark_r, " mm from the middle; outer edge ", mark_r + tsens_w / 2 + tsens_clear + pocket_wall,
         " mm (ball inside ", inner_r, "); light pocket edge ", pocket_d / 2, " mm, sensor inner edge ", mark_r - tsens_w / 2 - tsens_clear - pocket_wall));
