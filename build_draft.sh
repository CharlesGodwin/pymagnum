#!/bin/bash
rm -R -f dist
rm -R -f pymagnum.egg-info
python3 setup.py clean build
python3 setup.py sdist --formats=zip
