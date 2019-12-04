#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
import argparse
import time
import traceback
from os.path import abspath

from magnum import magnum, __version__

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

def main():
    global args
    parser = argparse.ArgumentParser("Magnum packet tester")
    parser.add_argument("filename", type=argparse.FileType("r", encoding="UTF-8"),
                        help="File name with dummy packets" )
    args = parser.parse_args()
    print('Version:{0}'.format(__version__))
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
    dummyreader = dummypackets()
    try:
        packets=dummyreader.getPackets()
        formatstring = "Length:{0:2} {1:10}=>{2}"
        for packet in packets:
            print(formatstring.format(
                len(packet[1]), packet[0], packet[1].hex().upper()))
    except:
        print("Error detected attempting to read network data - test failed")
        traceback.print_exc()
        exit(2)
    
if __name__ == '__main__':
    main()
