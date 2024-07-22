#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow, Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

# generated by wxGlade 0.9.3 on Fri Jul 19 16:05:14 2019


import wx
import wx.grid

from diffpy.pdfgui.gui import phasepanelutils, tooltips
from diffpy.pdfgui.gui.pdfpanel import PDFPanel
from diffpy.pdfgui.gui.wxextensions.autowidthlabelsgrid import AutoWidthLabelsGrid


class PhaseResultsPanel(wx.Panel, PDFPanel):
    """GUI Panel, holds phase (structure) related constraints."""

    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        # begin wxGlade: PhaseResultsPanel.__init__
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)

        sizerMain = wx.BoxSizer(wx.VERTICAL)

        sizerPanelName = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL
        )
        sizerMain.Add(sizerPanelName, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.labelPanelName = wx.StaticText(self, wx.ID_ANY, "Phase Results")
        self.labelPanelName.SetFont(
            wx.Font(
                18,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                0,
                "",
            )
        )
        sizerPanelName.Add(
            self.labelPanelName, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5
        )

        sizerLatticeParameters = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL
        )
        sizerMain.Add(sizerLatticeParameters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        grid_sizer_3 = wx.FlexGridSizer(2, 6, 0, 0)
        sizerLatticeParameters.Add(grid_sizer_3, 1, wx.EXPAND, 0)

        self.labelA = wx.StaticText(self, wx.ID_ANY, "a")
        grid_sizer_3.Add(
            self.labelA, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlA = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_3.Add(self.textCtrlA, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelB = wx.StaticText(self, wx.ID_ANY, "b")
        grid_sizer_3.Add(
            self.labelB, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlB = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_3.Add(self.textCtrlB, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelC = wx.StaticText(self, wx.ID_ANY, "c")
        grid_sizer_3.Add(
            self.labelC, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlC = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_3.Add(self.textCtrlC, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelAlpha = wx.StaticText(self, wx.ID_ANY, "alpha")
        grid_sizer_3.Add(
            self.labelAlpha, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlAlpha = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_3.Add(self.textCtrlAlpha, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelBeta = wx.StaticText(self, wx.ID_ANY, "beta")
        grid_sizer_3.Add(
            self.labelBeta, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlBeta = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_3.Add(self.textCtrlBeta, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelGamma = wx.StaticText(self, wx.ID_ANY, "gamma")
        grid_sizer_3.Add(
            self.labelGamma, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlGamma = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_3.Add(self.textCtrlGamma, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        sizerAdditionalParameters = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL
        )
        sizerMain.Add(sizerAdditionalParameters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        grid_sizer_4 = wx.FlexGridSizer(3, 6, 0, 0)
        sizerAdditionalParameters.Add(grid_sizer_4, 1, wx.EXPAND, 0)

        self.labelScaleFactor = wx.StaticText(self, wx.ID_ANY, "Scale Factor")
        grid_sizer_4.Add(
            self.labelScaleFactor,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL,
            5,
        )

        self.textCtrlScaleFactor = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_READONLY
        )
        grid_sizer_4.Add(
            self.textCtrlScaleFactor, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0
        )

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        self.labelDelta1 = wx.StaticText(self, wx.ID_ANY, "delta1")
        grid_sizer_4.Add(
            self.labelDelta1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlDelta1 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_4.Add(self.textCtrlDelta1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelDelta2 = wx.StaticText(self, wx.ID_ANY, "delta2")
        grid_sizer_4.Add(
            self.labelDelta2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlDelta2 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_4.Add(self.textCtrlDelta2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelSpdiameter = wx.StaticText(self, wx.ID_ANY, "spdiameter")
        grid_sizer_4.Add(
            self.labelSpdiameter,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL,
            5,
        )

        self.textCtrlSpdiameter = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_4.Add(
            self.textCtrlSpdiameter, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0
        )

        self.labelSratio = wx.StaticText(self, wx.ID_ANY, "sratio")
        grid_sizer_4.Add(
            self.labelSratio, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlSratio = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_4.Add(self.textCtrlSratio, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelRcut = wx.StaticText(self, wx.ID_ANY, "rcut")
        grid_sizer_4.Add(
            self.labelRcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlRcut = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_4.Add(self.textCtrlRcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelStepcut = wx.StaticText(self, wx.ID_ANY, "stepcut")
        grid_sizer_4.Add(
            self.labelStepcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5
        )

        self.textCtrlStepcut = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        grid_sizer_4.Add(self.textCtrlStepcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        sizerAtoms = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL)
        sizerMain.Add(sizerAtoms, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizerAtoms.Add(sizer_1, 0, wx.EXPAND, 0)

        self.labelIncludedPairs = wx.StaticText(self, wx.ID_ANY, "Included Pairs")
        sizer_1.Add(self.labelIncludedPairs, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.textCtrlIncludedPairs = wx.TextCtrl(
            self, wx.ID_ANY, "all-all", style=wx.TE_READONLY
        )
        self.textCtrlIncludedPairs.SetMinSize((240, 25))
        sizer_1.Add(self.textCtrlIncludedPairs, 0, wx.ALL, 5)

        self.gridAtoms = AutoWidthLabelsGrid(self, wx.ID_ANY, size=(1, 1))
        self.gridAtoms.CreateGrid(0, 11)
        self.gridAtoms.EnableEditing(0)
        self.gridAtoms.EnableDragRowSize(0)
        self.gridAtoms.SetColLabelValue(0, "elem")
        self.gridAtoms.SetColLabelValue(1, "x")
        self.gridAtoms.SetColLabelValue(2, "y")
        self.gridAtoms.SetColLabelValue(3, "z")
        self.gridAtoms.SetColLabelValue(4, "u11")
        self.gridAtoms.SetColLabelValue(5, "u22")
        self.gridAtoms.SetColLabelValue(6, "u33")
        self.gridAtoms.SetColLabelValue(7, "u12")
        self.gridAtoms.SetColLabelValue(8, "u13")
        self.gridAtoms.SetColLabelValue(9, "u23")
        self.gridAtoms.SetColLabelValue(10, "occ")
        sizerAtoms.Add(self.gridAtoms, 1, wx.EXPAND, 0)

        self.SetSizer(sizerMain)
        sizerMain.Fit(self)

        self.Layout()
        # end wxGlade
        self.__customProperties()
        return

    ##########################################################################
    # Misc Methods

    def __customProperties(self):
        """Custom properties for the panel."""
        # The resulting structure
        self.structure = None
        self.constraints = {}
        self.results = None
        # Define tooltips.
        self.setToolTips(tooltips.phasepanel)
        return

    def _cache(self):
        """Cache the current structure and constraints for future comparison."""
        pass

    def refresh(self):
        """Refreshes wigets on the panel."""
        # This makes the right thing happen in phasepanelutils. It saves a lot
        # of coding.
        pairs = self.structure.getSelectedPairs()
        self.textCtrlIncludedPairs.SetValue(pairs)
        self.structure = self.results
        phasepanelutils.refreshTextCtrls(self)
        phasepanelutils.refreshGrid(self)
        return


# end of class PhaseResultsPanel
