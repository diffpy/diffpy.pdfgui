#!/usr/bin/env python

"""Unit tests for class PDFStructure
"""


import unittest

from diffpy.pdfgui.control.pdfstructure import PDFStructure
from diffpy.pdfgui.control.controlerrors import ControlFileError
from diffpy.pdfgui.control.controlerrors import ControlKeyError
from diffpy.pdfgui.tests.testutils import datafile


##############################################################################
class TestPDFStructure(unittest.TestCase):


    def setUp(self):
        self.stru = PDFStructure('noname')
        return


    def tearDown(self):
        return


    def test___init__(self):
        """check PDFStructure.__init__()
        """
        self.assertEqual('noname', self.stru.name)
        return


    def test_read(self):
        """check PDFStructure.read()
        """
        stru = self.stru
        notastructurefile = datafile('300K.gr')
        self.assertRaises(ControlFileError,
                stru.read, notastructurefile, format='pdffit')
        return

#   def test_copy(self):
#       """check PDFStructure.copy()
#       """
#       return


    def test_setvar(self):
        """check PDFStructure.setvar()
        """
        stru = self.stru
        stru.setvar('lat(1)', 4)
        stru.setvar('lat(2)', 5)
        stru.setvar('lat(3)', 7)
        self.assertEqual(4, stru.lattice.a)
        self.assertEqual(5, stru.lattice.b)
        self.assertEqual(7, stru.lattice.c)
        stru.setvar('spdiameter', 17)
        self.assertEqual(17, stru.pdffit['spdiameter'])
        stru.setvar('stepcut', 19)
        self.assertEqual(19, stru.pdffit['stepcut'])
        self.assertRaises(ControlKeyError,
                stru.setvar, 'sstepcut', 6)
        return


    def test_getvar(self):
        """check PDFStructure.getvar()
        """
        from diffpy.Structure import Atom
        stru = self.stru
        abcABG = (3.0, 4.0, 5.0, 81, 82, 83)
        stru.lattice.setLatPar(*abcABG)
        for i in range(6):
            self.assertEqual(abcABG[i], stru.getvar('lat(%i)' % (i + 1)))
        stru.append(Atom('Ni', [0.1, 0.2, 0.3]))
        self.assertEqual(0.1, stru.getvar('x(1)'))
        self.assertEqual(0.2, stru.getvar('y(1)'))
        self.assertEqual(0.3, stru.getvar('z(1)'))
        # spdiameter
        self.assertEqual(0.0, stru.getvar('spdiameter'))
        stru.pdffit['spdiameter'] = 37.7
        self.assertEqual(37.7, stru.getvar('spdiameter'))
        # stepcut
        self.assertEqual(0.0, stru.getvar('stepcut'))
        stru.pdffit['stepcut'] = 17.7
        self.assertEqual(17.7, stru.getvar('stepcut'))
        return


# End of class TestPDFStructure


if __name__ == '__main__':
    unittest.main()

# End of file
