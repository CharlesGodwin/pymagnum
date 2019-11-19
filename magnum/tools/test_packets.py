#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
import time
import argparse
import traceback
from os.path import abspath
import magnum


class dummypackets(magnum.Magnum):
    def readPackets(self):
        line = args.filename.readline()
        # If the file is not empty keep reading one line at a time, till the file is empty
        packets = []
        while line:
            ix = line.find("=>")
            if ix >= 0:
                packets.append(bytes.fromhex(line[ix+2:].strip()))
            line = args.filename.readline()
        args.filename.close()
        return packets

parser = argparse.ArgumentParser("Magnum packet tester")
parser.add_argument("filename", type=argparse.FileType("r", encoding="UTF-8"),
                    help="File name with dummy packets" )
args = parser.parse_args()
print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
dummyreader = dummypackets()
try:
    packets=dummyreader.getPackets()
    formatstring = "Length:{0:2} {1:10}=>{2}"
    for packet in packets:
        if packet[0] == magnum.UNKNOWN:
            unknown += 1
        print(formatstring.format(
            len(packet[1]), packet[0], packet[1].hex().upper()))
except:
    print("Error detected attempting to read network data - test failed")
    traceback.print_exc()
    exit(2)


