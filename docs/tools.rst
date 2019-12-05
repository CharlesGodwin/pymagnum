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

::

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
    --trace               Add most recent raw packet info to data (default:
                          False)
    -nc, --nocleanup      Suppress clean up of unknown packets (default: True)

Copyright (c) 2018-2019 Charles Godwin magnum@godwin.ca

SPDX-License-Identifier: BSD-3-Clause
