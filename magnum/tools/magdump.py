#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a JSON logger
# run the program with --help for details of options.
# Each device is a seperate JSON record new-line delimited
# The JSON Record is like this:
# datetime is a timestamp for local time
# timestamp is the same time but as a Unix Epoch second as UTC time - this is useful for time series software
# the data object is pertiement to each device
# The curent devices are INVERTER, REMOTE, AGS, BMK, and PT100
# topic =  magnum/inverter
# payload
# {
# 	"datetime": "2019-10-08 12:49:14-04:00",
# 	"device": "INVERTER",
# 	"data": {
# 		"revision": "5.1",
# 		"mode": 64,
# 		"mode_text": "INVERT",
# 		"fault": 0,
# 		"fault_text": "None",
# 		"vdc": 24.6,
# 		"adc": 2,
# 		"VACout": 119,
# 		"VACin": 0,
# 		"invled": 1,
# 		"invled_text": "On",
# 		"chgled": 0,
# 		"chgled_text": "Off",
# 		"bat": 17,
# 		"tfmr": 36,
# 		"fet": 30,
# 		"model": 107,
# 		"model_text": "MS4024PAE",
# 		"stackmode": 0,
# 		"stackmode_text": "Stand Alone",
# 		"AACin": 0,
# 		"AACout": 1,
# 		"Hz": 60.0
# 	}
# }
import argparse
import json
import time
import traceback
from collections import OrderedDict
from datetime import datetime

from magnum import magnum

parser = argparse.ArgumentParser(description="Magnum Data Dump",
                                 epilog="Refer to https://github.com/CharlesGodwin/pymagnum for details")
parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                    help="Serial device name (default: %(default)s)")
parser.add_argument("-i", "--interval", default=0, type=int, dest='interval',
                    help="Interval, in seconds, between dump records, in seconds. 0 means once and exit. (default: %(default)s)")
parser.add_argument('-v', "--verbose", action="store_true", default=False,
                    help="Display options at runtime (default: %(default)s)")
seldom = parser.add_argument_group("Seldom used")
seldom.add_argument("--packets", default=50, type=int,
                    help="Number of packets to generate in reader (default: %(default)s)")
seldom.add_argument("--timeout", default=0.005, type=float,
                    help="Timeout for serial read (default: %(default)s)")
seldom.add_argument("--trace", action="store_true", default=False,
                    help="Add most recent raw packet info to data (default: %(default)s)")
seldom.add_argument("-nc", "--nocleanup", action="store_false",
                    help="Suppress clean up of unknown packets (default: %(default)s)", dest='cleanpackets')
args = parser.parse_args()

if args.verbose:
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
magnumReader = magnum.Magnum(device=args.device, packets=args.packets,
                             timeout=args.timeout, cleanpackets=args.cleanpackets)
if args.interval != 0 and args.verbose == True:
    print("Dumping every:{1} seconds. Using: {0} ".format(
        args.device, args.interval))
while True:
    start = time.time()
    devices = magnumReader.getDevices()
    if len(devices) != 0:
        try:
            magnumdata = []
            now = int(time.time())
            for device in devices:
                data = OrderedDict()
                data["datetime"] = str(
                    datetime.fromtimestamp(now).astimezone())
                data["device"] = device["device"]
                data["data"] = device["data"]
                magnumdata.append(data)
            print(json.dumps(
                magnumdata, indent=None, ensure_ascii=True, allow_nan=True, separators=(',', ':')))
        except:
            traceback.print_exc()
    if args.interval == 0:
        break
    interval = time.time() - start
    sleep = args.interval - interval
    if sleep > 0:
        time.sleep(sleep)
