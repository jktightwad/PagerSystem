// Pogo / magnetic connector fit tester (OpenSCAD)
//
// One plate with a row of slots, each holding the connector the same way
// the pager does: the contact face FLUSH with the top surface, the body
// through a hole, the flange in a pocket from underneath. Each slot uses a
// different clearance, engraved next to it, so one print shows which hole
// and pocket sizes fit best. Then copy the winning sizes into the shell
// (pager_shell_test.scad, "Pogo connector" group).
//
// Defaults are the ORIGINAL measured connector (2-pin magnetic, oval body
// with a flange). For another connector, change the "Connector" settings:
// body/flange shape (stadium = rounded ends, rect = rounded rectangle) and
// sizes. Sizes are the connector's real dimensions; clearance is added.
//
// Print top surface up (as exported): pockets open onto the bed, labels on
// top. Export: F6, wait for "Rendering finished", F7.

/* [Connector (real sizes, mm)] */
connector_name = "2-pin magnetic pogo";
body_shape   = "stadium"; // [stadium, rect]
// contact-face body length
body_l       = 13.15; // [1:0.01:60]
// contact-face body width
body_w       = 4.0; // [1:0.01:30]
// corner radius (rect only)
body_r       = 1.0; // [0:0.01:10]
// body height in front of the flange (= plastic thickness for a flush face)
face_body    = 2.0; // [0.4:0.01:10]
flange_shape = "stadium"; // [stadium, rect, none]
flange_l     = 19.2; // [1:0.01:80]
flange_w     = 4.0; // [1:0.01:30]
// corner radius (rect only)
flange_r     = 1.0; // [0:0.01:10]
flange_t     = 1.0; // [0.2:0.01:5]
// body behind the flange (needs no pocket here; listed for reference)
back_body    = 1.0; // [0:0.01:10]

/* [Clearances to test (added to length AND width, mm)] */
// Labels show the BODY clearance in hundredths of a mm (+5 = +0.05 mm);
// the console lists every slot's exact hole and pocket sizes.
// Negative values test holes TIGHTER than the connector, e.g.
// body_clears = [-0.1, -0.05, 0.0, 0.05, 0.10];
body_clears   = [0.0, 0.05, 0.10, 0.15, 0.20];
flange_clears = [0.0, 0.05, 0.10, 0.15, 0.20];   // same count as body_clears

/* [Plate] */
// plastic between neighbouring slots
gap_between  = 5; // [1:0.5:20]
margin       = 5; // [1:0.5:20]
label_size   = 6; // [3:0.5:12]
label_depth  = 0.8; // [0.2:0.1:2]
label_font   = "Liberation Sans:style=Bold";

/* [Hidden] */
$fn = 64;
n       = len(body_clears);
slot_w  = max(body_w, flange_shape == "none" ? 0 : flange_w) + max(body_clears) + gap_between;
max_l   = max(body_l, flange_shape == "none" ? 0 : flange_l) + max(max(body_clears), max(flange_clears));
label_w = 3 * label_size * 0.75;   // up to 3 characters, e.g. "+10"
plate_l = margin + max_l + 3 + label_w + margin;
plate_w = 2 * margin + n * slot_w - gap_between;
plate_t = face_body + (flange_shape == "none" ? 0 : flange_t);

module shape_2d(shape, l, w, r) {
  if (shape == "stadium") hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0]) circle(d = w);
  else offset(r = r) square([l - 2 * r, w - 2 * r], center = true);
}

function sgn(v) = v >= 0 ? "+" : "";   // negative numbers already carry "-"

module tester() {
  body_cx = margin + max_l / 2;
  difference() {
    cube([plate_l, plate_w, plate_t]);
    for (i = [0 : n - 1]) {
      y = margin + i * slot_w + (slot_w - gap_between) / 2;
      translate([body_cx, y, 0]) {
        // body hole through the face
        translate([0, 0, -1]) linear_extrude(plate_t + 2)
          shape_2d(body_shape, body_l + body_clears[i], body_w + body_clears[i], body_r);
        // flange pocket from underneath (flange_t deep), so the face ends up flush
        if (flange_shape != "none")
          translate([0, 0, -0.01]) linear_extrude(flange_t + 0.01)
            shape_2d(flange_shape, flange_l + flange_clears[i], flange_w + flange_clears[i], flange_r);
      }
      // engraved label: body clearance in HUNDREDTHS of a mm ("+5" = +0.05),
      // large enough to print with a 0.4 mm nozzle
      translate([body_cx + max_l / 2 + 3, y, plate_t - label_depth])
        linear_extrude(label_depth + 0.01)
          text(str(sgn(body_clears[i]), round(body_clears[i] * 100)), size = label_size,
               font = label_font, halign = "left", valign = "center");
      // backup marker: slot number as notches on the left edge (1 notch = slot 1)
      for (j = [0 : i]) translate([0, y - i * 0.9 + j * 1.8, -1]) cylinder(d = 1.2, h = plate_t + 2, $fn = 12);
    }
  }
}

tester();

echo(str("Plate ", plate_l, " x ", plate_w, " x ", plate_t, " mm, ", n, " slots"));
for (i = [0 : n - 1])
  echo(str("Slot ", i + 1, ": body hole ", body_l + body_clears[i], " x ", body_w + body_clears[i],
           ", flange pocket ", flange_l + flange_clears[i], " x ", flange_w + flange_clears[i]));
