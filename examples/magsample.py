#!/usr/bin/env python3
#
# This software was developed by Charles Godwin magnum@godwin.ca
#
# Copyright (c) 2019
#
#   cgmagnum package This software is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   cgmagnum is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License.
#   If not, see <http://www.gnu.org/licenses/>
# 
# This is a sample program for using the Magnum reader class.
#
# It is meant to provide an example of how to use the reader to produce JSON otput.
#
# 

import argparse
import json
import time

from magnum import Magnum

parser = argparse.ArgumentParser(description="Magnum Data Extractor Example")
parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                    help="Serial device name (default: %(default)s)")
parser.add_argument("-t", "--time", default=30, type=int, dest='interval',
                    help="Seconds between logging (default: %(default)s)")
args = parser.parse_args()
reader = Magnum(device=args.device)
while True: 
    start = time.time()
    models = reader.getModels()
    print(json.dumps(models, indent=2))
    duration = time.time() - start
    delay = args.interval - duration
    if delay > 0:
        time.sleep(delay)
