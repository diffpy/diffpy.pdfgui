#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
"""This module contains global parameters needed by PDFgui."""

from importlib.resources import files
from pathlib import Path

from diffpy.pdfgui.gui import debugoptions

# Name of the program
name = "PDFgui"
# Maximum number of files to be remembered
MAXMRU = 5
# The location of the configuration file
configfilename = Path.home() / ".pdfgui_py3.cfg"
# Project modification flag
isAltered = False

_mydir = Path(str(files(__name__))).resolve()

_upbasedir = _mydir.parents[2]
_development_mode = _upbasedir.name == "src" and (_upbasedir.parent / "pyproject.toml").is_file()

# Requirement must have egg-info.  Do not use in _development_mode.
_req = "diffpy.pdfgui"

if _development_mode:
    APPDATADIR = _mydir.parent
else:
    APPDATADIR = Path(str(files(_req))).resolve()

APPDATADIR = APPDATADIR.resolve()

# Location of the HTML manual
docMainFile = "https://diffpy.github.io/diffpy.pdfgui/manual.html"

del _upbasedir
del _development_mode
del _req


def iconpath(iconfilename):
    """Full path to the icon file in pdfgui installation.

    This function should be used whenever GUI needs access to custom
    icons.

    Parameters
    ----------
    iconfilename : str
        The icon file name without any path.

    Returns
    -------
    str
        The full path to the icon file.
    """
    rv = APPDATADIR / "icons" / iconfilename
    assert rv.is_file(), "icon file does not exist"
    return str(rv)


# options and arguments passed on command line
cmdopts = []
cmdargs = []

# debugging options:
dbopts = debugoptions.DebugOptions()

# End of file
