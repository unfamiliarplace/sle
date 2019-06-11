@echo off

:: initialize vars

set py2path=c:\python27\
set py2=%py2path%\python.exe

set pyipath=%py2path%\Tools\pyinstaller-2.0\
set pyi=%pyipath%\pyinstaller.py

set slepath="c:\users\Luke\Random\compsci\SLE\"
set pc_setup=%slepath%\setup\pc\

set sledist=%pyipath%\sle\

:: set up build directories

mkdir %sledist%

COPY %slepath%\gui.py %sledist%
COPY %slepath%\library.py %sledist%
COPY sle.ico %sledist%

:: build

cd %pyipath%

%py2% %pyi% -F -w --noupx --icon=%sledist%\sle.ico %sledist%\gui.py

:: copy and delete old

cd %pc_setup%

COPY %pyipath%\dist\gui.exe

DEL /q %pyipath%\SLE.spec
rd /q /s %pyipath%\build
rd /q /s %pyipath%\dist
rd /q /s %sledist%

:: upx and rename

"C:\Python27\Tools\pyinstaller-2.0\upx309w\upx.exe" --best "gui.exe"
REN "gui.exe" "SLE.exe"