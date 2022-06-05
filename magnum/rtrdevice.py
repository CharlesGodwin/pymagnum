from collections import OrderedDict
from copy import deepcopy

from magnum import *

class RTRDevice:
    def __init__(self, trace=False):
        self.trace = trace
        self.data = OrderedDict()
        self.deviceData = OrderedDict()
        self.deviceData["device"] = RTR
        self.deviceData["data"] = self.data
        if self.trace:
            self.deviceData["trace"] = []
        self.data["revision"] = "0.0"        

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append([packetType, packet[1].hex().upper()])
        if packetType == RTR_91:
            self.data["revision"] = str(round(unpacked[1] / 10))

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device
