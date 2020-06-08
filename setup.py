#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# tutorial https://packaging.python.org/tutorials/packaging-projects/
#
from distutils.core import setup
import setuptools
import magnum

with open("README.rst", "r") as file:
    long_description = file.read()

setup(name='pymagnum',
      version=magnum.__version__,
      description='Magnum Energy Network Interface (read-only)',
      author='Charles Godwin',
      author_email='magnum@godwin.ca',
      py_modules=['magnum.tools.magtest',
                  'magnum.tools.magdump', 'magnum.tools.test_packets'],
      long_description=long_description,
      long_description_content_type="text/x-rst",
      license="BSD",
      url='https://github.com/CharlesGodwin/pymagnum',
      packages=setuptools.find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3 :: Only",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent"
      ],
      install_requires=['pyserial', 'tzlocal'],
      python_requires='>=3.5',
      entry_points={
          'console_scripts': [
              'magdump = magnum.tools.magdump:main',
              'magtest = magnum.tools.magtest:main'
          ],
      },
      keywords='Magnum Energy Renewable Solar Network RS485 IoT'
      )
