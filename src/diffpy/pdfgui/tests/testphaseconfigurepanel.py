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
Unit tests for PhaseConfigurePanel class.
"""

import unittest

import wx

from diffpy.pdfgui.gui.phaseconfigurepanel import PhaseConfigurePanel
from diffpy.pdfgui.gui.mainframe import MainFrame
from diffpy.pdfgui.tests.testutils import GUITestCase, datafile, tooltiptext

# ----------------------------------------------------------------------------

@unittest.skipIf(wx.VERSION[0] == 3, "FIXME - wx3 font issues")
class TestPhaseConfigurePanel(GUITestCase):

    @classmethod
    def setUpClass(cls):
        GUITestCase.setUpClass()
        GUITestCase.setCmdArgs([datafile("lcmo.ddp")])
        cls.app = wx.App()
        cls.frame = MainFrame(None, -1, "")
        tree = cls.frame.treeCtrlMain
        fits = tree.GetChildren(tree.root)
        phases = tree.GetPhases(fits[0])
        cls.frame.makeTreeSelection(phases[0])
        return


    @classmethod
    def tearDownClass(cls):
        cls.frame.Close()
        cls.app.Destroy()
        GUITestCase.tearDownClass()
        return


    def setUp(self):
        self.panel = self.frame.rightPanel.notebook_phase.GetPage(0)
        assert isinstance(self.panel, PhaseConfigurePanel)
        return


    def test_restrictConstrainedParameters(self):
        "check restrictConstrainedParameters function"
        panel = self.panel
        grid = self.panel.gridAtoms
        self.assertTrue(panel.textCtrlScaleFactor.IsEditable())
        self.assertFalse(panel.textCtrlDelta1.IsEditable())
        self.assertTrue(grid.IsReadOnly(0, 1))
        self.assertFalse(grid.IsReadOnly(0, 3))
        self.assertEqual('@1', tooltiptext(panel.textCtrlA))
        return

# End of class TestPhaseConfigurePanel

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
