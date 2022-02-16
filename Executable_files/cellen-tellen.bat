:: File for running the cellen-tellen executable in Windows
:: It is meant to be copy-pasted in the dist folder generated when compiling

if exist .\cellen-tellen\cellen-tellen.exe (
    :: To be tested
    start "cellen-tellen" .\cellen-tellen\cellen-tellen.exe
) else (
    echo Couldn't find the cellen-tellen executable, aborting !
)
