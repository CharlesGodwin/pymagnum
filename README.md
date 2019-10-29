# pymagnum

pymagnum is a Python 3 implementation of a read only interface to the Magnum Energy network.

This software is not endorsed or supported by Magnum Energy, a product of Sensata Technologies https://www.magnum-dimensions.com/

Source site is: https://github.com/CharlesGodwin/pymagnum.

**Although this software has been tested, it is new. Please report all success and failure to the [author](#feedback). Thank you.**

In order to use this software you need to have a RS485 adaptor connected to a Magnum Energy Network. Refer to this document (https://gitlab.com/Magnum_Energy/distribution/blob/master/Building_a_Magnum_Energy_Adaptor.pdf) for instructions.

## Installation

Throughout this documentation `python` and its installer `pip` are refered to using the default convention of a Raspberry Pi. The term `python3` and `pip3` refer to Python 3 versions of the programs. On other systems the default installation may be Python 3 so just use `python` and `pip` in those systems. This software requires at least version 3.5 of Python.

You will need pip3 installed. On a Pi use:  
`sudo apt install python3-pip`

Then install or update this software package using:  
`sudo pip3 install --upgrade  -i https://test.pypi.org/simple/ pymagnum`

Once this software is installed test the interconnect hardware:

first determine your serial device by running  
`python3 -m serial.tools.list_ports`
Normally a USB device will show up as `/dev/ttyUSB0` and a HAT as `/dev/ttyAMA0` or `/dev/ttyS0`

Next run the provided test program  
`python3 -m magnum.tools.magtest --help`   will tell you choices.tesrs485

Usually just run  
`python3 -m magnum.tools.magtest -d /dev/ttyUSB0` or other device name.  
This should show up to 50 packets with names. such as:
<pre>
Length:21 REMOTE_A2 =>00003C04500F170601C8A5860100465000781478A2
Length:18 BMK_81    =>81550992FFC0089B0C77FFBFE11300390A01
Length:21 INVERTER  =>400000F60002780001003311241E6B000001025800
Length:21 REMOTE_A4 =>00003C04500F170601C8A58601001E1E00000000A4
Length: 6 AGS_A1    =>A102343A007C
Length:21 REMOTE_00 =>400000F60002770001003311241E6B000001025800
Length:21 REMOTE_00 =>400000F60002770001003311241E6B000001025800
.
.
Packets:45 in 1.10 seconds
</pre>
If nothing happens or you get a lot of UNKNOWN lines, try reversing the two wires on your setup and repeating the test. If that fails contact the [author](#feedback).

Here's an example of results if the wires are switched.
<pre>
Length:42 UNKNOWN   =>7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD7C7C7F173C5D7BD
Length:29 UNKNOWN   =>0076F8FEFCFEFCFE7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
Length:40 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FF5FFF0FD70FBBFA6EE933FFBBEFC9E711FFF92FB5FF89EBFDFE
Length:42 UNKNOWN   =>7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD74341FFB7FBFFB9
Length:42 UNKNOWN   =>7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD7C3C3FFFFFFFFB7
Length:29 UNKNOWN   =>00F4D15C46FC9EFC7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
Length:42 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FFFFFFFFA9FFFF7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
Length:42 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FFFFFFFFFFFFFF7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
Length:29 UNKNOWN   =>FFFF87F75FE1D1F3FF6FB5E6FAD7FBCDD7FF23FFBF007AE85C8CFE24FC
Length:42 UNKNOWN   =>7FFFFD99FFFF11FFFDFF99EFD3E129FFFFFFFB4FFFFFFF87F75FE1D1F3FF6FB5E6FAD7C7C7F173C5D7BD
Length:29 UNKNOWN   =>007AF45C8CFE24FC7FFFFD9BFFFF11FFFDFF99EFD3E129FFFFFFFB4FFF
</pre>

## Available Tools
Tools will be added as they are developed. Tools are implemented as Python modules and can be invoked with this generalized command:
`python3 -m magnum.tools.<tool name> --help`
Currently the tools available are:

### magtest
This tool is described in the installation instructions.
`python3 -m magnum.tools.magtest --help`

## magdump
This is a program that will dump a JSON string to the console for all available devices.  The default is to dump a string and exit. But if the interval is set to a number the program will dump a string every <interval> seconds

`python3 -m magnum.tools.magdump --help`
The regular options to set with this tool are:
<pre>
 -h, --help            show this help message and exit
 -d DEVICE, --device DEVICE
                       Serial device name (default: /dev/ttyUSB0)
 -i INTERVAL, --interval INTERVAL
                       Interval, in seconds, between dump records, in
                       seconds. 0 means once and exit. (default: 0)
 -v, --verbose         Display options at runtime (default: False)

seldom used:
 --packets PACKETS     Number of packets to generate in reader (default: 50)
 --timeout TIMEOUT     Timeout for serial read (default: 0.005)
 --trace               Add most recent raw packet info to data (default:
                       False)
 -nc, --nocleanup      Suppress clean up of unknown packets (default: True)
</pre>

## Remove software

If you want to know what version is installed use:  
`pip3 show pymagnum`

If you want to remove the software use:  
`sudo pip3 uninstall pymagnum`

## Usage
There are several example programs available on the git site.

Typical usage is:  
<pre>
from magnum import magnum

reader = magnum.Magnum(device='/dev/ttyUSB0')
devices = reader.getDevices()
print(devices)
</pre>

You need to import the magnum module, instantiate the class with optional parameters (more documentation soon) and then get an instance of the models for processing. If you need a time series just loop around the getDevices() method.

## Feedback
Your feedback is important. I want to hear the good, the bad and the ugly. I would also  like to knoe of any enhancements you would like. The  way to provide open feed back is to create an issue at https://github.com/CharlesGodwin/pymagnum/issues

Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>

SPDX-License-Identifier:    BSD-3-Clause
