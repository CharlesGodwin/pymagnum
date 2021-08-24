
from collections import OrderedDict
from copy import deepcopy

from magnum import *

class InverterDevice:
    inverter_models = {
                0x06: "MM612",
                0x07: "MM612-AE",
                0x08: "MM1212",
                0x09: "MMS1012",
                0x0A: "MM1012E",
                0x0B: "MM1512",
                0x0C: "MMS912E",
                0x0F: "ME1512",
                0x14: "ME2012",
                0x15: "RD2212",
                0x19: "ME2512",
                0x1E: "ME3112",
                0x23: "MS2012",
                0x24: "MS1512E",
                0x28: "MS2012E",
                0x2C: "MSH3012M",
                0x2D: "MS2812",
                0x2F: "MS2712E",
                0x35: "MM1324E",
                0x36: "MM1524",
                0x37: "RD1824",
                0x3B: "RD2624E",
                0x3F: "RD2824",
                0x45: "RD4024E",
                0x4A: "RD3924",
                0x5A: "MS4124E",
                0x5B: "MS2024",
                0x67: "MSH4024M",
                0x68: "MSH4024RE",
                0x69: "MS4024",
                0x6A: "MS4024AE",
                0x6B: "MS4024PAE",
                0x6F: "MS4448AE",
                0x70: "MS3748AEJ",
                0x72: "MS4048",
                0x73: "MS4448PAE",
                0x74: "MS3748PAEJ",
                0x75: "MS4348PE"
    }

    faults = {
        0x00: "None",
        0x01: "STUCK RELAY",
        0x02: "DC OVERLOAD",
        0x03: "AC OVERLOAD",
        0x04: "DEAD BAT",
        0x05: "BACKFEED",
        0x08: "LOW BAT",
        0x09: "HIGH BAT",
        0x0A: "HIGH AC VOLTS",
        0x10: "BAD_BRIDGE",
        0x12: "NTC_FAULT",
        0x13: "FET_OVERLOAD",
        0x14: "INTERNAL_FAULT4",
        0x16: "STACKER MODE FAULT",
        0x18: "STACKER CLK PH FAULT",
        0x17: "STACKER NO CLK FAULT",
        0x19: "STACKER PH LOSS FAULT",
        0x20: "OVER TEMP",
        0x21: "RELAY FAULT",
        0x80: "CHARGER_FAULT",
        0x81: "High Battery Temp",
        0x90: "OPEN SELCO TCO",
        0x91: "CB3 OPEN FAULT"
    }

    modes = {
        0x00:   "Standby",
        0x01:   "EQ",
        0x02:   "FLOAT",
        0x04:   "ABSORB",
        0x08:   "BULK",
        0x09:   "BATSAVER",
        0x10:   "CHARGE",
        0x20:   "Off",
        0x40:   "INVERT",
        0x50:   "Inverter_Standby",
        0x80:   "SEARCH"
    }

    stack_modes = {
        0x00:  "Stand Alone",
        0x01:  "Parallel stack - master",
        0x02:  "Parallel stack - slave",
        0x04:  "Series stack - master",
        0x08:  "Series stack - slave"
    }

    #
    # voltage multiplier
    #
    multiplier = 1

    def __init__(self, trace=False):
        self.trace = trace
        self.data = OrderedDict()
        self.deviceData = OrderedDict()
        self.deviceData["device"] = INVERTER
        self.deviceData["data"] = self.data
        self.data["revision"] = str(0.0)
        self.data["mode"] = 0
        self.data["mode_text"] = ""
        self.data["fault"] = 0
        self.data["fault_text"] = ""
        self.data["vdc"] = 0.0
        self.data["adc"] = 0.0
        self.data["VACout"] = 0.0
        self.data["VACin"] = 0.0
        self.data["invled"] = 0
        self.data["invled_text"] = ""
        self.data["chgled"] = 0
        self.data["chgled_text"] = ""
        self.data["bat"] = 0.0
        self.data["tfmr"] = 0.0
        self.data["fet"] = 0.0
        self.data["model"] = 0
        self.data["model_text"] = ""
        self.data["stackmode"] = 0
        self.data["stackmode_text"] = ""
        self.data["AACin"] = 0.0
        self.data["AACout"] = 0.0
        self.data["Hz"] = 0.0
        if self.trace:
            self.deviceData["trace"] = []

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append([packetType,  packet[1].hex().upper()])
        if packetType in( INV, INV_C):
            self.data["mode"] = unpacked[0]
            self.data["fault"] = unpacked[1]
            self.data["vdc"] = unpacked[2] / 10
            self.data["adc"] = float(unpacked[3])
            self.data["VACout"] = float(unpacked[4])
            self.data["VACin"] = float(unpacked[5])
            self.data["invled"] = unpacked[6]
            if self.data["invled"] != 0:
                self.data["invled"] = 1
            self.data["chgled"] = unpacked[7]
            if self.data["chgled"] != 0:
                self.data["chgled"] = 1
            self.data["revision"] = str(round(unpacked[8] / 10, 2))
            self.data["bat"] = float(unpacked[9])
            self.data["tfmr"] = float(unpacked[10])
            self.data["fet"] = float(unpacked[11])
            self.data["model"] = unpacked[12]
            if packetType == INV:
                self.data["stackmode"] = unpacked[13]
                self.data["AACin"] = float(unpacked[14])
                self.data["AACout"] = float(unpacked[15])
                self.data["Hz"] = round(unpacked[16] / 10, 2)
            else:
                self.data["stackmode"] = 0
                for key in ["AACin","AACout","Hz"]:
                    self.data.pop(key, '')
        #
        #    (Model <= 50) means 12V inverter
        #    (Model <= 107) means 24V inverter
        # 	 (Model < 150) means 48V inverter
        #
            if self.data["model"] <= 50:
                # voltage = 12
                InverterDevice.multiplier = 1
            elif self.data["model"] <= 107:
                # voltage = 24
                InverterDevice.multiplier = 2
            elif self.data["model"] <= 150:
                # voltage = 48
                InverterDevice.multiplier = 4

            if self.data["fault"] in self.faults:
                self.data["fault_text"] = self.faults[self.data["fault"]]
            self.data["chgled_text"] = "Off" if self.data["chgled"] == 0 else "On"
            self.data["invled_text"] = "Off" if self.data["invled"] == 0 else "On"
            if self.data["mode"] in self.modes:
                self.data["mode_text"] = self.modes[self.data["mode"]]
            else:
                self.data["mode_text"] = "??"
            if self.data["model"] in self.inverter_models:
                self.data["model_text"] = self.inverter_models[self.data["model"]]
            else:
                self.data["model_text"] = "Unknown"
            if self.data["stackmode"] in self.stack_modes:
                self.data["stackmode_text"] = self.stack_modes[self.data["stackmode"]]
            else:
                self.data["stackmode_text"] = "Unknown"

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device
