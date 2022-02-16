#!/bin/sh
# File for compiling cellen-tellen into an executable file in Linux

if type "pyinstaller" > /dev/null; then
  cd ..
  pyinstaller run.py --name cellen-tellen --paths ./venv/lib/python3.8/site-packages/ --hidden-import sklearn.utils._typedefs --hidden-import sklearn.neighbors._partition_nodes --hidden-import PIL._tkinter_finder --add-data "./cellen_tellen/app_images/:app_images"
else
  echo "You need to install the python module pyinstaller for compiling cellen-tellen !"
fi
