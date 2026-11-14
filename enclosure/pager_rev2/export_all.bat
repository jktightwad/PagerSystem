@echo off
rem Export the Rev 2 parts (number from number_text in the .scad) (Windows).
cd /d "%~dp0"
rem Edit OPENSCAD if OpenSCAD is installed somewhere else.
set OPENSCAD="C:\Program Files\OpenSCAD\openscad.exe"
for %%p in (ball white number base pogo_clamp) do (
  echo Exporting %%p.stl ...
  %OPENSCAD% -o "%%p.stl" -D "part=\"%%p\"" pager_rev2.scad
)
