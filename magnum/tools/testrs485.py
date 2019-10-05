#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
#  This module tests the functonality of the serial interface
#  by attempting to read 50 packets of def and parsing them
#  The results are dumped to the terminal
#
import argparse
import json
import traceback
import time

from magnum import magnum
def main():
    parser = argparse.ArgumentParser(description="Magnum RS485 Reader Test", fromfile_prefix_chars='@',
                                     prog="magtest", epilog="If neither --showpackets or --showjson enabled, default is --showpackets")
    parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                        help="Serial device name (default: %(default)s)")
    parser.add_argument("-p", "--showpackets", action="store_true",
                        help="Display raw packet information (default: %(default)s)")
    parser.add_argument("-j", "--showjson", action="store_true",
                        help="Display generated JSON information (default: %(default)s)")
    group = parser.add_argument_group("seldom used arguments")
    group.add_argument("-n", "--packets", default=50, type=int,
                        help="Number of packets to generate (default: %(default)s)")
    group.add_argument("-t", "--timeout", default=0.001, type=float,
                        help="Timeout for serial read - float between 0 and 1 second (default: %(default)s)")
    group.add_argument("-nc", "--nocleanup", action="store_true",
                        help="Suppress clean up of unknown packets (default: %(default)s)", dest='cleanpackets')

    args = parser.parse_args()
    if args.timeout < 0 or args.timeout > 1.0:
        parser.error("argument -t/--timeout: must be a number (float) between 0 and 1")
    if args.packets < 1:
        parser.error("argument -n/--packets: must be greater than 0.")
    if not args.showpackets and not args.showjson:
        args.showpackets = True
    args.cleanpackets = not args.cleanpackets
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
    try:
        reader = magnum.Magnum(device=args.device, packets=args.packets,
                            timeout=args.timeout, cleanpackets=args.cleanpackets)
    except:
        print("Error detected attempting to open serial device")
        traceback.print_exc()
        exit(2)
    try:
        start = time.time()
        packets = reader.getPackets()
        duration = time.time() - start
        unknown = 0
        if args.showpackets:
            print("Packets")
            formatstring = "Length:{0:2} {1:10}=>{2}"
        for packet in packets:
            if packet[0] == magnum.UNKNOWN:
                unknown += 1
            if args.showpackets:
                print(formatstring.format(len(packet[1]), packet[0], packet[1].hex().upper()))
        if args.showpackets:
            print()
        if args.showjson:
            try:
                models = reader.getModels(packets)
            except:
                print("Error detected attempting to extract models")
                traceback.print_exc()
                exit(2)
            print("Data")
            print(json.dumps(models, indent=2))
        format1 = "Packets:{0} of {1} with {2} UNKNOWN, in {3:2.2f} seconds"
        format2 = "Packets:{0} in {3:2.2f} seconds"
        format = format1 if unknown > 0 else format2
        print(format.format(len(packets), args.packets, unknown, duration))
    except:
        print("Error detected attempting to read network data - test failed")
        traceback.print_exc()
        exit(2)

if __name__ == "__main__":
    main()
