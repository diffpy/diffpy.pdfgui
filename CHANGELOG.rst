=============
Release Notes
=============

.. current developments

3.1.0
=====

**Added:**

* numpy >= 2.0 support
* Codecov coverage report in PRs
* Spelling check with Codespell in pre-commit
* Added Whittaker-Shannon interpolation option for grid_interpolation.
* Added support for python 3.13
* no-news needed: just tweaking installation instructions

**Changed:**

*  Package reformatted to comply with new Billinge Group package structure
* Changed the removed local manual link to the online page.
* Use WS interpolation for Nyquist grid.
* Refreshed tutorial manual and brought documentation up to date
* Plots now use colors from the billinge-group matplotlib stylesheet, bg-mpl-stylesheets
* Updated install instructions in README.rst.

**Fixed:**

* Change background color to match system settings in `Phase Configuration`.
* inability to find gui resources bug in py < 3.12
* fixed date rendering in 'about' dialog box
* fix "absent from setuptools' packages configuration" warnings during python -m build
* use conda.txt instead of run.txt for conda package dependencies
* remove conda-recipe folder - feedstock repo has the latest version
* two warnings with (1) linestyle redundantly defined and (2) no artists with labels found to put in legend
* Use miniforge in CI to avoid strange error of incorrect MacOS version logged from base     env
* Re-cookiecut to include GH issues templates, getting started, and install updates
* Fixed TypeError when using Nyquist interp.
* Fixed online manual not showing images.
* Code linted up to PEP8 and group standards

**Removed:**

* Removed wx3 support that was previously deprecated.
* Remove diffpy.structure and numpy in macOS Arm64 readme installation since they are installed by other conda-forge dependencies.
* six dependency in run.txt


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
