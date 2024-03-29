from copy import deepcopy

from magnum import *

class ACLDDevice:
    def __init__(self, trace=False):
        # self.trace = trace
        self.trace = True # force packet dump
        self.data = {}
        self.deviceData = {}
        self.deviceData["device"] = ACLD
        self.deviceData["data"] = self.data
        if self.trace:
            self.deviceData["trace"] = []
        self.data["revision"] = str("0.0")

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append([packetType,  packet[1].hex().upper()])
        # if packetType == ACLD_D1:
        #     pass

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device
