// Top-view component layout sketch for the pager chassis (looking down,
// 12 o'clock up). Outlines only, to check fit. Not a printable part.
// Geometry matches pager_shell_test.scad defaults (v10).
$fn = 96;
plate_d   = 104 - 2 * 2.4 - 0.4;     // chassis plate
ring_od   = 68.2; ring_id = 53.6;     // LED ring (sits 9 mm above the plate)
posts     = [[17.62, 26.4], [-17.62, 26.4], [17.62, -26.4], [-17.62, -26.4]];
boss_r    = 47.1;
module at(r, a) translate([r * sin(a), r * cos(a)]) rotate(-a) children();
module label(t, p, s = 2.6) color("black") translate(p) text(t, size = s, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");

color("gainsboro") circle(d = plate_d);
// clamp ring at the wall
color("silver") difference() { circle(d = plate_d - 1); circle(d = plate_d - 5); }
// screw columns (above the plate) and magnet caps / pogo under the brim
for (a = [45, 135, 225, 315]) color("dimgray") at(boss_r, a) circle(d = 7);
for (a = [60, 300]) color("orchid") at(43, a) circle(d = 10.4);
color("gold") at(44, 180) hull() for (s = [-1, 1]) translate([s * 7.6, 0]) circle(d = 4);
// LED ring footprint (above, 9 mm up) and its posts
color("lightskyblue", 0.35) difference() { circle(d = ring_od); circle(d = ring_id); }
for (p = posts) color("steelblue") translate(p) circle(d = 5);
// LOLIN32 Lite 49.6 x 25.7, flat on the plate, far from the pogo; USB-C / JST end towards 6 o'clock
color("mediumseagreen", 0.9) translate([0.15, 19.2]) square([25.7, 49.6], center = true);
color("orange", 0.6) translate([0.15, -5.6 - 8]) square([25.7, 16], center = true);   // plug clearance
// left: battery 30 x 35, boost 10.5 x 11, buzzer 9.2
color("khaki", 0.95) translate([-28, 0]) square([30, 35], center = true);
color("tomato") translate([-31, -24]) square([10.5, 11], center = true);
color("purple") translate([-22, -36]) circle(d = 9.2);
// right: motor 7 x 26 in U-clips, touch module 11 x 14 over the recess
color("brown") translate([39.5, 0]) square([7, 26], center = true);
for (sy = [-1, 1]) color("saddlebrown") translate([39.5, sy * 9]) square([9.4, 4], center = true);
color("deepskyblue") translate([22, -12]) square([11, 14], center = true);
// stacking recess outline (egg, on the underside)
color("navy", 0.5) difference() { offset(delta = 0.6) hull() { circle(d = 72); translate([0, 6]) circle(d = 62); } hull() { circle(d = 72); translate([0, 6]) circle(d = 62); } }

label("LOLIN32", [0.15, 22], 3.2);
label("USB-C / JST", [0.15, -12]);
label("pogo", [0, -40.5], 2.2);
translate([-28, 0]) rotate(90) label("battery 500 mAh", [0, 0], 2.4);
label("boost", [-31, -24], 2);
label("buzz", [-22, -36], 1.8);
translate([39.5, 0]) rotate(90) label("motor", [0, 0], 2);
label("touch", [22, -12], 2);
label("mag", [37.2, 21.5], 2); label("mag", [-37.2, 21.5], 2);
label("LED ring (9 mm up)", [0, 31], 2.2);
