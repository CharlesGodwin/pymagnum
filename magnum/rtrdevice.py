from copy import deepcopy

from magnum import *

class RTRDevice:
    def __init__(self, trace=False):
        self.trace = trace
        self.data = {}
        self.deviceData = {}
        self.deviceData["device"] = RTR
        self.deviceData["data"] = self.data
        self.data["revision"] = "0.0"
        if self.trace:
            self.data["trace"]  = []

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.data["trace"].append((packetType, packet[1].hex().upper()))
            self.data["trace"]=list(set(self.data["trace"]))
        if packetType == RTR_91:
            self.data["revision"] = str(round(unpacked[1] / 10))

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.data["trace"]  = []
        return device
