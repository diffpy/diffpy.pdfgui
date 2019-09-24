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
Unit tests for class InsertRowsDialog
"""

import unittest

import wx
from diffpy.pdfgui.gui.insertrowsdialog import InsertRowsDialog
from diffpy.pdfgui.tests.testutils import GUITestCase

# ----------------------------------------------------------------------------

class TestInsertRowsDialog(GUITestCase):

    def setUp(self):
        self.app = wx.App()
        self.dialog = InsertRowsDialog(None)
        return

    def tearDown(self):
        self.dialog.Close()
        self.app.Destroy()
        return


    def test_spin_ctrl_rows(self):
        "Check default number of rows to insert"
        d = self.dialog
        self.assertEqual(1, d.spin_ctrl_Rows.GetValue())
        return

# End of class TestInsertRowsDialog

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
