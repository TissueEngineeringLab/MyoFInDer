:: File for compiling cellen-tellen into an executable file in windows

where /q pyinstaller
if errorlevel 1 (
    echo You need to install the python module pyinstaller for compiling cellen-tellen !
) else (
    cd ..
    pyinstaller run.py --noconfirm --name cellen-tellen --paths .\venv\Lib\site-packages\ --hidden-import sklearn.utils._typedefs --hidden-import sklearn.neighbors._partition_nodes --add-data ".\cellen_tellen\app_images\;app_images"
    if exist .\dist\ (
        mkdir .\dist\Projects
        "C:\Program Files (x86)\Caphyon\Advanced Installer 19.3\bin\x86\AdvancedInstaller.com" /build .\Executable_files\Cellen-Tellen.aip
    ) else (
        echo Something went wrong, dist folder not found !
    )
)
