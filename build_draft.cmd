rd /s /q dist
rd /s /q pymagnum.egg-info
python setup.py clean build
python setup.py sdist --formats=zip
