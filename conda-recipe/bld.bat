%PYTHON% setup.py install
if errorlevel 1 exit 1

:: Add more build steps here, if they are necessary.

set MENU_DIR=%PREFIX%\Menu
if not exist (%MENU_DIR%) mkdir %MENU_DIR%

cd %RECIPE_DIR%
%PYTHON% expandpdfguibase.py menu-windows.json > %MENU_DIR%\menu-windows.json
if errorlevel 1 exit 1

copy pdfgui.ico %MENU_DIR%\
if errorlevel 1 exit 1

:: See http://docs.continuum.io/conda/build.html
:: for a list of environment variables that are set during the build process.
