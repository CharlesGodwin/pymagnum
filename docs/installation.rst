.. _installation:

=====
Setup
=====

`The Python package site <https://pypi.org/project/pymagnum/>`_

Installation Detail
===================

Throughout this documentation, ``python`` and its installer ``pip`` are referred to using the default convention of a python.
If you are using an older OS, such as Buster on a Raspberry Pi, Use ``python3`` and ``pip3`` to  refer to Python 3 versions of the programs. This software requires a minimum of
version 3.7 of Python.

| You will need pip installed. On a Pi use:
| ``sudo apt install python3-pip``

| Then install or upgrade this software package using:
| ``sudo pip install --upgrade pymagnum``

If you are using Python 3.11 or higher, you may be greeted by ``error: externally-managed-environment``.
You can install ``pymagnum`` in a virtual environment to avoid this message, but then you can only use magnum program when you enable this virtualenv first.
If you want to ignore this annoyance, you can just add the ``--break-system-packages`` flag and go on with your day.

If you want to check which version is have installed on your system, run this command:
``sudo pip show pymagnum``

.. _testing:

Testing
=======

Once this software is installed, test the interconnect hardware:

| First determine your serial device by running
| ``python -m serial.tools.list_ports``
| Normally a USB device will show up as ``/dev/ttyUSB0`` and a HAT as ``/dev/ttyAMA0`` or ``/dev/ttyS0``

| Next run the provided test program
| ``magtest --help``
| will tell you choices.

Usually you just need to run
``magtest --device /dev/ttyUSB0`` or other device name.
This should show up to 50 packets with names. such as:

.. code-block:: text

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


Troubleshooting
===============

If nothing happens or you get a lot of UNKNOWN lines, try these trouble shooting routines.

**Timeout is too short**
^^^^^^^^^^^^^^^^^^^^^^^^

One problem is that the default settings for determining the end of a packet
is not right for your setup. try increasing the timeout by adding this to your test
``magtest --timeout 0.005 -d /dev/ttyUSB0``

Increase the value if necessary.


**Reverse Wiring**
^^^^^^^^^^^^^^^^^^

try reversing the two wires on your setup and repeating the test. Also double check you
are referencing the right device. HAT serial device can be either
``/dev/ttyAMA0`` or ``/dev/ttyS0``. Try both. If that fails contact the
author using :ref:`feedback`.

Here’s an example of results if the wires are switched

.. code-block:: text

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

**System Startup**
^^^^^^^^^^^^^^^^^^

Some systems have encountered problems with stray voltage being sent to the RS-485 device if this software
starts too soon after initial system boot. The symptom of this is flickering in the inverter. To reduce the risk of this happening, this software delays initializing
the serial interface for 30 seconds after boot time.
This delay can modified, please refer to source named magnum.py for details, or contact the author using :ref:`feedback`.
