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
        Increase this size if you want a better analysis of the packets. Decrease to improve rsponse time but don't make it too small or you will get incomplete data.

    :param boolean cleanpackets:
        Allow object to try to fixup two adjacent :const:`UNKNOWN` packets by merging them, defaults to :const:`True`

    :param float timeout:
        How much time delay, in fractions of second,  to trigger end of packet, defaults to 0.001 second

    :param boolean trace:
        Enable adding last of every packet type processed. The packets, as HEX strings, are appended to to data object, Defaults to :const:`False`

.. method:: getDevices()

    Get a list of connected devices

    :return: List of device dictionaries

        Each dictionary has two items:

        - **device** - One of :const:`INVERTER`, :const:`REMOTE`, :const:`AGS`, :const:`BMK` or :const:`PT100`
        - **data** - A dictionary of name/value pairs for the fields in the device.

.. method:: getPackets()

    Retrieves the raw packets from the network. This is not normally used.

    :return: List of `tupple` objects

        **tupple contents**:

        - name of packet
        - bytes of packet
        - tupple of unpacked values for fields in packet - Based on ME documentation

Copyright (c) 2018-2019 Charles Godwin magnum@godwin.ca

SPDX-License-Identifier: BSD-3-Clause
