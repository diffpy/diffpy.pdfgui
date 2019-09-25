#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Unit tests for pdfgui.control.pdfguicontrol.py
"""


import unittest

from diffpy.pdfgui.control.pdfguicontrol import PDFGuiControl

# ----------------------------------------------------------------------------

class TestPDFGuiControl(unittest.TestCase):
    """test methods of PDFGuiControl"""

    def setUp(self):
        self.control = PDFGuiControl()
        return

    def tearDown(self):
        del self.control
        return


    def test___init__(self):
        "check PDFGuiControl.__init__"
        self.assertEqual('', self.control.journal)
        self.assertIsNone(self.control.projfile)
        return

# End of class TestPDFGuiControl

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

# End of file
