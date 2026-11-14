#!/bin/sh
# Export ball / white / number for every pager number into numbers/ (macOS / Linux).
# Load ball_N, white_N and number_N together in Bambu Studio as ONE object
# with three parts. NUMBERS="1 2 3" limits it.
cd "$(dirname "$0")"
OPENSCAD=${OPENSCAD:-openscad}
NUMBERS=${NUMBERS:-"1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"}
mkdir -p numbers
for n in $NUMBERS; do
  echo "Number $n ..."
  for p in ball white number; do
    "$OPENSCAD" -o "numbers/${p}_$n.stl" -D "part=\"$p\"" -D "number_text=\"$n\"" pager_rev2.scad
  done
done
