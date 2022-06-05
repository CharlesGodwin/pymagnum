
from collections import OrderedDict
from copy import deepcopy

from magnum import *

class BMKDevice:
    def __init__(self, trace=False):
        self.trace = trace
        self.data = OrderedDict()
        self.deviceData = OrderedDict()
        self.deviceData["device"] = BMK
        self.deviceData["data"] = self.data
        self.data["revision"] = ""
        self.data["soc"] = 0
        self.data["vdc"] = 0.0
        self.data["adc"] = 0.0
        self.data["vmin"] = 0.0
        self.data["vmax"] = 0.0
        self.data["amph"] = 0
        self.data["amphtrip"] = 0.0
        self.data["amphout"] = 0.0
        self.data["Fault"] = 0
        self.data["Fault_Text"] = ""
        if self.trace:
            self.deviceData["trace"] = []

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append([packetType,  packet[1].hex().upper()])
        if packetType == BMK_81:
            self.data["soc"] = unpacked[1]
            self.data["vdc"] = round(unpacked[2] / 100, 2)
            self.data["adc"] = round(unpacked[3] / 10, 1)
            self.data["vmin"] = round(unpacked[4] / 100, 2)
            self.data["vmax"] = round(unpacked[5] / 100, 2)
            self.data["amph"] = unpacked[6]
            self.data["amphtrip"] = round(unpacked[7] / 10, 1)
            self.data["amphout"] = round(unpacked[8] * 100, 2)
            self.data["revision"] = str(round(unpacked[9] / 10, 2))
            self.data["Fault"] = unpacked[10]
            if self.data["Fault"] == 0:
                self.data["Fault_Text"] = "Reserved"
            elif self.data["Fault"] == 1:
                self.data["Fault_Text"] = "Normal"
            elif self.data["Fault"] == 2:
                self.data["Fault_Text"] = "Fault Start"

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device
