#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""This module contains the BlankPanel class."""

import wx
from diffpy.pdfgui.gui.pdfpanel import PDFPanel

class BlankPanel(wx.Panel, PDFPanel):
    """A blank panel needed as a right panel in mainframe.py."""
    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        wx.Panel.__init__(self, *args, **kwds)

    def refresh(self):
        return

# end of class BlankPanel
