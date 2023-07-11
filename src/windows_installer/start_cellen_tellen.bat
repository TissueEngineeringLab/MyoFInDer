:: File for starting Cellen-Tellen in a virtual environment in Windows

@echo off

set "base_path=%userprofile%\AppData\Local\Cellen-Tellen"

echo Checking if Python is installed on the computer
python --version >nul 2>&1 && (
    echo Python is installed on the computer
) || (
    echo Python was not found on the computer ! & echo Install it and run Cellen Tellen again & exit /b 1
)

echo.

echo Checking if the project folder exists
if exist %base_path% (
    echo The project folder exists
) else (
    echo The project folder does not exist, creating it & mkdir %base_path%
)

echo.

echo Checking if the virtual environment is set
if exist %base_path%\venv (
    echo The virtual environment is already set
) else (
    echo The virtual environment does not exist, creating it & python -m venv %base_path%\venv
)

echo.

echo Checking if the dependencies are installed
%base_path%\venv\Scripts\python -m pip list | findstr "cellen" >nul 2>&1 && (
    echo The dependencies are installed
) || (
    echo The dependencies are not installed, installing them & %base_path%\venv\Scripts\python -m pip install cellen_tellen
)

echo.

echo Checking that Cellen Tellen was correctly installed
%base_path%\venv\Scripts\python -c "import cellen_tellen" && (
    echo Cellen-Tellen was correctly installed
) || (
    echo Something went wrong during Cellen-Tellen's installation !
)

echo.

echo Starting Cellen Tellen
%base_path%\venv\Scripts\python -m cellen_tellen
