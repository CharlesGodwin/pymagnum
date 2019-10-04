#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a JSON logger
# run the program with --help for details of options.
# By default consectutive duplicate data records are not logged.
# Each device is a seperate JSON record new-line delimited
# The JSON Record is like this:
    # datetime is a timestamp for local time
    # timestamp is the same time but as a Unix Epoch second as UTC time - this is useful for time series software
    # the data object is pertiement to each model
    # The curent models are INVERTER, REMOTE, AGS, BMK, and PT100
# {
# 	"datetime": "2019-09-30 15:59:03-04:00",
# 	"timestamp": 1569873543,
# 	"model": "INVERTER",
# 	"data": {
# 		"revision": "5.1",
# 		"mode": 64,
# 		"mode_text": "INVERT",
# 		"fault": 0,
# 		"fault_text": "None",
# 		"vdc": 24.6,
# 		"adc": 2,
# 		"VACout": 120,
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
from collections import OrderedDict
from http import HTTPStatus
from os.path import abspath

from magnum import magnum
import requests

parser = argparse.ArgumentParser(description="Magnum Data Logger")
parser.add_argument("logfile", type=argparse.FileType(
    'a', encoding='UTF-8'), help="output file name - required")
parser.add_argument("-s", "--server", default="localhost",
                    help="The IP address or URL of Magnum Server (default: %(default)s)")
parser.add_argument("-p", "--port", type=int, default=17223,
                    help="The port on the server (default: %(default)s)")
parser.add_argument("-t", "--time", default=60, type=int, dest='interval',
                    help="Seconds between logging (default: %(default)s)")
group = parser.add_argument_group("seldom used arguments")
group.add_argument("-d", "--duplicates", action="store_true",
                   help="Log duplicate entries (default: %(default)s)", dest="allowduplicates")
args = parser.parse_args()
args.logfile.close()
if args.interval < 10 or args.interval > (60*60):
    parser.error(
        "argument -t/--time: must be between 10 seconds and 3600 (1 hour)")
print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
url = "http://{0}:{1}".format(args.server, args.port)
print("Logging to:{0} Every:{2} seconds Using: {1} ".format(
    abspath(args.logfile.name), url, args.interval))
savedmodels = {}
while True:
    start = time.time()
    response = requests.get(url)
    if response.status_code == HTTPStatus.OK:
        logfile = open(args.logfile.name, args.logfile.mode,
                       args.logfile._CHUNK_SIZE, args.logfile.encoding)
        models = json.loads(response.text)
        data = OrderedDict()
        data["datetime"] = models["datetime"]
        data["timestamp"] = models["timestamp"]
        for model in models["models"]:
            data["model"] = model["model"]
            if "id" in model:
                data["id"] = model["id"]
                savedkey = data["model"]+data["id"]
            else:
                savedkey = data["model"]
            duplicate = False
            if not args.allowduplicates:
                if savedkey in savedmodels:
                    if model["model"] == magnum.REMOTE:
                        # normalize time of day for equal test
                        for key in ["remotetimehours", "remotetimemins"]:
                            savedmodels[savedkey][key] = model["data"][key]
                    if savedmodels[savedkey] == model["data"]:
                        duplicate = True
                savedmodels[savedkey] = model["data"]
            if not duplicate:
                data["data"] = model["data"]
                logfile.write(json.dumps(data))
                logfile.write("\n")
        logfile.close()
    interval = time.time() - start
    sleep = args.interval - interval
    if sleep > 0:
        time.sleep(sleep)
