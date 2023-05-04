#!/usr/bin/env python

"""Unit tests for class FitStructure
"""


import unittest

from diffpy.structure import Structure
from diffpy.pdfgui.control.pdfstructure import PDFStructure
from diffpy.pdfgui.control.fitstructure import FitStructure
from diffpy.pdfgui.control.constraint import Constraint
from diffpy.pdfgui.tests.testutils import datafile
from diffpy.pdfgui.control.controlerrors import ControlTypeError

# ----------------------------------------------------------------------------

class TestFitStructure(unittest.TestCase):


    def setUp(self):
        self.stru = FitStructure('noname')
        return


    def tearDown(self):
        return


    def test___init__(self):
        """check FitStructure.__init__()
        """
        stru = self.stru
        self.assertEqual('noname', stru.name)
        self.assertEqual('all-all', stru.selected_pairs)
        return


#   def test__update_custom_spacegroup(self):
#       """check FitStructure._update_custom_spacegroup()
#       """
#       return


#   def test_read(self):
#       """check FitStructure.read()
#       """
#       return


#   def test_readStr(self):
#       """check FitStructure.readStr()
#       """
#       return


    def test___getattr__(self):
        """check FitStructure.__getattr__()
        """
        stru = self.stru
        self.assertTrue(stru is stru.initial)
        self.assertRaises(AttributeError, eval,
                'stru.notdefined', locals())
        return


    def test__getStrId(self):
        """check FitStructure._getStrId()
        """
        stru = self.stru
        self.assertEqual('p_noname', stru._getStrId())
        return


#   def test_clearRefined(self):
#       """check FitStructure.clearRefined()
#       """
#       return


#   def test_obtainRefined(self):
#       """check FitStructure.obtainRefined()
#       """
#       return


    def test_findParameters(self):
        """check FitStructure.findParameters()
        """
        stru = self.stru
        stru.read(datafile('Ni.stru'), format='pdffit')
        for a in stru.initial:  a.Uiso = 0.00126651
        stru.constraints['lat(4)'] = Constraint('@1')
        stru.constraints['y(2)'] = Constraint('@3 + 0.4')
        stru.constraints['u11(3)'] = Constraint('@7 * 3.0')
        pd = stru.findParameters()
        self.assertEqual([1, 3, 7], sorted(pd.keys()))
        self.assertEqual(90, pd[1].initialValue())
        self.assertEqual(0.5 - 0.4, pd[3].initialValue())
        self.assertEqual(0.00126651/3.0, pd[7].initialValue())
        return


    def test_applyParameters(self):
        """check FitStructure.applyParameters()
        """
        stru = self.stru
        stru.read(datafile('Ni.stru'), format='pdffit')
        for a in stru.initial:  a.Uiso = 0.00126651
        stru.constraints['lat(4)'] = Constraint('@1')
        stru.constraints['u11(3)'] = Constraint('@7 * 3.0')
        pd = stru.findParameters()
        # adjust Parameter instances in pd
        pd[1].setInitial(99)
        pd[7].setInitial(0.5)
        stru.applyParameters(pd)
        self.assertEqual(99, stru.lattice.alpha)
        self.assertEqual(1.5, stru[2].U11)
        # pd values can be floats
        pd[1] = 89
        stru.applyParameters(pd)
        self.assertEqual(89, stru.lattice.alpha)
        return


    def test_changeParameterIndex(self):
        """check FitStructure.changeParameterIndex()
        """
        stru = self.stru
        stru.constraints['pscale'] = Constraint('@7+3')
        stru.changeParameterIndex(7, 13)
        self.assertEqual('@13+3', stru.constraints['pscale'].formula)
        stru.changeParameterIndex(2, 19)
        self.assertEqual('@13+3', stru.constraints['pscale'].formula)
        return


    # tested in insertAtoms and deleteAtoms
#   def test__popAtomConstraints(self):
#       """check FitStructure._popAtomConstraints()
#       """
#       return


#   def test__restoreAtomConstraints(self):
#       """check FitStructure._restoreAtomConstraints()
#       """
#       return


    def test_insertAtoms(self):
        """check FitStructure.insertAtoms()
        """
        from diffpy.structure import Atom
        stru = self.stru
        stru.read(datafile('Ni.stru'), format='pdffit')
        cns = Constraint('@1')
        stru.constraints['x(2)'] = cns
        stru.insertAtoms(0, [Atom('Na', (0, 0, 0))])
        self.assertEqual(5, len(stru))
        self.assertEqual(1, len(stru.constraints))
        self.assertTrue(cns is stru.constraints['x(3)'])
        stru.insertAtoms(5, [Atom('Cl', (0, 0, 0))])
        self.assertTrue(['x(3)'] == list(stru.constraints.keys()))
        return


    def test_deleteAtoms(self):
        """check FitStructure.deleteAtoms()
        """
        stru = self.stru
        stru.read(datafile('Ni.stru'), format='pdffit')
        cns = Constraint('@1')
        stru.constraints['x(2)'] = cns
        stru.deleteAtoms([3])
        self.assertEqual(['x(2)'], list(stru.constraints.keys()))
        self.assertTrue(cns is next(iter(stru.constraints.values())))
        stru.deleteAtoms([0])
        self.assertEqual(['x(1)'], list(stru.constraints.keys()))
        self.assertTrue(cns is next(iter(stru.constraints.values())))
        stru.deleteAtoms([0])
        self.assertEqual({}, stru.constraints)
        return


