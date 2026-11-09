@echo off
rem Export every part of the pager shell as its own STL (Windows).
rem Uses the values saved in pager_shell_test.scad (not Customizer presets).
rem Edit OPENSCAD if OpenSCAD is installed somewhere else.
set OPENSCAD="C:\Program Files\OpenSCAD\openscad.exe"
cd /d "%~dp0"
for %%p in (hat number ball chassis base) do (
  echo Exporting %%p.stl ...
  %OPENSCAD% -o "%%p.stl" -D "part=\"%%p\"" pager_shell_test.scad
)
echo Done.
pause
