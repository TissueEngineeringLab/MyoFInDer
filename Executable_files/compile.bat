:: File for compiling cellen-tellen into an executable file in windows

where /q pyinstaller
if errorlevel 1 (
    echo You need to install the python module pyinstaller for compiling cellen-tellen !
) else (
    :: To be tested and completed
    cd ..
    pyinstaller run.py --name cellen-tellen
)
