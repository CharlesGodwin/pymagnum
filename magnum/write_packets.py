#
# Copyright (c) 2018-2022 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
import serial
import time
import argparse
import traceback
from os.path import abspath

parser = argparse.ArgumentParser("Magnum mock packet writer")
parser.add_argument("--device", default="/dev/ttyUSB0",
                    help="Serial device (default: %(default)s)")
parser.add_argument("filename", type=argparse.FileType("r", encoding="UTF-8"),
                    help="File name with dummy packets" )
parser.add_argument("--timeout",  default=0.005, type=float,
                    help="Interpacket sleep time. (default: %(default)s seconds)")
parser.add_argument("--useall", dest='useall', default=False,
                    action='store_true', help="Use UNKNOWN packets. (default: %(default)s)")
args = parser.parse_args()
print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
device = args.device
sleeptime = args.timeout
useall = args.useall

try:
    writer = serial.Serial(port=args.device,
                            baudrate=19200,
                            bytesize=8,
                            stopbits=serial.STOPBITS_ONE,
                            parity=serial.PARITY_NONE,
                            exclusive=True,
                            write_timeout=1.0
                            )

except Exception as e:
    print('Error: Failed to open communications port, exiting')
    traceback.print_exc()
    exit(2)

line = args.filename.readline()
# If the file is not empty keep reading one line at a time, till the file is empty
packets = []
while line:
    ix = line.find("=>")
    if ix >= 0:
        if useall or line.find('UNKNOWN') == -1:
            packets.append(bytes.fromhex(line[ix+2:].strip()))
    # use realine() to read next line
    line = args.filename.readline()
args.filename.close()
print("Processing:{} records from:{} using {}".format(
    len(packets), abspath(args.filename.name), args.device))

try:
    while True:
        for packet in packets:
            writer.write(packet)
            writer.flush()
            time.sleep(sleeptime)
except Exception as e:
    print('Error: Timeout on write, exiting')
    traceback.print_exc()
    exit()
