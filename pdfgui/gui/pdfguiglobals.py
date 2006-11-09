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

"""This module contains gloabal parameters needed by PDFGui."""

import os.path

# Name of the program
name = "PDFGui"
# Maximum number of files to be remembered
MAXMRU = 5
# The location of the configuration file
configfilename = os.path.expanduser("~/.pdfgui.cfg")
# Project modification flag
isAltered = False

# Useful paths
guiDir = os.path.dirname(os.path.abspath(__file__))
iconsDir = os.path.join(guiDir, 'icons')
controlDir = os.path.join(os.path.dirname(guiDir), 'control')

# options and arguments passed on command line
cmdopts = []
cmdargs = []

# debugging options:
import debugoptions
dbopts = debugoptions.DebugOptions()

# version
__id__ = "$Id$"

# End of file
