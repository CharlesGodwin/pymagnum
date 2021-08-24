#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a JSON logger that writers to MQTT
# run the program with --help for details of options.
# Each device is a separate JSON record new-line delimited
# The JSON Record is like this:
# datetime is a timestamp for local time
# timestamp is the same time but as a Unix Epoch second as UTC time - this is useful for time series software
# the data object is pertinent to each device
# The current devices are INVERTER, REMOTE, AGS, BMK, and PT100
# topic =  magnum/inverter
# payload
# {
# 	"datetime": "2019-10-08 12:49:14-04:00",
# 	"device": "INVERTER",
# 	"data": {
# 		"revision": "5.1",
# 		"mode": 64,
# 		"mode_text": "INVERT",
# 		"fault": 0,
# 		"fault_text": "None",
# 		"vdc": 24.6,
# 		"adc": 2,
# 		"VACout": 119,
# 		"VACin": 0,
# 		"invled": 1,
# 		"invled_text": "On",
# 		"chgled": 0,
# 		"chgled_text": "Off",
# 		"bat": 17,
# 		"tfmr": 36,
# 		"fet": 30,
# 		"model": 107,
# 		"model_text": "MS4024PAE",
# 		"stackmode": 0,
# 		"stackmode_text": "Stand Alone",
# 		"AACin": 0,
# 		"AACout": 1,
# 		"Hz": 60.0
# 	}
# }
import argparse
import json
import time
import traceback
import uuid
from collections import OrderedDict
from datetime import datetime

import paho.mqtt.client as mqtt
from magnum.magnum import Magnum
from tzlocal import get_localzone

parser = argparse.ArgumentParser(description="Magnum Data MQTT Publisher",
                                 epilog="Refer to https://github.com/CharlesGodwin/pymagnum for details")
logger = parser.add_argument_group("MQTT publish")
reader = parser.add_argument_group("Magnum reader")
seldom = parser.add_argument_group("Seldom used")
logger.add_argument("-t", "--topic", default='magnum/',
                    help="Topic prefix (default: %(default)s)")
logger.add_argument("-b", "--broker", default='localhost',
                    help="MQTT Broker address (default: %(default)s)")
seldom.add_argument("-p", "--port", default=1883, type=int,
                    help="Broker port (default: %(default)s)")
logger.add_argument("-i", "--interval", default=60, type=int, dest='interval',
                    help="Interval, in seconds, between publishing (default: %(default)s)")
reader.add_argument("-d", "--device", default="/dev/ttyUSB0",
                    help="Serial device name (default: %(default)s)")
seldom.add_argument("--packets", default=50, type=int,
                    help="Number of packets to generate in reader (default: %(default)s)")
seldom.add_argument("--timeout", default=0.005, type=float,
                    help="Timeout for serial read (default: %(default)s)")
seldom.add_argument("--trace", action="store_true",
                    help="Add raw packet info to data (default: %(default)s)")
seldom.add_argument("-nc", "--nocleanup", action="store_false",
                    help="Suppress clean up of unknown packets (default: %(default)s)", dest='cleanpackets')

args = parser.parse_args()
if args.interval < 10 or args.interval > (60*60):
    parser.error(
        "argument -i/--interval: must be between 10 seconds and 3600 (1 hour)")
if args.topic[-1] != "/":
    args.topic += "/"
print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
magnumReader = Magnum(device=args.device, packets=args.packets, trace=args.trace,
                             timeout=args.timeout, cleanpackets=args.cleanpackets)
print("Publishing to broker:{0} Every:{2} seconds. Using: {1} ".format(args.broker, args.device, args.interval))
uuidstr = str(uuid.uuid1())
client = mqtt.Client(client_id=uuidstr, clean_session=False)
while True:
    start = time.time()
    devices = magnumReader.getDevices()
    if len(devices) != 0:
        try:
            client.connect(args.broker)
            data = OrderedDict()
            now = int(time.time())
            data["datetime"] = datetime.now(
                get_localzone()).replace(microsecond=0).isoformat()
            for device in devices:
                topic = args.topic + device["device"].lower()
                data["device"] = device["device"]
                data["data"] = device["data"]
                payload = json.dumps(
                    data, indent=None, ensure_ascii=True, allow_nan=True, separators=(',', ':'))
                client.publish(topic, payload=payload)
            client.disconnect()
        except:
            traceback.print_exc()
    interval = time.time() - start
    sleep = args.interval - interval
    if sleep > 0:
        time.sleep(sleep)
