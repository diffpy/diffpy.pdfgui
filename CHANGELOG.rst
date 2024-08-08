=============
Release Notes
=============

.. current developments

v3.0.5
====================




Version 2.0.3 – 2023-05-18
==========================
**Added**

* Support for Python 3.8, 3.9.
* Use `.ddp3` instead of `.ddp` to store project files.

**Changed**

* Update wxpython to 4.1.1 and remove incompatible align flags.
* Update configparser use strict as False.
* Update tutorial project files for py3.

**Deprecated**

**Removed**

**Fixed**

- Incompatible conversion between bytes and str from py2 to py3.
- The `listCtrlFiles.InsertItem` error in windows.
- Make the string parser in doping series working.
