#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfgui     Complex Modeling Initiative
#                   (c) 2018 Brookhaven Science Associates,
#                   Brookhaven National Laboratory.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""
Unit tests for PhaseConfigurePanel class.
"""

import unittest

import wx

from diffpy.pdfgui.gui.phaseconfigurepanel import PhaseConfigurePanel
from diffpy.pdfgui.control.fitstructure import FitStructure
from diffpy.pdfgui.tests.testutils import GUITestCase

# ----------------------------------------------------------------------------

class TestPhaseConfigurePanel(GUITestCase):

    def setUp(self):
        self.app = wx.App()
        self.frame = wx.Frame(None)
        self.panel = PhaseConfigurePanel(self.frame)
        self.panel.structure = FitStructure("stru")
        self.panel.refresh()
        self.panel.mainFrame = self._mockUpMainFrame()
        self.frame.window = self.panel
        return

    def tearDown(self):
        self.frame.Close()
        self.app.Destroy()
        return


    def test_ok(self):
        "FIXME - temporary dummy test"
        self.assertTrue(True)
        return

# End of class TestPhaseConfigurePanel

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
