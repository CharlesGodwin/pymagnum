#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a simple program to display
# device data every 60 seconds.
# run the program with --help for details of options.

import argparse
import json
import time
from magnum.magnum import Magnum

parser = argparse.ArgumentParser(description="Magnum Data Extractor Example")
parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                    help="Serial device name (default: %(default)s)")
parser.add_argument("--trace", action="store_true", default=False,
                        help="Add packet data to JSON (default: %(default)s)")                    
parser.add_argument("-i", "--interval", default=60, type=int, dest='interval',
                    help="Interval, in seconds between logging (default: %(default)s)")
args = parser.parse_args()
reader = Magnum(device=args.device, trace=args.trace)
while True: 
    start = time.time()
    devices = reader.getDevices()
    print(json.dumps(devices, indent=2))
    duration = time.time() - start
    delay = args.interval - duration
    if delay > 0:
        time.sleep(delay)
