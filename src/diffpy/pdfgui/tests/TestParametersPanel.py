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
Unit tests for ParametersPanel class
"""

import unittest

import wx.grid

from diffpy.pdfgui.gui.parameterspanel import ParametersPanel
from diffpy.pdfgui.control.parameter import Parameter
from diffpy.pdfgui.tests.testutils import GUITestCase, clickcell

# ----------------------------------------------------------------------------

class TestParametersPanel(GUITestCase):

    def setUp(self):
        self.app = wx.App()
        self.frame = wx.Frame(None)
        self.panel = ParametersPanel(self.frame, -1)
        self.panel.parameters.update([
            (1, Parameter(1, 0.1)),
            (5, Parameter(5, 0.5)),
        ])
        self.panel.refresh()
        self.panel.mainFrame = self._mockUpMainFrame()
        self.frame.window = self.panel
        return

    def tearDown(self):
        self.frame.Close()
        self.app.Destroy()
        return


    def test_onPopupFixFree(self):
        "Check ParametersPanel.onPopupFixFree"
        # event is not used, we just generate and reuse dummy event.
        e = wx.PyCommandEvent(wx.EVT_MENU.typeId, wx.ID_ANY)
        panel = self.panel
        gp = self.panel.grid_parameters
        plist = list(self.panel.parameters.values())
        gp.SetCellValue(0, 1, "")
        self.assertTrue(all(not p.fixed for p in plist))
        gp.SelectAll()
        panel.onPopupFixFree(e)
        self.assertTrue(all(p.fixed for p in plist))
        self.assertEqual("1", gp.GetCellValue(0, 1))
        panel.onPopupFixFree(e)
        self.assertTrue(all(not p.fixed for p in plist))
        gp.DeselectRow(0)
        panel.onPopupFixFree(e)
        self.assertFalse(plist[0].fixed)
        self.assertTrue(plist[1].fixed)
        return


    def test_applyCellChange(self):
        "Check ParametersPanel.applyCellChange"
        gp = self.panel.grid_parameters
        mf = self.panel.mainFrame
        panel = self.panel
        self.assertFalse(mf.altered)
        panel.applyCellChange(0, 0, 0.1)
        self.assertFalse(mf.altered)
        panel.applyCellChange(0, 0, 1.5)
        self.assertTrue(mf.altered)
        self.assertEqual("1.5", gp.GetCellValue(0, 0))
        self.assertEqual(1.5, panel.parameters[1].initialValue())
        return


    def test_onCellLeftClick(self):
        "Check click handling on the Parameters grid."
        gp = self.panel.grid_parameters
        p = self.panel.parameters[1]
        self.assertFalse(self.panel.mainFrame.altered)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        self.assertFalse(p.fixed)
        clickcell(gp, "left", 0, 1)
        self.assertEqual("1", gp.GetCellValue(0, 1))
        self.assertTrue(p.fixed)
        self.assertTrue(self.panel.mainFrame.altered)
        clickcell(gp, "left", 0, 1)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        clickcell(gp, "left", 0, 1, controlDown=True)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        clickcell(gp, "left", 0, 1, shiftDown=True)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        gp.SelectAll()
        clickcell(gp, "left", 0, 1)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        gp.ClearSelection()
        clickcell(gp, "left", 0, 1)
        self.assertEqual("1", gp.GetCellValue(0, 1))
        return


    def test_onCellRightClick(self):
        "Check right-click handling on the Parameters grid."
        # disable modal grid_parameters.PopupMenu
        gp = self.panel.grid_parameters
        gp.PopupMenu = lambda menu, pos: None
        try:
            clickcell(gp, "right", 0, 1)
        finally:
            del gp.PopupMenu
        self.assertTrue(self.panel.did_popupIDs)
        return

# End of class TestParametersPanel

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
