
import argparse
import shlex
import os
from serial.tools.list_ports import comports


class MagnumArgumentParser(argparse.ArgumentParser):
    isPosix = os.name != 'nt'
    def convert_arg_line_to_args(self, arg_line):
        return shlex.split(arg_line, True, self.isPosix)

    # This method cleans up device
    def magnum_parse_args(self):
        args = self.parse_known_args()[0]
        if hasattr(args, 'device'):
            if args.device == '' or args.device == None:
                args.device = []
            elif not isinstance(args.device, list):
                args.device = [args.device]
            serial_ports = []
            for device in comports(include_links=True):
                if self.isPosix:
                    serial_ports.append(device.device)
                else:
                    serial_ports.append(device.device.upper())
            devices = {}
            if len(args.device) == 0:
                args.device.append("/dev/ttyUSB0" if self.isPosix else "COM1")
            for name in args.device:
                name = name.strip("\"'")
                if name != "":
                    if name.lower() == "all":
                        for port in serial_ports:
                            devices[port] = "serial"
                    else:
                        if (self.isPosix and name in serial_ports) or (self.isPosix == False and name in serial_ports):
                            devices[name] = "serial"
                        else:
                            if name.startswith("!") and len(name)>1:
                                name = name[1:]
                            if os.path.exists(name):
                                devices["!"+name] = "file"
                            else:
                                self.error(f"option --device {name} is not available")
        if len(devices) == 0:
            self.error(f"No available devices")
        args.device = list(dict.fromkeys(devices))
        if hasattr(args, 'timeout'):
            if args.timeout < 0 or args.timeout > 1.0:
                self.error(
                    "option --timeout: Must be a number (float) between 0 and 1 second. i.e. 0.005")
        if hasattr(args, 'packets'):
            if args.packets < 1:
                self.error("option --packets: Must be greater than 0.")
        if hasattr(args, 'cleanpackets'):
            args.cleanpackets = not args.cleanpackets
        return args
