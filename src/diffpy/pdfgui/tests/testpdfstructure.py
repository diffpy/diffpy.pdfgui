#!/usr/bin/env python

"""Unit tests for class PDFStructure
"""


import unittest

from diffpy.pdfgui.control.pdfstructure import PDFStructure
from diffpy.pdfgui.control.controlerrors import ControlFileError
from diffpy.pdfgui.control.controlerrors import ControlKeyError
from diffpy.pdfgui.tests.testutils import datafile

# ----------------------------------------------------------------------------

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


    def test_copy(self):
        """check PDFStructure.copy()
        """
        stru2 = self.stru.copy()
        self.assertEqual('noname', stru2.name)
        self.assertEqual(self.stru.pdffit, stru2.pdffit)
        self.assertIsNot(self.stru.pdffit['ncell'], stru2.pdffit['ncell'])
        return


    def test_setvar(self):
        """check PDFStructure.setvar()
        """
        stru = self.stru
        stru.addNewAtom('C', [0, 0, 0], anisotropy=True)
        stru.setvar('pscale', 1.5)
        self.assertEqual(1.5, stru.pdffit['scale'])
        stru.setvar('lat(1)', 4)
        stru.setvar('lat(2)', 5)
        stru.setvar('lat(3)', 7)
        self.assertEqual(4, stru.lattice.a)
        self.assertEqual(5, stru.lattice.b)
        self.assertEqual(7, stru.lattice.c)
        stru.setvar('lat(4)', 91)
        stru.setvar('lat(5)', 92)
        stru.setvar('lat(6)', 93)
        self.assertEqual(91, stru.lattice.alpha)
        self.assertEqual(92, stru.lattice.beta)
        self.assertEqual(93, stru.lattice.gamma)
        stru.setvar('spdiameter', 17)
        self.assertEqual(17, stru.pdffit['spdiameter'])
        stru.setvar('stepcut', 19)
        self.assertEqual(19, stru.pdffit['stepcut'])
        self.assertRaises(ControlKeyError,
                stru.setvar, 'sstepcut', 6)
        stru.setvar('x(1)', 0.1)
        stru.setvar('y(1)', 0.2)
        stru.setvar('z(1)', 0.3)
        stru.setvar('occ(1)', 0.9)
        stru.setvar('u23(1)', 0.004)
        self.assertEqual([0.1, 0.2, 0.3], stru[0].xyz.tolist())
        self.assertEqual(0.9, stru[0].occupancy)
        self.assertEqual(0.004, stru[0].U[1, 2])
        self.assertRaises(ControlKeyError, stru.setvar, 'invalid(1)', 7)
        return


    def test_getvar(self):
        """check PDFStructure.getvar()
        """
        from diffpy.structure import Atom
        stru = self.stru
        abcABG = (3.0, 4.0, 5.0, 81, 82, 83)
        stru.lattice.setLatPar(*abcABG)
        for i in range(6):
            self.assertEqual(abcABG[i], stru.getvar('lat(%i)' % (i + 1)))
        stru.append(Atom('Ni', [0.1, 0.2, 0.3]))
        self.assertEqual(0.1, stru.getvar('x(1)'))
        self.assertEqual(0.2, stru.getvar('y(1)'))
        self.assertEqual(0.3, stru.getvar('z(1)'))
        self.assertEqual(1.0, stru.getvar('occ(1)'))
        # pscale
        self.assertEqual(1.0, stru.getvar('pscale'))
        # spdiameter
        self.assertEqual(0.0, stru.getvar('spdiameter'))
        stru.pdffit['spdiameter'] = 37.7
        self.assertEqual(37.7, stru.getvar('spdiameter'))
        # stepcut
        self.assertEqual(0.0, stru.getvar('stepcut'))
        stru.pdffit['stepcut'] = 17.7
        self.assertEqual(17.7, stru.getvar('stepcut'))
        self.assertRaises(ControlKeyError, stru.getvar, 'invalid(1)')
        self.assertRaises(ControlKeyError, stru.getvar, 'invalid')
        return


# End of class TestPDFStructure

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

# End of file
