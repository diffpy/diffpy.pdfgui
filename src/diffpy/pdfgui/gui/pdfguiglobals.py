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

"""This module contains gloabal parameters needed by PDFgui."""

import os.path
from pkg_resources import Requirement, resource_filename

# Name of the program
name = "PDFgui"
# Maximum number of files to be remembered
MAXMRU = 5
# The location of the configuration file
configfilename = os.path.expanduser("~/.pdfgui_py3.cfg")
# Project modification flag
isAltered = False

# Resolve APPDATADIR base path to application data files.
_mydir = os.path.abspath(resource_filename(__name__, ''))
_upbasedir = os.path.normpath(_mydir + '/../../..')
_development_mode = (
    os.path.basename(_upbasedir) == "src" and
    os.path.isfile(os.path.join(_upbasedir, "../setup.py"))
)

# Requirement must have egg-info.  Do not use in _development_mode.
_req = Requirement.parse("diffpy.pdfgui")

#pavol
# APPDATADIR = (os.path.dirname(_upbasedir) if _development_mode
#               else resource_filename(_req, ""))
#long
if _development_mode:
    APPDATADIR = os.path.dirname(_mydir)
else:
    APPDATADIR = os.path.join(resource_filename(_req, ""), "diffpy/pdfgui")

APPDATADIR = os.path.abspath(APPDATADIR)

# Location of the HTML manual
docMainFile = os.path.join(APPDATADIR, 'doc/manual/pdfgui.html')

del _upbasedir
del _development_mode
del _req


def iconpath(iconfilename):
    """Full path to the icon file in pdfgui installation.
    This function should be used whenever GUI needs access
    to custom icons.

    iconfilename -- icon file name without any path

    Return string.
    """
    rv = os.path.join(APPDATADIR, 'icons', iconfilename)
    assert os.path.isfile(rv), "icon file does not exist"
    return rv


# options and arguments passed on command line
cmdopts = []
cmdargs = []

# debugging options:
from diffpy.pdfgui.gui import debugoptions
dbopts = debugoptions.DebugOptions()

# End of file
