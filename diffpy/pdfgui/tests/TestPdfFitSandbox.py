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

"""Unit tests for pdfgui.control.pdffitsandbox.py
"""


import unittest

from diffpy.pdfgui.control.controlerrors import ControlRuntimeError
from diffpy.pdfgui.control.controlerrors import ControlKeyError
from diffpy.pdfgui.control.parameter import Parameter
from diffpy.pdfgui.tests.testutils import datafile


##############################################################################
class TestPdfFitSandbox(unittest.TestCase):
    """test methods of PdfFitSandbox"""

    def setUp(self):
        from diffpy.pdfgui.control.pdffitsandbox import PdfFitSandbox
        self.box = PdfFitSandbox()
        return

    def tearDown(self):
        import cPickle
        cPickle.dumps(self.box)
        return

    def test___init__(self):
        """check PdfFitSandbox.__init__()
        """
        # check if the first fit gets defined
        self.assertEqual(1, len(self.box._fits))
        f0 = self.box._fits[0]
        self.assertEqual('0', f0.name)
        # check string aliases
        sandbox = self.box.sandbox()
        self.assertEqual('X', eval("X", sandbox))
        self.assertEqual('ALL', eval("ALL", sandbox))
        self.assertEqual(None, self.box._curdataset)
        self.assertEqual(None, self.box._curphase)
        return

    def test_allfits(self):
        """check PdfFitSandbox.allfits()
        """
        self.assertEqual(0, len(self.box.allfits()))
        fNi_stru = datafile('Ni.stru')
        self.box.read_struct(fNi_stru)
        self.assertEqual(0, len(self.box.allfits()))
        self.box.refine()
        self.assertEqual(1, len(self.box.allfits()))
        return

    def test_read_struct(self):
        """check PdfFitSandbox.read_struct()
        """
        fNi_stru = datafile('Ni.stru')
        f300K_stru = datafile('300K.stru')
        self.box.read_struct(fNi_stru)
        self.box.read_struct(f300K_stru)
        self.assertEqual(2, len(self.box._fits[-1].strucs))
        self.assertEqual(1, self.box._curphase)
        p0 = self.box._fits[-1].strucs[0]
        p1 = self.box._fits[-1].strucs[1]
        self.assertEqual(4, len(p0))
        self.assertEqual('Ni', p0.name)
        self.assertEqual(20, len(p1))
        self.assertEqual('300K', p1.name)
        self.assertEqual(None, self.box._curdataset)
        return

    def test_read_struct_string(self):
        """check PdfFitSandbox.read_struct_string()
        """
        fNi_stru = datafile('Ni.stru')
        f300K_stru = datafile('300K.stru')
        sNi = open(fNi_stru).read()
        s300K = open(f300K_stru).read()
        self.box.read_struct_string(sNi)
        self.box.read_struct_string(s300K, 'LaMnO3 at 300K')
        self.assertEqual(2, len(self.box._fits[-1].strucs))
        self.assertEqual(1, self.box._curphase)
        p0 = self.box._fits[-1].strucs[0]
        p1 = self.box._fits[-1].strucs[1]
        self.assertEqual(4, len(p0))
        self.assertEqual('', p0.name)
        self.assertEqual(20, len(p1))
        self.assertEqual('LaMnO3 at 300K', p1.name)
        self.assertEqual(None, self.box._curdataset)
        return

    def test_read_data(self):
        """check PdfFitSandbox.read_data()
        """
        fNi_data = datafile("Ni_2-8.chi.gr")
        f300K_data = datafile("300K.gr")
        sandbox = self.box.sandbox()
        sandbox.update({ "fNi_data" : fNi_data, "f300K_data" : f300K_data })
        exec "read_data(fNi_data, X, 40.1, 0.05)" in sandbox
        exec "read_data(f300K_data, N, 32.1, 0.05)" in sandbox
        self.assertEqual(2, len(self.box._fits[-1].datasets))
        self.assertEqual(1, self.box._curdataset)
        d0 = self.box._fits[-1].datasets[0]
        self.assertEqual('Ni_2-8.chi', d0.name)
        self.assertEqual('X', d0.stype)
        self.assertAlmostEqual(40.1, d0.qmax, 8)
        self.assertAlmostEqual(0.05, d0.qdamp, 8)
        self.assertEqual(2000, len(d0.robs))
        d1 = self.box._fits[-1].datasets[1]
        self.assertEqual('300K', d1.name)
        self.assertEqual('N', d1.stype)
        self.assertAlmostEqual(32.1, d1.qmax, 8)
        self.assertAlmostEqual(0.05, d1.qdamp, 8)
        self.assertEqual(2000, len(d1.robs))
        self.assertEqual(None, self.box._curphase)
        return

    def test_read_data_string(self):
        """check PdfFitSandbox.read_data_string()
        """
        fNi_data = datafile("Ni_2-8.chi.gr")
        f300K_data = datafile("300K.gr")
        sNi = open(fNi_data).read()
        s300K = open(f300K_data).read()
        sandbox = self.box.sandbox()
        sandbox.update({ "sNi" : sNi, "s300K" : s300K })
        exec "read_data_string(sNi, X, 40.1, 0.05)" in sandbox
        exec "read_data_string(s300K, N, 32.1, 0.05, 'LaMnO3')" in sandbox
        self.assertEqual(2, len(self.box._fits[-1].datasets))
        self.assertEqual(1, self.box._curdataset)
        d0 = self.box._fits[-1].datasets[0]
        self.assertEqual('', d0.name)
        self.assertEqual('X', d0.stype)
        self.assertAlmostEqual(40.1, d0.qmax, 8)
        self.assertAlmostEqual(0.05, d0.qdamp, 8)
        self.assertEqual(2000, len(d0.robs))
        d1 = self.box._fits[-1].datasets[1]
        self.assertEqual('LaMnO3', d1.name)
        self.assertEqual('N', d1.stype)
        self.assertAlmostEqual(32.1, d1.qmax, 8)
        self.assertAlmostEqual(0.05, d1.qdamp, 8)
        self.assertEqual(2000, len(d1.robs))
        self.assertEqual(None, self.box._curphase)
        return

    def test_read_data_lists(self):
        """check PdfFitSandbox.read_data_lists()
        """
        self.assertRaises(NotImplementedError, self.box.read_data_lists,
                        'X', 40.1, 0.05, [], [] )
        return

    def test_pdfrange(self):
        """check PdfFitSandbox.pdfrange()
        """
        fNi_data = datafile("Ni_2-8.chi.gr")
        f300K_data = datafile("300K.gr")
        self.box.read_data(fNi_data, 'X', 40.1, 0.05)
        self.box.read_data(f300K_data, 'N', 32.1, 0.05)
        sandbox = self.box.sandbox()
        exec "pdfrange(1, 2.3, 11.13)" in sandbox
        exec "pdfrange(2, 5.7, 17.19)" in sandbox
        self.assertEqual(2, len(self.box._fits[-1].datasets))
        d0 = self.box._fits[-1].datasets[0]
        d1 = self.box._fits[-1].datasets[1]
        self.assertAlmostEqual(2.3, d0.fitrmin, 8)
        self.assertAlmostEqual(11.13, d0.fitrmax, 8)
        self.assertAlmostEqual(5.7, d1.fitrmin, 8)
        self.assertAlmostEqual(17.19, d1.fitrmax, 8)
        # exceptions for invalid ranges
        self.assertRaises(ControlRuntimeError, self.box.pdfrange, 1, 10, 1)
        self.assertRaises(ControlRuntimeError, self.box.pdfrange, 1, 0, 10)
        self.assertRaises(ControlRuntimeError, self.box.pdfrange, 1, 1, 1000)
        exec "pdfrange(ALL, 1.0, 7.0)" in sandbox
        self.assertEqual(1.0, d0.fitrmin)
        self.assertEqual(7.0, d0.fitrmax)
        self.assertEqual(1.0, d1.fitrmin)
        self.assertEqual(7.0, d1.fitrmax)
        exec "pdfrange('ALL', 2.0, 9.0)" in sandbox
        self.assertEqual(2.0, d0.fitrmin)
        self.assertEqual(9.0, d0.fitrmax)
        self.assertEqual(2.0, d1.fitrmin)
        self.assertEqual(9.0, d1.fitrmax)
        return

    def test_reset(self):
        """check PdfFitSandbox.reset()
        """
        fNi_stru = datafile('Ni.stru')
        fNi_data = datafile("Ni_2-8.chi.gr")
        sandbox = self.box.sandbox()
        sandbox.update({ "fNi_stru" : fNi_stru, "fNi_data" : fNi_data })
        exec "read_data(fNi_data, X, 40.1, 0.05)" in sandbox
        exec "read_struct(fNi_stru)" in sandbox
        self.assertEqual(1, len(self.box._fits))
        self.assertEqual(1, len(self.box._fits[-1].strucs))
        self.assertEqual(1, len(self.box._fits[-1].datasets))
        self.assertEqual(0, self.box._curdataset)
        self.assertEqual(0, self.box._curphase)
        exec "reset()" in sandbox
        self.assertEqual(1, len(self.box._fits))
        self.assertEqual(0, len(self.box._fits[-1].strucs))
        self.assertEqual(0, len(self.box._fits[-1].datasets))
        self.assertEqual(None, self.box._curdataset)
        self.assertEqual(None, self.box._curphase)
        return

    def test_alloc(self):
        """check PdfFitSandbox.alloc()
        """
        from diffpy.pdfgui.control.calculation import Calculation
        from diffpy.pdfgui.control.fitting import Fitting
        fNi_stru = datafile('Ni.stru')
        sandbox = self.box.sandbox()
        sandbox.update({ "fNi_stru" : fNi_stru })
        exec "read_struct(fNi_stru)" in sandbox
        self.assertEqual(1, len(self.box._fits))
        self.assertEqual(1, len(self.box._fits[-1].strucs))
        self.assertEqual(0, len(self.box._fits[-1].datasets))
        self.failUnless(isinstance(self.box._fits[-1], Fitting))
        exec "alloc(N, 37.0, 0.07, 0.01, 10.0, 1000)" in sandbox
        self.assertEqual(1, len(self.box._fits))
        self.assertEqual(1, len(self.box._fits[-1].strucs))
        self.failUnless(isinstance(self.box._fits[-1], Calculation))
        c = self.box._fits[-1]
        self.assertEqual(37.0, c.qmax)
        self.assertEqual(0.07, c.qdamp)
        self.assertEqual(0.01, c.rmin)
        self.assertAlmostEqual(0.01, c.rstep, 8)
        self.assertAlmostEqual(10.0, c.rmax, 8)
        self.assertEqual(1000, c.rlen)
        return

    def test_calc(self):
        """check PdfFitSandbox.calc()
        """
        from diffpy.pdfgui.control.calculation import Calculation
        fNi_stru = datafile('Ni.stru')
        sandbox = self.box.sandbox()
        sandbox.update({ "fNi_stru" : fNi_stru })
        exec "read_struct(fNi_stru)" in sandbox
        self.assertRaises(ControlRuntimeError, self.box.calc)
        exec "alloc(N, 37.0, 0.07, 0.01, 10.0, 1000)" in sandbox
        self.assertEqual(1, len(self.box._fits))
        exec "calc()" in sandbox
        self.failUnless(isinstance(self.box._fits[0], Calculation))
        self.assertEqual(2, len(self.box._fits))
        self.assertEqual(0, len(self.box._fits[-1].datasets))
        self.assertEqual(0, len(self.box._fits[-1].strucs))
        self.assertEqual(None, self.box._curdataset)
        self.assertEqual(None, self.box._curphase)
        return

    def test_refine(self):
        """check PdfFitSandbox.refine()
        """
        fNi_stru = datafile('Ni.stru')
        fNi_data = datafile("Ni_2-8.chi.gr")
        sandbox = self.box.sandbox()
        sandbox.update({ "fNi_stru" : fNi_stru, "fNi_data" : fNi_data })
        exec "read_data(fNi_data, X, 40.1, 0.05)" in sandbox
        exec "read_struct(fNi_stru)" in sandbox
        exec "refine()" in sandbox
        self.assertEqual(2, len(self.box._fits))
        self.assertEqual(1, len(self.box._fits[0].strucs))
        self.assertEqual(1, len(self.box._fits[0].datasets))
        self.assertEqual(1, len(self.box._fits[1].strucs))
        self.assertEqual(1, len(self.box._fits[1].datasets))
        # check fit linking:
        self.box._fits[-1].parameters[1] = Parameter(1, 0.05)
        exec "refine(0.01)" in sandbox
        self.assertEqual(3, len(self.box._fits))
        names = [ f.name for f in self.box._fits ]
        self.assertEqual('0', names[0])
        self.assertEqual('1', names[1])
        self.assertEqual('2', names[2])
        self.assertEqual(0, self.box._curdataset)
        self.assertEqual(0, self.box._curphase)
        s = self.box._fits[-1].parameters[1].initialStr()
        self.assertEqual("=1:1", s)
        return

    def test_refine_step(self):
        """check PdfFitSandbox.refine_step()
        """
        self.assertRaises(NotImplementedError, self.box.refine_step)
        self.assertRaises(NotImplementedError, self.box.refine_step, 0.01)
        return

    def test_save_pdf(self):
        """check PdfFitSandbox.save_pdf()
        """
        sandbox = self.box.sandbox()
        exec 'save_pdf(1, "filename.fgr")' in sandbox
        return

    def test_save_pdf_string(self):
        """check PdfFitSandbox.save_pdf_string()
        """
        self.assertRaises(NotImplementedError, self.box.save_pdf_string, 1)
        return

    def test_save_dif(self):
        """check PdfFitSandbox.save_dif()
        """
        sandbox = self.box.sandbox()
        exec 'save_dif(1, "filename.diff")' in sandbox
        return

    def test_save_dif_string(self):
        """check PdfFitSandbox.save_dif_string()
        """
        self.assertRaises(NotImplementedError, self.box.save_dif_string, 1)
        return

    def test_save_res(self):
        """check PdfFitSandbox.save_res()
        """
        sandbox = self.box.sandbox()
        exec 'save_res("filename.res")' in sandbox
        return

    def test_save_res_string(self):
        """check PdfFitSandbox.save_res_string()
        """
        self.assertRaises(NotImplementedError, self.box.save_res_string)
        return

    def test_save_struct(self):
        """check PdfFitSandbox.save_struct()
        """
        sandbox = self.box.sandbox()
        exec 'save_struct(1, "filename.rstr")' in sandbox
        return

    def test_save_struct_string(self):
        """check PdfFitSandbox.save_struct_string()
        """
        self.assertRaises(NotImplementedError, self.box.save_struct_string, 1)
        return

    def test_show_struct(self):
        """check PdfFitSandbox.show_struct()
        """
        sandbox = self.box.sandbox()
        exec 'show_struct(1)' in sandbox
        return

    def test_constrain(self):
        """check PdfFitSandbox.constrain()
        """
        sandbox = self.box.sandbox()
        self.assertRaises(ControlKeyError, self.box.constrain, 'delta', 1)
        fNi_stru = datafile('Ni.stru')
        self.box.read_struct(fNi_stru)
        exec 'constrain(delta, 1)' in sandbox
        self.assertRaises(ControlKeyError, self.box.constrain, 'qdamp', 10)
        fNi_data = datafile("Ni_2-8.chi.gr")
        self.box.read_data(fNi_data, "X", 40.1, 0.05)
        exec 'constrain(qdamp, 10)' in sandbox
        exec 'constrain(dscale, 2)' in sandbox
        exec 'constrain(lat(1), 3)' in sandbox
        exec 'constrain(lat(2), 3)' in sandbox
        exec 'constrain(lat(3), "@3")' in sandbox
        exec 'constrain(occ(1), 4)' in sandbox
        exec 'constrain(pfrac, 5)' in sandbox
        exec 'constrain(u11(1), 6)' in sandbox
        exec 'constrain(u22(1), 6)' in sandbox
        exec 'constrain(u33(1), 6)' in sandbox
        exec 'constrain(x(1), "@7+0.5")' in sandbox
        cphase = self.box._fits[-1].strucs[self.box._curphase]
        cdataset = self.box._fits[-1].datasets[self.box._curdataset]
        self.assertEqual(10, len(cphase.constraints))
        self.failUnless('pscale' in cphase.constraints)
        self.assertEqual('@6', cphase.constraints['u11(1)'].formula)
        self.assertEqual('@7+0.5', cphase.constraints['x(1)'].formula)
        self.assertEqual(2, len(cdataset.constraints))
        self.assertEqual('@10', cdataset.constraints['qdamp'].formula)
        exec 'constrain(x(2), 21, IDENT)' in sandbox
        exec 'constrain(y(2), 22, FCOMP)' in sandbox
        exec 'constrain(z(2), 23, FSQR)' in sandbox
        self.assertEqual('@21', cphase.constraints['x(2)'].formula)
        self.assertEqual('1.0-@22', cphase.constraints['y(2)'].formula)
        self.assertEqual('@23*@23', cphase.constraints['z(2)'].formula)
        return

    def test_constrain_calculation(self):
        """check exceptions when attempting to constrain Calculation
        """
        fNi_stru = datafile('Ni.stru')
        sandbox = self.box.sandbox()
        sandbox.update({ "fNi_stru" : fNi_stru })
        exec "read_struct(fNi_stru)" in sandbox
        exec "alloc(N, 37.0, 0.07, 0.01, 10.0, 1000)" in sandbox
        self.assertRaises(ControlRuntimeError,
                self.box.constrain, 'delta', 1)
        self.assertRaises(ControlRuntimeError,
                self.box.constrain, 'qdamp', "@3*@3")
        self.assertRaises(ControlRuntimeError,
                self.box.constrain, 'delta', 1, 'FCOMP')
        return

    def test_setpar(self):
        """check PdfFitSandbox.setpar()
        """
        sandbox = self.box.sandbox()
        curfit = self.box._fits[-1]
        self.box.setpar(1, 5.0)
        self.assertEqual(5.0, curfit.parameters[1].initialValue())
        fNi_stru = datafile('Ni.stru')
        fNi_data = datafile("Ni_2-8.chi.gr")
        self.box.read_struct(fNi_stru)
        self.box.read_data(fNi_data, "X", 40.1, 0.05)
        exec 'constrain(dscale, 1)' in sandbox
        exec 'constrain(lat(1), 3)' in sandbox
        exec 'constrain(lat(2), 3)' in sandbox
        exec 'constrain(lat(3), "@3")' in sandbox
        exec 'setpar(1, 1.25)' in sandbox
        exec 'setpar(3, 4.1)' in sandbox
        self.assertEqual(1.25, curfit.parameters[1].initialValue())
        self.assertEqual(4.1, curfit.parameters[3].initialValue())
        exec 'setpar(1, dscale)' in sandbox
        exec 'setpar(3, lat(1))' in sandbox
        dscale = curfit.datasets[self.box._curdataset].dscale
        a = curfit.strucs[self.box._curphase].lattice.a
        self.assertEqual(dscale, curfit.parameters[1].initialValue())
        self.assertEqual(a, curfit.parameters[3].initialValue())
        return

    def test_getpar(self):
        """check PdfFitSandbox.getpar()
        """
        sandbox = self.box.sandbox()
        curfit = self.box._fits[-1]
        self.box.setpar(1, 5.0)
        self.assertEqual(5.0, eval('getpar(1)', sandbox))
        fNi_stru = datafile('Ni.stru')
        fNi_data = datafile("Ni_2-8.chi.gr")
        self.box.read_struct(fNi_stru)
        self.box.read_data(fNi_data, "X", 40.1, 0.05)
        exec 'setpar(1, dscale)' in sandbox
        exec 'setpar(3, lat(1))' in sandbox
        self.assertEqual(1.0, eval('getpar(1)', sandbox))
        curphase = curfit.strucs[self.box._curphase]
        a = curphase.lattice.a
        self.assertEqual(a, eval('getpar(3)', sandbox))
        return

    def test_fixpar(self):
        """check PdfFitSandbox.fixpar()
        """
        sandbox = self.box.sandbox()
        curfit = self.box._fits[-1]
        for i in range(1, 4):
            curfit.parameters[i] = Parameter(i, 1.0*i)
        exec 'fixpar(1)' in sandbox
        self.assertEqual(True, curfit.parameters[1].fixed)
        self.assertEqual(False, curfit.parameters[2].fixed)
        self.assertEqual(False, curfit.parameters[3].fixed)
        exec 'fixpar(ALL)' in sandbox
        self.assertEqual(True, curfit.parameters[1].fixed)
        self.assertEqual(True, curfit.parameters[2].fixed)
        self.assertEqual(True, curfit.parameters[3].fixed)
        self.assertRaises(ControlKeyError, self.box.fixpar, 77)
        return

    def test_freepar(self):
        """check PdfFitSandbox.freepar()
        """
        sandbox = self.box.sandbox()
        curfit = self.box._fits[-1]
        for i in range(1, 4):
            curfit.parameters[i] = Parameter(i, 1.0*i)
            curfit.parameters[i].fixed = True
        exec 'freepar(1)' in sandbox
        self.assertEqual(False, curfit.parameters[1].fixed)
        self.assertEqual(True, curfit.parameters[2].fixed)
        self.assertEqual(True, curfit.parameters[3].fixed)
        exec 'freepar(ALL)' in sandbox
        self.assertEqual(False, curfit.parameters[1].fixed)
        self.assertEqual(False, curfit.parameters[2].fixed)
        self.assertEqual(False, curfit.parameters[3].fixed)
        self.assertRaises(ControlKeyError, self.box.freepar, 77)
        return

    def test_setvar(self):
        """check PdfFitSandbox.setvar()
        """
        sandbox = self.box.sandbox()
        fNi_stru = datafile('Ni.stru')
        fNi_data = datafile("Ni_2-8.chi.gr")
        self.box.read_struct(fNi_stru)
        self.box.read_data(fNi_data, "X", 40.1, 0.05)
        curfit = self.box._fits[-1]
        curdataset = curfit.datasets[self.box._curdataset]
        curphase = curfit.strucs[self.box._curphase]
        self.assertEqual(40.1, curdataset.qmax)
        exec "setvar(qdamp, 0.007)" in sandbox
        exec "setvar(lat(1), 3.75)" in sandbox
        exec "setvar(x(4), 0.123)" in sandbox
        exec "setvar(u13(1), 0.00123)" in sandbox
        exec "setvar('pscale', 0.97)" in sandbox
        self.assertEqual(0.007, curdataset.qdamp)
        self.assertEqual(3.75, curphase.lattice.a)
        self.assertEqual(0.123, curphase[3].xyz[0])
        self.assertEqual(0.00123, curphase[0].U[0,2])
        self.assertEqual(0.00123, curphase[0].U[2,0])
        self.assertEqual(0.97, curphase.pdffit['scale'])
        self.assertRaises(ControlKeyError, self.box.setvar, 'novar', 0.1)
        return

    def test_getvar(self):
        """check PdfFitSandbox.getvar()
        """
        sandbox = self.box.sandbox()
        f300K_stru = datafile('300K.stru')
        f300K_data = datafile("300K.gr")
        sandbox.update({"f300K_stru" : f300K_stru, "f300K_data" : f300K_data})
        exec "read_data(f300K_data, 'N', 32.1, 0.05)" in sandbox
        exec "read_struct(f300K_stru)" in sandbox
        self.assertEqual(0.05, eval("getvar(qdamp)", sandbox))
        self.assertEqual(1.0, eval("getvar('dscale')", sandbox))
        self.assertEqual(1.0, eval("getvar(dscale)", sandbox))
        self.assertAlmostEqual(0.95182216, eval("getvar(y(3))", sandbox), 8)
        self.assertAlmostEqual(0.00475572, eval("getvar(u22(4))", sandbox), 8)
        self.assertRaises(ControlKeyError, self.box.getvar, 'novar')
        return

    def test_getrw(self):
        """check PdfFitSandbox.getrw()
        """
        self.assertRaises(NotImplementedError, self.box.getrw)
        return

    def test_getR(self):
        """check PdfFitSandbox.getR()
        """
        self.assertRaises(NotImplementedError, self.box.getR)
        return

    def test_getpdf_fit(self):
        """check PdfFitSandbox.getpdf_fit()
        """
        self.assertRaises(NotImplementedError, self.box.getpdf_fit)
        return

    def test_getpdf_obs(self):
        """check PdfFitSandbox.getpdf_obs()
        """
        self.assertRaises(NotImplementedError, self.box.getpdf_obs)
        return

    def test_get_atoms(self):
        """check PdfFitSandbox.get_atoms()
        """
        self.assertRaises(NotImplementedError, self.box.get_atoms)
        return

    def test_setphase(self):
        """check PdfFitSandbox.setphase()
        """
        sandbox = self.box.sandbox()
        fNi_stru = datafile('Ni.stru')
        f300K_stru = datafile('300K.stru')
        self.assertEqual(None, self.box._curphase)
        self.box.read_struct(fNi_stru)
        self.assertEqual(0, self.box._curphase)
        self.box.read_struct(f300K_stru)
        self.assertEqual(1, self.box._curphase)
        self.assertEqual(20, eval("num_atoms()", sandbox))
        exec "setphase(1)" in sandbox
        self.assertEqual(0, self.box._curphase)
        self.assertEqual(4, eval("num_atoms()", sandbox))
        exec "setphase(2)" in sandbox
        self.assertEqual(1, self.box._curphase)
        self.assertEqual(20, eval("num_atoms()", sandbox))
        self.assertRaises(IndexError, self.box.setphase, 3)
        return

    def test_setdata(self):
        """check PdfFitSandbox.setdata()
        """
        sandbox = self.box.sandbox()
        fNi_data = datafile("Ni_2-8.chi.gr")
        f300K_data = datafile("300K.gr")
        self.assertEqual(None, self.box._curdataset)
        self.box.read_data(fNi_data, "X", 40.1, 0.05)
        self.assertEqual(0, self.box._curdataset)
        self.box.read_data(f300K_data, 'N', 32.1, 0.07)
        self.assertEqual(1, self.box._curdataset)
        self.assertEqual(0.07, eval("getvar('qdamp')", sandbox))
        exec "setdata(1)" in sandbox
        self.assertEqual(0, self.box._curdataset)
        self.assertEqual(0.05, eval("getvar('qdamp')", sandbox))
        exec "setdata(2)" in sandbox
        self.assertEqual(1, self.box._curdataset)
        self.assertEqual(0.07, eval("getvar('qdamp')", sandbox))
        self.assertRaises(IndexError, self.box.setdata, 3)
        return

    def test_psel(self):
        """check PdfFitSandbox.psel()
        """
        self.assertRaises(NotImplementedError, self.box.psel, 1)
        return

    def test_pdesel(self):
        """check PdfFitSandbox.pdesel()
        """
        self.assertRaises(NotImplementedError, self.box.pdesel, 1)
        return

    def test_isel(self):
        """check PdfFitSandbox.isel()
        """
        self.assertRaises(NotImplementedError, self.box.isel, 1, 1)
        return

    def test_idesel(self):
        """check PdfFitSandbox.idesel()
        """
        self.assertRaises(NotImplementedError, self.box.idesel, 1, 1)
        return

    def test_jsel(self):
        """check PdfFitSandbox.jsel()
        """
        self.assertRaises(NotImplementedError, self.box.jsel, 1, 1)
        return

    def test_jdesel(self):
        """check PdfFitSandbox.jdesel()
        """
        self.assertRaises(NotImplementedError, self.box.jdesel, 1, 1)
        return

    def test_bang(self):
        """check PdfFitSandbox.bang()
        """
        self.assertRaises(NotImplementedError, self.box.bang, 1, 2, 3)
        return

    def test_blen(self):
        """check PdfFitSandbox.blen()
        """
        sandbox = self.box.sandbox()
        exec 'blen(1, 2)' in sandbox
        exec 'blen(1, 1, 1.5, 5.0)' in sandbox
        exec 'blen(1, 2, 1.5, 5.0)' in sandbox
        return

    def test_show_scat(self):
        """check PdfFitSandbox.show_scat()
        """
        sandbox = self.box.sandbox()
        exec 'show_scat("X")' in sandbox
        return

    def test_show_scat_string(self):
        """check PdfFitSandbox.show_scat_string()
        """
        self.assertRaises(NotImplementedError, self.box.show_scat_string, 'X')
        return

    def test_get_scat(self):
        """check PdfFitSandbox.get_scat()
        """
        self.assertRaises(NotImplementedError, self.box.get_scat)
        return

    def test_set_scat(self):
        """check PdfFitSandbox.set_scat()
        """
        self.assertRaises(NotImplementedError, self.box.set_scat)
        return

    def test_reset_scat(self):
        """check PdfFitSandbox.reset_scat()
        """
        self.assertRaises(NotImplementedError, self.box.reset_scat)
        return

    def test_num_atoms(self):
        """check PdfFitSandbox.num_atoms()
        """
        self.assertRaises(ControlKeyError, self.box.num_atoms)
        sandbox = self.box.sandbox()
        fNi_stru = datafile('Ni.stru')
        self.box.read_struct(fNi_stru)
        self.assertEqual(4, eval('num_atoms()', sandbox))
        return

    def test_lat(self):
        """check PdfFitSandbox.lat()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('lat(1)', eval('lat(1)', sandbox))
        self.assertEqual('lat(2)', eval('lat(2)', sandbox))
        self.assertEqual('lat(3)', eval('lat(3)', sandbox))
        self.assertEqual('lat(4)', eval('lat(4)', sandbox))
        self.assertEqual('lat(5)', eval('lat(5)', sandbox))
        self.assertEqual('lat(6)', eval('lat(6)', sandbox))
        self.box.lat(7)
        return

    def test_x(self):
        """check PdfFitSandbox.x()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('x(1)', eval('x(1)', sandbox))
        return

    def test_y(self):
        """check PdfFitSandbox.y()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('y(1)', eval('y(1)', sandbox))
        return

    def test_z(self):
        """check PdfFitSandbox.z()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('z(1)', eval('z(1)', sandbox))
        return

    def test_u11(self):
        """check PdfFitSandbox.u11()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('u11(1)', eval('u11(1)', sandbox))
        return

    def test_u22(self):
        """check PdfFitSandbox.u22()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('u22(1)', eval('u22(1)', sandbox))
        return

    def test_u33(self):
        """check PdfFitSandbox.u33()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('u33(1)', eval('u33(1)', sandbox))
        return

    def test_u12(self):
        """check PdfFitSandbox.u12()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('u12(1)', eval('u12(1)', sandbox))
        return

    def test_u13(self):
        """check PdfFitSandbox.u13()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('u13(1)', eval('u13(1)', sandbox))
        return

    def test_u23(self):
        """check PdfFitSandbox.u23()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('u23(1)', eval('u23(1)', sandbox))
        return

    def test_occ(self):
        """check PdfFitSandbox.occ()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('occ(1)', eval('occ(1)', sandbox))
        return

    def test_pscale(self):
        """check PdfFitSandbox.pscale()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('pscale', eval('pscale()', sandbox))
        return

    def test_pfrac(self):
        """check PdfFitSandbox.pfrac()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('pscale', eval('pfrac()', sandbox))
        return

    def test_spdiameter(self):
        """check PdfFitSandbox.spdiameter()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('spdiameter', eval('spdiameter()', sandbox))
        return

    def test_stepcut(self):
        """check PdfFitSandbox.stepcut()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('stepcut', eval('stepcut()', sandbox))
        return

    def test_sratio(self):
        """check PdfFitSandbox.sratio() and PdfFitSandbox.srat()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('sratio', eval('sratio()', sandbox))
        self.assertEqual('sratio', eval('srat()', sandbox))
        return

    def test_delta1(self):
        """check PdfFitSandbox.delta1() and PdfFitSandbox.gamma()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('delta1', eval('delta1()', sandbox))
        self.assertEqual('delta1', eval('gamma()', sandbox))
        return

    def test_delta2(self):
        """check PdfFitSandbox.delta2() and PdfFitSandbox.delta()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('delta2', eval('delta2()', sandbox))
        self.assertEqual('delta2', eval('delta()', sandbox))
        return

    def test_dscale(self):
        """check PdfFitSandbox.dscale()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('dscale', eval('dscale()', sandbox))
        return

    def test_qdamp(self):
        """check PdfFitSandbox.qdamp() and PdfFitSandbox.qsig()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('qdamp', eval('qdamp()', sandbox))
        self.assertEqual('qdamp', eval('qsig()', sandbox))
        return

    def test_qbroad(self):
        """check PdfFitSandbox.qbroad() and PdfFitSandbox.qalp()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('qbroad', eval('qbroad()', sandbox))
        self.assertEqual('qbroad', eval('qalp()', sandbox))
        return

    def test_rcut(self):
        """check PdfFitSandbox.rcut()
        """
        sandbox = self.box.sandbox()
        self.assertEqual('rcut', eval('rcut()', sandbox))
        return

# End of TestPdfFitSandbox

if __name__ == '__main__':
    unittest.main()

# End of file
