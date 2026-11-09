#!/bin/sh
# Export every part of the pager shell as its own STL (macOS / Linux).
# Uses the values saved in pager_shell_test.scad (not Customizer presets).
cd "$(dirname "$0")"
OPENSCAD=${OPENSCAD:-openscad}
for p in crown number brim ball chassis base; do
  echo "Exporting $p.stl ..."
  "$OPENSCAD" -o "$p.stl" -D "part=\"$p\"" pager_shell_test.scad
done
