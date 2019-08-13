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
        if self.focusedId == -1: return

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
        # focusedId = event.GetOldSelection()
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

# End of file
