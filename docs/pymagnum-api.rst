============
pyMagnum API
============

.. module:: magnum

.. class:: Magnum

    This class handles all intercommunications with the network

.. method:: __init__(device='/dev/ttyUSB0', timeout=0.001, packets=50, cleanpackets=True, trace=False)

    :param device:
        The serial device to connect to, defaults to `/dev/ttyUSB0`

    :param int packets:
        How many packets to capture in one sample, defaults to 50.
        Increase this size if you want a better analysis of the packets. Decrease to improve response time but don't make it too small or you will get incomplete data.

    :param boolean cleanpackets:
        Allow object to try to fixup two adjacent :const:`UNKNOWN` packets by merging them, defaults to :const:`True`

    :param float timeout:
        How much time delay, in fractions of second,  to trigger end of packet, defaults to 0.001 second

    :param boolean trace:
        Enable adding a list of every packet processed since last getDevices(). The trace, is added to the "trace" dictionary item as a list of packet type and HEX of packet pairs, Defaults to :const:`False`

.. method:: getDevices()

    Get a list of connected devices

    :return: List of device dictionaries

          Each dictionary has two or, optionally, three items:

        - **device** - One of :const:`INVERTER`, :const:`REMOTE`, :const:`AGS`, :const:`BMK`, :const:`RTR`, :const:`ACLD` or :const:`PT100`
        - **data** - A dictionary of name/value pairs for the fields in the device.
        - **trace** - If trace is set to True then trace will have a list of tuples of every packet since last time invoked

.. method:: getPackets()

    Retrieves the raw packets from the network. This is not normally used.

    :return: List of `tuple` objects

        **tuple contents**:

        - name of packet
        - bytes of packet
        - tuple of unpacked values for fields in packet - Based on ME documentation

Copyright (c) 2018-2022 Charles Godwin magnum@godwin.ca

SPDX-License-Identifier: BSD-3-Clause
