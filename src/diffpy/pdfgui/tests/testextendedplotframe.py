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
Unit tests for the ExtendedPlotFrame class.
"""

import unittest

import numpy
import wx

from diffpy.pdfgui.gui import extendedplotframe as epf
from diffpy.pdfgui.gui.extendedplotframe import ExtendedPlotFrame
from diffpy.pdfgui.control.plotter import Plotter
from diffpy.pdfgui.tests.testutils import GUITestCase, overridefiledialog

# ----------------------------------------------------------------------------

class TestExtendedPlotFrame(GUITestCase):

    def setUp(self):
        self.app = wx.App()
        self.frame = ExtendedPlotFrame(None)
        return

    def tearDown(self):
        self.frame.Close()
        self.app.Destroy()
        return

    def _clicktoolbar(self, tbid):
        e = wx.CommandEvent(wx.EVT_TOOL.typeId, tbid)
        self.frame.toolbar.ProcessEvent(e)
        return


    def test_insertCurve(self):
        "Check ExtendedPlotFrame.insertCurve"
        x = numpy.linspace(-5, 5)
        ys = numpy.sin(x)
        style = {'with': 'lines', 'color': 'blue',
                 'line': 'solid', 'width': 2.3}
        line = self.frame.insertCurve(x, ys, style)
        self.assertEqual(2.3, line.get_linewidth())
        return


    def test_savePlotData(self):
        self.frame.plotter = Plotter()
        # intercept plotter.export to avoid plot setup and temporary files
        self.frame.plotter.export = lambda fn: setattr(self, 'spd', fn)
        self.spd = ''
        with overridefiledialog(wx.ID_OK, ['testfile.dat']):
            self._clicktoolbar(epf.DATA_SAVE_ID)
        self.assertEqual('testfile.dat', self.spd)
        self.spd = ''
        with overridefiledialog(wx.ID_CANCEL, ['testfile2.dat']):
            self._clicktoolbar(epf.DATA_SAVE_ID)
        self.assertEqual('', self.spd)
        return

# End of class TestExtendedPlotFrame

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
