#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# tutorial https://packaging.python.org/tutorials/packaging-projects/
#
from distutils.core import setup
import setuptools
import magnum

with open("README.md", "r") as file:
    long_description = file.read()

setup(name='pymagnum',
      version=magnum.__version__,
      description='Magnum Energy Network Interface (read-only)',
      author='Charles Godwin',
      author_email='magnum@godwin.ca',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license="BSD",
      url='https://github.com/CharlesGodwin/pymagnum',
      packages=setuptools.find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3 :: Only",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Topic:: Home Automation",
      ],
      install_requires=['pyserial'],
      python_requires='>=3.4',
      keywords='Magnum Energy Renewable Solar Network RS485'
      )