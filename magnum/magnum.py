#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
import time
from collections import OrderedDict
from struct import calcsize
from struct import error as unpack_error
from struct import unpack

import serial

UNKNOWN = "UNKNOWN"
INVERTER = "INVERTER"
AGS = "AGS"
REMOTE = "REMOTE"
BMK = "BMK"
PT100 = "PT100"
RTR = "RTR"

AGS_A1 = "AGS_A1"
AGS_A2 = "AGS_A2"
BMK_81 = "BMK_81"
INV = "INVERTER"
PT_C1 = "PT_C1"
PT_C2 = "PT_C2"
PT_C3 = "PT_C3"
PT_C4 = "PT_C4"
REMOTE_00 = "REMOTE_00"
REMOTE_11 = "REMOTE_11"
REMOTE_80 = "REMOTE_80"
REMOTE_A0 = "REMOTE_A0"
REMOTE_A1 = "REMOTE_A1"
REMOTE_A2 = "REMOTE_A2"
REMOTE_A3 = "REMOTE_A3"
REMOTE_A4 = "REMOTE_A4"
REMOTE_C0 = "REMOTE_C0"
REMOTE_C1 = "REMOTE_C1"
REMOTE_C2 = "REMOTE_C2"
REMOTE_C3 = "REMOTE_C3"
REMOTE_D0 = "REMOTE_D0"
RTR_91 = "RTR_91"
sevenzeros = bytes([0, 0, 0, 0, 0, 0, 0])
#
# refer to struct.unpack for format description
#
default_remote = 'BBBBBbBBBBBBBB'
formats = {
    AGS_A1: 'BbBbBB',
    AGS_A2: 'BBBHB',
    BMK_81:  'BbHhHHhHHBB',
    INV: 'BBhhBBbbBBBBBBBBhb',
    PT_C1: 'BbBBHhhbbbbbb',
    PT_C2: 'BbBHBbBBBB',
    PT_C3: 'BH11B',
    PT_C4: '7B',
    REMOTE_00: default_remote + '7B',
    REMOTE_11: default_remote + '7B',  # just the first 2 bytes count
    REMOTE_80: default_remote + 'bbbb3B',
    REMOTE_A0: default_remote + 'BBBbBBB',
    REMOTE_A1: default_remote + '7B',
    REMOTE_A2: default_remote + 'bb5B',
    REMOTE_A3: default_remote + '7B',
    REMOTE_A4: default_remote + '7B',
    REMOTE_C0: default_remote + 'bbbbHB',
    REMOTE_C1: default_remote + 'BBbbbbB',
    REMOTE_C2: default_remote + 'BBbbBbB',
    REMOTE_C3: default_remote + 'BBBBBbB',
    REMOTE_D0: default_remote + '7B',
    RTR_91: 'BB',
    UNKNOWN: ''
}

class Magnum:
    multiplier = 1
    def __init__(self, device="/dev/ttyUSB0", timeout=0.001, packets=50, id=None, cleanpackets=True):
        self.packetcount = packets
        self.timeout = timeout
        self.id = id
        self.cleanpackets = cleanpackets
        self.reader = serial.serial_for_url(device,
                                            baudrate=19200,
                                            bytesize=8,
                                            timeout=timeout,
                                            stopbits=serial.STOPBITS_ONE,
                                            dsrdtr=False,
                                            parity=serial.PARITY_NONE)
        self.reader.close()
        self.inverter = None
        self.remote = None
        self.bmk = None
        self.ags = None
        self.rtr = None
        self.pt100 = None
        self.inverter_revision = -1
        self.inverter_model = -1
    #
    # returns a list of tupples of message type, bytes of packet, and unpacked packet values
    #

    def getPackets(self):
        packet = bytearray()
        packets = []
        self.reader.open()
        time.sleep(0.25)
        if self.reader.inWaiting() == 0:
            raise ConnectionError("There doesn't seem to be a network")
        packetsleft = self.packetcount
        self.reader.flushInput()
        #
        # Start of packet reads
        # This is a tight loop
        #
        while packetsleft > 0:
            readbytes = self.reader.read(self.reader.in_waiting or 1)
            packet += readbytes
            if len(readbytes) == 0 and len(packet) != 0:
                packets.append(packet)
                packetsleft -= 1
                packet = bytearray()
        self.reader.close()
        #
        # end of packet reads
        #
        messages = []
        unknown = 0
        for packet in packets:
            message = self.parsePacket(packet)
            if message[0] == UNKNOWN:
                unknown += 1
            messages.append(message)
        if unknown > 1 and self.cleanpackets:
            messages = self.cleanup(messages)
        return messages

    def parsePacket(self, packet):
        if len(packet) == 22:
            packet = packet[:21]
        packetType = UNKNOWN
        if len(packet) > 0:
            packetLen = len(packet)
            firstbyte = packet[0]
            lastbyte = packet[-1]
            if packetLen == 2:
                if firstbyte == 0x91:
                    packetType = RTR_91
            elif packetLen == 6:
                if firstbyte == 0xa1:
                    packetType = AGS_A1
                elif firstbyte == 0xa2:
                    packetType = AGS_A2
            elif packetLen == 8:
                if firstbyte == 0xC4:
                    packetType = PT_C4
            elif packetLen == 13:
                if firstbyte == 0xC2:
                    packetType = PT_C2
            elif packetLen == 14:
                if firstbyte == 0xC3:
                    packetType = PT_C3
            elif packetLen == 16:
                if firstbyte == 0xC1:
                    packetType = PT_C1
            elif packetLen == 18:
                if firstbyte == 0x81:
                    packetType = BMK_81
            elif packetLen == 21:
                version = packet[10]
                model = packet[14]
                if lastbyte == 0 and firstbyte == 0:
                    #
                    #  There is an undocumented Remote message generated with seven 0x00 bytes at
                    #  the end. This code distinguishes it from a Inverter record with status byte 0  = 0x00

                    #  Also the ME-ARC sends a spurious record with a zero end byte
                    #

                    if packet[:14] == sevenzeros:
                        packetType = REMOTE_00
                    else:
                        if version == (self.inverter_revision and model == self.inverter_model) or self.inverter_revision == -1:
                            packetType = INV
                        else:
                            packetType = REMOTE_00
                else:
                    if lastbyte == 0:
                        if version == (self.inverter_revision and model == self.inverter_model) or self.inverter_revision == -1:
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
            mask = ">" + formats[packetType]
            if len(mask) > 1:
                try:
                    fields = unpack(mask, packet)
                except Exception as e:
                    msg = "{0} Converting {1} - {2} bytes".format(
                        e.args[0], packetType, len(packet))
                    raise unpack_error(msg) from e
            else:
                fields = {}
            return([packetType, packet, fields])

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
                    newmessage = self.parsePacket(message[1] + nextmessage[1])
                    ignoreit = True
                    cleaned.append(newmessage)
        return cleaned
    #
    #     returns an array of device orderded dictionary
    #

    def getModels(self, packets=None):
        workpackets = packets if packets else self.getPackets()
        for packet in workpackets:
            packetType = packet[0]
            if packetType == INV:
                if self.inverter == None:
                    self.inverter = InverterDevice(id=self.id)
                self.inverter.parse(packet)
            elif packetType in (REMOTE_00, REMOTE_11, REMOTE_80, REMOTE_A0, REMOTE_A1, REMOTE_A2, REMOTE_A3, REMOTE_A4, REMOTE_C0, REMOTE_C1, REMOTE_C2, REMOTE_C3, REMOTE_D0):
                if self.remote == None:
                    self.remote = RemoteDevice(id=self.id)
                self.remote.parse(packet)
            elif packetType == BMK_81:
                if self.bmk == None:
                    self.bmk = BMKDevice(id=self.id)
                self.bmk.parse(packet)
            elif packetType in (AGS_A1, AGS_A2):
                if self.ags == None:
                    self.ags = AGSDevice(id=self.id)
                self.ags.parse(packet)
            elif packetType == RTR_91:
                if self.rtr == None:
                    self.rtr = RTRDevice(id=self.id)
                self.rtr.parse(packet)
            elif packetType in (PT_C1, PT_C2, PT_C3, PT_C4):
                if self.pt100 == None:
                    self.pt100 = PT100Device(id=self.id)
                self.pt100.parse(packet)
        if self.remote:
            if self.bmk == None:
                self.remote.removeBMK()
            if self.ags == None:
                self.remote.removeAGS()
            if self.pt100 == None:
                self.remote.removePT100()
        models = []
        for model in [self.inverter, self.remote, self.bmk, self.ags, self.rtr, self.pt100]:
            if model:
                modeldict = model.getModel()
                if modeldict:
                    models.append(modeldict)
        return models

