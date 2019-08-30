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

import os
from unittest import TestCase
from contextlib import contextmanager

import wx

from diffpy.pdfgui.gui import pdfguiglobals
from diffpy.pdfgui.control import pdfguicontrol
from diffpy.pdfgui.gui import mainframe

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


@contextmanager
def overridefiledialog(status, paths):
    "Temporarily replace wx.FileDialog with non-blocking ShowModal()."
    save_filedialog = wx.FileDialog
    class NBFileDialog(wx.FileDialog):
        def ShowModal(self):
            return status
        def GetPaths(self):
            return paths
        pass
    wx.FileDialog = NBFileDialog
    try:
        yield
    finally:
        wx.FileDialog = save_filedialog
    return


def tooltiptext(widget):
    tt = widget.GetToolTip()
    return tt.GetTip()

# GUI-specialized TestCase ---------------------------------------------------

class GUITestCase(TestCase):
    "Test GUI widgets without invoking ErrorReportDialog."

    @classmethod
    def setUpClass(cls):
        cls._save_noerrordialog = pdfguiglobals.dbopts.noerrordialog
        pdfguiglobals.dbopts.noerrordialog = True
        cls._save_noconfirm = pdfguiglobals.dbopts.noconfirm
        pdfguiglobals.dbopts.noconfirm = True
        cls._save_cmdargs = list(pdfguiglobals.cmdargs)
        cls._save_configfilename = pdfguiglobals.configfilename
        mainframe.pdfguicontrol = pdfguicontrol.PDFGuiControl
        cls._save_qmrun = pdfguicontrol.PDFGuiControl.QueueManager.run
        pdfguicontrol.PDFGuiControl.QueueManager.run = lambda self: None
        cls._save_factory = mainframe.pdfguicontrol
        pdfguiglobals.configfilename = os.devnull
        return

    @classmethod
    def tearDownClass(cls):
        pdfguiglobals.dbopts.noerrordialog = cls._save_noerrordialog
        pdfguiglobals.dbopts.noconfirm = cls._save_noconfirm
        pdfguiglobals.cmdargs[:] = cls._save_cmdargs
        pdfguiglobals.configfilename = cls._save_configfilename
        pdfguicontrol.PDFGuiControl.QueueManager.run = cls._save_qmrun
        mainframe.pdfguicontrol = cls._save_factory
        return

    @classmethod
    def setCmdArgs(cls, args):
        assert hasattr(cls, '_save_cmdargs')
        pdfguiglobals.cmdargs[:] = args
        return

    @staticmethod
    def _mockUpMainFrame():
        return _TMainFrame()

# end of class GUITestCase

# Helper for GUITestCase -----------------------------------------------------

class _TMainFrame(object):
    "Think mockup of the used MainFrame methods."

    altered = False

    def needsSave(self):
        self.altered = True
        return

# end of class _TMainFrame

# End of file