#   def test_expandSuperCell(self):
#       """check FitStructure.expandSuperCell()
#       """
#       return
#
#
#   def test_isSpaceGroupPossible(self):
#       """check FitStructure.isSpaceGroupPossible()
#       """
#       return
#
#
#   def test_getSpaceGroupList(self):
#       """check FitStructure.getSpaceGroupList()
#       """
#       return
#
#
#   def test_getSpaceGroup(self):
#       """check FitStructure.getSpaceGroup()
#       """
#       return
#
#
#   def test_expandAsymmetricUnit(self):
#       """check FitStructure.expandAsymmetricUnit()
#       """
#       return
#
#
#   def test_applySymmetryConstraints(self):
#       """check FitStructure.applySymmetryConstraints()
#       """
#       return
#
#
#   def test_setSelectedPairs(self):
#       """check FitStructure.setSelectedPairs()
#       """
#       return
#
#
#   def test_getSelectedPairs(self):
#       """check FitStructure.getSelectedPairs()
#       """
#       return


    def test_getPairSelectionFlags(self):
        """check FitStructure.getPairSelectionFlags()
        """
        cdse = self.stru
        cdse.read(datafile('CdSe_bulk_wur.stru'), format='pdffit')
        self.assertEqual('all-all', cdse.getSelectedPairs())
        psf = cdse.getPairSelectionFlags()
        self.assertEqual(4 * [True], psf['firstflags'])
        self.assertEqual(4 * [True], psf['secondflags'])
        psf = cdse.getPairSelectionFlags('Cd-Cd')
        self.assertEqual(2 * [True] + 2 * [False], psf['firstflags'])
        self.assertEqual(psf['firstflags'], psf['secondflags'])
        psf = cdse.getPairSelectionFlags('all-all, !Cd-')
        self.assertEqual(2 * [False] + 2 * [True], psf['firstflags'])
        self.assertEqual(4 * [True], psf['secondflags'])
        psf = cdse.getPairSelectionFlags('all-all, -!Cd')
        self.assertEqual(4 * [True], psf['firstflags'])
        self.assertEqual(2 * [False] + 2 * [True], psf['secondflags'])
        psf = cdse.getPairSelectionFlags('Cd-3:4')
        self.assertEqual(2 * [True] + 2 * [False], psf['firstflags'])
        self.assertEqual(2 * [False] + 2 * [True], psf['secondflags'])
        psf = cdse.getPairSelectionFlags('all-all, !Se-!Se')
        self.assertEqual(2 * [True] + 2 * [False], psf['firstflags'])
        self.assertEqual(2 * [True] + 2 * [False], psf['secondflags'])
        psf = cdse.getPairSelectionFlags('all-all, !Se-, -!Se')
        self.assertEqual(2 * [True] + 2 * [False], psf['firstflags'])
        self.assertEqual(2 * [True] + 2 * [False], psf['secondflags'])
        psf = cdse.getPairSelectionFlags('1-all')
        self.assertEqual([True] + 3 * [False], psf['firstflags'])
        self.assertEqual(4 * [True], psf['secondflags'])
        return


#   def test_applyPairSelection(self):
#       """check FitStructure.applyPairSelection()
#       """
#       return


    def test_copy(self):
        """check FitStructure.copy()
        """
        stru2 = self.stru.copy()
        self.assertEqual('noname', stru2.name)
        stru3 = Structure()
        self.assertRaises(ControlTypeError, stru2.copy, stru3)
        self.stru.refined = PDFStructure('refined-name')
        stru4 = self.stru.copy()
        self.assertIsNot(self.stru.refined, stru4.refined)
        self.assertEqual('refined-name',  stru4.refined.name)
        return


#   def test_load(self):
#       """check FitStructure.load()
#       """
#       return
#
#
#   def test_save(self):
#       """check FitStructure.save()
#       """
#       return
#
#
#   def test_getYNames(self):
#       """check FitStructure.getYNames()
#       """
#       return
#
#
#   def test_getXNames(self):
#       """check FitStructure.getXNames()
#       """
#       return
#
#
#   def test_getData(self):
#       """check FitStructure.getData()
#       """
#       return


# End of class TestFitStructure

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

# End of file
