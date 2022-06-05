#
# Copyright (c) 2018-2022 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of a REST API server
# run the program with --help for details of options.
import json
import signal
import sys

from collections import OrderedDict
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

import magnum
from magnum.magnum import Magnum
from magnum.magparser import MagnumArgumentParser
from tzlocal import get_localzone


def sigint_handler(signal, frame):
    print('Interrupted. Shutting down.')
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)

magnumReaders = dict()


class magServer(BaseHTTPRequestHandler):

    def log_request(self, code='-', size='-'):
        #
        # suppress OK type messages
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
        response = []
        code = None
        message = None
        timestamp = datetime.now(get_localzone()).replace(
            microsecond=0).isoformat()
        devices = []
        for comm_device, magnumReader in magnumReaders.items():
            try:
                devices = magnumReader.getDevices()
                if len(devices) != 0:
                    self._set_headers(contenttype="application/json")
                    data = OrderedDict()
                    data["datetime"] = timestamp
                    data["devices"] = devices
                    device = dict()
                    device['comm_device'] = comm_device
                    device['data'] = data
                    response.append(device)
                else:
                    message = "No data avaliable"
                    code = HTTPStatus.NO_CONTENT
            except Exception as e:
                message = "Exception detected attempting to read network data - {0} {1}".format(comm_device, str(e))
                code = HTTPStatus.INTERNAL_SERVER_ERROR
        if len(response) > 0:
            jsonString = json.dumps(response)
            self.wfile.write(jsonString.encode("utf8"))
            return
        self.send_error(code, message=message)


def run(server_class=HTTPServer, handler_class=magServer, addr="", port=17223):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting Magnum Reader on {addr}:{port}")
    httpd.serve_forever()


signal.signal(signal.SIGINT, sigint_handler)
parser = MagnumArgumentParser(description="Magnum Network Reader",fromfile_prefix_chars='@',)
parser.add_argument("-p", "--port", type=int, default=17223,
                    help="Port on which the server listens (default: %(default)s)")
parser.add_argument("-d", "--device", nargs='*', action='append', default=[],
                    help="Serial device name (default: /dev/ttyUSB0). You can specify more than one.")
parser.add_argument('-v', "--verbose", action="store_true", default=False,
                    help="Display options at runtime (default: %(default)s)")
seldom = parser.add_argument_group("Seldom used")
seldom.add_argument('--version', action='version',
                    version="%(prog)s Version:{}".format(magnum.__version__))
seldom.add_argument("-l", "--listen", default="ALL",
                    help="IP address on which the server listens (default: %(default)s)")
seldom.add_argument("--packets", default=50, type=int,
                    help="Number of packets to generate in reader (default: %(default)s)")
seldom.add_argument("--timeout", default=0.005, type=float,
                    help="Timeout for serial read (default: %(default)s)")
seldom.add_argument("--trace", action="store_true", default=False,
                    help="Add most recent raw packet(s) info to data (default: %(default)s)")
seldom.add_argument("--nocleanup", action="store_true", default=False, dest='cleanpackets',
                    help="Suppress clean up of unknown packets (default: False)")
args = parser.magnum_parse_args()
if args.listen.upper() == 'ALL':
    args.listen = ''
print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
for device in args.device:
    try:
        magnumReader = Magnum(device=device, packets=args.packets, trace=args.trace,
                                timeout=args.timeout, cleanpackets=args.cleanpackets)
        magnumReader.getDevices()  # test read to see if all's good
        magnumReaders[magnumReader.getComm_Device()] = magnumReader
    except Exception as e:
        print("{0} {1}".format(device, str(e)))
if len(magnumReaders) == 0:
    print("Error: There are no usable devices connected.")
    exit(2)

run(addr=args.listen, port=args.port)
