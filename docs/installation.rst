.. _installation:

Setup
-----

`The Python package site <https://pypi.org/project/pymagnum/>`_

Installation
============

Throughout this documentation ``python`` and its installer ``pip`` are
refered to using the default convention of a Raspberry Pi. The term
``python3`` and ``pip3`` refer to Python 3 versions of the programs. On
other systems the default installation may be Python 3, so just use
``python`` and ``pip`` in those systems. This software requires a minimum of
version 3.5 of Python.

| You will need pip3 installed. On a Pi use:
| ``sudo apt install python3-pip``

| Then install or upgrade this software package using:
| ``sudo pip3 install --upgrade pymagnum``

.. _testing:

Testing
=======

Once this software is installed, test the interconnect hardware:

| First determine your serial device by running
| ``python3 -m serial.tools.list_ports``
| Normally a USB device will show
  up as ``/dev/ttyUSB0`` and a HAT as ``/dev/ttyAMA0`` or ``/dev/ttyS0``

| Next run the provided test program
| ``python3 -m magnum.tools.magtest --help``
| will tell you choices.

Usually you just need to run
``python3 -m magnum.tools.magtest -d /dev/ttyUSB0`` or other device
name.
This should show up to 50 packets with names. such as: ::

   Length:21 REMOTE_A2 =>00003C04500F170601C8A5860100465000781478A2
   Length:18 BMK_81    =>81550992FFC0089B0C77FFBFE11300390A01
   Length:21 INVERTER  =>400000F60002780001003311241E6B000001025800
   Length:21 REMOTE_A4 =>00003C04500F170601C8A58601001E1E00000000A4
   Length: 6 AGS_A1    =>A102343A007C
   Length:21 REMOTE_00 =>400000F60002770001003311241E6B000001025800
   Length:21 REMOTE_00 =>400000F60002770001003311241E6B000001025800
   .
   .
   Packets:50 in 1.10 seconds

If nothing happens or you get a lot of UNKNOWN lines, try reversing the
two wires on your setup and repeating the test. Also double check you
are referencing the right device. HAT serial device can be either
``/dev/ttyAMA0`` or ``/dev/ttyS0``. Try both. If that fails contact the
author using :ref:`feedback`.

Here’s an example of results if the wires are switched::

   Length:42 UNKNOWN   =>7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD7C7C7F173C5D7BD
   Length:29 UNKNOWN   =>0076F8FEFCFEFCFE7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
   Length:40 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FF5FFF0FD70FBBFA6EE933FFBBEFC9E711FFF92FB5FF89EBFDFE
   Length:42 UNKNOWN   =>7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD74341FFB7FBFFB9
   Length:42 UNKNOWN   =>7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD7C3C3FFFFFFFFB7
   Length:29 UNKNOWN   =>00F4D15C46FC9EFC7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
   Length:42 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FFFFFFFFA9FFFF7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
   Length:42 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FFFFFFFFFFFFFF7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
   Length:29 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FBCDD7FF23FFBF007AE85C8CFE24FC
   Length:42 UNKNOWN   =>7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD7C7C7F173C5D7BD
   Length:29 UNKNOWN   =>007AF45C8CFE24FC7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFF

Copyright (c) 2018-2019 Charles Godwin magnum@godwin.ca

SPDX-License-Identifier: BSD-3-Clause
