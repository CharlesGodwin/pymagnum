#!/usr/bin/env python3
#
# Copyright (c) 2023 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# This code is provided as an example of loading data into MySql/MariaDB database
# run the program with --help for details of options.
#  python3 magsql.py --help
#
# You must install mariadb package and dependencies
# `sudo apt install libmariadb3 libmariadb-dev -y`
# `sudo pip3 install python3-dev mariadb`
#
# This has been tested ONLY on a Raspberry Pi
# This is example code and is not supported by the author although he will try to respond to questions.
#
# The --allinone option will log a single flat table row with table name of `log_data`
#
# The program will only load columns that match between the variable in the defined data and columns in the database.
# To see what data is available run magdump.py with same parameters
#
# The user is responsible for defining the MySQL table(s) and database but can exploit the mag2sql module
#
import signal
import sys
import time

from datetime import datetime, timezone
from xmlrpc.client import Boolean
import mariadb

import magnum
from magnum.magnum import Magnum
from magnum.magparser import MagnumArgumentParser

global args, cursor, first_time, db_columns

first_time = True
db_columns = {}


def main():
    global first_time, cursor, args
    signal.signal(signal.SIGINT, sigint_handler)
    parser = MagnumArgumentParser(description="Magnum SQL Load", prog="magsql", fromfile_prefix_chars='@',
                                  epilog="Refer to https://github.com/CharlesGodwin/pymagnum for details")
    parser.add_argument("--device", "-d", default=f"{'/dev/ttyUSB0' if parser.isPosix else 'COM1'}",
                        help="Serial device name (default: %(default)s). You can specify ONLY one.")
    parser.add_argument("--interval", "-i", default=60, type=int, dest='interval',
                        help="Interval, in seconds, between dump records, in seconds. 0 means once and exit. (default: %(default)s)")
    parser.add_argument("--verbose", '-v', action="store_true", default=False,
                        help="Display options at runtime (default: %(default)s)")
    parser.add_argument("--db_username", default=None, required=True,
                        help="MySQL User name(default: %(default)s)")
    parser.add_argument("--db_password", default=None, required=True,
                        help="MySQL User password(default: %(default)s)")
    parser.add_argument("--db_database", default='magnum',
                        help="MySQL database name(default: %(default)s)")
    parser.add_argument("--db_host", default='localhost',
                        help="MySQL Server host name(default: %(default)s)")
    seldom = parser.add_argument_group("Seldom used")
    seldom.add_argument('--version', action='version',
                        version="%(prog)s Version:{}".format(magnum.__version__))
    seldom.add_argument("--packets", default=50, type=int,
                        help="Number of packets to generate in reader (default: %(default)s)")
    seldom.add_argument("--timeout", default=0.005, type=float,
                        help="Timeout for serial read (default: %(default)s)")
    seldom.add_argument("--trace", action="store_true", default=False,
                        help="Add most recent raw packet(s) info to data (default: %(default)s)")
    seldom.add_argument("--nocleanup", action="store_true", default=False, dest='cleanpackets',
                        help="Suppress clean up of unknown packets (default: False)")
    seldom.add_argument("--db_port", default=3306, type=int,
                        help="MySQL port(default: %(default)s)")
    seldom.add_argument("--allinone", action="store_true", default=False,
                        help="Process data as a flat single row (default: %(default)s)")

    args = parser.magnum_parse_args()
    # Only supports one device
    if len(args.device) > 1:
        parser.error("magsql only supports 1 device at a time.")
    if hasattr(args, 'v1'): # a relic but not harmful
        args.allinone = True
    if args.verbose:
        savepw = args.db_password
        args.db_password = "******"
        print('Magnum SQL Load Version:{0}'.format(magnum.__version__))
        print("Options:{0}".format(str(args)
                                   .replace('Namespace(', '')
                                   .replace(')', '')
                                   .replace('[', '')
                                   .replace('\'', '')
                                   .replace(']', '')))
        args.db_password = savepw
    try:
        magnumReader = Magnum(device=args.device[0], packets=args.packets, trace=args.trace,
                              timeout=args.timeout, cleanpackets=args.cleanpackets)
    except Exception as e:
        print("{0} {1}".format(args.device, str(e)))
        exit(2)
    if args.interval != 0 and args.verbose == True:
        print(f"Logging every:{args.interval} seconds.")
    while True:
        start = time.time()
        commdevices = []
        timestamp = datetime.now(timezone.utc).replace(
            microsecond=0).astimezone().isoformat()
        try:
            devices = magnumReader.getDevices()
            if len(devices) != 0:
                alldata = {}
                alldata["datetime"] = timestamp
                alldata["device"] = 'MAGNUM'
                alldata['comm_device'] = magnumReader.getComm_Device()
                magnumdata = []
                for device in devices:
                    data = {}
                    data["device"] = device["device"]
                    data["data"] = device["data"]
                    magnumdata.append(data)
                alldata["data"] = magnumdata
                commdevices.append(alldata)
                if args.allinone:
                    alldata = magnumReader.allinone(alldata)
                # Now the heavy lifting
                try:
                    db_connection = mariadb.connect(
                        user=args.db_username,
                        password=args.db_password,
                        host=args.db_host,
                        port=args.db_port,
                        database=args.db_database
                    )
                    db_connection.autocommit = True
                    cursor = db_connection.cursor()
                    if first_time:
                        initialize_tables_def(alldata)
                        first_time = False
                    post_data(alldata)
                    db_connection.commit()
                    db_connection.close()
                except mariadb.Error as e:
                    print(f"Error connecting to Database Platform: {e}")
                    sys.exit(1)

        except Exception as e:
            print(str(e))
        if args.interval == 0:
            break
        interval = time.time() - start
        sleep = args.interval - interval
        if sleep > 0:
            time.sleep(sleep)


