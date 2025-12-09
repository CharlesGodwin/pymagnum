#!/bin/bash
# read how_to_build.md
# this assumes python 3.7 or higher is installed
rm -R -f dist
rm -R -f pymagnum.egg-info
python3 -m build