#
# All the device classes
#

class AGSDevice:

    def __init__(self, id=None):

        self.data = OrderedDict()
        self.model = OrderedDict()
        self.model["model"] = AGS
        if id:
            self.model["id"] = str(id)
        self.model["data"] = self.data
        self.data["revision"] = 0.0
        self.data["status"] = 0
        self.data["status_text"] = ""
        self.data["running"] = False
        self.data["temp"] = 0
        self.data["runtime"] = 0
        self.data["gen_last_run"] = 0
        self.data["last_full_soc"] = 0
        self.data["gen_total_run"] = 0
        self.data["vdc"] = 0

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if packetType == AGS_A1:
            self.data["status"] = unpacked[1]
            self.data["revision"] = str(round(unpacked[2] / 10, 1))
            self.data["temp"] = unpacked[3]
            if self.data["temp"] < 105:
                self.data["temp"] = round((self.data["temp"] - 32) * 5 / 9, 1)
            self.data["runtime"] = round(unpacked[4] / 10, 2)
            self.setStatusText()
            self.data["vdc"] = round(unpacked[5] / 10 * Magnum.multiplier, 2)
            self.setRunning()
        elif packetType == AGS_A2:
            self.data["gen_last_run"] = unpacked[1]
            self.data["last_full_soc"] = unpacked[2]
            self.data["gen_total_run"] = unpacked[3]

    def setRunning(self):
        if self.data["status"] in (3, 6, 7, 8, 12, 13, 14, 18, 19, 26, 2):
            self.data["running"] = True
        else:
            self.data["running"] = False

    def setStatusText(self):
        if self.data["status"] == 0:
            self.data["status_text"] = "Not Connected"
        elif self.data["status"] == 1:
            self.data["status_text"] = "Off"
        elif self.data["status"] == 2:
            self.data["status_text"] = "Ready"
        elif self.data["status"] == 3:
            self.data["status_text"] = "Manual Run"
        elif self.data["status"] == 4:
            self.data["status_text"] = "AC In"
        elif self.data["status"] == 5:
            self.data["status_text"] = "In quiet time"
        elif self.data["status"] == 6:
            self.data["status_text"] = "Start in test mode"
        elif self.data["status"] == 7:
            self.data["status_text"] = "Start on temperature"
        elif self.data["status"] == 8:
            self.data["status_text"] = "Start on voltage"
        elif self.data["status"] == 9:
            self.data["status_text"] = "Fault start on test"
        elif self.data["status"] == 10:
            self.data["status_text"] = "Fault start on temp"
        elif self.data["status"] == 11:
            self.data["status_text"] = "Fault start on voltage"
        elif self.data["status"] == 12:
            self.data["status_text"] = "Start TOD"
        elif self.data["status"] == 13:
            self.data["status_text"] = "Start SOC"
        elif self.data["status"] == 14:
            self.data["status_text"] = "Start Exercise"
        elif self.data["status"] == 15:
            self.data["status_text"] = "Fault start TOD"
        elif self.data["status"] == 16:
            self.data["status_text"] = "Fault start SOC"
        elif self.data["status"] == 17:
            self.data["status_text"] = "Fault start Exercise"
        elif self.data["status"] == 18:
            self.data["status_text"] = "Start on Amp"
        elif self.data["status"] == 19:
            self.data["status_text"] = "Start on Topoff"
        elif self.data["status"] == 20:
            self.data["status_text"] = "Not used"
        elif self.data["status"] == 21:
            self.data["status_text"] = "Fault start on Amp"
        elif self.data["status"] == 22:
            self.data["status_text"] = "Fault on Topoff"
        elif self.data["status"] == 23:
            self.data["status_text"] = "Not used"
        elif self.data["status"] == 24:
            self.data["status_text"] = "Fault max run"
        elif self.data["status"] == 25:
            self.data["status_text"] = "Gen Run Fault"
        elif self.data["status"] == 26:
            self.data["status_text"] = "Gen in Warm up"
        elif self.data["status"] == 27:
            self.data["status_text"] = "Gen in Cool down"

    def getModel(self):
        return self.model

