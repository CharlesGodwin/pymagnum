
from collections import OrderedDict
from copy import deepcopy

from magnum import *
from magnum.inverterdevice import InverterDevice
class RemoteDevice:

    noAGS = ["ampsstartdelay", "ampsstopdelay", "ampstart", "ampstop", "begintime", "cool", "exercisedays", "exerciseruntime", "exercisestart", "genstart", "maxrun", "quietbegintime", "quietendtime",
             "quiettime", "remotetimehours", "remotetimemins", "runtime", "socstart", "socstop", "starttemp", "startvdc", "stoptime", "topoff", "vdcstop", "voltstartdelay", "voltstopdelay", "warmup"]

    noBMK = ["batteryefficiency"]

    # noMSH = ["mshinputamps", "mshcutoutvoltage"]
    noPT100 = ["address", "packet", "lognumber", "relayonvdc", "relayoffvdc", "relayondelayseconds",
               "relaydelayoffseconds", "batterytempcomp", "powersavetime", "alarmonvdc",
               "alarmoffvdc", "alarmdondelay", "alarmoffdelay", "eqdonetimer", "chargerate",
               "rebulkonsunup", "AbsorbVoltage", "FloatVoltage", "EqualizeVoltage", "AbsorbTime",
               "RebulkVoltage", "BatteryTemperatureCompensation"]

    def __init__(self, trace=False):
        self.trace = trace
        self.data = OrderedDict()
        self.deviceData = OrderedDict()
        self.deviceData["device"] = REMOTE
        self.deviceData["data"] = self.data
        if self.trace:
            self.deviceData["trace"] = []
        self.data["revision"] = "0.0"
        # self.data["action"] = 0
        self.data["searchwatts"] = 0
        self.data["batterysize"] = 0
        # see extract method for a note
        self.data["battype"] = 0
        self.data["absorb"] = 0
        self.data["chargeramps"] = 0
        self.data["ainput"] = 0
        self.data["parallel"] = 0
        # self.data["force_charge"] = 0
        # self.data["genstart"] = 0
        self.data["lbco"] = 0.0
        self.data["vaccutout"] = 0.0
        self.data["vsfloat"] = 0.0
        self.data["vEQ"] = 0.0
        self.data["absorbtime"] = 0
        # end of core info
        # A0
        # self.data["remotetimehours"] = 0
        # self.data["remotetimemins"] = 0
        self.data["runtime"] = 0
        self.data["starttemp"] = 0.0
        self.data["startvdc"] = 0.0
        self.data["quiettime"] = 0
        # A1
        self.data["begintime"] = 0
        self.data["stoptime"] = 0
        self.data["vdcstop"] = 0.0
        self.data["voltstartdelay"] = 0
        self.data["voltstopdelay"] = 0
        self.data["maxrun"] = 0
        # A2
        self.data["socstart"] = 0
        self.data["socstop"] = 0
        self.data["ampstart"] = 0.0
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
        # self.data["resetbmk"] = 0
        # 11 MSH - not supported
        # self.data["mshinputamps"] = 0
        # self.data["mshcutoutvoltage"] = 0
        # C0
        # self.data[" forcechgcode"] = 0
        # self.data["relayonoff"] = 0
        # self.data["buzzeronoff"] = 0
        # self.data["resetpt100"] = 0
        # self.data["address"] = 0
        # self.data["packet"] = 0
        # self.data["lognumber"] = 0
        # # C1
        # self.data["relayonvdc"] = 0
        # self.data["relayoffvdc"] = 0
        # self.data["relayondelayseconds"] = 0
        # self.data["relaydelayoffseconds"] = 0
        # self.data["batterytempcomp"] = 0
        # self.data["powersavetime"] = 0
        # # C2
        # self.data["alarmonvdc"] = 0
        # self.data["alarmoffvdc"] = 0
        # self.data["alarmdondelay"] = 0
        # self.data["alarmoffdelay"] = 0
        # self.data["eqdonetimer"] = 0
        # self.data["chargerate"] = 0
        # self.data["rebulkonsunup"] = 0
        # # C3
        # self.data["AbsorbVoltage"] = 0
        # self.data["FloatVoltage"] = 0
        # self.data["EqualizeVoltage"] = 0
        # self.data["RebulkVoltage"] = 0
        # self.data["BatteryTemperatureCompensation"] = 0

    def setBaseValues(self, unpacked):
        # self.data["action"] = unpacked[0]
        self.data["searchwatts"] = unpacked[1]
        value = unpacked[3]
        if(value > 100):
            self.data["absorb"] = value * InverterDevice.multiplier / 10
            self.data["battype"] = 0
        else:
            self.data["absorb"] = 0
            self.data["battype"] = value
        self.data["chargeramps"] = unpacked[4]
        self.data["ainput"] =  unpacked[5]
        self.data["revision"] = unpacked[6] / 10
        value = unpacked[7]
        self.data["parallel"] = (value & 0x0f) * 10
        # self.data["force_charge"] = value & 0xf0
        # self.data["force_charge"] = self.data["force_charge"] >> 4
        # self.data["genstart"] = unpacked[8]
        self.data["lbco"] = unpacked[9] / 10
        self.data["vaccutout"] = float(unpacked[10])
        self.data["vsfloat"] = unpacked[11] * InverterDevice.multiplier / 10
        self.data["vEQ"] = self.data["absorb"] + (unpacked[12] / 10)
        self.data["absorbtime"] = unpacked[13] / 10

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append([packetType,  packet[1].hex().upper()])
        if packetType == REMOTE_C:
            self.setBaseValues(unpacked)
            #
            # The documentation is very weird on this value
            #
            self.data["batterysize"] = (unpacked[2] * 10)
            for key in ["vsfloat","vEQ","absorbtime", "remotetimehours","remotetimemins"]:
                self.data.pop(key, '')
        elif packetType == REMOTE_00:
            self.setBaseValues(unpacked)
        elif packetType == REMOTE_80:
            self.setBaseValues(unpacked)
            # batterysize is ill defined in documentation
            self.data["batterysize"] = (unpacked[2] * 10)
            # self.data["remotetimehours"] = unpacked[14]
            # self.data["remotetimemins"] = unpacked[15]
            self.data["batteryefficiency"] = unpacked[16]
            # self.data["resetbmk"] = unpacked[17]
        elif packetType == REMOTE_A0:
            self.setBaseValues(unpacked)
            # self.data["remotetimehours"] = unpacked[14]
            # self.data["remotetimemins"] = unpacked[15]
            self.data["runtime"] = unpacked[16] / 10
            self.data["starttemp"] = float(unpacked[17])
            self.data["starttemp"] = round((self.data["starttemp"] - 32) * 5 / 9, 1)
            value = unpacked[18] * InverterDevice.multiplier
            self.data["startvdc"] = value / 10
            self.data["quiettime"] = unpacked[19]
        elif packetType == REMOTE_A1:
            self.setBaseValues(unpacked)
            minutes = unpacked[14] * 15
            self.data["begintime"] = ((minutes // 60) * 100) + (minutes % 60)
            minutes = unpacked[15] * 15
            self.data["stoptime"] = ((minutes // 60) * 100) + (minutes % 60)
            value = unpacked[16]
            self.data["vdcstop"] = value * InverterDevice.multiplier / 10
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
            self.data["ampstart"] = float(unpacked[16])
            self.data["ampsstartdelay"] = unpacked[17]
            if self.data["ampsstartdelay"] > 127:
                self.data["ampsstartdelay"] = (self.data["ampsstartdelay"] & 0x0f) * 60
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
        elif packetType in [REMOTE_11, REMOTE_C0, REMOTE_C1, REMOTE_C2, REMOTE_C3, REMOTE_D0]:
                self.setBaseValues(unpacked)
                #
                # REMOTE_11, REMOTE_C0 through REMOTE_C3 and REMOTE_D0 are ignored
                #
    def cleanup(self, bmk, ags, pt100):
        if bmk == None:
            for item in self.noBMK:
                if item in self.data:
                    self.data.pop(item)

        if ags == None:
            for item in self.noAGS:
                if item in self.data:
                    self.data.pop(item)

        if pt100 == None:
            for item in self.noPT100:
                if item in self.data:
                    self.data.pop(item)
        # remove MSH as it's not supported - yet
        # for item in self.noMSH:
        #     if item in self.data:
        #         self.data.pop(item)

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device
