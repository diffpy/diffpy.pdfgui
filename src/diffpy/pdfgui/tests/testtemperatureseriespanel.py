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
Unit tests for the TemperatureSeriesPanel class.
"""

import unittest

import wx

from diffpy.pdfgui.gui.temperatureseriespanel import TemperatureSeriesPanel
from diffpy.pdfgui.tests.testutils import GUITestCase, overridefiledialog
from diffpy.pdfgui.tests.testutils import datafile

# ----------------------------------------------------------------------------

class TestTemperatureSeriesPanel(GUITestCase):

    def setUp(self):
        self.app = wx.App()
        self.frame = wx.Frame(None)
        self.panel = TemperatureSeriesPanel(self.frame)
        self.panel.mainFrame = self._mockUpMainFrame()
        self.panel.mainFrame.workpath = datafile('')
        return

    def tearDown(self):
        self.frame.Close()
        self.app.Destroy()
        return


    def test_onAdd(self):
        "Check TemperatureSeriesPanel.onAdd"
        panel = self.panel
        paths = ['T017K.gr', '137K.gr', 'lcmo_00.gr', 'lcmo_20.gr']
        paths = [datafile(p) for p in paths]
        with overridefiledialog(wx.ID_OK, paths):
            panel.onAdd(None)
        self.assertEqual(paths[-1], panel.fullpath)
        self.assertEqual([17, 137, 10, 10], [tf[0] for tf in panel.datasets])
        return

# End of class TestTemperatureSeriesPanel

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
