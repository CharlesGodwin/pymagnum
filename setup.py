#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause

from distutils.core import setup
import setuptools

setup(name='pymagnum',
      version='0.1.2',
      description='Magnum Energy Network Interface (read-only)',
      author='Charles Godwin',
      author_email='magnum@godwin.ca',
      license="BSD",
      packages=['magnum', 'magnum.tools'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
      ],
      install_requires=['pyserial'],
      python_requires='>=3.4'
      )
