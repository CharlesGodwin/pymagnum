
from collections import OrderedDict
from copy import deepcopy

from magnum import *
from magnum.inverterdevice import InverterDevice


class AGSDevice:
    status = {
        0: "Not Connected",
        1: "Off",
        2: "Ready",
        3: "Manual Run",
        4: "AC In",
        5: "In quiet time",
        6: "Start in test mode",
        7: "Start on temperature",
        8: "Start on voltage",
        9: "Fault start on test",
        10: "Fault start on temp",
        11: "Fault start on voltage",
        12: "Start TOD",
        13: "Start SOC",
        14: "Start Exercise",
        15: "Fault start TOD",
        16: "Fault start SOC",
        17: "Fault start Exercise",
        18: "Start on Amp",
        19: "Start on Topoff",
        20: "Not used",
        21: "Fault start on Amp",
        22: "Fault on Topoff",
        23: "Not used",
        24: "Fault max run",
        25: "Gen Run Fault",
        26: "Gen in Warm up",
        27: "Gen in Cool down"
    }
# some data is unreliable as remote doesn't send it often enough

    def __init__(self, trace=False):
        self.trace = trace
        self.data = OrderedDict()
        self.deviceData = OrderedDict()
        self.deviceData["device"] = AGS
        self.deviceData["data"] = self.data
        self.data["revision"] = '0.0'
        self.data["status"] = 0
        self.data["status_text"] = ""
        self.data["running"] = False
        self.data["temp"] = 0.0
        self.data["runtime"] = 0.0
        self.data["gen_last_run"] = 0
        self.data["last_full_soc"] = 0
        self.data["gen_total_run"] = 0
        self.data["vdc"] = 0.0
        if self.trace:
            self.deviceData["trace"] = []

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append(
                [packetType,  packet[1].hex().upper()])
        if packetType == AGS_A1:
            self.data["status"] = unpacked[1]
            if self.data["status"] in (3, 6, 7, 8, 12, 13, 14, 18, 19, 26, 27):
                self.data["running"] = True
            else:
                self.data["running"] = False
            self.data["revision"] = str(round(unpacked[2] / 10, 1))
            self.data["temp"] = float(unpacked[3])
            if self.data["temp"] < 105.0:
                self.data["temp"] = round((self.data["temp"] - 32) * 5 / 9, 1)
            self.data["runtime"] = round(unpacked[4] / 10, 2)
            if self.data["status"] in self.status:
                self.data["status_text"] = self.status[self.data["status"]]
            else:
                self.data["status_text"] = "Unknown"
            self.data["vdc"] = round(
                unpacked[5] / 10 * InverterDevice.multiplier, 2)
        elif packetType == AGS_A2:
            self.data["gen_last_run"] = unpacked[1]
            self.data["last_full_soc"] = unpacked[2]
            self.data["gen_total_run"] = unpacked[3]

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device
