:: File for compiling cellen-tellen into an executable file in windows

where /q pyinstaller
if errorlevel 1 (
    echo You need to install the python module pyinstaller for compiling cellen-tellen !
) else (
    :: To be tested and completed
    cd ..
    pyinstaller run.py --name cellen-tellen --paths .\venv\Lib\site-packages\ --hidden-import sklearn.utils._typedefs --hidden-import sklearn.neighbors._partition_nodes --add-data ".\cellen_tellen\app_images\;app_images"
)
