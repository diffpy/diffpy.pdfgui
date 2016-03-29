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

from diffpy.pdfgui.control.controlerrors import ControlRuntimeError
from diffpy.pdfgui.tests.testutils import datafile


##############################################################################
class TestPDFGuiControl(unittest.TestCase):
    """test methods of PDFGuiControl"""

    def setUp(self):
        from diffpy.pdfgui.control.pdfguicontrol import PDFGuiControl
        self.control = PDFGuiControl()
        return

    def tearDown(self):
        del self.control
        return

    def test_importPdffit2Script(self):
        """check PDFGuiControl.importPdffit2Script()
        """
        self.assertEqual(0, len(self.control.fits))
        fgoodNi = datafile('goodNiScript.py')
        ftwophases = datafile('CdSe15_twophases.py')
        fbadNi1 = datafile('badNiScript1.py')
        fbadNi2 = datafile('badNiScript2.py')
        newfits = self.control.importPdffit2Script(fgoodNi)
        self.assertEqual(1, len(newfits))
        self.assertEqual(1, len(self.control.fits))
        newfits = self.control.importPdffit2Script(ftwophases)
        self.assertEqual(5, len(newfits))
        self.assertEqual(6, len(self.control.fits))
        self.assertRaises(ControlRuntimeError,
                self.control.importPdffit2Script, fbadNi1)
        self.assertRaises(ControlRuntimeError,
                self.control.importPdffit2Script, fbadNi2)
        return

# End of class TestPDFGuiControl

if __name__ == '__main__':
    unittest.main()

# End of file
