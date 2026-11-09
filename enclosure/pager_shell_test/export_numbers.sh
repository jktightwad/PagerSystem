#!/bin/sh
# Export hat + number inlay for every pager number into numbers/ (macOS / Linux).
# Uses the values saved in pager_shell_test.scad. NUMBERS="1 2 3" limits it.
cd "$(dirname "$0")"
OPENSCAD=${OPENSCAD:-openscad}
NUMBERS=${NUMBERS:-"1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"}
mkdir -p numbers
for n in $NUMBERS; do
  echo "Number $n ..."
  "$OPENSCAD" -o "numbers/hat_$n.stl"    -D 'part="hat"'    -D "number_text=\"$n\"" pager_shell_test.scad
  "$OPENSCAD" -o "numbers/number_$n.stl" -D 'part="number"' -D "number_text=\"$n\"" pager_shell_test.scad
done
