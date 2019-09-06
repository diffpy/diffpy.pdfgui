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

from diffpy.pdfgui.gui.extendedplotframe import ExtendedPlotFrame
from diffpy.pdfgui.tests.testutils import GUITestCase

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


    def test_insertCurve(self):
        "Check ExtendedPlotFrame.insertCurve"
        x = numpy.linspace(-5, 5)
        ys = numpy.sin(x)
        style = {'with': 'lines', 'color': 'blue',
                 'line': 'solid', 'width': 2.3}
        line = self.frame.insertCurve(x, ys, style)
        self.assertEqual(2.3, line.get_linewidth())
        return


    @unittest.expectedFailure
    def test_savePlotData(self):
        # TODO - cover the FileDialog code and invalid wx constants
        assert 0

# End of class TestExtendedPlotFrame

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
