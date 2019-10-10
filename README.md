# pymagnum

pymagnum is a Python 3 implementation of a read only interface to the Magnum Energy network.

This software is not endorsed or supported by Magnum Energy, a product of Sensata Technologies https://www.magnum-dimensions.com/

Source site is: https://github.com/CharlesGodwin/pymagnum. This site is currently private with access by request only. Contact the author for access.

publishing systemThe package software is also being hosted on a test publishing system. It will be migrated to the regular, public PyPi host when testing is complete.

**This is untested software! It will not be publicly published until it has been tested with live equipment. Please report all success and failure to the author**

In order to use this software you need to have a RS485 adaptor connected to a Magnum Energy Network. Refer to this document (https://gitlab.com/Magnum_Energy/distribution/blob/master/Building_a_Magnum_Energy_Adaptor.pdf) for instructions.

## Installation

You will need pip3 installed. On a Pi use:  
`sudo apt install python3-pip`

Then install or update the software package using:  
`sudo pip3 install --upgrade  -i https://test.pypi.org/simple/ pymagnum`

Once this software is installed test the interconnect hardware:

first determine your serial device by running  
`python3 -m serial.tools.list_ports`
Normally a USB device will show up as /dev/ttyUSB0 and a HAT as /dev/ttyAMA0

Next run the provided test program  
`python3 -m magnum.tools.testrs485 --help`   will tell you choices.  
Usually just run  
`python3 -m magnum.tools.testrs485 -d /dev/ttyUSB0` or other device name.  
This should show up to 50 packets with names. such as
<pre>
Length:21 REMOTE_A2 =>00003C04500F170601C8A5860100465000781478A2
Length:18 BMK_81    =>81550992FFC0089B0C77FFBFE11300390A01
Length:21 INVERTER  =>400000F60002780001003311241E6B000001025800
Length:21 REMOTE_A4 =>00003C04500F170601C8A58601001E1E00000000A4
Length: 6 AGS_A1    =>A102343A007C
Length:21 REMOTE_00 =>400000F60002770001003311241E6B000001025800
Length:21 REMOTE_00 =>400000F60002770001003311241E6B000001025800

Packets:45 in 1.10 seconds
</pre>
If nothing happens or you get a lot of UNKNOWN try reversing your two wires and repeating the test. If that fails contact the author

## Available Tools
Tools will be added as they are developed. Tools are implemented as Python moduels and can be invloked with this generalized command:
`python3 -m magnum.tools.<tool name> --help`
Currently the tools avaiable are:

### testrs495
This tool is described in the installation instructions.
`python3 -m magnum.tools.testrs485 --help`

## mqttlogger
This is a long running program that will send MQTT messages for each device in your system at the designated interval. Refer to thse links for information on implementing and using MQTT services.  
http://mqtt.org
https://mosquitto.org

`python3 -m magnum.tools.mqttlogger --help`
The regular options to set with this service are:
<pre>
MQTT publish:
  -t TOPIC, --topic TOPIC
                        Topic prefix (default: magnum/)
  -b BROKER, --broker BROKER
                        MQTT Broker address (default: localhost)
  -i INTERVAL, --interval INTERVAL
                        Interval, in seconds, between publishing (default: 60)
  --duplicates          Log duplicate entries (default: False)

Magnum reader:
  -d DEVICE, --device DEVICE
                        Serial device name (default: /dev/ttyUSB0)
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

You need to import the magnum module, instantiate the class with optional parameters (more documentation soon) and then get an instance of the models for processing. If you need a time series just loop around the getModels() method.

Copyright (c) 2018-2019 Charles Godwin <magnum@godwin.ca>

SPDX-License-Identifier:    BSD-3-Clause