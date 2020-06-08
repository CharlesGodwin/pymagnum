#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
import argparse
import time
import traceback
import json
from os.path import abspath
try:
    from magnum import magnum
except:
    import magnum
# import magnum
# from magnum import magnum, __version__
# from magnum import Magnum, __version__

args = None
class dummypackets(magnum.Magnum):
    global args
    def readPackets(self):
        line = args.filename.readline()
        # If the file is not empty keep reading one line at a time, till the file is empty
        packets = []
        while line:
            ix = line.find("=>")
            decode = line.find("decode:")
            if ix >= 0:
                decode = line.find("decode:") # supports traced packets
                if decode > ix:
                    stop = decode
                else:
                    stop = len(line)
                packets.append(bytes.fromhex(line[ix+2:stop].strip()))
            line = args.filename.readline()
        args.filename.close()
        return packets

def main():
    global args
    parser = argparse.ArgumentParser("Magnum packet tester")
    parser.add_argument('-d', "--dump", action="store_true", default=False,
                        help="Display packets as JSON (default: %(default)s)")
    parser.add_argument("--trace", action="store_true", default=False,
                        help="Show unpacked info for packet data (default: %(default)s)")
    parser.add_argument("filename", type=argparse.FileType("r", encoding="UTF-8"),
                        help="File name with dummy packets" )
    args = parser.parse_args()
    # print('Version:{0}'.format(__version__))
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
    dummyreader = dummypackets(cleanpackets=False)
    try:
        if args.dump:
            devices = dummyreader.getDevices()
            print(json.dumps(devices, indent=4, ensure_ascii=True, allow_nan=True, separators=(',', ':')))
        else:
            packets=dummyreader.getPackets()
            formatstring = "Length:{0:2} {1:10}=>{2}"
            if args.trace:
                end = ' decode:'
            else:
                end ='\n'
            for packet in packets:
                print(formatstring.format(
                    len(packet[1]), packet[0], packet[1].hex().upper()), end = end)
                if args.trace:
                    print(*packet[2], end = ' ')
                    print(packet[3])
    except:
        print("Error detected attempting to read data - test failed")
        traceback.print_exc()
        exit(2)
    
if __name__ == '__main__':
    main()
