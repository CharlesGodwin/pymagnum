#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
#
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
