#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfgui     Complex Modeling Initiative
#                   (c) 2019 Brookhaven Science Associates,
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
Unit tests for the MainFrame class.
"""

import unittest

import wx

from diffpy.pdfgui.gui.mainframe import MainFrame
from diffpy.pdfgui.tests.testutils import GUITestCase

# ----------------------------------------------------------------------------

class TestMainFrame(GUITestCase):

    @classmethod
    def setUpClass(cls):
        GUITestCase.setUpClass()
        cls.app = wx.App()
        cls.frame = MainFrame(None, -1, "")
        return


    @classmethod
    def tearDownClass(cls):
        cls.frame.Close()
        cls.app.Destroy()
        GUITestCase.tearDownClass()
        return


    def test_onRightClick(self):
        "check MainFrame.onRightClick method for context menu"
        # just open and close menu
        e = wx.MouseEvent(wx.EVT_RIGHT_DOWN.typeId)
        ui = wx.UIActionSimulator()
        wx.CallLater(1, ui.Char, wx.WXK_ESCAPE)
        self.frame.treeCtrlMain.ProcessEvent(e)
        return

# End of class TestMainFrame

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
