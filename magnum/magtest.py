#
# Copyright (c) 2018-2022 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
#  This module tests the functionality of the serial interface
#  by attempting to read 50 packets of data and parsing them
#  The results are dumped to the terminal

import os
import signal
import sys
import time

import magnum
from magnum.magnum import Magnum
from magnum.magparser import MagnumArgumentParser


class Logger(object):
    def __init__(self, logname=None):
        self.terminal = sys.stdout
        if logname:
            self.log = open(logname, 'w')
        else:
            self.log = None

    def write(self, message):
        self.terminal.write(message)
        if self.log:
            self.log.write(message)

    def flush(self):
        if self.log and not self.log.closed:
            self.log.flush()

    def close(self):
        if self.log:
            self.log.close()


def sigint_handler(signal, frame):
    print('Interrupted. Shutting down.')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, sigint_handler)
    parser = MagnumArgumentParser(
        description="Magnum RS485 Reader Test", prog="Magnum Test",
        epilog="Use `python -m serial.tools.list_ports` to identify devices. This program does NOT support use of options @file.")
    parser.add_argument("-d", "--device", default=[],
                        help="Serial device name (default: /dev/ttyUSB0). MUST be only one device.")
    parser.add_argument("--packets", default=50, type=int,
                        help="Number of packets to generate in reader (default: %(default)s)")
    parser.add_argument("--timeout", default=0.005, type=float,
                        help="Timeout for serial read (default: %(default)s)")

    seldom = parser.add_argument_group("Seldom used")
    seldom.add_argument('--version', action='version',
                        version="%(prog)s Version:{}".format(magnum.__version__))
    seldom.add_argument("--trace", action="store_true", default=False,
                       help="Add most recent raw packet(s) info to data (default: %(default)s)")
    seldom.add_argument("--nocleanup", action="store_true", default=False, dest='cleanpackets',
                         help="Suppress clean up of unknown packets (default: False)")
    seldom.add_argument("--log", action="store_true", default=False,
                       help="Write copy of program output to log file in current directory (default: %(default)s)")
    args = parser.magnum_parse_args()
    # Only supports one device
    args.device = args.device[0]
    if args.log:
        logfile = os.path.join(os.getcwd(), "magtest_" + time.strftime("%Y-%m-%d_%H%M%S") + ".txt")
        print(f"Output is being logged to {logfile}")
        sys.stdout = Logger(logname=logfile)
    print('Magnum Test Version:{0}'.format(magnum.__version__))
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
    try:
        reader = Magnum(device=args.device, packets=args.packets, trace=args.trace,
                        timeout=args.timeout, cleanpackets=args.cleanpackets)
    except Exception as e:
        print("{0} {1}".format(args.device, str(e)))
        exit(2)
    try:
        start = time.time()
        packets = reader.getPackets()
        duration = time.time() - start
        unknown = 0
        formatstring = "Length:{0:2} {1:10}=>{2}"
        device_list = dict()
        for item in [magnum.INVERTER, magnum.REMOTE, magnum.RTR, magnum.BMK, magnum.AGS, magnum.PT100, magnum.ACLD]:
            device_list[item] = 'NA'
        device_list[magnum.RTR] = False
        for packet in packets:
            if packet[0] == magnum.UNKNOWN:
                unknown += 1
            if args.trace:
                end = ' decode:'
            else:
                end = '\n'
            print(formatstring.format(
                len(packet[1]), packet[0], packet[1].hex().upper()), end=end)
            if args.trace:
                print(*packet[2], end=' ')
                print(packet[3])
            packetType = packet[0]
            if packetType in (magnum.INV, magnum.INV_C):
                device_list[magnum.INVERTER] = True
            elif packetType in (magnum.REMOTE_C,
                                magnum.REMOTE_00):
                device_list[magnum.REMOTE] = True
            elif packetType == magnum.REMOTE_11:
                pass  # ignored
            elif packetType == magnum.REMOTE_80:
                device_list[magnum.REMOTE] = True
                if device_list[magnum.BMK] != True:
                    device_list[magnum.BMK] = False
            elif packetType in (
                    magnum.REMOTE_A0,
                    magnum.REMOTE_A1,
                    magnum.REMOTE_A2,
                    magnum.REMOTE_A3,
                    magnum.REMOTE_A4):
                device_list[magnum.REMOTE] = True
                if device_list[magnum.AGS] != True:
                    device_list[magnum.AGS] = False
            elif packetType in (
                magnum.REMOTE_C0,
                magnum.REMOTE_C1,
                magnum.REMOTE_C2,
                magnum.REMOTE_C3
            ):
                device_list[magnum.REMOTE] = True
                if device_list[magnum.PT100] != True:
                    device_list[magnum.PT100] = False
            elif packetType == magnum.REMOTE_D0:
                device_list[magnum.REMOTE] = True
                if device_list[magnum.ACLD] != True:
                    device_list[magnum.ACLD] = False
            elif packetType == magnum.BMK_81:
                device_list[magnum.BMK] = True
            elif packetType in (magnum.AGS_A1, magnum.AGS_A2):
                device_list[magnum.AGS] = True
            elif packetType == magnum.RTR_91:
                device_list[magnum.RTR] = True
            elif packetType in (magnum.PT_C1, magnum.PT_C2, magnum.PT_C3):
                device_list[magnum.PT100] = True
            elif packetType == magnum.ACLD_D1:
                device_list[magnum.ACLD] = True

        format1 = "Packets:{0} of {1} with {2} UNKNOWN, in {3:2.2f} seconds"
        format2 = "Packets:{0} in {3:2.2f} seconds"
        format = format1 if unknown > 0 else format2
        print(format.format(len(packets), args.packets, unknown, duration))
    # Analyze packets
        if len(packets) > unknown:
            for key, value in device_list.items():
                if value == 'NA':
                    print(f"{key} not supported")
                elif value == False:
                    print(f"{key} not connected")
                else:
                    print(f"{key} Detected")
            if device_list[magnum.PT100] == True:
                print(f"{magnum.PT100} has limited support, contact the author.")
            if device_list[magnum.ACLD] == True:
                print("f{magnum.ACLD} is not currently supported, contact the author.")
        if args.log:
            print(f"Output was logged to {logfile}")
    except Exception as e:
        print("{0} {1}".format(reader.getComm_Device(), str(e)))
        print("Error detected attempting to read network data - test failed.")
        exit(2)

if __name__ == '__main__':
    main()
