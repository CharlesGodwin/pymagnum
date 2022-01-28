#
# Copyright (c) 2018-2022 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a JSON object
# run the program with --help for details of options.
#
import json
import signal
import sys
import time

from collections import OrderedDict
from datetime import datetime

from tzlocal import get_localzone

import magnum
from magnum.magnum import Magnum
from magnum.magparser import MagnumArgumentParser


def sigint_handler(signal, frame):
    print('Interrupted. Shutting down.')
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, sigint_handler)
    parser = MagnumArgumentParser(description="Magnum Data Dump", prog="Magnum Dump", fromfile_prefix_chars='@',
                                  epilog="Refer to https://github.com/CharlesGodwin/pymagnum for details")
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
        print('Magnum Dump Version:{0}'.format(magnum.__version__))
        print("Options:{0}".format(str(args)
                                  .replace('Namespace(', '')
                                   .replace(')', '')
                                   .replace('[', '')
                                   .replace('\'', '')
                                   .replace(']', '')))
    magnumReaders = dict()
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
    if args.interval != 0 and args.verbose == True:
        print("Dumping every:{1} seconds. Using: {0} ".format(
            list(magnumReaders.keys()), args.interval))
    while True:
        start = time.time()
        for comm_device, magnumReader in magnumReaders.items():
            try:
                devices = magnumReader.getDevices()
                if len(devices) != 0:
                    alldata = OrderedDict()
                    alldata["datetime"] = datetime.now(
                        get_localzone()).replace(microsecond=0).isoformat()
                    alldata["device"] = 'MAGNUM'
                    alldata['comm_device'] = comm_device
                    magnumdata = []
                    for device in devices:
                        data = OrderedDict()
                        data["device"] = device["device"]
                        data["data"] = device["data"]
                        magnumdata.append(data)
                    alldata["data"] = magnumdata
                    print(json.dumps(
                        alldata, indent=None, ensure_ascii=True, allow_nan=True, separators=(',', ':')))
            except Exception as e:
                print("{0} {1}".format(comm_device, str(e)))
        if args.interval == 0:
            break
        interval = time.time() - start
        sleep = args.interval - interval
        if sleep > 0:
            time.sleep(sleep)


if __name__ == '__main__':
    main()
