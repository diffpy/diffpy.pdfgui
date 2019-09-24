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
        # just instantiate the context menu
        # disable modal Frame.PopupMenu
        self.frame.PopupMenu = lambda menu, pos: None
        e = wx.MouseEvent(wx.EVT_RIGHT_DOWN.typeId)
        try:
            self.frame.treeCtrlMain.ProcessEvent(e)
        finally:
            del self.frame.PopupMenu
        self.assertIsNotNone(self.frame.PopupMenu)
        return


    def test_disableMainMenuItems(self):
        "cover MainFrame.disableMainMenuItems method."
        self.frame.disableMainMenuItems()
        return

# End of class TestMainFrame

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
