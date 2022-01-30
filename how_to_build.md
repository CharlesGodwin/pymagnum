__How to Build pyMagnum for Testing__

This is a simple description of the steps needed to build a version locally.

**NOTE** you must be using Python 3 for all this. In windows use `pip` and `python` and in Linux use `sudo pip3` and `python3`. If you have experience with Python Virtual Environments, you can use one of those too.

Clone the repository from https://github.com/CharlesGodwin/pymagnum

One time, run:
`sudo pip3 install -r requirements.txt`

- Search for `BUILDINFO` in all files to identify changes needed for documentation and software builds.

- Build the package by running the script / batch file `build_draft.sh` or, in Windows, `build_draft.cmd`
  The Windows version will also build the documentation and place it in `./build/html`. There is no script for building the documentation in linux.
- If you want to publish a private version of documentation modify README.rst
- Install by running the following:  (replace \<version number\> with the current version number).
`sudo pip3 install --update dist/pymagnum-<version number>.zip`

__Visual Studio Code development__

If you are developing in VS Code, You need to do this to ensure the debug environment picks up the right program code. You do not need to install the package in this environment, but make sure you run the same version of Python as VS code is using.

`python setup.py develop` or
`sudo python3 setup.py develop`
