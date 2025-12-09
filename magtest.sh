#!/bin/bash
# This is a script to test availability to magnum serial device
# It installs pymagnum in virtual environment named .magtest, runs the test, and deletes the virtual environment folder
MAGTEST=.magtest
if [ -d $MAGTEST ]
then
    echo "**********************************"
    echo "* Folder $MAGTEST already exists *"
    echo "* The test cannot be completed   *"
    echo "* Job terminated!!               *"
    echo "**********************************"
    exit 1
fi
python3 -m venv --prompt magtest $MAGTEST
source $MAGTEST/bin/activate
pip3 install pymagnum --quiet
magtest --device all
deactivate
rm -rf $MAGTEST
