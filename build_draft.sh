#!/bin/bash
# readhow_to_build.md
# this assumes python 3.7 or higher is installed
rm -R -f dist
rm -R -f pymagnum.egg-info
python setup.py clean build
python setup.py sdist --formats=zip
