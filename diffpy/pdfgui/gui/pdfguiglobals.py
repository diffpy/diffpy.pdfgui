########################################################################
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
########################################################################

"""This module contains gloabal parameters needed by PDFgui."""

import os.path

# Name of the program
name = "PDFgui"
# Maximum number of files to be remembered
MAXMRU = 5
# The location of the configuration file
configfilename = os.path.expanduser("~/.pdfgui.cfg")
# Project modification flag
isAltered = False

# Atomeye path
atomeyepath = ""

# Useful paths
guiDir = os.path.dirname(os.path.abspath(__file__))
controlDir = os.path.join(os.path.dirname(guiDir), 'control')
from diffpy import diffpyDataDir
pdfguiDataDir = os.path.join(diffpyDataDir, 'pdfgui')
docDir = os.path.join(pdfguiDataDir, 'doc')
docMainFile = 'pdfgui.html'

def iconpath(iconfilename):
    """Full path to the icon file in pdfgui installation.
    This function should be used whenever GUI needs access
    to custom icons.

    iconfilename -- icon file name without any path

    Return string.
    """
    from pkg_resources import Requirement, resource_filename
    rv = resource_filename(Requirement.parse("diffpy.pdffit2"),
        "icons/" + iconfilename)
    return rv

# options and arguments passed on command line
cmdopts = []
cmdargs = []

# debugging options:
import debugoptions
dbopts = debugoptions.DebugOptions()

# version
__id__ = "$Id$"

# End of file
