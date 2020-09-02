=======================
 pyMagnum Release Notes
=======================
Version 2.0   pending
---------------------
- Revised: PT-100 processing issue #15
- Added: 30 second delay from boot time issue #16
- Enhanced: ``magtest``
- Enhanced: Normalized fields and field types
    - many Integer fields become Float
    - Some fields have been dropped
- Added: documentation of fields
- Fixed: Bug in battery size calculation - now using BMK value
- Fixed: Source code was refactored to simplify coding
    - each device class was moved to an individual file
    - the tools subdirectory was collapsed into the main directory

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
