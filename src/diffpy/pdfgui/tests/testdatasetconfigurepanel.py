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
Unit tests for DataSetConfigurePanel class.
"""

import unittest

import wx

from diffpy.pdfgui.gui.datasetconfigurepanel import DataSetConfigurePanel
from diffpy.pdfgui.gui.mainframe import MainFrame
from diffpy.pdfgui.tests.testutils import GUITestCase, datafile, tooltiptext

# ----------------------------------------------------------------------------

@unittest.skipIf(wx.VERSION[0] == 3, "FIXME - wx3 font issues")
class TestDataSetConfigurePanel(GUITestCase):

    @classmethod
    def setUpClass(cls):
        GUITestCase.setUpClass()
        GUITestCase.setCmdArgs([datafile("lcmo.ddp")])
        cls.app = wx.App()
        cls.frame = MainFrame(None, -1, "")
        tree = cls.frame.treeCtrlMain
        fits = tree.GetChildren(tree.root)
        dsids = tree.GetDataSets(fits[0])
        cls.frame.makeTreeSelection(dsids[0])
        return


    @classmethod
    def tearDownClass(cls):
        cls.frame.Close()
        cls.app.Destroy()
        GUITestCase.tearDownClass()
        return


    def setUp(self):
        self.panel = self.frame.rightPanel.configurePanel
        assert isinstance(self.panel, DataSetConfigurePanel)
        return


    def test_restrictConstrainedParameters(self):
        "check restrictConstrainedParameters function"
        panel = self.panel
        self.assertFalse(panel.textCtrlScaleFactor.IsEditable())
        self.assertTrue(panel.textCtrlQbroad.IsEditable())
        self.assertEqual('@100', tooltiptext(panel.textCtrlScaleFactor))
        return

# End of class TestDataSetConfigurePanel

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
