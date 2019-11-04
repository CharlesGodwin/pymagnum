#
# Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a REST API server
# run the program with --help for details of options.
import argparse
import json
import time
import traceback
from collections import OrderedDict
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

from magnum import magnum

magnumReader = None

class magServer(BaseHTTPRequestHandler):

    def log_request(self, code='-', size='-'):
        #
        # suppress OK type messges
        #
        if isinstance(code, HTTPStatus):
            code = code.value
        if code < 200 or code >= 300:
            super().log_request(code=code, size=size)

    def _set_headers(self, contenttype="text/html"):
        self.send_response(200)
        self.send_header("Content-type", contenttype)
        self.end_headers()

    def do_GET(self):
        try:
            devices = magnumReader.getDevices()
            if len(devices) != 0:
                self._set_headers(contenttype="application/json")
                data = OrderedDict()
                now = int(time.time())
                data["datetime"] = str(
                    datetime.fromtimestamp(now).astimezone())

                data["devices"] = devices
                jsonString = json.dumps(data)
                self.wfile.write(jsonString.encode("utf8"))
                return
            else:
                message = "No data avaliable"
                code = HTTPStatus.NO_CONTENT
        except:
            message = "Exception detected attempting to read network data - " + traceback.format_exc()
            code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.send_error(code, message=message)


def run(server_class=HTTPServer, handler_class=magServer, addr="", port=17223):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting Magnum Reader on {addr}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Magnum Network Reader")
    parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                        help="Serial device name (default: %(default)s)")
    parser.add_argument("-p", "--port", type=int, default=17223,
                        help="Port on which the server listens (default: %(default)s)")
    seldom_used = parser.add_argument_group("seldom used arguments")
    seldom_used.add_argument("-n", "--packets", default=50, type=int,
                       help="Number of packets to generate (default: %(default)s)")
    seldom_used.add_argument("-t", "--timeout", default=0.005, type=float,
                        help="Timeout for serial read (default: %(default)s)")
    seldom_used.add_argument("-l", "--listen", default="ALL",
                        help="IP address on which the server listens (default: %(default)s)")
    seldom_used.add_argument("-nc", "--nocleanup", action="store_false",
                        help="Suppress clean up of unknown packets (default: %(default)s)", dest='cleanpackets')
    args = parser.parse_args()
    if args.listen.upper() == 'ALL':
        args.listen = ''
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
    try:
        magnumReader = magnum.Magnum(device=args.device, packets=args.packets,
                                     timeout=args.timeout, cleanpackets=args.cleanpackets)
    except Exception as e:
        print("Error detected attempting to connect to Magnum network")
        traceback.print_exc()
        exit(2)
    run(addr=args.listen, port=args.port)
