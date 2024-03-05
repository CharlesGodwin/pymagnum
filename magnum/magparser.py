
import argparse
import shlex
import os


class MagnumArgumentParser(argparse.ArgumentParser):
    isPosix = os.name != 'nt'
    def convert_arg_line_to_args(self, arg_line):
        return shlex.split(arg_line, True,  self.isPosix)

    # This method cleans up device
    def magnum_parse_args(self):

        args = self.parse_known_args()[0]
        if hasattr(args, 'device'):
            if not isinstance(args.device, list):
                args.device = [args.device]
            else:
                devices = []
                for dev in args.device:
                    for subdev in dev:
                        subdev = subdev.replace(",", " ")
                        for item in subdev.split():
                            devices.append(item)
                args.device = list(dict.fromkeys(devices))  # strips duplicates
            if len(args.device) == 0:
                args.device = ['/dev/ttyUSB0']
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