def sigint_handler(signal, frame):
    print('Interrupted. Shutting down.')
    sys.exit(0)


def initialize_tables_def(allstuff):
    global args, cursor, db_columns
    if type(allstuff) != list:
        allstuff = [allstuff]
    for alldata in allstuff:
        for data in alldata['data']:
            db_table = data['device']
            query = f"SELECT GROUP_CONCAT(COLUMN_NAME) AS COLUMNS FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{args.db_database}' AND TABLE_NAME = '{db_table}';"
            try:
                cursor.execute(query)
                fields = cursor.fetchone()
                field_names = fields[0].split(",")
                db_columns[db_table] = field_names
            except Exception as e:
                print(
                    f"Unable to find table {db_table}: logging of this data will be ignored.")
    if len(db_columns) == 0:
        print('No tables to load. Shutting down.')
        sys.exit(1)
    return


def post_data(alldata):
    global args, cursor, db_columns
    if type(alldata) == list:
        alldata = alldata[0]
    for data in alldata['data']:
        inserts = {}
        db_table = data['device']
        if db_table not in db_columns:
            return
        timestamp = datetime.fromisoformat(
            alldata['datetime']).strftime('%Y-%m-%d %H:%M:%S')
        if 'timestamp' in db_columns[db_table]:
            inserts['timestamp'] = f"\"{timestamp}\""
        elif 'datetime' in db_columns[db_table]:
            inserts['datetime'] = f"\"{timestamp}\""
        rowdata = data['data']
        for field in db_columns[db_table]:
            if field in rowdata:
                if rowdata[field] != None:
                    value = rowdata[field]

                    if type(value) == bool:
                        if value:
                            value = str(1)
                        else:
                            value = str(0)
                    elif type(value) == float:
                        value = str(value)
                    elif type(value) == int:
                        value = str(value)
                    else:
                        value = f"\"{value}\""
                    inserts[field] = value
        columns = ', '.join(inserts.keys())
        values = list(inserts.values())
        values = ', '.join(values)
        query = f"INSERT INTO {db_table} ({columns}) VALUES ({values});"
        try:
            cursor.execute(query)
        except Exception as e:
            print(f"Error updating {db_table}:{e}")
    return


if __name__ == '__main__':
    main()
