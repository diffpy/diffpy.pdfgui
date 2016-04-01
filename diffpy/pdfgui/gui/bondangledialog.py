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


import wx
from diffpy.pdfgui.gui.pdfpanel import PDFPanel

class BondAngleDialog(wx.Dialog, PDFPanel):
    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.sizer_2_staticbox = wx.StaticBox(self, -1, "Bond Angle Calculation")
        self.instructionsLabel = wx.StaticText(self, -1, "Calculate the angle defined by three atoms.")
        self.atomsLabel = wx.StaticText(self, -1, "Atom Indices")
        self.aSpinCtrl = wx.SpinCtrl(self, -1, "1", min=1, max=1)
        self.bSpinCtrl = wx.SpinCtrl(self, -1, "1", min=1, max=1)
        self.cSpinCtrl = wx.SpinCtrl(self, -1, "1", min=1, max=1)
        self.static_line_1 = wx.StaticLine(self, -1)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.okButton = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin, self.aSpinCtrl)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin, self.bSpinCtrl)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin, self.cSpinCtrl)
        self.__customProperties()

    def __set_properties(self):
        self.SetTitle("Calculate Bond Angles")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SGStructureDialog.__do_layout
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_4_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.instructionsLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_4.Add(self.atomsLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.aSpinCtrl, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.bSpinCtrl, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.cSpinCtrl, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_2.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_4_copy.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_4_copy.Add(self.cancelButton, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_4_copy.Add(self.okButton, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(sizer_4_copy, 0, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        sizer_2.SetSizeHints(self)
        self.Layout()
        # end wxGlade


    ###########################################################################

    def __customProperties(self):
        """Set the custom properties."""
        self.a = 1
        self.b = 2
        self.c = 3
        return

    def setStructure(self, structure):
        """Set the structure and update the widgets.

        This must be called before the spin control boxes will be settable to
        anything other than 1.
        """
        natoms = len(structure)
        self.aSpinCtrl.SetRange(1, natoms)
        self.bSpinCtrl.SetRange(1, natoms)
        self.cSpinCtrl.SetRange(1, natoms)
        self.aSpinCtrl.SetValue(min(1,natoms))
        self.bSpinCtrl.SetValue(min(2,natoms))
        self.cSpinCtrl.SetValue(min(3,natoms))
        self.okButton.Enable(True)
        if natoms < 3:
            self.okButton.Enable(False)
        return

    def getCtrlLetter(self, ctrl):
        """Get the letter associated with the control."""
        if ctrl is self.aSpinCtrl: return "a"
        if ctrl is self.bSpinCtrl: return "b"
        return "c"

    def onSpin(self, event):
        """Handle atom selection events.

        This makes sure that no two controls can have the same value.
        """
        letters = ["a", "b", "c"]
        ctrl = event.GetEventObject()
        val = event.GetSelection()

        atomLetter = self.getCtrlLetter(ctrl)

        # Check to see if the value is increasing or decreasing
        increasing = True
        oldval = getattr(self, atomLetter)
        if val < oldval: increasing = False

        # Check to see if the value is equal to another. If so, move it along in
        # the direction it was going.
        letters.remove(atomLetter)
        newval = val
        loop = True
        while loop:
            loop = False
            for l in letters:
                if newval == getattr(self, l):
                    loop = True
                    if increasing:
                        newval += 1
                    else:
                        newval -= 1

        # Set the new value, depending on what it is.
        if newval > 0 and newval <= ctrl.GetMax():
            setattr(self, atomLetter, newval)
            wx.CallAfter(ctrl.SetValue, newval)
        else:
            setattr(self, atomLetter, oldval)
            wx.CallAfter(ctrl.SetValue, oldval)
        return


    def onOk(self, event):
        event.Skip()
        return

    def onCancel(self, event): # wxGlade: SGStructureDialog.<event_handler>
        event.Skip()
        return

# end of class SGStructureDialog
