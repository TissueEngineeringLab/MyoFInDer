#!/bin/sh
# File for running the cellen-tellen executable in Linux
# It is meant to be copy-pasted in the dist folder generated when compiling

if [ -e ./cellen-tellen/cellen-tellen ]; then
  ./cellen-tellen/cellen-tellen
else
  echo "Couldn't find the cellen-tellen executable, aborting !"
fi
