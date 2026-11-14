#!/bin/sh
# Export the Rev 2 parts (number from number_text in the .scad) (macOS / Linux).
cd "$(dirname "$0")"
OPENSCAD=${OPENSCAD:-openscad}
for p in ball white number base pogo_clamp pogo_test; do
  echo "Exporting $p.stl ..."
  "$OPENSCAD" -o "$p.stl" -D "part=\"$p\"" pager_rev2.scad
done
