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

docMainFile = resource_filename(Requirement.parse("diffpy.pdfgui"),
        'doc/manual/pdfgui.html')

# static variable for the iconpath function
_cached_iconpaths = {}

def iconpath(iconfilename):
    # cached_iconpaths is a static variable
    """Full path to the icon file in pdfgui installation.
    This function should be used whenever GUI needs access
    to custom icons.

    iconfilename -- icon file name without any path

    Return string.
    """
    if iconfilename not in _cached_iconpaths:
        f = resource_filename(Requirement.parse("diffpy.pdfgui"),
                "icons/" + iconfilename)
        _cached_iconpaths[iconfilename] = f
    rv = _cached_iconpaths[iconfilename]
    return rv

# options and arguments passed on command line
cmdopts = []
cmdargs = []

# debugging options:
from diffpy.pdfgui.gui import debugoptions
dbopts = debugoptions.DebugOptions()

# End of file
