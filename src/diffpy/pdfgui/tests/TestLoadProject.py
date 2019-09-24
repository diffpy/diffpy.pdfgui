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

"""Unit tests for tui.py
"""


import unittest

from diffpy.pdfgui.control.controlerrors import ControlFileError
from diffpy.pdfgui.tui import LoadProject
from diffpy.pdfgui.tests.testutils import GUITestCase, datafile

# ----------------------------------------------------------------------------

class TestLoadProject(GUITestCase):

    prj_lcmo = None
    prj_lcmo_full = None
    prj_ni = None

    def setUp(self):
        # load project files once
        if TestLoadProject.prj_lcmo is None:
            TestLoadProject.prj_lcmo = LoadProject(datafile('lcmo.ddp'))
            TestLoadProject.prj_lcmo_full = LoadProject(
                    datafile('lcmo_full.ddp'))
            TestLoadProject.prj_ni = LoadProject(datafile('ni.ddp'))
        # assign them to this instance
        self.prj_lcmo = TestLoadProject.prj_lcmo
        self.prj_lcmo_full = TestLoadProject.prj_lcmo_full
        self.prj_ni = TestLoadProject.prj_ni
        return

    def tearDown(self):
        return

    def test___init__(self):
        """check LoadProject.__init__()
        """
        self.assertEqual(1, len(self.prj_ni.getFits()))
        self.assertRaises(ControlFileError, LoadProject, "does/not/exist.ddp")
        return

    def test_getFits(self):
        """check LoadProject.getFits()
        """
        lcmofits = self.prj_lcmo.getFits()
        lcmofullfits = self.prj_lcmo_full.getFits()
        self.assertEqual(1, len(lcmofits))
        self.assertEqual("fit-d300", lcmofits[0].name)
        self.assertEqual(10, len(lcmofullfits))
        self.assertEqual("fit-d300", lcmofullfits[0].name)
        self.assertEqual("fit-d980", lcmofullfits[-1].name)
        return

    def test_getDataSets(self):
        """check LoadProject.getDataSets()
        """
        lcmofullfits = self.prj_lcmo_full.getFits()
        datasets = self.prj_lcmo_full.getDataSets()
        self.assertEqual(10, len(datasets))
        self.assertEqual("d550", datasets[1].name)
        datasets5 = self.prj_lcmo_full.getDataSets(lcmofullfits[:5])
        self.assertEqual(5, len(datasets5))
        self.assertEqual("d720", datasets5[-1].name)
        return

    def test_getPhases(self):
        """check LoadProject.getPhases()
        """
        lcmofullfits = self.prj_lcmo_full.getFits()
        phases = self.prj_lcmo_full.getPhases()
        self.assertAlmostEqual(5.53884, phases[0].refined.lattice.a, 4)
        self.assertAlmostEqual(5.54342, phases[1].refined.lattice.a, 4)
        self.assertEqual(10, len(phases))
        phases3 = self.prj_lcmo_full.getPhases(lcmofullfits[:3])
        self.assertEqual(3, len(phases3))
        return

    def test_getTemperatures(self):
        """check LoadProject.getTemperatures()
        """
        temps = self.prj_lcmo_full.getTemperatures()
        self.assertEqual(10, len(temps))
        self.assertEqual(300, temps[0])
        self.assertEqual(980, temps[-1])
        datasets3 = self.prj_lcmo_full.getDataSets()[:3]
        temps3 = self.prj_lcmo_full.getTemperatures(datasets3)
        self.assertEqual(650, temps3[-1])
        return

    def test_getDopings(self):
        """check LoadProject.getDopings()
        """
        dopings = self.prj_lcmo_full.getDopings()
        self.assertEqual(10*[None], dopings)
        datasets3 = self.prj_lcmo_full.getDataSets()[:3]
        dopings3 = self.prj_lcmo_full.getDopings(datasets3)
        self.assertEqual(3*[None], dopings3)
        return

# End of class TestLoadProject

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

# End of file
