#!/usr/bin/env python3
# 
# Copyright (c) 2018-2022 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a simple program to display
# device data every 60 seconds.
# run the program with --help for details of options.

import json
import signal
import sys
import time

import magnum
from magnum.magnum import Magnum
from magnum.magparser import MagnumArgumentParser


def sigint_handler(signal, frame):
    print('Interrupted. Shutting down.')
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)
parser = MagnumArgumentParser(
    description="Magnum Data Extractor Example", fromfile_prefix_chars='@')
parser.add_argument("-d", "--device", nargs='*', action='append', default=[],
                    help="Serial device name (default: /dev/ttyUSB0). You can specify more than one.")
parser.add_argument("-i", "--interval", default=0, type=int, dest='interval',
                    help="Interval, in seconds, between dump records, in seconds. 0 means once and exit. (default: %(default)s)")
parser.add_argument('-v', "--verbose", action="store_true", default=False,
                    help="Display options at runtime (default: %(default)s)")
seldom = parser.add_argument_group("Seldom used")
seldom.add_argument('--version', action='version',
                    version="%(prog)s Version:{}".format(magnum.__version__))
seldom.add_argument("--packets", default=50, type=int,
                    help="Number of packets to generate in reader (default: %(default)s)")
seldom.add_argument("--timeout", default=0.005, type=float,
                    help="Timeout for serial read (default: %(default)s)")
seldom.add_argument("--trace", action="store_true", default=False,
                    help="Add most recent raw packet(s) info to data (default: %(default)s)")
seldom.add_argument("--nocleanup", action="store_true", default=False, dest='cleanpackets',
                    help="Suppress clean up of unknown packets (default: False)")
args = parser.magnum_parse_args()
if args.verbose:
    print(f"Magnum Sample Version:{magnum.__version__}")
    print(f"Options:{str(args)[10:-1]}")

magnumReaders = {}
for device in args.device:
    try:
        magnumReader = Magnum(device=device, packets=args.packets, trace=args.trace,
                              timeout=args.timeout, cleanpackets=args.cleanpackets)
        magnumReader.getDevices()  # test read to see if all's good
        magnumReaders[magnumReader.getComm_Device()] = magnumReader
    except Exception as e:
        print("{0} {1}".format(device, str(e)))
if len(magnumReaders) == 0:
    print("Error: There are no usable devices connected.")
    exit(2)
while True:
    start = time.time()
    for comm_device, magnumReader in magnumReaders.items():
        try:
            devices = magnumReader.getDevices()
            if len(magnumReaders) > 1:
                data = {}
                data['comm_device'] = comm_device
                data["data"] = devices
                print(json.dumps(data, indent=2))
            else:
                print(json.dumps(devices, indent=2))
        except Exception as e:
            print("{0} {1}".format(comm_device, str(e)))
    if args.interval == 0:
        break
    duration = time.time() - start
    delay = args.interval - duration
    if delay > 0:
        time.sleep(delay)
