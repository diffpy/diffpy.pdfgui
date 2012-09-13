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

# version
__id__ = '$Id$'

def test():
    '''Execute all unit tests for the diffpy.pdfgui package.
    Return a unittest TestResult object.
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
    for mname in modulenames:
        exec ('import %s as mobj' % mname)
        suite.addTests(loader.loadTestsFromModule(mobj))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result

# End of file