class BMKDevice:
    def __init__(self, id=None):

        self.data = OrderedDict()
        self.model = OrderedDict()
        self.model["model"] = BMK
        if id:
            self.model["id"] = str(id)
        self.model["data"] = self.data
        self.data["revision"] = ""
        self.data["soc"] = 0
        self.data["vdc"] = 0
        self.data["adc"] = 0
        self.data["vmin"] = 0
        self.data["vmax"] = 0
        self.data["amph"] = 0
        self.data["amphtrip"] = 0
        self.data["amphout"] = 0
        self.data["Fault"] = 0
        self.data["Fault_Text"] = ""

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if packetType == BMK_81:
            self.data["soc"] = unpacked[1]
            self.data["vdc"] = round(unpacked[2] / 100, 2)
            self.data["adc"] = round(unpacked[3] / 10, 2)
            self.data["vmin"] = round(unpacked[4] / 100, 2)
            self.data["vmax"] = round(unpacked[5] / 100, 2)
            self.data["amph"] = unpacked[6]
            self.data["amphtrip"] = round(unpacked[7] / 10, 2)
            self.data["amphout"] = round(unpacked[8] * 100, 2)
            self.data["revision"] = str(round(unpacked[9] / 10, 2))
            self.data["Fault"] = unpacked[10]
            if self.data["Fault"] == 0:
                self.data["Fault_Text"] = "Reserved"
            elif self.data["Fault"] == 1:
                self.data["Fault_Text"] = "Normal"
            elif self.data["Fault"] == 2:
                self.data["Fault_Text"] = "Fault Start"

    def getModel(self):
        return self.model

