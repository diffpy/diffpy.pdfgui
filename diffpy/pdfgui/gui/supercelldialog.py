#!/usr/bin/env python
########################################################################
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
########################################################################

# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4 on Mon Oct 30 11:18:45 2006

import wx

class SupercellDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SupercellDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.sizer_1_staticbox = wx.StaticBox(self, -1, "Supercell Expansion")
        self.aLabel = wx.StaticText(self, -1, "a multiplier")
        self.aSpinCtrl = wx.SpinCtrl(self, -1, "1", min=1, max=10)
        self.bLabel = wx.StaticText(self, -1, "b multiplier")
        self.bSpinCtrl = wx.SpinCtrl(self, -1, "1", min=1, max=10)
        self.cLabel = wx.StaticText(self, -1, "c multiplier")
        self.cSpinCtrl = wx.SpinCtrl(self, -1, "1", min=1, max=10)
        self.static_line_1 = wx.StaticLine(self, -1)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.okButton = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
        # end wxGlade
        self.__customProperties()

    def __set_properties(self):
        # begin wxGlade: SupercellDialog.__set_properties
        self.SetTitle("Supercell Expansion")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SupercellDialog.__do_layout
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.aLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(self.aSpinCtrl, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_2_copy.Add(self.bLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_2_copy.Add(self.bSpinCtrl, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_1.Add(sizer_2_copy, 0, wx.EXPAND, 0)
        sizer_2_copy_1.Add(self.cLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_2_copy_1.Add(self.cSpinCtrl, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_1.Add(sizer_2_copy_1, 0, wx.EXPAND, 0)
        sizer_3.Add(self.static_line_1, 1, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        sizer_1.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_4.Add(self.cancelButton, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.okButton, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_1.Add(sizer_4, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        # end wxGlade

   ############################################################################

    def __customProperties(self):
        """Set custom properties."""
        # Set the text validators
        self.m = 1
        self.n = 1
        self.o = 1
        return

    def getMNO(self):
        """Get the [m, n, o] expansion parameters from the dialog."""
        return [self.m, self.n, self.o]

    def onOk(self, event): # wxGlade: SupercellDialog.<event_handler>
        """Accept the expansion."""
        self.m = self.aSpinCtrl.GetValue()
        self.n = self.bSpinCtrl.GetValue()
        self.o = self.cSpinCtrl.GetValue()
        event.Skip()
        return

    def onCancel(self, event): # wxGlade: SupercellDialog.<event_handler>
        """Get out of here."""
        event.Skip()
        return

# end of class SupercellDialog
__id__ = "$Id$"