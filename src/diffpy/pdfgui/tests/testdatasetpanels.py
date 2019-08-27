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
Unit tests for DataSet panels.
"""

import unittest

import wx

from diffpy.pdfgui.gui.datasetpanel import DataSetPanel
from diffpy.pdfgui.gui.mainframe import MainFrame
from diffpy.pdfgui.tests.testutils import GUITestCase, datafile, tooltiptext

# ----------------------------------------------------------------------------

class TestDataSetPanel(GUITestCase):

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
        self.pconfigure = self.frame.rightPanel.configurePanel
        self.pconstraints = self.frame.rightPanel.constraintPanel
        self.presults = self.frame.rightPanel.resultsPanel
        return


    def _selectpage(self, page):
        nb = self.frame.rightPanel.dataSetNotebook
        nb.SetSelection(page)
        return


    def test_restrictConstrainedParameters(self):
        "check DataSetConfigurePanel.restrictConstrainedParameters method"
        self._selectpage(0)
        panel = self.pconfigure
        self.assertFalse(panel.textCtrlScaleFactor.IsEditable())
        self.assertTrue(panel.textCtrlQbroad.IsEditable())
        self.assertEqual('@100', tooltiptext(panel.textCtrlScaleFactor))
        return


    def test_setConstraintsData(self):
        "check DataSetConstraintPanel.setConstraintsData method"
        self._selectpage(1)
        panel = self.pconstraints
        self.assertEqual('@100', panel.textCtrlScaleFactor.GetValue())
        self.assertEqual('Data scale factor',
                         tooltiptext(panel.textCtrlScaleFactor))
        return

# End of class TestDataSetConfigurePanel

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
