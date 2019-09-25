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
        def GetPath(self):
            return paths[-1] if paths else ''
        def GetPaths(self):
            return paths
        pass
    wx.FileDialog = NBFileDialog
    try:
        yield
    finally:
        wx.FileDialog = save_filedialog
    return


@contextmanager
def overrideclipboard():
    "Temporarily replace wx.TheClipboard with a dummy object."
    save_theclipboard = wx.TheClipboard
    class _TTheClipboard(object):
        def IsSupported(self, fmt):
            return False
        pass
    wx.TheClipboard = _TTheClipboard()
    try:
        yield wx.TheClipboard
    finally:
        wx.TheClipboard = save_theclipboard
    return


def tooltiptext(widget):
    tt = widget.GetToolTip()
    return tt.GetTip()


def clickcell(grid, leftright, row, col, **kw):
    """Simulate left or right mouse click over wx.grid.Grid

    Parameters
    ----------
    grid : wx.grid.Grid
        The grid object to be clicked
    leftright : str
        The button that is clicked, possible values are ("left", "right").
    row : int
        The zero-based row of the clicked cell.
    col : int
        The zero-based columnt of the clicked cell.
    kw : misc, optional
        Keyword arguments for the wx.GridEvent constructor.
        Typically a keyboard modifier for the click.
    """
    assert leftright in ('left', 'right')
    if leftright == "left":
        eventtype = wx.grid.EVT_GRID_CELL_LEFT_CLICK.typeId
    else:
        eventtype = wx.grid.EVT_GRID_CELL_RIGHT_CLICK.typeId
    kbd = {'kbd': wx.KeyboardState(**kw)}
    # TODO: remove this after deprecations of wxpython 3
    if wx.VERSION[0] == 3:
        kbd = {k.replace('Down', ''): v for k, v in kw.items()}
    e = wx.grid.GridEvent(grid.Id, eventtype, grid, row, col, **kbd)
    grid.ProcessEvent(e)
    return

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
        cls._save_qmrun = (pdfguicontrol.PDFGuiControl.QueueManager.run,)
        pdfguicontrol.PDFGuiControl.QueueManager.run = lambda self: None
        cls._save_factory = (mainframe.pdfguicontrol,)
        cls.__pdfguicontrol = None
        assert mainframe.pdfguicontrol is pdfguicontrol.pdfguicontrol
        mainframe.pdfguicontrol = cls.pdfguicontrol
        pdfguicontrol.pdfguicontrol = cls.pdfguicontrol
        pdfguiglobals.configfilename = os.devnull
        return

    @classmethod
    def tearDownClass(cls):
        pdfguiglobals.dbopts.noerrordialog = cls._save_noerrordialog
        pdfguiglobals.dbopts.noconfirm = cls._save_noconfirm
        pdfguiglobals.cmdargs[:] = cls._save_cmdargs
        pdfguiglobals.configfilename = cls._save_configfilename
        pdfguicontrol.PDFGuiControl.QueueManager.run, = cls._save_qmrun
        mainframe.pdfguicontrol, = cls._save_factory
        pdfguicontrol.pdfguicontrol, = cls._save_factory
        assert mainframe.pdfguicontrol is pdfguicontrol.pdfguicontrol
        cls.__pdfguicontrol = None
        return

    @classmethod
    def setCmdArgs(cls, args):
        assert hasattr(cls, '_save_cmdargs')
        pdfguiglobals.cmdargs[:] = args
        return

    @classmethod
    def pdfguicontrol(cls, *args, **kwargs):
        if cls.__pdfguicontrol is not None:
            return cls.__pdfguicontrol
        cls.__pdfguicontrol = pdfguicontrol.PDFGuiControl(*args, **kwargs)
        return cls.pdfguicontrol()

    @staticmethod
    def _mockUpMainFrame():
        return _TMainFrame()

# end of class GUITestCase

# Helper for GUITestCase -----------------------------------------------------

class _TMainFrame(object):
    "Thin mockup of the used MainFrame methods."

    altered = False

    def needsSave(self):
        self.altered = True
        return

# end of class _TMainFrame

# End of file
