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

# generated by wxGlade 0.9.3 on Fri Jul 19 16:06:15 2019

import math
import wx
from diffpy.pdfgui.control.controlerrors import ControlValueError
from diffpy.pdfgui.gui.pdfpanel import PDFPanel

class SGStructureDialog(wx.Dialog, PDFPanel):
    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        # begin wxGlade: SGStructureDialog.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.numConstrainedLabel = wx.StaticText(self, wx.ID_ANY, "")
        self.sgLabel = wx.StaticText(self, wx.ID_ANY, "Space Group")
        self.sgComboBox = wx.ComboBox(self, wx.ID_ANY, choices=["P1"], style=0)
        self.offsetLabel = wx.StaticText(self, wx.ID_ANY, "Origin Offset")
        self.offsetTextCtrlX = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_PROCESS_ENTER)
        self.offsetTextCtrlY = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_PROCESS_ENTER)
        self.offsetTextCtrlZ = wx.TextCtrl(self, wx.ID_ANY, "0", style=wx.TE_PROCESS_ENTER)
        self.static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.okButton = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_COMBOBOX, self.onSGSelect, self.sgComboBox)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSGTextEnter, self.sgComboBox)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOXTextEnter, self.offsetTextCtrlX)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOYTextEnter, self.offsetTextCtrlY)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOZTextEnter, self.offsetTextCtrlZ)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.onOk, self.okButton)
        # end wxGlade
        self.__customProperties()

    def __set_properties(self):
        # begin wxGlade: SGStructureDialog.__set_properties
        self.SetTitle("Space Group Expansion")
        self.sgComboBox.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SGStructureDialog.__do_layout
        sizer_2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Space Group Expansion"), wx.VERTICAL)
        sizer_4_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.numConstrainedLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sizer_3.Add(self.sgLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sizer_3.Add(self.sgComboBox, 0, wx.ALL, 5)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_4.Add(self.offsetLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sizer_4.Add(self.offsetTextCtrlX, 0, wx.ALL, 5)
        sizer_4.Add(self.offsetTextCtrlY, 0, wx.ALL, 5)
        sizer_4.Add(self.offsetTextCtrlZ, 0, wx.ALL, 5)
        sizer_2.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_2.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_4_copy.Add((0, 0), 1, wx.EXPAND, 0)
        sizer_4_copy.Add(self.cancelButton, 0, wx.ALL, 5)
        sizer_4_copy.Add(self.okButton, 0, wx.ALL, 5)
        sizer_2.Add(sizer_4_copy, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
        # end wxGlade


    ###########################################################################

    def __customProperties(self):
        """Set the custom properties."""
        # setting of combo box items was deferred to updateSpaceGroupList()
        self.spacegroup = None
        self.offset = [0.0,0.0,0.0]
        self.structure = None
        self.indices = []

        self.textCtrls = [self.offsetTextCtrlX, self.offsetTextCtrlY,
                self.offsetTextCtrlZ]

        # Set the focus events.
        for textctrl in self.textCtrls:
            textctrl.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
        self.sgComboBox.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
        return

    def updateSpaceGroupList(self):
        """Update space group choices in combobox according to
        self.structure.getSpaceGroupList().
        Requires that structure attribute is defined.
        """
        self.sgComboBox.Clear()
        sglist = self.structure.getSpaceGroupList()
        self.spacegroup = self.structure.getSpaceGroup('P1')
        for sg in sglist:
            self.sgComboBox.Append(sg.short_name)
        return

    def setStructure(self, structure):
        """Set the structure and update the dialog."""
        self.structure = structure
        self.updateSpaceGroupList()
        sgname = self.structure.pdffit.get("spcgr")
        offset = self.structure.pdffit.get("sgoffset")
        if sgname:
            self.sgComboBox.SetValue(sgname)
        if offset:
            self.offsetTextCtrlX.SetValue(str(offset[0]))
            self.offsetTextCtrlY.SetValue(str(offset[1]))
            self.offsetTextCtrlZ.SetValue(str(offset[2]))
        self.updateWidgets()
        return

    def getSpaceGroup(self):
        """Get the current space group."""
        return self.spacegroup

    def getOffset(self):
        """Get the offset."""
        return self.offset

    def updateWidgets(self):
        """Update the widgets."""
        # Update space group
        sgname = self.sgComboBox.GetValue()
        try:
            self.spacegroup = self.structure.getSpaceGroup(sgname)
            error = None
        except ValueError:
            error = "Space group %s does not exist." % sgname
        # This changes list box value to the short_name of the new spacegroup
        # or to the name of previous spacegroup when getSpaceGroup failed.
        self.sgComboBox.SetValue(self.spacegroup.short_name)

        # Update offset
        for i in range(3):
            textctrl = self.textCtrls[i]
            val = textctrl.GetValue()
            # make sure the value is meaningful
            try:
                val = float(eval("1.0*"+val, dict(math.__dict__)))
            except (NameError, TypeError, SyntaxError):
                val = 0.0
            textctrl.SetValue("%s"%val)
            self.offset[i] = val

        # find how many new atoms would be generated
        from diffpy.structure.symmetryutilities import ExpandAsymmetricUnit
        corepos = [ self.structure[i].xyz for i in self.indices ]
        symposeps = self.structure.symposeps
        eau = ExpandAsymmetricUnit(self.spacegroup, corepos,
                sgoffset=self.offset, eps=symposeps)
        newsize = sum(eau.multiplicity)
        s = ""
        if len(self.indices) != 1:
            s = "s"
        message = "%i atom%s selected.  Expanding to %i positions." %\
                (len(self.indices), s, newsize)
        self.numConstrainedLabel.SetLabel(message)

        # Raise an error if we had to change the space group
        if error:
            raise ControlValueError(error);
        return

    ### Events
    def onKillFocus(self, event):
        """Check value of widgets and update the dialog message."""
        self.updateWidgets()
        event.Skip()
        return

    def onSGTextEnter(self, event): # wxGlade: SGStructureDialog.<event_handler>
        self.updateWidgets()
        self.onOk(None)
        return

    def onSGSelect(self, event): # wxGlade: SGStructureDialog.<event_handler>
        self.updateWidgets()
        return

    def onOXTextEnter(self, event): # wxGlade: SGStructureDialog.<event_handler>
        self.updateWidgets()
        self.onOk(None)
        return

    def onOYTextEnter(self, event): # wxGlade: SGStructureDialog.<event_handler>
        self.updateWidgets()
        self.onOk(None)
        return

    def onOZTextEnter(self, event): # wxGlade: SGStructureDialog.<event_handler>
        self.updateWidgets()
        self.onOk(None)
        return

    def onOk(self, event): # wxGlade: SGStructureDialog.<event_handler>
        # check to see if the space group is consistant
        if not self.structure.isSpaceGroupPossible(self.spacegroup):
            message =  "The chosen space group is not consistent\n"
            message += "with the lattice parameters.\n"
            message += "Would you like to proceed anyways?"
            d = wx.MessageDialog( self, message,
                    "Inconsistent space group", wx.YES_NO)
            code = d.ShowModal()
            if code == wx.ID_YES:
                self.EndModal(wx.ID_OK)
        else:
            self.EndModal(wx.ID_OK)
        return

    def onCancel(self, event): # wxGlade: SGStructureDialog.<event_handler>
        event.Skip()
        return

# end of class SGStructureDialog
