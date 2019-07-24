#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfgui     by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2016 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Helper routines for running other unit tests.
"""

from unittest import TestCase
from contextlib import contextmanager

from diffpy.pdfgui.gui.pdfguiglobals import dbopts

# helper functions

def datafile(filename):
    from pkg_resources import resource_filename
    rv = resource_filename(__name__, "testdata/" + filename)
    return rv


@contextmanager
def overridewebbrowser(fnc_open):
    "Temporarily replace `webbrowser.open` with given function."
    import webbrowser
    controller = webbrowser.get()
    save_open = controller.open
    def open_override(url, new=0, autoraise=True):
        fnc_open(url)
        return True
    controller.open = open_override
    try:
        yield save_open
    finally:
        del controller.open
        assert controller.open == save_open
    pass

# GUI-specialized TestCase ---------------------------------------------------

class GUITestCase(TestCase):
    "Test GUI widgets without invoking ErrorReportDialog."

    @classmethod
    def setUpClass(cls):
        cls._save_noerrordialog = dbopts.noerrordialog
        return

    @classmethod
    def tearDownClass(cls):
        dbopts.noerrordialog = cls._save_noerrordialog
        return

# end of class GUITestCase

# End of file
