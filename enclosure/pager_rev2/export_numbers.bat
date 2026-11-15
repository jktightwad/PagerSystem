@echo off
rem Export white + number for every pager number into numbers\ (Windows).
rem The ball and touch_mark are the same for every number (export_all). Load ball,
rem white_N, number_N and touch_mark together in Bambu Studio as ONE object.
cd /d "%~dp0"
rem Edit OPENSCAD if OpenSCAD is installed somewhere else.
set OPENSCAD="C:\Program Files\OpenSCAD\openscad.exe"
if not exist numbers mkdir numbers
for %%n in (1 2 3 4 5 6 7 8 9 10 11 12 13 14 15) do (
  echo Number %%n ...
  for %%p in (white number) do (
    %OPENSCAD% -o "numbers\%%p_%%n.stl" -D "part=\"%%p\"" -D "number_text=\"%%n\"" pager_rev2.scad
  )
)
