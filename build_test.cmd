python setup.py clean
rd /s /q dist
rd /s /q pymagnum.egg-info
python setup.py sdist bdist_wheel
python -m twine upload --verbose -u CharlesG --repository-url https://test.pypi.org/legacy/ dist/*
@echo Use this to install
@echo sudo pip install --upgrade -i https://test.pypi.org/simple/ pymagnum==VERSION