class InverterDevice:
    def __init__(self, id=None):
        self.data = OrderedDict()
        self.model = OrderedDict()
        self.model["model"] = INVERTER
        if id:
            self.model["id"] = str(id)
        self.model["data"] = self.data
        self.data["revision"] = str(0.0)
        self.data["mode"] = 0
        self.data["mode_text"] = ""
        self.data["fault"] = 0
        self.data["fault_text"] = ""
        self.data["vdc"] = 0
        self.data["adc"] = 0
        self.data["VACout"] = 0
        self.data["VACin"] = 0
        self.data["invled"] = 0
        self.data["invled_text"] = ""
        self.data["chgled"] = 0
        self.data["chgled_text"] = ""
        self.data["bat"] = 0
        self.data["tfmr"] = 0
        self.data["fet"] = 0
        self.data["model"] = 0
        self.data["model_text"] = ""
        self.data["stackmode"] = 0
        self.data["stackmode_text"] = ""
        self.data["AACin"] = 0
        self.data["AACout"] = 0
        self.data["Hz"] = 0.0

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if packetType == INV:
            self.data["mode"] = unpacked[0]
            self.data["fault"] = unpacked[1]
            self.data["vdc"] = unpacked[2] / 10
            self.data["adc"] = unpacked[3]
            self.data["VACout"] = unpacked[4]
            self.data["VACin"] = unpacked[5]
            self.data["invled"] = unpacked[6]
            self.data["chgled"] = unpacked[7]
            self.data["revision"] = str(round(unpacked[8] / 10, 2))
            self.data["bat"] = unpacked[9]
            self.data["tfmr"] = unpacked[10]
            self.data["fet"] = unpacked[11]
            self.data["model"] = unpacked[12]
            self.data["stackmode"] = unpacked[13]
            self.data["AACin"] = unpacked[14]
            self.data["AACout"] = unpacked[15]
            self.data["Hz"] = round(unpacked[16] / 10, 2)
        #
        #    (Model <= 50) means 12V inverter
        #    (Model <= 107) means 24V inverter
        # 	 (Model < 150) means 48V inverter
        #
            if self.data["model"] <= 50:
                # voltage = 12
                Magnum.multiplier = 1
            elif self.data["model"] <= 107:
                # voltage = 24
                Magnum.multiplier = 2
            elif self.data["model"] <= 150:
                # voltage = 48
                Magnum.multiplier = 4
            self.set_fault_text()
            self.set_chgled_text()
            self.set_invled_text()
            self.set_mode_text()
            self.set_model_text()
            self.set_stackmode_text()

    def set_fault_text(self):
        if self.data["fault"] == 0x00:
            self.data["fault_text"] = "None"
        elif self.data["fault"] == 0x01:
            self.data["fault_text"] = "STUCK RELAY"
        elif self.data["fault"] == 0x02:
            self.data["fault_text"] = "DC OVERLOAD"
        elif self.data["fault"] == 0x03:
            self.data["fault_text"] = "AC OVERLOAD"
        elif self.data["fault"] == 0x04:
            self.data["fault_text"] = "DEAD BAT"
        elif self.data["fault"] == 0x05:
            self.data["fault_text"] = "BACKFEED"
        elif self.data["fault"] == 0x08:
            self.data["fault_text"] = "LOW BAT"
        elif self.data["fault"] == 0x09:
            self.data["fault_text"] = "HIGH BAT"
        elif self.data["fault"] == 0x0A:
            self.data["fault_text"] = "HIGH AC VOLTS"
        elif self.data["fault"] == 0x10:
            self.data["fault_text"] = "BAD_BRIDGE"
        elif self.data["fault"] == 0x12:
            self.data["fault_text"] = "NTC_FAULT"
        elif self.data["fault"] == 0x13:
            self.data["fault_text"] = "FET_OVERLOAD"
        elif self.data["fault"] == 0x14:
            self.data["fault_text"] = "INTERNAL_FAULT4"
        elif self.data["fault"] == 0x16:
            self.data["fault_text"] = "STACKER MODE FAULT"
        elif self.data["fault"] == 0x18:
            self.data["fault_text"] = "STACKER CLK PH FAULT"
        elif self.data["fault"] == 0x17:
            self.data["fault_text"] = "STACKER NO CLK FAULT"
        elif self.data["fault"] == 0x19:
            self.data["fault_text"] = "STACKER PH LOSS FAULT"
        elif self.data["fault"] == 0x20:
            self.data["fault_text"] = "OVER TEMP"
        elif self.data["fault"] == 0x21:
            self.data["fault_text"] = "RELAY FAULT"
        elif self.data["fault"] == 0x80:
            self.data["fault_text"] = "CHARGER_FAULT"
        elif self.data["fault"] == 0x81:
            self.data["fault_text"] = "High Battery Temp"
        elif self.data["fault"] == 0x90:
            self.data["fault_text"] = "OPEN SELCO TCO"
        elif self.data["fault"] == 0x91:
            self.data["fault_text"] = "CB3 OPEN FAULT"

    def set_chgled_text(self):
        if self.data["chgled"] == 0:
            self.data["chgled_text"] = "Off"
        else:
            self.data["chgled_text"] = "On"

    def set_invled_text(self):
        if self.data["invled"] == 0:
            self.data["invled_text"] = "Off"
        else:
            self.data["invled_text"] = "On"

    def set_mode_text(self):
        if self.data["mode"] == 0x00:
            self.data["mode_text"] = "Standby"
        elif self.data["mode"] == 0x01:
            self.data["mode_text"] = "EQ"
        elif self.data["mode"] == 0x02:
            self.data["mode_text"] = "FLOAT"
        elif self.data["mode"] == 0x04:
            self.data["mode_text"] = "ABSORB"
        elif self.data["mode"] == 0x08:
            self.data["mode_text"] = "BULK"
        elif self.data["mode"] == 0x09:
            self.data["mode_text"] = "BATSAVER"
        elif self.data["mode"] == 0x10:
            self.data["mode_text"] = "CHARGE"
        elif self.data["mode"] == 0x20:
            self.data["mode_text"] = "Off"
        elif self.data["mode"] == 0x40:
            self.data["mode_text"] = "INVERT"
        elif self.data["mode"] == 0x50:
            self.data["mode_text"] = "Inverter_Standby"
        elif self.data["mode"] == 0x80:
            self.data["mode_text"] = "SEARCH"
        else:
            self.data["mode_text"] = "??"

    def set_model_text(self):
        if self.data["model"] == 6:
            self.data["model_text"] = "MM612"
        elif self.data["model"] == 7:
            self.data["model_text"] = "MM612-AE"
        elif self.data["model"] == 8:
            self.data["model_text"] = "MM1212"
        elif self.data["model"] == 9:
            self.data["model_text"] = "MMS1012"
        elif self.data["model"] == 10:
            self.data["model_text"] = "MM1012E"
        elif self.data["model"] == 11:
            self.data["model_text"] = "MM1512"
        elif self.data["model"] == 12:
            self.data["model_text"] = "MMS912E"
        elif self.data["model"] == 15:
            self.data["model_text"] = "ME1512"
        elif self.data["model"] == 20:
            self.data["model_text"] = "ME2012"
        elif self.data["model"] == 21:
            self.data["model_text"] = "RD2212"
        elif self.data["model"] == 25:
            self.data["model_text"] = "ME2512"
        elif self.data["model"] == 30:
            self.data["model_text"] = "ME3112"
        elif self.data["model"] == 35:
            self.data["model_text"] = "MS2012"
        elif self.data["model"] == 36:
            self.data["model_text"] = "MS1512E"
        elif self.data["model"] == 40:
            self.data["model_text"] = "MS2012E"
        elif self.data["model"] == 44:
            self.data["model_text"] = "MSH3012M"
        elif self.data["model"] == 45:
            self.data["model_text"] = "MS2812"
        elif self.data["model"] == 47:
            self.data["model_text"] = "MS2712E"
        elif self.data["model"] == 53:
            self.data["model_text"] = "MM1324E"
        elif self.data["model"] == 54:
            self.data["model_text"] = "MM1524"
        elif self.data["model"] == 55:
            self.data["model_text"] = "RD1824"
        elif self.data["model"] == 59:
            self.data["model_text"] = "RD2624E"
        elif self.data["model"] == 63:
            self.data["model_text"] = "RD2824"
        elif self.data["model"] == 69:
            self.data["model_text"] = "RD4024E"
        elif self.data["model"] == 74:
            self.data["model_text"] = "RD3924"
        elif self.data["model"] == 90:
            self.data["model_text"] = "MS4124E"
        elif self.data["model"] == 91:
            self.data["model_text"] = "MS2024"
        elif self.data["model"] == 103:
            self.data["model_text"] = "MSH4024M"
        elif self.data["model"] == 104:
            self.data["model_text"] = "MSH4024RE"
        elif self.data["model"] == 105:
            self.data["model_text"] = "MS4024"
        elif self.data["model"] == 106:
            self.data["model_text"] = "MS4024AE"
        elif self.data["model"] == 107:
            self.data["model_text"] = "MS4024PAE"
        elif self.data["model"] == 111:
            self.data["model_text"] = "MS4448AE"
        elif self.data["model"] == 112:
            self.data["model_text"] = "MS3748AEJ"
        elif self.data["model"] == 114:
            self.data["model_text"] = "MS4048"
        elif self.data["model"] == 115:
            self.data["model_text"] = "MS4448PAE"
        elif self.data["model"] == 116:
            self.data["model_text"] = "MS3748PAEJ"
        elif self.data["model"] == 117:
            self.data["model_text"] = "MS4348PE"
        else:
            self.data["model_text"] = "Unknown"

    def set_stackmode_text(self):
        if self.data["stackmode"] == 0x00:
            self.data["stackmode_text"] = "Stand Alone"
        elif self.data["stackmode"] == 0x01:
            self.data["stackmode_text"] = "Parallel stack - master"
        elif self.data["stackmode"] == 0x02:
            self.data["stackmode_text"] = "Parallel stack - slave"
        elif self.data["stackmode"] == 0x04:
            self.data["stackmode_text"] = "Series stack - master"
        elif self.data["stackmode"] == 0x08:
            self.data["stackmode_text"] = "Series stack - slave"
        else:
            self.data["stackmode_text"] = "Unknown"

    def getModel(self):
        return self.model

