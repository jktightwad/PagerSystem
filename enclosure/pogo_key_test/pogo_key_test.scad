// Magnetic pogo connector + keystone fit test (OpenSCAD)
//
// Two small coupons that stack like two pagers:
//   top    - stands in for the TOP of a pager (and the dock): a raised
//            keystone carrying the FLAT-contact half of the connector
//   bottom - stands in for the UNDERSIDE of the pager above: a matching
//            keystone recess carrying the SPRING-PIN half (protected in the
//            recess when the pager is set down on a desk)
// The keystone is a trapezoid, so the coupons only mate one way round; in
// the real pager it sits off-centre in the coloured border.
//
// Each connector half: oval body passes through the plastic; its mounting
// flange is recessed into the keystone from the inside so it sits flush.
// Protrusion of each oval face is adjustable.
//
// Render: openscad -D 'part="top"' -o pogo_key_top.stl pogo_key_test.scad
//         part = "top", "bottom", or "all" (assembled preview)

part = "all";

// ---- Connector (measured; adjust to fit) ----
oval_l        = 13.15;  // oval body length
oval_w        = 4.0;    // oval body width
oval_clear    = 0.25;   // added to the hole all round (per side)
body_depth    = 2.0;    // flange face to oval face
flange_l      = 19.2;   // flange length
flange_w      = 4.0;    // flange width (measured: same as the oval)
flange_t      = 1.0;    // flange thickness
flange_clear  = 0.25;   // pocket clearance per side
flange_hole_outside = 17.44;  // mounting holes, outside edge to outside edge
flange_hole_d = 1.6;    // NOT MEASURED YET, guess
flange_hole_cc = flange_hole_outside - flange_hole_d;   // centre-to-centre
screw_pilot_d = 1.3;    // pilot for small self-tapping screws (or glue)

// Protrusion of each oval face beyond the plastic surface it sits in
// (positive = sticks out). Spring pins are usually best slightly protruding.
protrude_flat = 0.2;    // top coupon: flat contacts above the keystone top
protrude_pins = 0.4;    // bottom coupon: pin face below the recess ceiling

// ---- Keystone ----
key_long  = 28;    // long side of the trapezoid
key_short = 22;    // short side
key_depth = 12;    // front to back
key_h     = 3.0;   // how far the keystone stands up
key_r     = 1.5;   // corner rounding
key_clear = 0.3;   // recess clearance per side
seat_gap  = 0.2;   // extra recess depth so connector faces meet before the plastic does

// ---- Coupons ----
plate_l = 44;
plate_w = 34;
top_plate_t    = 3.0;
bottom_plate_t = key_h + protrude_flat + protrude_pins + seat_gap + 3.0;
wire_groove_w  = 4;
wire_groove_d  = 1.5;

$fn = 64;

// Plastic thickness the connector body passes through, from the protrusion
// wanted: body_depth = (plastic under flange) + protrusion
function plastic_t(protrusion) = body_depth - protrusion;

module stadium(l, w, h) {
  hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0, 0]) cylinder(d = w, h = h);
}

module rounded_rect(l, w, h, r) {
  hull() for (sx = [-1, 1], sy = [-1, 1])
    translate([sx * (l / 2 - r), sy * (w / 2 - r), 0]) cylinder(r = r, h = h);
}

module trapezoid(long, short, depth, h, r, grow = 0) {
  // long side at -Y, short side at +Y
  hull() for (p = [[-long / 2, -depth / 2], [long / 2, -depth / 2],
                   [short / 2, depth / 2], [-short / 2, depth / 2]])
    translate([p[0] + sign(p[0]) * (grow - r) , p[1] + sign(p[1]) * (grow - r), 0])
      cylinder(r = r, h = h);
}

