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
from diffpy.pdfgui.gui.pdfguiglobals import dbopts

# ----------------------------------------------------------------------------

class TestParametersPanel(unittest.TestCase):

    def setUp(self):
        self._save_noerrordialog = dbopts.noerrordialog
        dbopts.noerrordialog = True
        self.app = wx.App()
        self.frame = wx.Frame(None)
        self.panel = ParametersPanel(self.frame, -1)
        self.panel.parameters.update([
            (1, Parameter(1, 0.1)),
            (5, Parameter(5, 0.5)),
        ])
        self.panel.refresh()
        self.panel.mainFrame = _TMainFrame()
        self.frame.window = self.panel
        return

    def tearDown(self):
        self.frame.Close()
        dbopts.noerrordialog = self._save_noerrordialog
        return


    def _leftclickcell(self, row, col, **kw):
        gp = self.panel.grid_parameters
        eventtype = wx.grid.EVT_GRID_CELL_LEFT_CLICK.typeId
        e = wx.grid.GridEvent(gp.Id, eventtype, gp, row, col, **kw)
        gp.ProcessEvent(e)
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
        self._leftclickcell(0, 1)
        self.assertEqual("1", gp.GetCellValue(0, 1))
        self.assertTrue(p.fixed)
        self.assertTrue(self.panel.mainFrame.altered)
        self._leftclickcell(0, 1)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        self._leftclickcell(0, 1, control=True)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        self._leftclickcell(0, 1, shift=True)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        gp.SelectAll()
        self._leftclickcell(0, 1)
        self.assertEqual("0", gp.GetCellValue(0, 1))
        gp.ClearSelection()
        self._leftclickcell(0, 1)
        self.assertEqual("1", gp.GetCellValue(0, 1))
        return

# End of class TestParametersPanel

# Local Helpers --------------------------------------------------------------

class _TMainFrame(object):
    "Think mockup of the used MainFrame methods."

    altered = False

    def needsSave(self):
        self.altered = True
        return

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
