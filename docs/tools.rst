.. _tools:

Available Tools
---------------

Tools will be added as they are developed. Currently the tools
available are:

magtest
=======

This tool is described in the installation instructions.

``magtest --help``

magdump
=======

This is a program that will dump a JSON string to the console for all
available devices. The default is to dump a string and exit. But if the
interval is set to a number, the program will dump a string every
``interval`` seconds

``magdump --help``

The regular options to set with this tool are:

.. code-block:: text

    -h, --help            show this help message and exit
    -d DEVICE, --device DEVICE
                          Serial device name (default: /dev/ttyUSB0)
    -i INTERVAL, --interval INTERVAL
                          Interval, in seconds, between dump records, in
                          seconds. 0 means once and exit. (default: 0)
    -v, --verbose         Display options at runtime (default: False)

   seldom used:
    --packets PACKETS     Number of packets to generate in reader (default: 50)
    --timeout TIMEOUT     Timeout for serial read (default: 0.005)
    --trace               Add most recent raw packet info to data (default: False)
    --nocleanup           Suppress clean up of unknown packets (default: False)

You can define more than one device. Just provide multiple ``--device /dev/ttyUSBX`` options when invoking the command.

Configuration (options) File
============================

The example programs and ``magdump`` support the use of an options file that is read instead of completing all the options on the command line.
For example, instead of ``magdump --device /dev/ttyUSB1 --interval 60``, these cound be included in an options file named, for example `pymagnum.opt` and the
command could be ``magdump @pymagnum.opt``. The `@` sign indicates the following is a file name and it read. There is an example in the `example` folder in GitHub.
It looks like this: (# denotes comments)

.. code-block:: text

    # Alter these to suit
    --device /dev/ttyUSB0
    --interval 60
    --packets 50
    --timeout 0.005
    # Remove # to enable the following
    #--verbose
    #--trace
    #--nocleanup

Copyright (c) 2018-2022 Charles Godwin magnum@godwin.ca

SPDX-License-Identifier: BSD-3-Clause
