#
# Copyright (c) 2018-2023 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a JSON logger that writes to MQTT
# The data is published at every interval seconds
# If you publish the subtopic 'refresh' (i.e magnum/refresh) this will publish data immediately
# run the program with --help for details of options.
# Each device is a separate JSON record new-line delimited
# The JSON Record is like this:
# datetime is a timestamp for local time
# timestamp is the same time but as a Unix Epoch second as UTC time - this is useful for time series software
# the data object is pertinent to each device
# The current devices are INVERTER, REMOTE, AGS, BMK, and PT100
# topic =  magnum/inverter
# payload - refer to testdata/allpackets.json
#  NOTE This will only work with paho.mqtt Version 2.0 and newer
#
import json
import signal
import sys
import time
import uuid
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.reasoncodes import ReasonCode
from magnum.magnum import Magnum
from magnum.magparser import MagnumArgumentParser


def on_connect(client: mqtt.Client, userdata, connect_flags: mqtt.ConnectFlags, reason_code: ReasonCode, properties):
    if reason_code.is_failure:
        raise Exception(f"Connection failed. {ReasonCode.getName(reason_code)}")
    else:
        global args
        client.subscribe(f"{args.topic}refresh")
        if args.trace:
            print("Connected")


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    global args
    if message.topic == f"{args.topic}refresh":
        publish_data()


def on_publish(client: mqtt.Client, userdata, mid: int, reason_code: ReasonCode, properties):
    print(f"Message {mid} published\n")


def sigint_handler(signal, frame):
    print('Interrupted. Shutting down.')
    global client
    client.disconnect()
    client.loop_stop()
    sys.exit(0)


def publish_data():
    global magnumReaders, client, args
    try:
        for comm_device, magnumReader in magnumReaders.items():
            try:
                devices = magnumReader.getDevices()
                if len(devices) != 0:
                    data = {}
                    now = int(time.time())
                    data["datetime"] = datetime.now(timezone.utc).replace(
                        microsecond=0).astimezone().isoformat()
                    data['comm_device'] = comm_device
                    for device in devices:
                        topic = args.topic + device["device"].lower()
                        data["device"] = device["device"]
                        data["data"] = device["data"]
                        payload = json.dumps(data, indent=None, ensure_ascii=True, allow_nan=True, separators=(',', ':'))
                        client.publish(topic, payload=payload)
            except Exception as e:
                print(f"{comm_device} {str(e)}")
    except Exception as e:
        print(str(e))


signal.signal(signal.SIGINT, sigint_handler)
parser = MagnumArgumentParser(description="Magnum Data MQTT Publisher", fromfile_prefix_chars='@',
                              epilog="Refer to https://github.com/CharlesGodwin/pymagnum for details")
logger = parser.add_argument_group("MQTT publish")
reader = parser.add_argument_group("Magnum reader")
logger.add_argument("-t", "--topic", default='magnum/', help="Topic prefix (default: %(default)s)")
logger.add_argument("-b", "--broker", default='localhost:1883', help="MQTT Broker address and (optional port)(default: %(default)s)")
logger.add_argument("-i", "--interval", default=60, type=int, dest='interval', help="Interval, in seconds, between publishing (default: %(default)s)")
logger.add_argument("-u", "--username", default='None', help="MQTT User name, if needed (default: %(default)s)")
logger.add_argument("-p", "--password", default='None', help="MQTT User password, if needed (default: %(default)s)")
reader.add_argument("-d", "--device", nargs='*', action='append', default=[], help="Serial device name (default: /dev/ttyUSB0). You can specify more than one.")
reader.add_argument("--packets", default=50, type=int, help="Number of packets to generate in reader (default: %(default)s)")
reader.add_argument("--timeout", default=0.005, type=float, help="Timeout for serial read (default: %(default)s)")
reader.add_argument("--trace", action="store_true", help="Add raw packet info to data (default: %(default)s)")
reader.add_argument("--nocleanup", action="store_true", default=False, dest='cleanpackets', help="Suppress clean up of unknown packets (default: False)")
args = parser.magnum_parse_args()
if args.interval < 10 or args.interval > (60*60):
    parser.error("Argument -i/--interval: Must be between 10 seconds and 3600 (1 hour)")
if args.topic[-1] != "/":
    args.topic += "/"
savepw = args.password
args.password = "******"
print(f"Options:{str(args)[10:-1]}")
args.password = savepw
magnumReaders = {}
for device in args.device:
    try:
        magnumReader = Magnum(device=device, packets=args.packets, trace=args.trace,timeout=args.timeout, cleanpackets=args.cleanpackets)
        magnumReader.getDevices()  # test read to see if all's good
        magnumReaders[magnumReader.getComm_Device()] = magnumReader
    except Exception as e:
        print(f"{e} {device}")
if len(magnumReaders) == 0:
    print("Error: There are no usable devices connected.")
    exit(2)

uuidstr = str(uuid.uuid1())
brokerinfo = args.broker.split(':')
if len(brokerinfo) == 1:
    brokerinfo.append(1883)
client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=uuidstr, clean_session=False)
if args.username != 'None':
    client.username_pw_set(username=args.username, password=args.password)
client.on_connect = on_connect
client.on_message = on_message
if args.trace:
    client.on_publish = on_publish
try:
    client.connect(brokerinfo[0], port=int(brokerinfo[1]))
except Exception as e:
    print(f"Failed to connect to broker {brokerinfo[0]}:{brokerinfo[1]}, exiting")
    print(f"Reason: {e}")
    exit(2)
print(f"Publishing to broker:{brokerinfo[0]}:{brokerinfo[1]} Every:{args.interval} seconds. Using: {list(magnumReaders.keys())}")
client.loop_start()
while True:
    start = time.time()
    publish_data()
    sleep = args.interval - (time.time() - start)
    if sleep > 0:
        time.sleep(sleep)
