:: File for compiling the Windows installer

@echo off

set advinst_path="C:\Program Files (x86)\Caphyon\Advanced Installer 20.8\bin\x86\"

echo Checking if Advanced Installer is installed
if exist %advinst_path% (
    echo Advanced Installer 20.8 found on the system
) else (
    echo Please install Advanced Installer 20.8 for compiling the installer
    pause
    exit /b 1
)

echo.

echo Building the installer
%advinst_path%advinst /build "%~dp0config.aip" && (
    echo Successfully built the installer
) || (
    echo Something went wrong when building the installer !
    pause
    exit /b 1
)

echo.

echo Deleting the cache files
rmdir /s /q "%~dp0config-cache"
echo Creating the bin folder if it does not already exist
mkdir "%~dp0..\..\bin\"
echo Moving the installer file to the bin folder
move "%~dp0\config-SetupFiles\config.msi" "%~dp0..\..\bin\cellen_tellen.msi"
echo Deleting the remaining setup files folder
rmdir /s /q "%~dp0config-SetupFiles"
