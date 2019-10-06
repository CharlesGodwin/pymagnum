python setup.py clean
rd /s /q dist
python setup.py sdist bdist_wheel
python -m twine upload -u CharlesG --repository-url https://test.pypi.org/legacy/ dist/*
@echo Use this to install
@echo sudo pip3 install --upgrade -i https://test.pypi.org/simple/ pymagnum
