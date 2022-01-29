#
# Copyright (c) 2018-2022 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# DO NOT SORT IMPORTS
#

import os
import sys
from collections import OrderedDict
from struct import error as unpack_error
from struct import unpack
from time import sleep

from uptime import uptime

# from magnum import magnum
# import magnum
from magnum import *
from magnum.aclddevice import ACLDDevice
from magnum.agsdevice import AGSDevice
from magnum.bmkdevice import BMKDevice
from magnum.inverterdevice import InverterDevice
from magnum.pt100device import PT100Device
from magnum.remotedevice import RemoteDevice
from magnum.rtrdevice import RTRDevice

# MAGNUM_DELAY can be defined in environment
# export MAGNUM_DELAY=nnn.nn

try:
    MAGNUM_DELAY = float(os.getenv('MAGNUM_DELAY', 30.0))
except:
    MAGNUM_DELAY = 30.0
# delay serial startup until system settles down - at least MAGNUM_DELAY seconds
delay = MAGNUM_DELAY - uptime()
if delay > 0.0:
    sleep(delay)
# This must be after the sleep(delay)
import serial  # noqa


class Magnum:
    '''
    :param device: The serial device to connect to, defaults to /dev/ttyUSB0
    :type device: str, optional
    :param packets: How many packets to capture in one sample, defaults to 50
    :type packets: int, optional
    :param cleanpackets: Allow system to try to fixup adjacent packets by merging them, defaults to True
    :type cleanpackets: boolean, optional
    :param timeout: How much time delay, in fractions of second,  to trigger end of packet, defaults to 0.001 second
    :type timeout: float, optional
    :param trace: Enable adding last of every packet type processed. The packets, as HEX strings, are appended to data object, Defaults to False
    :type trace: boolean, optional
    '''

    sevenzeros = bytes([0, 0, 0, 0, 0, 0, 0])
    #
    # refer to struct.unpack for format description
    #
    default_remote = 'BBBBBbBBBBBBBB'
    unpackFormats = {
        AGS_A1: 'BbBbBB',
        AGS_A2: 'BBBHB',
        BMK_81: 'BbHhHHhHHBB',
        INV:   'BBhhBBBBBBBBBBBBhb',
        INV_C: "BBhhBBBBBBBBBB",  # old style inverter
        PT_C1: 'BBBBHhHBBBBBB',
        PT_C2: 'BBHHBBBBBBB',
        PT_C3: '15B',  # double check documentation
        REMOTE_C:  default_remote + 'BB',  # old style remote
        REMOTE_00: default_remote + '7B',
        REMOTE_11: default_remote + '7B',  # just the first 2 bytes count
        REMOTE_80: default_remote + 'bbbb3B',
        REMOTE_A0: default_remote + 'BBBbBBB',
        REMOTE_A1: default_remote + '7B',
        REMOTE_A2: default_remote + 'bb5B',
        REMOTE_A3: default_remote + '7B',
        REMOTE_A4: default_remote + '7B',
        REMOTE_C0: default_remote + '7B',  # PT100  not used
        REMOTE_C1: default_remote + '7B',  # PT100  not used
        REMOTE_C2: default_remote + '7B',  # PT100  not used
        REMOTE_C3: default_remote + '7B',  # PT100  not used
        REMOTE_D0: default_remote + '7B',  # ACLD Needs work
        ACLD_D1: '7B',                    # ACLD Needs work
        RTR_91: 'BB',
        UNKNOWN: ''
    }

    def __init__(self, device="/dev/ttyUSB0", timeout=0.005, packets=50, cleanpackets=True, trace=False, flip=False):
        self.packetcount = packets
        self.timeout = timeout
        self.cleanpackets = cleanpackets
        self.trace = trace
        self.comm_device = device
        self.flip = flip
        self.reader = None
        self.inverter = None
        self.remote = None
        self.bmk = None
        self.ags = None
        self.rtr = None
        self.pt100 = None
        self.acld = None
        self.inverter_revision = -1
        self.inverter_model = -1
        if device[0:1] == '!':
            self.stored_packets = self._load_packets(device[1:])
        else:
            self.stored_packets = None
        return
    def getComm_Device(self):
        return self.comm_device

    def _load_packets(self, filename):
        ix = filename.find('!')
        if ix > 0:
            self.comm_device = filename[0:ix]
            filename = filename[ix+1:]
        else:
            self.comm_device = filename
        packets = []
        with open(filename) as file:
            lines = file.readlines()
        for line in lines:
            ix = line.find("=>")
            decode = line.find("decode:")
            if ix >= 0:
                decode = line.find("decode:")  # supports traced packets
                if decode > ix:
                    stop = decode
                else:
                    stop = len(line)
                data = bytes.fromhex(line[ix+2:stop].strip())
                packets.append(data)
        if len(packets) == 0:
            raise ValueError(f"There were no valid records in {filename}")
        return packets
    #
    # returns a list of tuples of {message type, bytes of packet, and tuple of {unpacked packet values)}
    #

    def getPackets(self):
        '''
        Retrieves the raw packets. This is not normally used.

        :return: List of `tuple` objects
        :rtype: list

        **tuple contents**:

        - name of packet
        - bytes of packet
        - tuple of unpacked values - Based on ME documentation
        '''
        packets = self.readPackets()
        messages = []
        unknown = 0
        for packet in packets:
            message = self._parsePacket(packet)
            if message[0] == UNKNOWN:
                unknown += 1
            messages.append(message)
        #
        # if there at least 2 UNKNOWN packets
        # attempt to clean them up
        #
        if unknown > 1 and self.cleanpackets:
            messages = self.cleanup(messages)
        return messages
        #

    #  raw read of packets to bytes[]
    #  This can be overridden for tests
    #

    def readPackets(self):
        packet = bytearray()
        packets = []
        if self.stored_packets != None:
            for ix in range(self.packetcount):
                packet = self.stored_packets.pop()
                packets.append(packet)
                self.stored_packets.append(packet)
            return packets
        if self.reader == None:
            self.reader = serial.serial_for_url(self.comm_device,
                                                baudrate=19200,
                                                bytesize=8,
                                                timeout=self.timeout,
                                                stopbits=serial.STOPBITS_ONE,
                                                dsrdtr=False,
                                                parity=serial.PARITY_NONE)
            self.reader.close()

        #
        # open port every time
        #
        self.reader.open()
        #
        # wait to see if there is any traffic on the device
        #
        sleep(0.25)
        if self.reader.inWaiting() == 0:
            self.reader.close()
            self.reader = None
            raise ConnectionError("There doesn't seem to be a network")
        packetsleft = self.packetcount
        self.reader.flushInput()
        #
        # Start of packet reads into a list of bytearray()
        # This is a tight loop
        #
        while packetsleft > 0:
            readbytes = self.reader.read(self.reader.in_waiting or 1)
            packet += readbytes
            #
            # assumes an empty read is an inter packet gap
            #
            if len(readbytes) == 0 and len(packet) != 0:
                packets.append(packet)
                packetsleft -= 1
                packet = bytearray()
        self.reader.close()
        return packets
    #
    #
    # based on what we know from ME documentation
    # attempt to build a known packet and unpack its data into values
    #

    def _parsePacket(self, packet):
        # Needs work
        if self.flip:
            pass
        if len(packet) == 22:
            packet = packet[:21]
        elif len(packet) == 17:  # takes care of classic
            packet = packet[:16]
        packetType = UNKNOWN
        if len(packet) > 0:
            packetLen = len(packet)
            firstbyte = packet[0]
            lastbyte = packet[-1]
            if packetLen == 2 and firstbyte == 0x91:
                packetType = RTR_91
            elif packetLen == 6:
                if firstbyte == 0xa1:
                    packetType = AGS_A1
                elif firstbyte == 0xa2:
                    packetType = AGS_A2
            elif packetLen == 8 and firstbyte == 0xD1:
                packetType = ACLD_D1
            elif packetLen == 13 and firstbyte == 0xC2:
                packetType = PT_C2
            elif packetLen == 14 and firstbyte == 0xC3:
                packetType = PT_C3
            elif packetLen == 16:
                if firstbyte == 0xC1:
                    packetType = PT_C1
                elif packet[10] <= 0x27 and packet[14] in InverterDevice.inverter_models:
                    packetType = INV_C
                    if self.inverter_revision == -1:
                        self.inverter_revision = packet[10]
                        self.inverter_model = packet[14]
                else:
                    packetType = REMOTE_C
            elif packetLen == 18 and firstbyte == 0x81:
                packetType = BMK_81
            elif packetLen == 21:
                version = packet[10]
                model = packet[14]
                if lastbyte == 0 and firstbyte == 0:
                    #
                    #  There is an undocumented Remote message generated with seven 0x00 bytes at the end.
                    #  This code distinguishes it from a Inverter record with status byte 0 == 0x0
                    #
                    #  Also the ME-ARC sends a spurious record with a zero end byte
                    #
                    if packet[-7:] == self.sevenzeros:
                        packetType = REMOTE_00
                    else:
                        if version == (self.inverter_revision and model == self.inverter_model) or self.inverter_revision == -1:
                            packetType = INV
                        else:
                            packetType = REMOTE_00
                else:
                    if lastbyte == 0:
                        if (version == self.inverter_revision and model == self.inverter_model) or self.inverter_revision == -1:
                            if model in InverterDevice.inverter_models:
                                packetType = INV
                                if self.inverter_revision == -1:
                                    self.inverter_revision = version
                                    self.inverter_model = model
                        else:
                            packetType = REMOTE_00
                    elif lastbyte == 0xa0:
                        packetType = REMOTE_A0
                    elif lastbyte == 0xa1:
                        packetType = REMOTE_A1
                    elif lastbyte == 0xa2:
                        packetType = REMOTE_A2
                    elif lastbyte == 0xa3:
                        packetType = REMOTE_A3
                    elif lastbyte == 0xa4:
                        packetType = REMOTE_A4
                    elif lastbyte == 0x80:
                        packetType = REMOTE_80
                    elif lastbyte == 0xC0:
                        packetType = REMOTE_C0
                    elif lastbyte == 0xC1:
                        packetType = REMOTE_C1
                    elif lastbyte == 0xC2:
                        packetType = REMOTE_C2
                    elif lastbyte == 0xC3:
                        packetType = REMOTE_C3
                    elif lastbyte == 0x11:
                        packetType = REMOTE_11
                    elif lastbyte == 0xD0:
                        packetType = REMOTE_D0
            #
            # Unpack as big endian
            # Refer to unpackFormats
            #
            mask = ">" + self.unpackFormats[packetType]
            if len(mask) > 1:
                try:
                    fields = unpack(mask, packet)
                except Exception as e:
                    msg = "{0} Converting {1} - {2} bytes".format(
                        e.args[0], packetType, len(packet))
                    fields = {}
                    print(msg)
                    packetType = UNKNOWN
                    # raise unpack_error(msg) from e
            else:
                fields = {}
            return([packetType, packet, fields, self.unpackFormats[packetType]])

    #
    # cleanup looks for consecutive UNKNOWN packet pairs and concatenates the pair
    # and attempts to parse the result. It has reasonable success.
    #
    def cleanup(self, messages):
        cleaned = []
        lastone = len(messages) - 2
        ignoreit = False
        for index, message in enumerate(messages):
            if ignoreit:
                ignoreit = False
            elif index > lastone or message[0] != UNKNOWN:
                ignoreit = False
                cleaned.append(message)
            else:
                nextmessage = messages[index + 1]
                if nextmessage[0] == UNKNOWN:
                    # we may have a match
                    newmessage = self._parsePacket(message[1] + nextmessage[1])
                    ignoreit = True
                    cleaned.append(newmessage)
        return cleaned
    #
    #     returns an array of device ordered dictionary
    #
    #  Each class is instantiated only once per run time execution
    #  This allows an object to reflect the latest CUMULATIVE value for the packets.
    #  This is useful for PT100 and AGS packets which are not too numerous
    #
    #  returns a deepcopy of the device data collections
    #

    def getDevices(self):
        '''
        Get a list of connected devices

        :return: List of device dictionaries
        :rtype: list

        Each dictionary has two or, optionally, three items:

        - **device**  One of INVERTER, REMOTE, AGS, BMK or PT100
        - **data** A dictionary of name/value pairs for the device.
        - **trace** If trace is set to True then trace will have a list of tupples of every packet since last time invoked
        '''
        # pass each the packets to the correct object
        #
        # each packet is a tuple of:
        #     type(string) name of packet
        #     raw packet (bytes) the raw binary bytes of the packet
        #     unpacked data (tuple int) integers of data deconstructed to match ME documentation
        #
        for packet in self.getPackets():
            packetType = packet[0]
            if packetType in (INV, INV_C):
                if self.inverter == None:
                    self.inverter = InverterDevice(trace=self.trace)
                self.inverter.parse(packet)
            elif packetType in (REMOTE_C,
                                REMOTE_00,
                                REMOTE_11,
                                REMOTE_80,
                                REMOTE_A0,
                                REMOTE_A1,
                                REMOTE_A2,
                                REMOTE_A3,
                                REMOTE_A4,
                                REMOTE_C0,
                                REMOTE_C1,
                                REMOTE_C2,
                                REMOTE_C3,
                                REMOTE_D0):
                if self.remote == None:
                    self.remote = RemoteDevice(trace=self.trace)
                self.remote.parse(packet)
            elif packetType == BMK_81:
                if self.bmk == None:
                    self.bmk = BMKDevice(trace=self.trace)
                self.bmk.parse(packet)
            elif packetType in (AGS_A1, AGS_A2):
                if self.ags == None:
                    self.ags = AGSDevice(trace=self.trace)
                self.ags.parse(packet)
            elif packetType == RTR_91:
                if self.rtr == None:
                    self.rtr = RTRDevice(trace=self.trace)
                self.rtr.parse(packet)
            elif packetType in (PT_C1, PT_C2, PT_C3):
                if self.pt100 == None:
                    self.pt100 = PT100Device(trace=self.trace)
                self.pt100.parse(packet)
            elif packetType == ACLD_D1:
                if self.acld == None:
                    self.acld = ACLDDevice(trace=self.trace)
                self.rtr.parse(packet)
        if self.remote:
            #
            # remove extraneous REMOTE fields if corresponding device is not present
            #
            self.remote.cleanup(self.bmk, self.ags, self.pt100)
        devices = []
        for device in [self.inverter, self.remote, self.bmk, self.ags, self.rtr, self.pt100, self.acld]:
            if device:
                deviceinfo = device.getDevice()
                if deviceinfo:
                    devices.append(deviceinfo)
        return devices