class PT100Device:
    def __init__(self, id=None):
        self.data = OrderedDict()
        self.model = OrderedDict()
        self.model["model"] = PT100
        if id:
            self.model["id"] = str(id)
        self.model["data"] = self.data
        self.data["address"] = 0
        self.data["on_off"] = 0
        self.data["mode"] = 0
        self.data["mode_text"] = ''
        self.data["regulation"] = 0
        self.data["regulation_text"] = ''
        self.data["fault"] = 0
        self.data["fault_text"] = ''
        self.data["battery"] = 0
        self.data["battery_amps"] = 0
        self.data["pv_voltage"] = 0
        self.data["charge_time"] = 0
        self.data["target_battery_voltage"] = 0
        self.data["relay_state"] = 0
        self.data["alarm_state"] = 0
        self.data["battery_temperature"] = 0
        self.data["inductor_temperature"] = 0
        self.data["fet_temperature"] = 0
        self.data["lifetime_kwhrs"] = 0
        self.data["resettable_kwhrs"] = 0
        self.data["ground_fault_current"] = 0
        self.data["nominal_battery_voltage"] = 0
        self.data["stacker_info"] = 0
        self.data["model"] = ''
        self.data["output_current_rating"] = 0
        self.data["input_voltage_rating"] = 0
        self.data["record"] = 0
        self.data["daily_kwh"] = 0
        self.data["max_daily_pv_volts"] = 0
        self.data["max_daily_pv_volts_time"] = 0
        self.data["max_daily_battery_volts"] = 0
        self.data["max_daily_battery_volts_time"] = 0
        self.data["minimum_daily_battery_volts"] = 0
        self.data["minimum_daily_battery_volts_time"] = 0
        self.data["daily_time_operational"] = 0
        self.data["daily_amp_hours"] = 0
        self.data["peak_daily_power"] = 0
        self.data["peak_daily_power_time"] = 0
        self.data["fault_number"] = 0
        self.data["max_battery_volts"] = 0
        self.data["max_pv_to_battery_vdc"] = 0
        self.data["max_battery_temperature"] = 0
        self.data["max_fet_temperature"] = 0
        self.data["max_inductor_temperature"] = 0

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if packetType == PT_C1:
            #  skip header
            self.data['address'] = unpacked[1] >> 5
            byte_value = unpacked[2]
            #  byte 2
            self.data['on_off'] = True if (
                byte_value & 0x80) >> 7 != 0 else False
            self.data['mode'] = (byte_value & 0x70) >> 4
            self.data['regulation'] = byte_value & 0x0F
            #  byte 3
            byte_value = unpacked[3]
            self.data['fault'] = byte_value >> 3
            self.data['battery'] = unpacked[4] / 10
            self.data['battery_amps'] = unpacked[5] / 10
            self.data['pv_voltage'] = unpacked[6] / 10
            self.data['charge_time'] = unpacked[7] / 10
            byte_value = unpacked[8]
            self.data['target_battery_voltage'] = (
                byte_value / 10) * Magnum.multiplier
            byte_value = unpacked[9]
            self.data['relay_state'] = True if (
                (byte_value & 0x80) >> 7) != 0 else False
            self.data['alarm_state'] = True if (
                (byte_value & 0x70) >> 6) != 0 else False
            byte_value = unpacked[10]
            self.data['battery_temperature'] = byte_value / 10
            byte_value = unpacked[11]
            self.data['inductor_temperature'] = byte_value
            byte_value = unpacked[12]
            self.data['fet_temperature'] = (byte_value)
            if self.data['mode'] == 2:
                self.data['mode_text'] = "Sleep"
            elif self.data['mode'] == 3:
                self.data['mode_text'] = "Float"
            elif self.data['mode'] == 4:
                self.data['mode_text'] = "Bulk"
            elif self.data['mode'] == 5:
                self.data['mode_text'] = "Absorb"
            elif self.data['mode'] == 6:
                self.data['mode_text'] = "EQ"
            else:
                self.data['mode_text'] = "Unknown"
            if self.data['regulation'] == 0:
                self.data['regulation_text'] = "Off"
            elif self.data['regulation'] == 1:
                self.data['regulation_text'] = "Voltage"
            elif self.data['regulation'] == 2:
                self.data['regulation_text'] = "Current"
            elif self.data['regulation'] == 3:
                self.data['regulation_text'] = "Temperature"
            elif self.data['regulation'] == 4:
                self.data['regulation_text'] = "Hardware"
            elif self.data['regulation'] == 5:
                self.data['regulation_text'] = "Voltage Off Limit"
            elif self.data['regulation'] == 6:
                self.data['regulation_text'] = "PPT Limit"
            elif self.data['regulation'] == 7:
                self.data['regulation_text'] = "Fault Limit"
            elif self.data['fault'] == 0:
                self.data['fault_text'] = "No Fault"
            elif self.data['fault'] == 1:
                self.data['fault_text'] = "Input er Fault"
            elif self.data['fault'] == 2:
                self.data['fault_text'] = "Output er Fault"
            elif self.data['fault'] == 3:
                self.data['fault_text'] = "PV High Fault"
            elif self.data['fault'] == 4:
                self.data['fault_text'] = "Battery High Fault"
            elif self.data['fault'] == 5:
                self.data['fault_text'] = "BTS Shorted Fault"
            elif self.data['fault'] == 6:
                self.data['fault_text'] = "FET Overtemp Fault"
            elif self.data['fault'] == 7:
                self.data['fault_text'] = "Inductor Overtemp Fault"
            elif self.data['fault'] == 8:
                self.data['fault_text'] = "Over Current Fault"
            elif self.data['fault'] == 9:
                self.data['fault_text'] = "Internal Phase Fault"
            elif self.data['fault'] == 10:
                self.data['fault_text'] = "Repeated Internal Phase Fault"
            elif self.data['fault'] == 11:
                self.data['fault_text'] = "Internal Fault 1"
            elif self.data['fault'] == 12:
                self.data['fault_text'] = "GFP Fault"
            elif self.data['fault'] == 13:
                self.data['fault_text'] = "ARC Fault"
            elif self.data['fault'] == 14:
                self.data['fault_text'] = "NTC Fault"
            elif self.data['fault'] == 15:
                self.data['fault_text'] = "FET Overload Fault"
            elif self.data['fault'] == 16:
                self.data['fault_text'] = "Stack Fault 1"
            elif self.data['fault'] == 17:
                self.data['fault_text'] = "Stack Fault 2"
            elif self.data['fault'] == 18:
                self.data['fault_text'] = "Stack Fault 3"
            elif self.data['fault'] == 19:
                self.data['fault_text'] = "High Battery Temp Fault"
            else:
                self.data['fault_text'] = "unknown"
        elif packetType == PT_C2:
            self.data['address'] = unpacked[1] >> 5
            self.data['lifetime_kwhrs'] = unpacked[2] * 10
            self.data['resettable_kwhrs'] = unpacked[3] / 10
            self.data['ground_fault_current'] = unpacked[4]
            byte_value = unpacked[5]
            self.data['nominal_battery_voltage'] = byte_value >> 2
            self.data['stacker_info'] = byte_value & 0x03
            self.data['revision'] = str(unpacked[6] / 10)
            self.data['model'] = unpacked[7]
            self.data['output_current_rating'] = unpacked[8]
            self.data['input_voltage_rating'] = unpacked[9]
        elif packetType == PT_C3:
            short_value = unpacked[1]
            self.data['address'] = ((short_value & 0xE000) >> 13)
            self.data['record'] = (short_value & 0x1ffffff)
            self.data['daily_kwh'] = unpacked[2] / 10
            self.data['max_daily_pv_volts'] = unpacked[3]
            self.data['max_daily_pv_volts_time'] = unpacked[4] / 10
            self.data['max_daily_battery_volts'] = unpacked[5]
            self.data['max_daily_battery_volts_time'] = unpacked[6] / 10
            self.data['minimum_daily_battery_volts'] = unpacked[7]
            self.data['minimum_daily_battery_volts_time'] = unpacked[8] / 10
            self.data['daily_time_operational'] = unpacked[7] / 10
            self.data['daily_amp_hours'] = unpacked[10]
            self.data['peak_daily_power'] = unpacked[11]
            self.data['peak_daily_power_time'] = unpacked[12] / 10
        elif packetType == PT_C4:
            byte_value = unpacked[1]
            self.data['address'] = ((byte_value & 0xE0) >> 5)
            self.data['fault_number'] = (byte_value & 0x1f)
            self.data['max_battery_volts'] = unpacked[2]
            self.data['max_pv_to_battery_vdc'] = unpacked[3]
            self.data['max_battery_temperature'] = unpacked[4]
            self.data['max_fet_temperature'] = unpacked[5]
            self.data['max_inductor_temperature'] = unpacked[6]

    def getModel(self):
        return self.model

