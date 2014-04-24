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


import os
import unittest

from diffpy.pdfgui.control.controlerrors import ControlRuntimeError

# useful variables
thisfile = locals().get('__file__', 'TestPDFGuiControl.py')
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, 'testdata')

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
        fgoodNi = os.path.join(testdata_dir, 'goodNiScript.py')
        ftwophases = os.path.join(testdata_dir, 'CdSe15_twophases.py')
        fbadNi1 = os.path.join(testdata_dir, 'badNiScript1.py')
        fbadNi2 = os.path.join(testdata_dir, 'badNiScript2.py')
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
