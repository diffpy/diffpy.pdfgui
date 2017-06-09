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
configfilename = os.path.expanduser("~/.pdfgui.cfg")
# Project modification flag
isAltered = False

# Resolve APPDATADIR base path to application data files.
_req = Requirement.parse("diffpy.pdfgui")
_development_mode = (
    os.path.basename(resource_filename(_req, "")) == "src" and
    os.path.isfile(resource_filename(_req, "../setup.py"))
)

APPDATADIR = resource_filename(_req, ".." if _development_mode else "")
APPDATADIR = os.path.abspath(APPDATADIR)

# Location of the HTML manual
docMainFile = os.path.join(APPDATADIR, 'doc/manual/pdfgui.html')


def iconpath(iconfilename):
    """Full path to the icon file in pdfgui installation.
    This function should be used whenever GUI needs access
    to custom icons.

    iconfilename -- icon file name without any path

    Return string.
    """
    rv = os.path.join(APPDATADIR, 'icons', iconfilename)
    return rv


# options and arguments passed on command line
cmdopts = []
cmdargs = []

# debugging options:
from diffpy.pdfgui.gui import debugoptions
dbopts = debugoptions.DebugOptions()

# End of file
