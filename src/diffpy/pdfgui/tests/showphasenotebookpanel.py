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

"""Display the PhaseNotebookPanel.
"""


import wx

from diffpy.pdfgui.gui.phasenotebookpanel import PhaseNotebookPanel
from diffpy.pdfgui.tui import LoadProject
from diffpy.pdfgui.tests.testutils import datafile


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.window = PhaseNotebookPanel(self, -1)
        self.SetTitle("testing")
        # choke, mainframe.needsSave() emulation
        self.window.mainFrame = self.window
        self.window.mainFrame.needsSave = self.dummy

        # choke, treeCtrlMain.GetSelections() emulation
        self.window.treeCtrlMain = self.window
        self.window.treeCtrlMain.GetSelections = self.dummy_dict
        #self.window.treeCtrlMain.GetBranchType = self.dummy_true
        self.window.quitting = False
        self.test()


    def dummy(self, *args, **kwds):
        pass

    def dummy_dict(self, *args, **kwds):
        return [True]

    def dummy_true(self, *args, **kwds):
        return True


    def test(self):
        '''Testing code goes here'''
        project = LoadProject(datafile('lcmo.ddp'))
        fstru = project.getPhases()[0]
        self.window.configuration = fstru
        self.window.results = fstru.refined
        self.window.constraints = fstru.constraints
        self.window.refresh()


class MyApp(wx.App):
    def OnInit(self):
        frame_1 = MyFrame(None, -1, "")
        self.SetTopWindow(frame_1)
        frame_1.Show()
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

# End of file
