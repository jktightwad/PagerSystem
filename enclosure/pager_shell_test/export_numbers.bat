@echo off
rem Export hat + number inlay for every pager number into numbers\ (Windows).
rem Uses the values saved in pager_shell_test.scad (not Customizer presets).
rem Change the list after "in" to export only some numbers, e.g. (1 2 3).
set OPENSCAD="C:\Program Files\OpenSCAD\openscad.exe"
cd /d "%~dp0"
if not exist numbers mkdir numbers
for %%n in (1 2 3 4 5 6 7 8 9 10 11 12 13 14 15) do (
  echo Number %%n ...
  %OPENSCAD% -o "numbers\hat_%%n.stl" -D "part=\"hat\"" -D "number_text=\"%%n\"" pager_shell_test.scad
  %OPENSCAD% -o "numbers\number_%%n.stl" -D "part=\"number\"" -D "number_text=\"%%n\"" pager_shell_test.scad
)
echo Done. The ball, chassis and base are the same for every pager: use export_all.bat.
pause