class RemoteDevice:

    noAGS = ["genstart", "runtime", "starttemp", "startvdc", "quiettime",
             "begintime", "stoptime", "vdcstop", "voltstartdelay", "voltstopdelay", "maxrun",
             "socstart", "socstop", "ampstart", "ampsstartdelay", "ampstop", "ampsstopdelay",
             "quietbegintime", "quietendtime", "exercisedays", "exercisestart",
             "exerciseruntime", "topoff", "warmup", "cool"]

    noBMK = ["batteryefficiency", "resetbmk"]
    noMSH = ["mshinputamps", "mshcutoutvoltage"]
    noPT100 = ["forcechgode", "relayonoff", "buzzeronoff", "resetpt100", "address",
               "packet", "lognumber", "relayonvdc", "relayoffvdc", "relayondelayseconds",
               "relaydelayoffseconds", "batterytempcomp", "powersavetime", "alarmonvdc",
               "alarmoffvdc", "alarmdondelay", "alarmoffdelay", "eqdonetimer", "chargerate",
               "rebulkonsunup", "AbsorbVoltage", "FloatVoltage", "EqualizeVoltage", "AbsorbTime",
               "RebulkVoltage", "BatteryTemperatureCompensation"]

    def __init__(self, id=None):
        self.data = OrderedDict()
        self.model = OrderedDict()
        self.model["model"] = REMOTE
        if id:
            self.model["id"] = str(id)
        self.model["data"] = self.data
        self.data["revision"] = "0.0"
        self.data["action"] = 0
        self.data["searchwatts"] = 0
        self.data["batterysize"] = 0
        # see extract method for a note
        self.data["battype"] = 0
        self.data["absorb"] = 0
        self.data["chargeramps"] = 0
        self.data["ainput"] = 0
        self.data["parallel"] = 0
        self.data["force_charge"] = 0
        self.data["genstart"] = 0
        self.data["lbco"] = 0
        self.data["vaccutout"] = 0
        self.data["vsfloat"] = 0
        self.data["vEQ"] = 0
        self.data["absorbtime"] = 0
        # end of core info
        # A0
        self.data["remotetimehours"] = 0
        self.data["remotetimemins"] = 0
        self.data["runtime"] = 0
        self.data["starttemp"] = 0
        self.data["startvdc"] = 0
        self.data["quiettime"] = 0
        # A1
        self.data["begintime"] = 0
        self.data["stoptime"] = 0
        self.data["vdcstop"] = 0
        self.data["voltstartdelay"] = 0
        self.data["voltstopdelay"] = 0
        self.data["maxrun"] = 0
        # A2
        self.data["socstart"] = 0
        self.data["socstop"] = 0
        self.data["ampstart"] = 0
        self.data["ampsstartdelay"] = 0
        self.data["ampstop"] = 0
        self.data["ampsstopdelay"] = 0
        # A3
        self.data["quietbegintime"] = 0
        self.data["quietendtime"] = 0
        self.data["exercisedays"] = 0
        self.data["exercisestart"] = 0
        self.data["exerciseruntime"] = 0
        self.data["topoff"] = 0
        # A4
        self.data["warmup"] = 0
        self.data["cool"] = 0
        # 80
        self.data["batteryefficiency"] = 0
        self.data["resetbmk"] = 0
        # 11 MSH - not supported
        self.data["mshinputamps"] = 0
        self.data["mshcutoutvoltage"] = 0
        # C0
        self.data["forcechgode"] = 0
        self.data["relayonoff"] = 0
        self.data["buzzeronoff"] = 0
        self.data["resetpt100"] = 0
        self.data["address"] = 0
        self.data["packet"] = 0
        self.data["lognumber"] = 0
        # C1
        self.data["relayonvdc"] = 0
        self.data["relayoffvdc"] = 0
        self.data["relayondelayseconds"] = 0
        self.data["relaydelayoffseconds"] = 0
        self.data["batterytempcomp"] = 0
        self.data["powersavetime"] = 0
        # C2
        self.data["alarmonvdc"] = 0
        self.data["alarmoffvdc"] = 0
        self.data["alarmdondelay"] = 0
        self.data["alarmoffdelay"] = 0
        self.data["eqdonetimer"] = 0
        self.data["chargerate"] = 0
        self.data["rebulkonsunup"] = 0
        # C3
        self.data["AbsorbVoltage"] = 0
        self.data["FloatVoltage"] = 0
        self.data["EqualizeVoltage"] = 0
        self.data["RebulkVoltage"] = 0
        self.data["BatteryTemperatureCompensation"] = 0

    def setBaseValues(self, unpacked):
        self.data["action"] = unpacked[0]
        self.data["searchwatts"] = unpacked[1]
        #
        # The documentation is very weird on this value
        #
        self.data["batterysize"] = (unpacked[2] * 2) + 200
        value = unpacked[3]
        if(value > 100):
            self.data["absorb"] = value * Magnum.multiplier / 10
            self.data["battype"] = 0
        else:
            self.data["absorb"] = 0
            self.data["battype"] = value
        self.data["chargeramps"] = unpacked[4]
        self.data["ainput"] = unpacked[5]
        self.data["revision"] = unpacked[6] / 10
        value = unpacked[7]
        self.data["parallel"] = value & 0x0f
        self.data["parallel"] = self.data["parallel"] * 10
        self.data["force_charge"] = value & 0xf0
        self.data["force_charge"] = self.data["force_charge"] >> 4
        self.data["genstart"] = unpacked[8]
        self.data["lbco"] = unpacked[9] / 10
        self.data["vaccutout"] = unpacked[10]
        self.data["vsfloat"] = unpacked[11] * Magnum.multiplier / 10
        self.data["vEQ"] = self.data["absorb"] + (unpacked[12] / 10)
        self.data["absorbtime"] = unpacked[13] / 10

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if packetType == REMOTE_00:
            self.setBaseValues(unpacked)
        elif packetType == REMOTE_11:
            self.setBaseValues(unpacked)
            self.data["mshinputamps"] = unpacked[14]
            self.data["mshcutoutvoltage"] = unpacked[15]
        elif packetType == REMOTE_80:
            self.setBaseValues(unpacked)
            self.data["remotetimehours"] = unpacked[14]
            self.data["remotetimemins"] = unpacked[15]
            self.data["batteryefficiency"] = unpacked[16]
            self.data["resetbmk"] = unpacked[17]
        elif packetType == REMOTE_A0:
            self.setBaseValues(unpacked)
            self.data["remotetimehours"] = unpacked[14]
            self.data["remotetimemins"] = unpacked[15]
            self.data["runtime"] = unpacked[16] / 10
            self.data["starttemp"] = unpacked[17]
            self.data["starttemp"] = round(
                (self.data["starttemp"] - 32) * 5 / 9, 1)
            value = unpacked[18] * Magnum.multiplier
            self.data["startvdc"] = value / 10
            self.data["quiettime"] = unpacked[19]
        elif packetType == REMOTE_A1:
            self.setBaseValues(unpacked)
            minutes = unpacked[14] * 15
            self.data["begintime"] = ((minutes // 60) * 100) + (minutes % 60)
            minutes = unpacked[15] * 15
            self.data["stoptime"] = ((minutes // 60) * 100) + (minutes % 60)
            value = unpacked[16]
            self.data["vdcstop"] = value * Magnum.multiplier / 10
            self.data["voltstartdelay"] = unpacked[17]
            if self.data["voltstartdelay"] > 127:
                self.data["voltstartdelay"] = (
                    self.data["voltstartdelay"] & 0x0f) * 60
            self.data["voltstopdelay"] = unpacked[18]
            if self.data["voltstopdelay"] > 127:
                self.data["voltstopdelay"] = (
                    self.data["voltstopdelay"] & 0x0f) * 60
            self.data["maxrun"] = unpacked[19] / 10
        elif packetType == REMOTE_A2:
            self.setBaseValues(unpacked)
            self.data["socstart"] = unpacked[14]
            self.data["socstop"] = unpacked[15]
            self.data["ampstart"] = unpacked[16]
            self.data["ampsstartdelay"] = unpacked[17]
            if self.data["ampsstartdelay"] > 127:
                self.data["ampsstartdelay"] = (
                    self.data["ampsstartdelay"] & 0x0f) * 60
            self.data["ampstop"] = unpacked[18]
            self.data["ampsstopdelay"] = unpacked[19]
            if self.data["ampsstopdelay"] > 127:
                self.data["ampsstopdelay"] = (
                    self.data["ampsstopdelay"] & 0x0f) * 60
        elif packetType == REMOTE_A3:
            self.setBaseValues(unpacked)
            minutes = unpacked[14] * 15
            self.data["quietbegintime"] = (
                (minutes // 60) * 100) + (minutes % 60)
            minutes = unpacked[15] * 15
            self.data["quietendtime"] = (
                (minutes // 60) * 100) + (minutes % 60)
            minutes = unpacked[16] * 15
            self.data["exercisestart"] = (
                (minutes // 60) * 100) + (minutes % 60)
            self.data["runtime"] = unpacked[17] / 10
            self.data["topoff"] = unpacked[18]
        elif packetType == REMOTE_A4:
            self.setBaseValues(unpacked)
            self.data["warmup"] = unpacked[14]
            if self.data["warmup"] > 127:
                self.data["warmup"] = (self.data["warmup"] & 0x0f) * 60
            self.data["cool"] = unpacked[15]
            if self.data["cool"] > 127:
                self.data["cool"] = (self.data["cool"] & 0x0f) * 60
        elif packetType == REMOTE_C0:
            self.setBaseValues(unpacked)
            self.data["forcechgode"] = unpacked[14] & 0x03
            byte_value = unpacked[15]
            self.data["relayonoff"] = (byte_value & 0x60) >> 6
            self.data["buzzeronoff"] = (byte_value & 0x30) >> 4
            self.data["resetpt100"] = unpacked[16]
            byte_value = unpacked[17]
            self.data["address"] = byte_value >> 5
            self.data["packet"] = byte_value & 0x1f
            self.data["lognumber"] = unpacked[18]
        elif packetType == REMOTE_C1:
            self.setBaseValues(unpacked)
            self.data["relayonvdc"] = unpacked[14] / 10 * Magnum.multiplier
            self.data["relayoffvdc"] = unpacked[15] / 10 * Magnum.multiplier
            self.data["relayondelayseconds"] = unpacked[16]
            if self.data["relayondelayseconds"] < 0:
                self.data["relayondelayseconds"] = (
                    60 * (0 - self.data["relayondelayseconds"]))
            self.data["relaydelayoffseconds"] = unpacked[17]
            if self.data["relaydelayoffseconds"] < 0:
                self.data["relaydelayoffseconds"] = (
                    60 * (0 - self.data["relaydelayoffseconds"]))
            self.data["batterytempcomp"] = unpacked[18]
            self.data["powersavetime"] = unpacked[19] >> 2
        elif packetType == REMOTE_C2:
            self.setBaseValues(unpacked)
            self.data["alarmonvdc"] = unpacked[14] / 10 * Magnum.multiplier
            self.data["alarmoffvdc"] = unpacked[15] / 10 * Magnum.multiplier
            self.data["alarmdondelay"] = unpacked[16]
            if self.data["alarmdondelay"] < 0:
                self.data["alarmdondelay"] = 60 * \
                    (0 - self.data["alarmdondelay"])
            self.data["alarmoffdelay"] = unpacked[17]
            if self.data["alarmoffdelay"] < 0:
                self.data["alarmoffdelay"] = 60 * \
                    (0 - self.data["alarmoffdelay"])
            self.data["eqdonetimer"] = unpacked[18] / 10
            byte_value = unpacked[19]
            self.data["chargerate"] = (byte_value & 0xFE) >> 1
            self.data["rebulkonsunup"] = byte_value & 0x01
        elif packetType == REMOTE_C3:
            self.setBaseValues(unpacked)
            self.data["AbsorbVoltage"] = unpacked[14] / 10 * Magnum.multiplier
            self.data["FloatVoltage"] = unpacked[15] / 10 * Magnum.multiplier
            self.data["EqualizeVoltage"] = unpacked[16] / \
                10 * Magnum.multiplier
            self.data["AbsorbTime"] = unpacked[17] / 10
            # akip a  byte"]
            self.data["RebulkVoltage"] = unpacked[19] / 10 * Magnum.multiplier
            self.data["BatteryTemperatureCompensation"] = unpacked[20]
        elif packetType == REMOTE_D0:
            self.setBaseValues(unpacked)
            # I have no idea what a D0 is

    def removeBMK(self):
        for item in RemoteDevice.noBMK:
            if item in self.data:
                self.data.pop(item)

    def removeAGS(self):
        for item in RemoteDevice.noAGS:
            if item in self.data:
                self.data.pop(item)

    def removePT100(self):
        for item in RemoteDevice.noPT100:
            if item in self.data:
                self.data.pop(item)

    def getModel(self):
        # remove MSH as it's not supported - yet
        for item in RemoteDevice.noMSH:
            if item in self.data:
                self.data.pop(item)
        return self.model

class RTRDevice:
    def __init__(self, id=None):
        self.data = OrderedDict()
        self.model = OrderedDict()
        self.model["model"] = RTR
        if id:
            self.model["id"] = str(id)
        self.model["data"] = self.data
        self.data["revision"] = "0.0"

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if packetType == RTR_91:
            self.data["revision"] = str(round(unpacked[1] / 10))

    def getModel(self):
        return self.model