// Cut-outs for one connector half, with its outer face at z = 0 (pointing +Z)
// and the plastic surface at z = -protrusion. Flange pocket opens downward.
module connector_cut(protrusion, inner_surface_z) {
  t = plastic_t(protrusion);
  // oval through-hole
  translate([0, 0, inner_surface_z - 1])
    stadium(oval_l + 2 * oval_clear, oval_w + 2 * oval_clear, 50);
  // flange pocket from the inside surface up to the flange position
  flange_z = -protrusion - t;   // underside of plastic above flange
  translate([0, 0, inner_surface_z - 1])
    stadium(flange_l + 2 * flange_clear, flange_w + 2 * flange_clear,
            flange_z - inner_surface_z + 1);
  // screw pilots
  for (s = [-1, 1]) translate([s * flange_hole_cc / 2, 0, inner_surface_z - 1])
    cylinder(d = screw_pilot_d, h = flange_z - inner_surface_z + 1 + 2, $fn = 16);
}

module connector_body(protrusion) {   // for the preview only
  color("silver") {
    translate([0, 0, -body_depth]) stadium(oval_l, oval_w, body_depth);
    translate([0, 0, -body_depth - flange_t]) stadium(flange_l, flange_w, flange_t);
  }
}

// Top coupon: plate + keystone, flat contacts on top of the keystone
module top_coupon() {
  face_z = top_plate_t + key_h + protrude_flat;   // connector outer face
  difference() {
    union() {
      translate([0, 0, 0]) rounded_rect(plate_l, plate_w, top_plate_t, 3);
      translate([0, 0, top_plate_t]) trapezoid(key_long, key_short, key_depth, key_h, key_r);
    }
    translate([0, 0, face_z]) connector_cut(protrude_flat, -face_z);
    // wire groove under the plate, from the flange pocket to the edge
    translate([-wire_groove_w / 2, 0, -0.01]) cube([wire_groove_w, plate_w, wire_groove_d]);
  }
}

// Bottom coupon, modelled in its stacked position (recess facing down).
module bottom_coupon_stacked() {
  base_z = top_plate_t;                 // sits on the top coupon's plate
  ceiling_z = base_z + key_h + protrude_flat + protrude_pins + seat_gap;
  pin_face_z = ceiling_z - protrude_pins;
  top_z = base_z + bottom_plate_t;
  difference() {
    translate([0, 0, base_z]) rounded_rect(plate_l, plate_w, bottom_plate_t, 3);
    // keystone recess
    translate([0, 0, base_z - 0.01])
      trapezoid(key_long, key_short, key_depth, ceiling_z - base_z + 0.01, key_r, key_clear);
    // connector: outer face points DOWN, so mirror the cut in Z
    translate([0, 0, pin_face_z]) mirror([0, 0, 1])
      connector_cut(protrude_pins, -(top_z - pin_face_z));
    // wire groove on the top (inside) face
    translate([-wire_groove_w / 2, 0, top_z - wire_groove_d]) cube([wire_groove_w, plate_w, wire_groove_d + 0.01]);
  }
}

// Print orientations: both with the "inside" (flange) face on the bed
module top_print() { top_coupon(); }
module bottom_print() {
  translate([0, 0, top_plate_t + bottom_plate_t]) rotate([180, 0, 0]) bottom_coupon_stacked();
}

module preview() {
  top_coupon();
  translate([0, 0, top_plate_t + key_h + protrude_flat]) connector_body(protrude_flat);
  translate([0, 0, 25]) {
    color("lightblue", 0.6) bottom_coupon_stacked();
    pin_face_z = top_plate_t + key_h + protrude_flat + protrude_pins + seat_gap - protrude_pins;
    translate([0, 0, pin_face_z]) mirror([0, 0, 1]) connector_body(protrude_pins);
  }
}

if (part == "top") top_print();
else if (part == "bottom") bottom_print();
else preview();

echo(str("Plastic under flange: top ", plastic_t(protrude_flat),
         " mm, bottom ", plastic_t(protrude_pins), " mm"));
echo(str("Bottom coupon thickness ", bottom_plate_t, " mm, recess depth ",
         key_h + protrude_flat + protrude_pins + seat_gap, " mm"));
