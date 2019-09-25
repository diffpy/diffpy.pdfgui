#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Unit tests for calculation.py
"""


import unittest

from diffpy.pdfgui.control.controlerrors import ControlValueError
from diffpy.pdfgui.control.calculation import Calculation

##############################################################################
class TestCalculation(unittest.TestCase):

    def setUp(self):
        self.calc = Calculation('calc')
        return

    def tearDown(self):
        return

#   def test___init__(self):
#       """check Calculation.__init__()
#       """
#       return
#
#   def test__getStrId(self):
#       """check Calculation._getStrId()
#       """
#       return

    def test_setRGrid(self):
        """check Calculation.setRGrid()
        """
        # helper function
        def rgriddata(calc):
            rv = (calc.rmin, calc.rstep, calc.rmax, calc.rlen)
            return rv
        # original data:
        rgd0 = rgriddata(self.calc)
        # test input argument checks
        self.assertRaises(ControlValueError,
                self.calc.setRGrid, rmin=-1)
        self.assertRaises(ControlValueError,
                self.calc.setRGrid, rmin=0)
        self.assertRaises(ControlValueError,
                self.calc.setRGrid, rmin=500)
        self.assertRaises(ControlValueError,
                self.calc.setRGrid, rstep=0)
        self.assertRaises(ControlValueError,
                self.calc.setRGrid, rmax=1e-10)
        # data should be the same
        self.assertEqual(rgd0, rgriddata(self.calc))
        # check round-offs for very close values
        self.calc.setRGrid(1, 0.2, 10.0 - 1e-14)
        self.assertEqual(1, self.calc.rmin)
        self.assertEqual(10, self.calc.rmax)
        self.assertEqual(0.2, self.calc.rstep)
        self.assertEqual(46, self.calc.rlen)
        # range should cover the argument range.
        self.calc.setRGrid(1, 0.7, 10)
        self.assertEqual(1, self.calc.rmin)
        self.assertTrue(10 < self.calc.rmax)
        self.assertEqual(0.7, self.calc.rstep)
        return

#   def test_start(self):
#       """check Calculation.start()
#       """
#       return
#
#   def test_calculate(self):
#       """check Calculation.calculate()
#       """
#       return
#
#   def test_write(self):
#       """check Calculation.write()
#       """
#       return
#
#   def test_writeStr(self):
#       """check Calculation.writeStr()
#       """
#       return
#
#   def test_load(self):
#       """check Calculation.load()
#       """
#       return
#
#   def test_save(self):
#       """check Calculation.save()
#       """
#       return
#
#   def test_copy(self):
#       """check Calculation.copy()
#       """
#       return
#
#   def test_getYNames(self):
#       """check Calculation.getYNames()
#       """
#       return
#
#   def test_getXNames(self):
#       """check Calculation.getXNames()
#       """
#       return
#
#   def test_getData(self):
#       """check Calculation.getData()
#       """
#       return
#
#   def test_getMetaDataNames(self):
#       """check Calculation.getMetaDataNames()
#       """
#       return
#
#   def test_getMetaData(self):
#       """check Calculation.getMetaData()
#       """
#       return
#
#   def test_close(self):
#       """check Calculation.close()
#       """
#       return

# End of class TestCalculation


if __name__ == '__main__':
    unittest.main()

# End of file
