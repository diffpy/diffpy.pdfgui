#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfgui     by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2012 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Unit tests for diffpy.pdfgui.
"""


def testsuite():
    '''Build a unit tests suite for the diffpy.pdfgui package.

    Return a unittest.TestSuite object.
    '''
    import unittest
    modulenames = '''
        diffpy.pdfgui.tests.TestBugReport
        diffpy.pdfgui.tests.TestCalculation
        diffpy.pdfgui.tests.TestConstraint
        diffpy.pdfgui.tests.TestFitDataSet
        diffpy.pdfgui.tests.TestFitStructure
        diffpy.pdfgui.tests.TestLoadProject
        diffpy.pdfgui.tests.TestPDFDataSet
        diffpy.pdfgui.tests.TestPDFGuiControl
        diffpy.pdfgui.tests.TestPDFStructure
        diffpy.pdfgui.tests.TestPdfFitSandbox
        diffpy.pdfgui.tests.TestStructureViewer
    '''.split()
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    mobj = None
    for mname in modulenames:
        exec ('import %s as mobj' % mname)
        suite.addTests(loader.loadTestsFromModule(mobj))
    return suite


def test():
    '''Execute all unit tests for the diffpy.pdfgui package.
    Return a unittest TestResult object.
    '''
    import unittest
    suite = testsuite()
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result


def testdeps():
    '''Execute all unit tests for diffpy.pdfgui and its dependencies.

    Return a unittest TestResult object.
    '''
    import unittest
    modulenames = '''
        diffpy.pdfgui.tests
        diffpy.Structure.tests
        diffpy.pdffit2.tests
        diffpy.utils.tests
    '''.split()
    suite = unittest.TestSuite()
    t = None
    for mname in modulenames:
        exec ('from %s import testsuite as t' % mname)
        suite.addTests(t())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result


# End of file
