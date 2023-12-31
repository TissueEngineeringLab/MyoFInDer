:: File for starting MyoFInDer in a virtual environment in Windows

@echo off

set "base_path=%localappdata%\MyoFInDer"

echo Checking if Python is installed on the computer
python --version >nul 2>&1 && (
    echo Python is installed on the computer
) || (
    echo Python was not found on the computer !
    echo Install it first and run MyoFInDer again
    pause
    exit /b 1
)

echo.

echo Checking if the project folder exists
if exist %base_path% (
    echo The project folder exists
) else (
    echo The project folder does not exist, creating it
    mkdir %base_path%
)

echo.

echo Checking if the virtual environment is set
if exist %base_path%\venv (
    echo The virtual environment is already set
) else (
    echo The virtual environment does not exist, creating it
    python -m venv %base_path%\venv
)

echo.

echo Checking if MyoFInDer should run in test mode
if "%1"=="-t" (
    set test=true
    echo Running in test mode
) else (
    set test=false
    echo Running in regular mode
)

echo.

echo Checking if the dependencies are installed
%base_path%\venv\Scripts\python -m pip list | findstr "myofinder" >nul 2>&1 && (
    echo The dependencies are installed
) || (
    echo The dependencies are not installed, installing them
    if "%test%"=="false" (
        %base_path%\venv\Scripts\python -m pip install myofinder==1.0.7
    ) else (
        echo Installing the locally built package in test mode
        %base_path%\venv\Scripts\python -m pip install "%2"
    )
)

echo.

echo Checking that MyoFInDer is correctly installed
%base_path%\venv\Scripts\python -c "import myofinder" && (
    echo MyoFInDer was correctly installed
) || (
    echo Something went wrong during MyoFInDer's installation !
    pause
    exit /b 1
)

echo.

echo Starting MyoFInDer
if "%test%"=="false" (
    %base_path%\venv\Scripts\python -m myofinder
) else (
    %base_path%\venv\Scripts\python -m myofinder -t
)
