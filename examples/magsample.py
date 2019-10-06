#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a simple program to display
# model data every 60 seconds.
# run the program with --help for details of options.

import argparse
import json
import time

from magnum import magnum

parser = argparse.ArgumentParser(description="Magnum Data Extractor Example")
parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                    help="Serial device name (default: %(default)s)")
parser.add_argument("-i", "--interval", default=30, type=int, dest='interval',
                    help="Interval, in seconds between logging (default: %(default)s)")
args = parser.parse_args()
reader = magnum.Magnum(device=args.device)
while True: 
    start = time.time()
    models = reader.getModels()
    print(json.dumps(models, indent=2))
    duration = time.time() - start
    delay = args.interval - duration
    if delay > 0:
        time.sleep(delay)
