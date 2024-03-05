=======================
 pyMagnum Release Notes
Version 2.0.4 2023/11/05
------------------------
- Fixed bug in emitted JSON when using multiple devices
- Cleaned up code when using dummy data files instead of RS485 serial device
- Provided a complete dummy test file testdata/allpackets.txt
- Provided a JSON file testdata/allpackets.JSON

- Fixed All revision values are defined as string. It used to be mixed
- Enhancement --pretty option to magdump for formatted JSON output

Version 2.0.3 2023/10/20
------------------------
- Fixed problem with installing tzlocal on some systems
- Changed minimum Python version to 3.7
- Added warning about use of ``--break-system-packages`` with Python 3.11 and higher.
- Improved how to build information.

Version 2.0.2 2022/11/09
------------------------
- Fixed bug in issue #44 https://github.com/CharlesGodwin/pymagnum/issues/44

Version 2.0.1 2022/06/18
------------------------
- Enhancement: Added MQTT username and password support to examples/mqttlogger.py (issue #38)
- Fixed bug in magtest related to PT100
- Fixed bug in example mqttlogger.py

Version 2.0   2022/06/06
------------------------
- Added: The ability to define all options in a configuration file. For example ``magdump @pymagnum.opt``. See documentation.
- Added: ``magdump`` and examples programs support use of configuration file.
- Added: A new method ``getComm_Device()`` in the Magnum class to retrieve name of device.
- Added: 30 second delay from boot time issue #16
- Added: documentation of fields
- Enhanced: The utility tool ``magdump`` now supports defining more that one device. See documentation. **NOTE** ``magtest`` does NOT support multiple devices.
- Enhanced: The example programs have been enhanced to support multiple devices.
- Enhanced: The utility tool ``magtest`` now supports writing a copy of the displayed messages to a log file. ``--log``
- Enhanced: ``magtest``
- Enhanced: Normalized fields and field types
    - Many Integer fields have become Float
    - Some fields have been dropped
- Revised: PT-100 processing issue #15
  (refer to Installation in documentation)
- Fixed: Bug in battery size calculation - now using BMK value
- Fixed: Source code was refactored to simplify coding
    - each device class was moved to an individual file
    - the tools subdirectory was collapsed into the main directory
- Fixed: The voltage multiplier was not being handled correctly. Some values were being generated as if you have a 12VDC system when voltage of system was 24VDC or 48VDC.

Version 1.1.3   2020/07/12
--------------------------
- Fixed issue #13 leaving port open when no network detected

Version 1.1.2   2020/06/17
--------------------------
- Fixed error in 'running' status for AGS device

Version 1.1.1.post1 2020/06/11
------------------------------
- Improved PT-100 processing
- Added support for older (classic) Inverter and Remote issue #10
- Revised documentation to indicate support for only MS series inverters and ME-RC, ME-ARC, ME-RTR and ME-ARTR remotes
- Added how to build instructions
- Removed reference to duplicates in examples/mqttlogger.py

Version 1.1     2019/12/08
---------------------------
- Fixed issue #4 misinterpreting REMOTE_00 packet
- Added a note in the documentation about emails relating to use of GitHub issues
- Changed modules to script commands
- Fixed problem with Python 3.5 time zone function

Version 1.0     2019/11/05
---------------------------
- First public release.
