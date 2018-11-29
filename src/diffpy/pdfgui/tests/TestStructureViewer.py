#!/usr/bin/env python

"""Unit tests for diffpy.pdfgui.control.structureviewer
"""


import os
import unittest

from diffpy.pdfgui.control.controlerrors import ControlConfigError
from diffpy.pdfgui.control.structureviewer import getStructureViewer
from diffpy.pdfgui.control.structureviewer import StructureViewer
from diffpy.pdfgui.tests.testutils import datafile


##############################################################################
class TestRoutines(unittest.TestCase):

    def test_getStructureViewer(self):
        """check getStructureViewer() returns a singleton.
        """
        sv0 = getStructureViewer()
        uid0 = id(sv0)
        del sv0
        sv1 = getStructureViewer()
        uid1 = id(sv1)
        self.assertEqual(uid0, uid1)
        return

# End of class TestRoutines


##############################################################################
class TestStructureViewer(unittest.TestCase):


    def setUp(self):
        return


    def tearDown(self):
        return


    def test___init__(self):
        """check StructureViewer.__init__()
        """
        sv = StructureViewer()
        self.assertEqual('%s', sv.argstr)
        return


    def test_getConfig(self):
        """check StructureViewer.getConfig()
        """
        sv = StructureViewer()
        self.assertEqual('%s', sv.getConfig()['argstr'])
        sv.argstr = 'foooo'
        self.assertEqual('foooo', sv.getConfig()['argstr'])
        return


    def test_setConfig(self):
        """check StructureViewer.setConfig()
        """
        sv = StructureViewer()
        cfg0 = sv.getConfig()
        sv.setConfig({'asdf' : 7})
        self.assertEqual(cfg0, sv.getConfig())
        sv.setConfig({'executable' : None})
        self.assertNotEqual(cfg0, sv.getConfig())
        return


    def test_plot(self):
        """check StructureViewer.plot()
        """
        from diffpy.pdfgui.control.fitstructure import FitStructure
        sv = StructureViewer()
        # default executable is empty string
        self.assertEqual('', sv.executable)
        # and so plot raises ControlConfigError
        fs = FitStructure('s1')
        fs.read(datafile('LaMnO3.stru'))
        self.assertRaises(ControlConfigError, sv.plot, fs)
        sv.executable = 'does/not/exist'
        self.assertTrue(None is sv._tmpdir)
        self.assertEqual(0, sv._plotcount)
        self.assertRaises(ControlConfigError, sv.plot, fs)
        self.assertTrue(os.path.isdir(sv._tmpdir))
        self.assertEqual(1, sv._plotcount)
        return


    def test___del__(self):
        """check StructureViewer.__del__()
        """
        import gc
        from diffpy.pdfgui.control.fitstructure import FitStructure
        sv = StructureViewer()
        sv.executable = 'does/not/exist'
        fs = FitStructure('s1')
        fs.read(datafile('LaMnO3.stru'))
        self.assertRaises(ControlConfigError, sv.plot, fs)
        tmpd = sv._tmpdir
        self.assertTrue(os.path.isdir(tmpd))
        del sv
        gc.collect()
        self.assertFalse(os.path.isdir(tmpd))
        return

#   def test__writeTemporaryStructure(self):
#       """check StructureViewer._writeTemporaryStructure()
#       """
#       return
#
#   def test__createTemporaryDirectory(self):
#       """check StructureViewer._createTemporaryDirectory()
#       """
#       return

# End of class TestStructureViewer

if __name__ == '__main__':
    unittest.main()

# End of file
