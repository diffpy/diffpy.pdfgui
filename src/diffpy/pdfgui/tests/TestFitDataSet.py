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

"""Unit tests for fitdataset.py
"""


import unittest
import numpy

import diffpy.pdfgui.control.fitdataset as fds
from diffpy.pdfgui.control.fitdataset import FitDataSet
from diffpy.pdfgui.tests.testutils import datafile

# ----------------------------------------------------------------------------

class TestRoutines(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_grid_interpolation(self):
        """check grid_interpolation()
        """
        x0 = numpy.arange(-5, 5, 0.25)
        y0 = numpy.sin(x0)
        x1 = [-6, x0[0], -0.2, x0[-1], 37]
        y1a = fds.grid_interpolation(x0, y0, x1)
        y1b = fds.grid_interpolation(x0, y0, x1, youtleft=637, youtright=638)
        # outside values
        self.assertEqual(0.0, y1a[0])
        self.assertEqual(637, y1b[0])
        self.assertEqual(0.0, y1a[-1])
        self.assertEqual(638, y1b[-1])
        # boundary values
        self.assertEqual(y0[0], y1a[1])
        self.assertEqual(y0[0], y1b[1])
        self.assertEqual(y0[-1], y1a[3])
        self.assertEqual(y0[-1], y1b[3])
        # inside values
        self.assertAlmostEqual(-0.197923167403618, y1a[2])
        self.assertAlmostEqual(-0.197923167403618, y1b[2])
        # interpolate to empty grid:
        y2 = fds.grid_interpolation(x0, y0, [])
        self.assertEqual(0, len(y2))
        # interpolate over empty grid
        y3 = fds.grid_interpolation([], [], [0, 1])
        self.assertEqual(0, y3[0])
        self.assertEqual(0, y3[1])
        # interpolate over trivial grid
        y4 = fds.grid_interpolation([0], [5], [-1, 0, 1])
        self.assertEqual(0, y4[0])
        self.assertEqual(5, y4[1])
        self.assertEqual(0, y4[2])
        return

# End of class TestRoutines

# ----------------------------------------------------------------------------

class TestFitDataSet(unittest.TestCase):

#   def setUp(self):
#       return
#
#   def tearDown(self):
#       return
#
#   def test___init__(self):
#       """check FitDataSet.__init__()
#       """
#       return
#
#   def test___setattr__(self):
#       """check FitDataSet.__setattr__()
#       """
#       return
#
#   def test___getattr__(self):
#       """check FitDataSet.__getattr__()
#       """
#       return
#
#   def test__getStrId(self):
#       """check FitDataSet._getStrId()
#       """
#       return
#
#   def test_getYNames(self):
#       """check FitDataSet.getYNames()
#       """
#       return
#
#   def test_getXNames(self):
#       """check FitDataSet.getXNames()
#       """
#       return
#
#   def test_getData(self):
#       """check FitDataSet.getData()
#       """
#       return
#
#   def test_clear(self):
#       """check FitDataSet.clear()
#       """
#       return
#
#   def test_clearRefined(self):
#       """check FitDataSet.clearRefined()
#       """
#       return
#
#   def test_obtainRefined(self):
#       """check FitDataSet.obtainRefined()
#       """
#       return
#
#   def test_read(self):
#       """check FitDataSet.read()
#       """
#       return
#
#   def test__updateRcalcRange(self):
#       """check FitDataSet._updateRcalcRange()
#       """
#       return
#
#   def test_readObs(self):
#       """check FitDataSet.readObs()
#       """
#       return
#
#   def test_readStr(self):
#       """check FitDataSet.readStr()
#       """
#       return
#
#   def test_readObsStr(self):
#       """check FitDataSet.readObsStr()
#       """
#       return
#
#   def test_write(self):
#       """check FitDataSet.write()
#       """
#       return
#
#   def test_writeCalc(self):
#       """check FitDataSet.writeCalc()
#       """
#       return
#
#   def test_writeStr(self):
#       """check FitDataSet.writeStr()
#       """
#       return
#
#   def test_writeCalcStr(self):
#       """check FitDataSet.writeCalcStr()
#       """
#       return
#
#   def test_writeObs(self):
#       """check FitDataSet.writeObs()
#       """
#       return
#
#   def test_writeObsStr(self):
#       """check FitDataSet.writeObsStr()
#       """
#       return

    def test__resampledPDFDataSet(self):
        """check FitDataSet._resampledPDFDataSet()
        """
        fNi_data = datafile("Ni_2-8.chi.gr")
        fds = FitDataSet('Ni')
        fds.read(fNi_data)
        npts = len(fds.rcalc)
        rds = fds._resampledPDFDataSet()
        self.assertEqual(npts, len(rds.robs))
        self.assertEqual(npts, len(rds.drobs))
        self.assertEqual(npts, len(rds.Gobs))
        self.assertEqual(npts, len(rds.dGobs))
        # reduce fitrmax to one half
        fds.fitrmax = fds.rmax / 2.0
        npts1 = len(fds.rcalc)
        self.assertTrue(npts1 < npts)
        rds1 = fds._resampledPDFDataSet()
        self.assertEqual(npts1, len(rds1.robs))
        self.assertEqual(npts1, len(rds1.drobs))
        self.assertEqual(npts1, len(rds1.Gobs))
        self.assertEqual(npts1, len(rds1.dGobs))
        return

#   def test_writeResampledObs(self):
#       """check FitDataSet.writeResampledObs()
#       """
#       return
#
#   def test_writeResampledObsStr(self):
#       """check FitDataSet.writeResampledObsStr()
#       """
#       return
#
#   def test_findParameters(self):
#       """check FitDataSet.findParameters()
#       """
#       return
#
#   def test_applyParameters(self):
#       """check FitDataSet.applyParameters()
#       """
#       return
#
#   def test_changeParameterIndex(self):
#       """check FitDataSet.changeParameterIndex()
#       """
#       return
#
#   def test_copy(self):
#       """check FitDataSet.copy()
#       """
#       return
#
#   def test_load(self):
#       """check FitDataSet.load()
#       """
#       return
#
#   def test_save(self):
#       """check FitDataSet.save()
#       """
#       return
#
#   def test_getFitSamplingType(self):
#       """check FitDataSet.getFitSamplingType()
#       """
#       return
#
#   def test_setFitSamplingType(self):
#       """check FitDataSet.setFitSamplingType()
#       """
#       return
#
#   def test_getObsSampling(self):
#       """check FitDataSet.getObsSampling()
#       """
#       return
#
#   def test_getNyquistSampling(self):
#       """check FitDataSet.getNyquistSampling()
#       """
#       return
#
#   def test__updateRcalcSampling(self):
#       """check FitDataSet._updateRcalcSampling()
#       """
#       return
#
#   def test__get_fitrmin(self):
#       """check FitDataSet._get_fitrmin()
#       """
#       return
#
#   def test__set_fitrmin(self):
#       """check FitDataSet._set_fitrmin()
#       """
#       return
#
#   def test__get_fitrmax(self):
#       """check FitDataSet._get_fitrmax()
#       """
#       return
#
#   def test__set_fitrmax(self):
#       """check FitDataSet._set_fitrmax()
#       """
#       return
#
#   def test__get_fitrstep(self):
#       """check FitDataSet._get_fitrstep()
#       """
#       return
#
#   def test__set_fitrstep(self):
#       """check FitDataSet._set_fitrstep()
#       """
#       return
#
#   def test__get_rcalc(self):
#       """check FitDataSet._get_rcalc()
#       """
#       return
#
#   def test__set_rcalc(self):
#       """check FitDataSet._set_rcalc()
#       """
#       return
#
#   def test__get_Gcalc(self):
#       """check FitDataSet._get_Gcalc()
#       """
#       return
#
#   def test__set_Gcalc(self):
#       """check FitDataSet._set_Gcalc()
#       """
#       return
#
#   def test__get_dGcalc(self):
#       """check FitDataSet._get_dGcalc()
#       """
#       return
#
#   def test__set_dGcalc(self):
#       """check FitDataSet._set_dGcalc()
#       """
#       return
#
#   def test__get_Gtrunc(self):
#       """check FitDataSet._get_Gtrunc()
#       """
#       return
#
#   def test__set_Gtrunc(self):
#       """check FitDataSet._set_Gtrunc()
#       """
#       return
#
#   def test__get_dGtrunc(self):
#       """check FitDataSet._get_dGtrunc()
#       """
#       return
#
#   def test__set_dGtrunc(self):
#       """check FitDataSet._set_dGtrunc()
#       """
#       return
#
#   def test__get_Gdiff(self):
#       """check FitDataSet._get_Gdiff()
#       """
#       return
#
#   def test_close(self):
#       """check FitDataSet.close()
#       """
#       return
#
#   def test_getvar(self):
#       """check FitDataSet.getvar()
#       """
#       return
#
#   def test_setvar(self):
#       """check FitDataSet.setvar()
#       """
#       return

# End of class TestFitDataSet

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

# End of file
