#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Elizabeth Vargas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

import random
import wx


class DialogSetSpins(wx.Dialog):
    '''"Mag Viewer Set Spins" Dialog: '''

    def __init__(self, *args, **kwds):

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((600, 595))
        self.labelSpinVector = wx.StaticText(self, wx.ID_ANY, "<b>Spin Vector</b><br>Format: <b>a,b,c</b>")
        self.textCtrlSpinVector = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.checkboxCrystalCoords = wx.CheckBox(self, label = 'Crystallographic Coordinates (a, b, c)')
        self.labelMagnitude = wx.StaticText(self, wx.ID_ANY, "<b>Magnitude</b><br>(Optional: will default to unit length)<br>")
        self.textCtrlMagnitude = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.labelPropVec = wx.StaticText(self, wx.ID_ANY, "<b>Propagation Vector</b><br>Format: <b>k1,k2,k3</b><br>(Optional: will default to (0, 0, 0))")
        self.textCtrlPropVec = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.labelMultProps = wx.StaticText(self, wx.ID_ANY, "<i>For Multiple Propagation Vectors:<br>insert in tuples of 3, delimited by commas:<br>Ex: (0,0.5,0.5), (1,0,0.5), ...</i>")
        self.buttonSetSpin = wx.Button(self, wx.ID_OK, "Set Spin")
        self.buttonBack = wx.Button(self, wx.ID_OK, "Go Back")

        self.__set_properties()
        self.__do_layout()

        # end wxGlade

        self.Fit()
        return

    def __set_properties(self):
        self.SetTitle("Set Spins")
        self.SetSize((600, 595))

    def __do_layout(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_spin = wx.BoxSizer(wx.VERTICAL)
        sizer_buttons = wx.BoxSizer(wx.VERTICAL)

        sizer_spin.Add(self.labelSpinVector, 0, wx.RIGHT, 10)
        sizer_spin.Add(self.textCtrlSpinVector, 0, wx.RIGHT, 10)
        sizer_spin.Add(self.checkboxCrystalCoords, 0, wx.RIGHT, 10)
        sizer_spin.Add(self.labelMagnitude, 0, wx.RIGHT, 10)
        sizer_spin.Add(self.textCtrlMagnitude, 0, wx.RIGHT, 10)
        sizer_spin.Add(self.labelPropVec, 0, wx.RIGHT, 10)
        sizer_spin.Add(self.labelMultProps, 0, wx.RIGHT, 10)
        sizer_main.Add(sizer_spin, 0, wx.EXPAND, 0)

        sizer_buttons.Add((20, 20), 1, wx.EXPAND, 0)
        sizer_buttons.Add(self.buttonSetSpin, 0, wx.RIGHT, 10)
        sizer_buttons.Add(self.buttonBack, 0, wx.RIGHT, 10)
        sizer_main.Add(sizer_buttons, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_main)
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class DialogSetSpins

##### testing code ###########################################################

if __name__ == "__main__":
    app = wx.App()
    dialog = DialogSetSpins(None, -1, "")
    dialog.ShowModal()
