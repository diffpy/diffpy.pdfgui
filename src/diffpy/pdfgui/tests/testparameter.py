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
Unit tests for the Parameter class.
"""

import unittest

import wx

from diffpy.pdfgui.control.parameter import Parameter
from diffpy.pdfgui.control.controlerrors import ControlTypeError
from diffpy.pdfgui.control.controlerrors import ControlKeyError
from diffpy.pdfgui.gui.mainframe import MainFrame
from diffpy.pdfgui.tests.testutils import GUITestCase, datafile

# ----------------------------------------------------------------------------

class TestParameter(GUITestCase):

    @classmethod
    def setUpClass(cls):
        GUITestCase.setUpClass()
        GUITestCase.setCmdArgs([datafile("lcmo.ddp")])
        cls.app = wx.App()
        cls.frame = MainFrame(None, -1, "")
        tree = cls.frame.treeCtrlMain
        fits = tree.GetChildren(tree.root)
        cls.frame.makeTreeSelection(fits[0])
        return


    @classmethod
    def tearDownClass(cls):
        cls.frame.Close()
        cls.app.Destroy()
        GUITestCase.tearDownClass()
        return


    def setUp(self):
        self.fitting = self.frame.rightPanel.fit
        return


    def test___init__(self):
        "check Parameter.__init__"
        p = Parameter(3, 2.2)
        self.assertEqual(3, p.idx)
        self.assertIsNone(p.refined)
        self.assertEqual(2.2, p.initialValue())
        p100 = Parameter(100, self.fitting)
        self.assertAlmostEqual(0.7957747, p100.initialValue(), 6)
        p102 = Parameter(102, "=fit-d300:102")
        self.assertAlmostEqual(1.1811493, p102.initialValue(), 6)
        self.assertRaises(ControlTypeError, Parameter, 1, None)
        return


    def test_initialValue(self):
        "check Parameter.initialValue"
        p1 = Parameter(1, 0.25)
        self.assertEqual(0.25, p1.initialValue())
        self.assertEqual("0.25", p1.initialStr())
        px = Parameter(7, "=undefined")
        self.assertRaises(ControlKeyError, px.initialValue)
        self.assertEqual("=undefined:7", px.initialStr())
        return

# End of class TestParameter

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
