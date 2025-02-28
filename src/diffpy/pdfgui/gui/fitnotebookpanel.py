#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

# generated by wxGlade 0.9.3 on Fri Jul 19 17:16:20 2019

import wx

from diffpy.pdfgui.gui.parameterspanel import ParametersPanel
from diffpy.pdfgui.gui.pdfpanel import PDFPanel
from diffpy.pdfgui.gui.resultspanel import ResultsPanel


class FitNotebookPanel(wx.Panel, PDFPanel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: FitNotebookPanel.__init__
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.fitnotebook = wx.Notebook(self, wx.ID_ANY, style=0)
        self.parametersPanel = ParametersPanel(self.fitnotebook, wx.ID_ANY)
        self.resultsPanel = ResultsPanel(self.fitnotebook, wx.ID_ANY)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged, self.fitnotebook)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging, self.fitnotebook)
        # end wxGlade
        self.__customProperties()

    def __set_properties(self):
        # begin wxGlade: FitNotebookPanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: FitNotebookPanel.__do_layout
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.fitnotebook.AddPage(self.parametersPanel, "Parameters")
        self.fitnotebook.AddPage(self.resultsPanel, "Results")
        sizer_1.Add(self.fitnotebook, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def __customProperties(self):
        """Set the custom properties."""
        self.fit = None
        self.mainFrame = None
        return

    def onPageChanged(self, event):  # wxGlade: FitNotebookPanel.<event_handler>
        """Refresh the panel visible panel."""
        self.refresh()
        return

    def onPageChanging(self, event):  # wxGlade: FitNotebookPanel.<event_handler>
        event.Skip()

    def refresh(self):
        """Refresh the panels."""
        if not self.fit:
            return
        panel = self.fitnotebook.GetCurrentPage()
        panel.mainFrame = self.mainFrame
        panel.refresh()
        panel.fit = self.fit
        panel.parameters = self.fit.parameters
        panel.refresh()

    # Overloaded from Panel.
    def Enable(self, enable=True):
        """Keep the notebook enabled, just not the panels.

        outputPanel is immune from this, since it needs to be interacted
        with.
        """
        self.parametersPanel.Enable(enable)
        return


# end of class FitNotebookPanel
