
import math
from collections import OrderedDict
from copy import deepcopy

from magnum import *
from magnum.inverterdevice import InverterDevice

class PT100Device:
    def __init__(self, trace=False):
        # self.trace = trace
        self.trace = True # force packet dump for now
        self.data = OrderedDict()
        self.deviceData = OrderedDict()
        self.deviceData["device"] = PT100
        self.deviceData["data"] = self.data
        if self.trace:
            self.deviceData["trace"] = []
        self.data['revision'] = '1.x' # from 0xC2
        # Start of C1
        self.data["address"] = 0
        self.data["mode"] = 0
        self.data["mode_text"] = ''
        self.data["mode_hex"] = ''
        self.data["regulation"] = 0
        self.data["regulation_text"] = ''
        self.data["fault"] = 0
        self.data["fault_text"] = ''
        self.data["battery"] = 0.0
        self.data["battery_amps"] = 0.0
        self.data["pv_voltage"] = 0.0
        self.data["charge_time"] = 0.0
        self.data["target_battery_voltage"] = 0.0
        self.data["relay_state"] = 1
        self.data["alarm_state"] = 0
        # check page 14 for fan on and Day
        self.data["fan_on"] = 0
        self.data["day"] = 0
        #
        self.data["battery_temperature"] = 0.0
        self.data["inductor_temperature"] = 0.0
        self.data["fet_temperature"] = 0.0
        # Start of C2
        # 2022-11-08 09:18:48 data only generated if a C2 packet is received
        # self.data["lifetime_kwhrs"] = math.nan
        # self.data["resettable_kwhrs"] = math.nan
        # self.data["ground_fault_current"] = math.nan
        # self.data["nominal_battery_voltage"] = 12.0
        # self.data["stacker_info"] = 0
        # self.data['dip_switches'] = '00000000'
        # self.data["model"] = ''
        # self.data["output_current_rating"] = math.nan
        # self.data["input_voltage_rating"] = math.nan
        # Start of C3
        # self.data["daily_kwh"] = math.nan
        # self.data["max_daily_pv_volts"] = math.nan
        # self.data["max_daily_pv_volts_time"] = math.nan
        # self.data["max_daily_battery_volts"] = math.nan
        # self.data["max_daily_battery_volts_time"] = math.nan
        # self.data["minimum_daily_battery_volts"] = math.nan
        # self.data["minimum_daily_battery_volts_time"] = math.nan
        # self.data["daily_time_operational"] = math.nan
        # self.data["daily_amp_hours"] = math.nan
        # self.data["peak_daily_power"] = math.nan
        # self.data["peak_daily_power_time"] = math.nan

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append([packetType,  packet[1].hex().upper()])
        address = unpacked[1] & 0X07
        if packetType == PT_C1 and address == 0:
            self.data['address'] == address
            #  skip header
            byte_value = unpacked[2]
            #  byte 2 assumes lower 4 bits and upper 4 bits
            self.data['mode'] = byte_value & 0x0F
            self.data['mode_hex'] = hex(unpacked[2]).upper()
            self.data['regulation'] = byte_value >> 4 & 0x0F
            #  byte 3
            byte_value = unpacked[3]
            self.data['fault'] = byte_value >> 3
            self.data['battery'] = unpacked[4] / 10
            self.data['battery_amps'] = unpacked[5] / 10
            self.data['pv_voltage'] = unpacked[6] / 10
            self.data['charge_time'] = unpacked[7] / 10
            byte_value = unpacked[8]
            self.data['target_battery_voltage'] = byte_value / 10 * InverterDevice.multiplier
            byte_value = unpacked[9]
            self.data['relay_state'] = byte_value & 0x01
            self.data['alarm_state'] = (byte_value >> 1) & 0x01
            self.data["fan_on"] = (byte_value >> 3) & 0x01
            self.data["day"] = (byte_value  >> 4) & 0x01

            byte_value = unpacked[10]
            if byte_value == 0X97 or byte_value == 0X98:
                self.data['battery_temperature'] = None # Short or open
            else:
                self.data['battery_temperature'] = float(byte_value)
            byte_value = unpacked[11]
            self.data['inductor_temperature'] = float(byte_value)
            byte_value = unpacked[12]
            self.data['fet_temperature'] = float(byte_value)
            modes = {
                1: "Float",
                2: "Bulk",
                3: "Absorb",
                4: "EQ"
            }
            if self.data['mode'] in modes:
                self.data['mode_text'] = modes[self.data['mode']]
            else:
                self.data['mode_text'] = "Unknown"
            regulations = {
                0: "Off",
                1: "Voltage",
                2: "Current",
                3: "Temperature",
                4: "Hardware",
                15: "MPPT"
                }
            if self.data['regulation']  in regulations:
                self.data['regulation_text'] = regulations[self.data['regulation']]
            else:
                self.data['regulation_text'] = "Unknown"
            faults = {
                0: "No Fault",
                1: "Input breaker Fault",
                2: "OPS Fault",
                3: "PV High Fault",
                4: "Battery High Fault",
                5: "BTS Shorted Fault",
                6: "FET Overtemp Fault",
                7: "Battery Overtemp Fault",
                8: "Over Current Fault",
                9: "Internal Phase Fault",
                10: "Open BTS Fault",
                11: "Internal Fault 1",
                12: "GFP Fault",
                13: "ARC Fault",
                14: "NTC Fault",
                15: "HW overtemp Fault",
                16: "Overyemp Fault",
                17: "USB Fault",
                20: "Stack Fault",
                21: "Stack warning",
                22: "Stack DIP Fault",
                23: "Stack DT Fault"
                }
            if self.data['fault'] in faults:
                self.data['fault_text'] = faults[self.data['fault']]
            else:
                self.data['fault_text'] = "unknown"
        elif packetType == PT_C2 and address == 0:
            self.data['lifetime_kwhrs'] = unpacked[2] * 10
            self.data['resettable_kwhrs'] = unpacked[3] / 10
            self.data['ground_fault_current'] = unpacked[4]
            byte_value = unpacked[5]
            self.data['stacker_info'] = byte_value >> 2
            byte_value = byte_value & 0x03
            if byte_value == 0:
                 self.data['nominal_battery_voltage']  = 12.0
            else:
                 self.data['nominal_battery_voltage']  = float(byte_value * 24.0)
            self.data['dip_switches'] = format(unpacked[6], '08b')
            self.data['revision'] = str(unpacked[7] / 10)
            # self.data['model'] = unpacked[7]
            self.data['model'] = 100 # That will have to do for now
            self.data['output_current_rating'] = unpacked[8]
            self.data['input_voltage_rating'] = unpacked[9] * 10
        # elif packetType == PT_C3 and address == 0:
        #     short_value = unpacked[1]
        #     self.data['daily_kwh'] = unpacked[2] / 10
        #     self.data['max_daily_pv_volts'] = unpacked[3]
        #     self.data['max_daily_pv_volts_time'] = unpacked[4] / 10
        #     self.data['max_daily_battery_volts'] = unpacked[5]
        #     self.data['max_daily_battery_volts_time'] = unpacked[6] / 10
        #     self.data['minimum_daily_battery_volts'] = unpacked[7]
        #     self.data['minimum_daily_battery_volts_time'] = unpacked[8] / 10
        #     self.data['daily_time_operational'] = unpacked[7] / 10
        #     self.data['daily_amp_hours'] = unpacked[10]
        #     self.data['peak_daily_power'] = unpacked[11]
        #     self.data['peak_daily_power_time'] = unpacked[12] / 10

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device
