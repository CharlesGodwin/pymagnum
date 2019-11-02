python setup.py clean
rd /s /q dist
python setup.py sdist bdist_wheel
rem python -m twine upload -u CharlesG --repository-url https://test.pypi.org/legacy/ dist/*
python -m twine upload -u CharlesGodwin dist/*
@echo Use this to install
rem @echo sudo pip3 install --upgrade -i https://test.pypi.org/simple/ pymagnum
@echo sudo pip3 install --upgrade pymagnum
