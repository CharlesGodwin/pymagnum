#!/bin/bash
rm -R -f dist
rm -R -f pymagnum.egg-info
python setup.py clean build
python setup.py sdist --formats=zip
