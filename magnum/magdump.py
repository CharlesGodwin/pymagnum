#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a JSON object
# run the program with --help for details of options.
# {
# 	"datetime": "2019-10-22 10:39:02-04:00",
# 	"device": "MAGNUM",
# 	"data": [
# 		{
# 			"device": "INVERTER",
# 			"data": {
# 				"revision": "5.1",
# 				"mode": 64,
# 				"mode_text": "INVERT",
# 				"fault": 0,
# 				"fault_text": "None",
# 				"vdc": 24.6,
# 				"adc": 2,
# 				"VACout": 121,
# 				"VACin": 0,
# 				"invled": 1,
# 				"invled_text": "On",
# 				"chgled": 0,
# 				"chgled_text": "Off",
# 				"bat": 17,
# 				"tfmr": 36,
# 				"fet": 30,
# 				"model": 107,
# 				"model_text": "MS4024PAE",
# 				"stackmode": 0,
# 				"stackmode_text": "Stand Alone",
# 				"AACin": 0,
# 				"AACout": 1,
# 				"Hz": 60.0
# 			}
# 		},
# 		{
# 			"device": "REMOTE",
# 			"data": {
# 				"revision": 2.3,
# 				"action": 0,
# 				"searchwatts": 0,
# 				"batterysize": 320,
# 				"battype": 4,
# 				"absorb": 0,
# 				"chargeramps": 80,
# 				"ainput": 15,
# 				"parallel": 60,
# 				"force_charge": 0,
# 				"genstart": 1,
# 				"lbco": 20.0,
# 				"vaccutout": 165,
# 				"vsfloat": 26.8,
# 				"vEQ": 0.1,
# 				"absorbtime": 0.0,
# 				"remotetimehours": 7,
# 				"remotetimemins": 57,
# 				"runtime": 3.6,
# 				"starttemp": -17.8,
# 				"startvdc": 22.0,
# 				"quiettime": 0,
# 				"begintime": 700,
# 				"stoptime": 700,
# 				"vdcstop": 27.0,
# 				"voltstartdelay": 70,
# 				"voltstopdelay": 29,
# 				"maxrun": 2.0,
# 				"socstart": 70,
# 				"socstop": 80,
# 				"ampstart": 0,
# 				"ampsstartdelay": 120,
# 				"ampstop": 20,
# 				"ampsstopdelay": 120,
# 				"quietbegintime": 2330,
# 				"quietendtime": 2345,
# 				"exercisedays": 0,
# 				"exercisestart": 0,
# 				"exerciseruntime": 0,
# 				"topoff": 2,
# 				"warmup": 30,
# 				"cool": 30,
# 				"batteryefficiency": 0,
# 				"resetbmk": 0
# 			}
# 		},
# 		{
# 			"device": "BMK",
# 			"data": {
# 				"revision": "1.0",
# 				"soc": 85,
# 				"vdc": 24.5,
# 				"adc": -6.6,
# 				"vmin": 22.03,
# 				"vmax": 31.91,
# 				"amph": -65,
# 				"amphtrip": 5761.9,
# 				"amphout": 5700,
# 				"Fault": 1,
# 				"Fault_Text": "Normal"
# 			}
# 		},
# 		{
# 			"device": "AGS",
# 			"data": {
# 				"revision": "5.2",
# 				"status": 2,
# 				"status_text": "Ready",
# 				"running": true,
# 				"temp": 14.4,
# 				"runtime": 0.0,
# 				"gen_last_run": 2,
# 				"last_full_soc": 0,
# 				"gen_total_run": 0,
# 				"vdc": 24.4
# 			}
# 		}
# 	]
# }
#
import argparse
import json
import time
import traceback
from collections import OrderedDict
from datetime import datetime

from tzlocal import get_localzone

import magnum
from magnum.magnum import Magnum


def main():
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
                        help="Add most recent raw packet(s) info to data (default: %(default)s)")
    seldom.add_argument("-nc", "--nocleanup", action="store_false",
                        help="Suppress clean up of unknown packets (default: %(default)s)", dest='cleanpackets')
    args = parser.parse_args()

    if args.verbose:
        print('Version:{0}'.format(magnum.__version__))
        print("Options:{}".format(str(args).replace(
            "Namespace(", "").replace(")", "")))
    magnumReader = Magnum(device=args.device, packets=args.packets, trace=args.trace,
                                        timeout=args.timeout, cleanpackets=args.cleanpackets)
    if args.interval != 0 and args.verbose == True:
        print("Dumping every:{1} seconds. Using: {0} ".format(
            args.device, args.interval))
    while True:
        start = time.time()
        devices = magnumReader.getDevices()
        if len(devices) != 0:
            try:
                alldata = OrderedDict()
                alldata["datetime"] = datetime.now(
                    get_localzone()).replace(microsecond=0).isoformat()
                alldata["device"] = 'MAGNUM'
                magnumdata = []
                for device in devices:
                    data = OrderedDict()
                    data["device"] = device["device"]
                    data["data"] = device["data"]
                    magnumdata.append(data)
                alldata["data"] = magnumdata
                print(json.dumps(
                    alldata, indent=None, ensure_ascii=True, allow_nan=True, separators=(',', ':')))
            except:
                traceback.print_exc()
        if args.interval == 0:
            break
        interval = time.time() - start
        sleep = args.interval - interval
        if sleep > 0:
            time.sleep(sleep)

if __name__ == '__main__':
    main()
