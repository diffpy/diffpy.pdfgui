#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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

# generated by wxGlade 0.9.3 on Fri Jul 19 16:00:35 2019

import wx

from diffpy.pdfgui.gui import tooltips
from diffpy.pdfgui.gui.pdfpanel import PDFPanel
from diffpy.pdfgui.gui.wxextensions.textctrlutils import textCtrlAsGridCell
from diffpy.pdfgui.gui.wxextensions.validators import FLOAT_ONLY, TextValidator


class DataSetConfigurePanel(wx.Panel, PDFPanel):
    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        # begin wxGlade: DataSetConfigurePanel.__init__
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)

        outerSizer = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(outerSizer, 1, wx.EXPAND, 0)

        sizer_panelname = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        outerSizer.Add(sizer_panelname, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.panelNameLabel = wx.StaticText(self, wx.ID_ANY, "Data Set Configuration")
        self.panelNameLabel.SetFont(
            wx.Font(
                18,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                0,
                "",
            )
        )
        sizer_panelname.Add(self.panelNameLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)

        outerSizer.Add((450, 5), 0, 0, 0)

        self.radioBoxStype = wx.RadioBox(
            self,
            wx.ID_ANY,
            "Scatterer Type",
            choices=["Neutron", "X-ray"],
            majorDimension=2,
            style=wx.RA_SPECIFY_COLS,
        )
        self.radioBoxStype.SetMinSize((330, 43))
        self.radioBoxStype.SetSelection(0)
        outerSizer.Add(self.radioBoxStype, 0, wx.ALL, 5)

        self.radioBoxSampling = wx.RadioBox(
            self,
            wx.ID_ANY,
            "Data Sampling",
            choices=["Data", "Nyquist", "Custom"],
            majorDimension=3,
            style=wx.RA_SPECIFY_COLS,
        )
        self.radioBoxSampling.SetMinSize((232, 44))
        self.radioBoxSampling.SetSelection(0)
        outerSizer.Add(self.radioBoxSampling, 0, wx.ALL, 5)

        grid_sizer_1 = wx.FlexGridSizer(5, 6, 5, 10)
        outerSizer.Add(grid_sizer_1, 0, wx.ALL | wx.EXPAND, 5)

        self.labelDataRange = wx.StaticText(self, wx.ID_ANY, "Data Range")
        grid_sizer_1.Add(
            self.labelDataRange,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT,
            5,
        )

        self.textCtrlDataFrom = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.textCtrlDataFrom.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        grid_sizer_1.Add(self.textCtrlDataFrom, 0, 0, 0)

        self.labelDataTo = wx.StaticText(self, wx.ID_ANY, "to")
        grid_sizer_1.Add(self.labelDataTo, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 20)

        self.textCtrlDataTo = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.textCtrlDataTo.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        grid_sizer_1.Add(self.textCtrlDataTo, 0, 0, 0)

        self.labelDataStep = wx.StaticText(self, wx.ID_ANY, "spacing")
        grid_sizer_1.Add(
            self.labelDataStep,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT,
            20,
        )

        self.textCtrlDataStep = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.textCtrlDataStep.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        grid_sizer_1.Add(self.textCtrlDataStep, 0, 0, 0)

        self.labelFitRange = wx.StaticText(self, wx.ID_ANY, "Fit Range", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(
            self.labelFitRange,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT,
            5,
        )

        self.textCtrlFitFrom = wx.TextCtrl(self, wx.ID_ANY, "1.0")
        grid_sizer_1.Add(self.textCtrlFitFrom, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.labelFitTo = wx.StaticText(self, wx.ID_ANY, "to", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(self.labelFitTo, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 20)

        self.textCtrlFitTo = wx.TextCtrl(self, wx.ID_ANY, "10.0")
        grid_sizer_1.Add(self.textCtrlFitTo, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.labelFitStep = wx.StaticText(self, wx.ID_ANY, "spacing")
        grid_sizer_1.Add(
            self.labelFitStep,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT,
            20,
        )

        self.textCtrlFitStep = wx.TextCtrl(self, wx.ID_ANY, "0")
        grid_sizer_1.Add(self.textCtrlFitStep, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.labelScaleFactor = wx.StaticText(self, wx.ID_ANY, "Scale Factor", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(
            self.labelScaleFactor,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT,
            5,
        )

        self.textCtrlScaleFactor = wx.TextCtrl(self, wx.ID_ANY, "1.0")
        grid_sizer_1.Add(self.textCtrlScaleFactor, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.labelQmax = wx.StaticText(self, wx.ID_ANY, "Qmax", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(self.labelQmax, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 20)

        self.textCtrlQmax = wx.TextCtrl(self, wx.ID_ANY, "25.0")
        grid_sizer_1.Add(self.textCtrlQmax, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.blank1_copy = wx.StaticText(self, wx.ID_ANY, "")
        grid_sizer_1.Add(self.blank1_copy, 0, 0, 0)

        self.blank1_copy_4 = wx.StaticText(self, wx.ID_ANY, "")
        grid_sizer_1.Add(self.blank1_copy_4, 0, 0, 0)

        self.labelQdamp = wx.StaticText(self, wx.ID_ANY, "Qdamp", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(self.labelQdamp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 5)

        self.textCtrlQdamp = wx.TextCtrl(self, wx.ID_ANY, "0.0")
        grid_sizer_1.Add(self.textCtrlQdamp, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.labelQbroad = wx.StaticText(self, wx.ID_ANY, "Qbroad", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(self.labelQbroad, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 20)

        self.textCtrlQbroad = wx.TextCtrl(self, wx.ID_ANY, "0.0")
        grid_sizer_1.Add(self.textCtrlQbroad, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.blank1_copy_1 = wx.StaticText(self, wx.ID_ANY, "")
        grid_sizer_1.Add(self.blank1_copy_1, 0, 0, 0)

        self.blank1_copy_5 = wx.StaticText(self, wx.ID_ANY, "")
        grid_sizer_1.Add(self.blank1_copy_5, 0, 0, 0)

        self.labelTemperature = wx.StaticText(self, wx.ID_ANY, "Temperature", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(
            self.labelTemperature,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT,
            5,
        )

        self.textCtrlTemperature = wx.TextCtrl(self, wx.ID_ANY, "300.0")
        grid_sizer_1.Add(self.textCtrlTemperature, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.labelDoping = wx.StaticText(self, wx.ID_ANY, "Doping", style=wx.ALIGN_RIGHT)
        grid_sizer_1.Add(self.labelDoping, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 20)

        self.textCtrlDoping = wx.TextCtrl(self, wx.ID_ANY, "1.0")
        grid_sizer_1.Add(self.textCtrlDoping, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.blank1_copy_3 = wx.StaticText(self, wx.ID_ANY, "")
        grid_sizer_1.Add(self.blank1_copy_3, 0, 0, 0)

        self.blank1_copy_7 = wx.StaticText(self, wx.ID_ANY, "")
        grid_sizer_1.Add(self.blank1_copy_7, 0, 0, 0)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Layout()

        self.Bind(wx.EVT_RADIOBOX, self.onStype, self.radioBoxStype)
        self.Bind(wx.EVT_RADIOBOX, self.onSampling, self.radioBoxSampling)
        # end wxGlade
        self.__customProperties()

    # USER CONFIGURATION CODE #################################################

    def __customProperties(self):
        # Set some reasonable defaults
        self.configuration = None
        self.constraints = {}
        self.stypeMap = {0: "N", 1: "X"}
        self.metaNames = ["doping", "temperature"]
        self.constrainables = ["dscale", "qdamp", "qbroad"]
        self.sampList = ["data", "Nyquist", "custom"]
        self._focusedText = None

        # Note that the rstep and fitrstep attributes are special cases, so they
        # are handled separately. Qmax is also handled with these.
        self.ctrlMap = {
            "fitrmin": "textCtrlFitFrom",
            "fitrmax": "textCtrlFitTo",
            "rmin": "textCtrlDataFrom",
            "rmax": "textCtrlDataTo",
            "dscale": "textCtrlScaleFactor",
            "qdamp": "textCtrlQdamp",
            "qbroad": "textCtrlQbroad",
            "temperature": "textCtrlTemperature",
            "doping": "textCtrlDoping",
        }

        # Give each textCtrl a name that can be referenced and setup the
        # validator
        for key, value in self.ctrlMap.items():
            textCtrl = getattr(self, value)
            textCtrl.SetName(key)
            textCtrl.SetValidator(TextValidator(FLOAT_ONLY))
        self.textCtrlFitStep.SetValidator(TextValidator(FLOAT_ONLY))

        # Setup the event code.
        for ctrlName in self.ctrlMap.values():
            textCtrl = getattr(self, ctrlName)
            textCtrl.Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
            textCtrl.Bind(wx.EVT_KILL_FOCUS, self.onLoseFocus)
            textCtrl.Bind(wx.EVT_KEY_DOWN, self.onTextCtrlKey)

        self.textCtrlFitStep.Bind(wx.EVT_KILL_FOCUS, self.onSampling)
        self.textCtrlQmax.Bind(wx.EVT_KILL_FOCUS, self.onSampling)
        self.textCtrlFitStep.Bind(wx.EVT_KEY_DOWN, self.onTextCtrlKey)
        self.textCtrlQmax.Bind(wx.EVT_KEY_DOWN, self.onTextCtrlKey)

        # define tooltips
        self.setToolTips(tooltips.datasetconfigurepanel)
        # make sure tooltips exist for all controls in `constrainables` as
        # this is later assumed in restrictConstrainedParameters code
        for tname in map(self.ctrlMap.get, self.constrainables):
            assert getattr(self, tname).GetToolTip() is not None

        # For blocked text controls.
        self.message = "This variable is constrained. Edit the associated parameter."
        return

    # Create the onTextCtrlKey event handler from textCtrlAsGridCell from
    # wxextensions.textctrlutils
    onTextCtrlKey = textCtrlAsGridCell

    def setConfigurationData(self):
        """Set the values in the configuration panel.

        The values come from the configuration member dictionary.
        stype           --  'N' or 'X'
        dscale          --  float
        qmax            --  float
        qdamp           --  float
        rmin            --  float
        rmax            --  float
        fitrmin         --  float
        fitrmax         --  float
        temperature     --  float
        doping          --  float
        """
        if not self.configuration:
            return

        stype = self.configuration.stype

        if stype == "N":
            self.radioBoxStype.SetSelection(0)
        elif stype == "X":
            self.radioBoxStype.SetSelection(1)
        else:
            self.configuration.stype = "N"
            self.radioBoxStype.SetSelection(0)

        # iterate over all configurable items
        for key, value in self.ctrlMap.items():
            textCtrl = getattr(self, value)

            if key in self.metaNames:
                value = self.configuration.metadata.get(key)
            else:
                value = getattr(self.configuration, key)

            if value is not None:
                textCtrl.SetValue(str(value))
            else:
                textCtrl.SetValue("0.0")

        # Set qmax
        val = self.configuration.qmax
        self.textCtrlQmax.SetValue(str(val))

        # Set the data step
        val = self.configuration.getObsSampling()
        self.textCtrlDataStep.SetValue(str(val))

        # Set up the sampling type and fit step type
        st = self.configuration.getFitSamplingType()
        si = self.sampList.index(st)
        self.radioBoxSampling.SetSelection(si)
        val = self.configuration.fitrstep
        self.textCtrlFitStep.SetValue(str(val))

        # Make sure the sampling info is consistent
        self.onSampling(None)
        return

    def restrictConstrainedParameters(self):
        """Set 'read-only' boxes that correspond to constrained
        parameters."""
        if not self.configuration:
            return

        self.setToolTips(tooltips.datasetconfigurepanel)
        txtbg = self.textCtrlScaleFactor.DefaultStyle.BackgroundColour

        for key in self.constrainables:
            value = self.ctrlMap[key]
            textCtrl = getattr(self, value)
            if key in self.constraints:
                textCtrl.SetEditable(False)
                textCtrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
                tt = textCtrl.GetToolTip()
                tt.SetTip(self.constraints[key].formula)
            else:
                textCtrl.SetEditable(True)
                textCtrl.SetBackgroundColour(txtbg)

        return

    def __coerseText(self, value):
        """Turn the text representation of a float into a float."""
        if not value:
            value = "0"
        if value[-1].lower() in ("-", "e"):
            value += "0"
        return float(value)

    def __adjustFitRange(self, name, value):
        """Check the fit range values.

        The fit range values are set to their defaults (the data range)
        when the fit range is nonsensical.
        """
        if name == "fitrmin":
            if value < self.configuration.rmin or value >= self.configuration.fitrmax:
                value = self.configuration.rmin
                self.textCtrlFitFrom.SetValue(str(value))
        elif name == "fitrmax":
            if value < self.configuration.fitrmin or value >= self.configuration.rmax:
                value = self.configuration.rmax
                self.textCtrlFitTo.SetValue(str(value))
        return value

    # EVENT CODE #############################################################

    def onStype(self, event):  # wxGlade: DataSetConfigurePanel.<event_handler>
        """Record the user's selection for stype."""
        value = event.GetInt()
        self.configuration.stype = self.stypeMap[value]
        self.mainFrame.needsSave()
        return

    def onSampling(self, event):  # wxGlade: DataSetConfigurePanel.<event_handler>
        """Record how the data is to be sampled during the fit.

        This does not use the event argument, so feel free to call this
        method programmatically.
        """
        si = self.radioBoxSampling.GetSelection()
        oldsampling = self.configuration.getFitSamplingType()
        sampling = self.sampList[si]
        oldstep = self.configuration.fitrstep
        # Get the value of the custom sampling and enable/disable status
        if sampling == "custom":  # "custom"
            txtbg = self.textCtrlFitStep.DefaultStyle.BackgroundColour
            step = self.__coerseText(self.textCtrlFitStep.GetValue())
            self.textCtrlFitStep.SetEditable(True)
            self.textCtrlFitStep.SetBackgroundColour(txtbg)
        else:
            step = None
            self.textCtrlFitStep.SetEditable(False)
            self.textCtrlFitStep.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))

        # Set the value of qmax
        val = self.__coerseText(self.textCtrlQmax.GetValue())
        oldqmax = self.configuration.qmax
        if oldqmax != val:
            self.configuration.qmax = val
            self.mainFrame.needsSave()

        # Set the configured value
        if oldsampling != sampling or (sampling == "custom" and oldstep != step):
            self.configuration.setFitSamplingType(sampling, step)
            self.mainFrame.needsSave()
            # Update the text control
            self.textCtrlFitStep.SetValue(str(self.configuration.fitrstep))

        if event is not None:
            event.Skip()
        return

    def onSetFocus(self, event):
        """Saves a TextCtrl value, to be used later."""
        self._focusedText = event.GetEventObject().GetValue()
        event.Skip()
        return

    def onLoseFocus(self, event):
        """Record the user's selection for the text ctrl data."""
        event.Skip()
        if not self.configuration:
            return
        textCtrl = event.GetEventObject()
        value = textCtrl.GetValue()
        value = self.__coerseText(value)
        name = textCtrl.GetName()
        # Check the fit range
        value = self.__adjustFitRange(name, value)
        if name in self.metaNames:
            temp = self.configuration.metadata.get(name)
            if temp != value:
                self.configuration.metadata[name] = value
                self.mainFrame.needsSave()
        else:
            temp = getattr(self.configuration, name)
            if temp != value:
                setattr(self.configuration, name, value)
                self.mainFrame.needsSave()
        return

    # Methods overloaded from PDFPanel

    def refresh(self):
        """Refresh the panel."""
        self.setConfigurationData()
        self.restrictConstrainedParameters()
        return


# end of class DataSetConfigurePanel
