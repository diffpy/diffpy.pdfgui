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
Unit tests for class DialogAbout
"""

import unittest

import wx
from diffpy.pdfgui.gui import aboutdialog
from diffpy.pdfgui.tests.testutils import GUITestCase
from diffpy.pdfgui.tests.testutils import overridewebbrowser

# ----------------------------------------------------------------------------

class TestDialogAbout(GUITestCase):

    def setUp(self):
        self.app = wx.App()
        self.dialog = aboutdialog.DialogAbout(None)
        return

    def tearDown(self):
        self.dialog.Close()
        self.app.Destroy()
        return


    def _clickbutton(self, button):
        e = wx.CommandEvent(wx.EVT_BUTTON.typeId, button.Id)
        self.dialog.ProcessEvent(e)
        return


    def test_LogoClicks(self):
        "Check handling of clicks on various logos"
        d = self.dialog
        stealurl = lambda u: setattr(self, 'url', u)
        with overridewebbrowser(stealurl):
            self._clickbutton(d.bitmap_button_nsf)
            self.assertTrue(self.url.endswith('www.nsf.gov'))
            self._clickbutton(d.bitmap_button_danse)
            self.assertTrue(self.url.endswith('danse.us'))
            self._clickbutton(d.bitmap_button_msu)
            self.assertTrue(self.url.endswith('www.msu.edu'))
            self._clickbutton(d.bitmap_button_columbia)
            self.assertTrue(self.url.endswith('www.columbia.edu'))
        return

# End of class TestDialogAbout

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
