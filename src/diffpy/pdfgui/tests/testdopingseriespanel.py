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
Unit tests for the DopingSeriesPanel class.
"""

import unittest

import wx

from diffpy.pdfgui.gui.dopingseriespanel import DopingSeriesPanel
from diffpy.pdfgui.tests.testutils import GUITestCase, overridefiledialog
from diffpy.pdfgui.tests.testutils import datafile

# ----------------------------------------------------------------------------

class TestDopingSeriesPanel(GUITestCase):

    def setUp(self):
        self.app = wx.App()
        self.frame = wx.Frame(None)
        self.panel = DopingSeriesPanel(self.frame)
        self.panel.mainFrame = self._mockUpMainFrame()
        self.panel.mainFrame.workpath = datafile('')
        return

    def tearDown(self):
        self.frame.Close()
        self.app.Destroy()
        return


    def test_onAdd(self):
        "Check DopingSeriesPanel.onAdd"
        panel = self.panel
        paths = ['x000.gr', 'x020.gr', 'lcmo_00.gr', 'lcmo_20.gr']
        paths = [datafile(p) for p in paths]
        with overridefiledialog(wx.ID_OK, paths):
            panel.onAdd(None)
        self.assertEqual(paths[-1], panel.fullpath)
        self.assertEqual([0, 20, 0, 0.2], [xf[0] for xf in panel.datasets])
        return

# End of class TestDopingSeriesPanel

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
