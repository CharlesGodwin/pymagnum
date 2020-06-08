#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
#  This module tests the functonality of the serial interface
#  by attempting to read 50 packets of data and parsing them
#  The results are dumped to the terminal
#
import argparse
import time
import traceback

from magnum import magnum, __version__

def main():
    global args
    parser = argparse.ArgumentParser(
        description="Magnum RS485 Reader Test", fromfile_prefix_chars='@', prog="Magnum Test", epilog="Use `python -m serial.tools.list_ports` to identify devices.")
    parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                        help="Serial device name (default: %(default)s)")
    group = parser.add_argument_group("seldom used arguments")
    group.add_argument("-n", "--packets", default=50, type=int,
                    help="Number of packets to generate (default: %(default)s)")
    group.add_argument("-t", "--timeout", default=0.001, type=float,
                    help="Timeout for serial read - float between 0 and 1 second (default: %(default)s)")
    group.add_argument("-nc", "--nocleanup", action="store_true",
                    help="Suppress clean up of unknown packets (default: %(default)s)", dest='cleanpackets')
    group.add_argument("--trace", action="store_true", default=False,
                        help="Add most recent raw packet info to data (default: %(default)s)")
    args = parser.parse_args()
    if args.timeout < 0 or args.timeout > 1.0:
        parser.error(
            "argument -t/--timeout: must be a number (float) between 0 and 1 second. i.e. 0.005")
    if args.packets < 1:
        parser.error("argument -n/--packets: must be greater than 0.")
    args.cleanpackets = not args.cleanpackets
    print('Version:{0}'.format(__version__))
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
        formatstring = "Length:{0:2} {1:10}=>{2}"
        for packet in packets:
            if packet[0] == magnum.UNKNOWN:
                unknown += 1
            if args.trace:
                end = ' decode:'
            else:
                end = '\n'
            print(formatstring.format(len(packet[1]), packet[0], packet[1].hex().upper()), end=end)
            if args.trace:
                print(*packet[2], end = ' ')
                print(packet[3])
        format1 = "Packets:{0} of {1} with {2} UNKNOWN, in {3:2.2f} seconds"
        format2 = "Packets:{0} in {3:2.2f} seconds"
        format = format1 if unknown > 0 else format2
        print(format.format(len(packets), args.packets, unknown, duration))
    except:
        print("Error detected attempting to read network data - test failed")
        traceback.print_exc()
        exit(2)

if __name__ == '__main__':
    main()
