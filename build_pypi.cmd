python setup.py clean
rd /s /q dist
python setup.py sdist bdist_wheel
python -m twine upload -u CharlesGodwin dist/*
@echo Use this to install
@echo sudo pip3 install --upgrade pymagnum
