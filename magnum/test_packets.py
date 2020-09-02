#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
import argparse
import json
import time
import traceback
from os.path import abspath

import magnum
from magnum.magnum import Magnum

args = None
class dummypackets(Magnum):
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
                        help="Add most recent raw packet(s) info to data (default: %(default)s)")                        
    parser.add_argument("filename", type=argparse.FileType("r", encoding="UTF-8"),
                        help="File name with dummy packets" )
    args = parser.parse_args()
    # print('Version:{0}'.format(__version__))
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
    dummyreader = dummypackets(cleanpackets=False, trace=True)
    try:
        if args.dump:
            devices = dummyreader.getDevices()
            print(json.dumps(devices, indent=4, ensure_ascii=True, allow_nan=True, separators=(',', ':')))
        else:
            packets=dummyreader.getPackets()
            formatstring = "Length:{0:2} {1:10}=>{2}"
            device_list = dict()
            for item in [magnum.INVERTER, magnum.REMOTE, magnum.RTR, magnum.BMK, magnum.AGS, magnum.PT100, magnum.ACLD]:
                device_list[item] = 'NA'
            device_list[magnum.RTR] = False
            if args.trace:
                end = ' decode:'
            else:
                end ='\n'
            for packet in packets:
                packetType = packet[0]
                if packetType in (magnum.INV, magnum.INV_C):
                    device_list[magnum.INVERTER]  = True
                elif packetType in (magnum.REMOTE_C,
                                    magnum.REMOTE_00):
                    device_list[magnum.REMOTE]  = True
                elif packetType == magnum.REMOTE_11:
                    pass #ignored
                elif packetType == magnum.REMOTE_80:
                    device_list[magnum.REMOTE]  = True
                    if device_list[magnum.BMK]  != True:
                        device_list[magnum.BMK]  = False
                elif packetType in (
                                    magnum.REMOTE_A0,
                                    magnum.REMOTE_A1,
                                    magnum.REMOTE_A2,
                                    magnum.REMOTE_A3,
                                    magnum.REMOTE_A4):
                    device_list[magnum.REMOTE]  = True
                    if device_list[magnum.AGS]  != True:
                        device_list[magnum.AGS]  = False
                elif packetType in (
                                    magnum.REMOTE_C0,
                                    magnum.REMOTE_C1,
                                    magnum.REMOTE_C2,
                                    magnum.REMOTE_C3
                                    ):
                    device_list[magnum.REMOTE]  = True
                    if device_list[magnum.PT100]  != True:
                        device_list[magnum.PT100]  = False            
                elif packetType == magnum.REMOTE_D0:
                    device_list[magnum.REMOTE]  = True
                    if device_list[magnum.ACLD]  != True:
                            device_list[magnum.ACLD]  = False  
                elif packetType == magnum.BMK_81:
                    device_list[magnum.BMK]  = True 
                elif packetType in (magnum.AGS_A1, magnum.AGS_A2):
                    device_list[magnum.AGS]  = True 
                elif packetType == magnum.RTR_91:
                    device_list[magnum.RTR]  = True 
                elif packetType in (magnum.PT_C1, magnum.PT_C2, magnum.PT_C3):
                    device_list[magnum.PT100]  = True       
                elif packetType == magnum.ACLD_D1:
                    device_list[magnum.ACLD]  = True        
                print(formatstring.format(
                    len(packet[1]), packet[0], packet[1].hex().upper()), end = end)
                if args.trace:
                    print(*packet[2], end = ' ')
                    print(packet[3])
            for key, value in device_list.items():
                if value == 'NA':
                    print ("{0} not supported".format(key))
                elif value == False:
                    print ("{0} not connected".format(key))
                else:
                    print("{0} Detected".format(key))
            if device_list[magnum.PT100] == True:
                print ("{0} has limited support, contact the author.".format(magnum.PT100))
            if device_list[magnum.ACLD] == True:
                print ("{0} is not currently supported, contact the author.".format(magnum.ACLD))
    except:
        print("Error detected attempting to read data - test failed")
        traceback.print_exc()
        exit(2)
    
if __name__ == '__main__':
    main()
