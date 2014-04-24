#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

#
# Phase notebook panel
#
# Just a notebook, holds three panels:  "Configure", "Constraints", "Results"
#
# Dmitriy Bryndin


import wx

from diffpy.pdfgui.gui.pdfpanel import PDFPanel

from diffpy.pdfgui.gui.phaseconfigurepanel import PhaseConfigurePanel
from diffpy.pdfgui.gui.phaseconstraintspanel import PhaseConstraintsPanel
from diffpy.pdfgui.gui.phaseresultspanel import PhaseResultsPanel



class PhaseNotebookPanel(wx.Panel, PDFPanel):
    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.notebook_phase = wx.Notebook(self, -1, style=0)
        self.notebook_phase_pane_Configure   = PhaseConfigurePanel(self.notebook_phase, -1)
        self.notebook_phase_pane_Constraints = PhaseConstraintsPanel(self.notebook_phase, -1)
        self.notebook_phase_pane_Results     = PhaseResultsPanel(self.notebook_phase, -1)

        self.__set_properties()
        self.__do_layout()

        self.notebook_phase.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,  self.onNotebookPageChanged )
        self.notebook_phase.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onNotebookPageChanging )

        self.configuration = None
        self.constraints   = {}
        self.results       = None
        self.mainFrame     = None
        self.focusedId     = 0


    def __set_properties(self):
        pass


    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.notebook_phase.AddPage(self.notebook_phase_pane_Configure,   "Configure")
        self.notebook_phase.AddPage(self.notebook_phase_pane_Constraints, "Constraints")
        self.notebook_phase.AddPage(self.notebook_phase_pane_Results,     "Results")
        sizer_1.Add(self.notebook_phase, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)


    def refresh(self):
        """Refreshes the currently shown panel."""
        if self.mainFrame.quitting: return
        if self.focusedId is -1: return

        panel = self.notebook_phase.GetPage(self.focusedId)

        panel.structure = self.configuration
        panel.constraints = self.constraints
        panel.results = self.results

        # This has to be done here, because this panel does not know who it
        # belongs to until after it is instantiated.
        panel.mainFrame = self.mainFrame
        panel.refresh()
        return

    def onNotebookPageChanging(self, event):
        """Called during the page selection change."""
        focusedId = event.GetOldSelection()
        panel = self.notebook_phase.GetPage(self.focusedId)
        panel._cache()
        return

    def onNotebookPageChanged(self, event):
        """Called after the page selection is changed."""
        self.focusedId = event.GetSelection()
        self.refresh()
        event.Skip()
        return

    # Overloaded from Panel.
    def Enable(self, enable = True):
        """Keep the notebook enabled, just not the panels."""
        self.notebook_phase_pane_Configure.Enable(enable)
        self.notebook_phase_pane_Constraints.Enable(enable)
        self.notebook_phase_pane_Results.Enable(enable)
        return


# end of class PhaseNotebookPanel

##### testing code ############################################################
if __name__ == "__main__":
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
            self.test()


        def dummy(self, *args, **kwds):
            pass

        def dummy_dict(self, *args, **kwds):
            return [True]

        def dummy_true(self, *args, **kwds):
            return True


        def test(self):
            '''Testing code goes here'''
            from diffpy.Structure.PDFFitStructure import PDFFitStructure
            from diffpy.pdfgui.control.constraint import Constraint

            self.window.configuration = PDFFitStructure()
            self.window.configuration.read('../../tests/testdata/LaMnO3.pdb')
            self.window.results       = PDFFitStructure()
            self.window.results.read('../../tests/testdata/LaMnO3.pdb')

            formulas =['@1','@45','23+@3','@5 / 2',' @6 ', 'sin(@5)', '12+2*sqrt(@4)',' cos( @9 ) ','(@9*@9)','@10*2', '@6+@1']
            self.window.constraints = {}
            # fill textcontrols
            for i in xrange( len(self.window.notebook_phase_pane_Constraints.lConstraints) ):
                self.window.constraints[self.window.notebook_phase_pane_Constraints.lConstraints[i]] = Constraint(formulas[i])
            # fill some cells (on diagonal)
            for i in xrange(len(self.window.notebook_phase_pane_Constraints.lAtomConstraints)):
                key = self.window.notebook_phase_pane_Constraints.lAtomConstraints[i] + '('+`i+1`+')'
                self.window.constraints[key] = Constraint(formulas[i])

            self.window.refresh()



    class MyApp(wx.App):
        def OnInit(self):
            wx.InitAllImageHandlers()
            frame_1 = MyFrame(None, -1, "")
            self.SetTopWindow(frame_1)
            frame_1.Show()
            return 1

    app = MyApp(0)
    app.MainLoop()
##### end of testing code #####################################################
