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

_instructions = """<b>Mouse Controls</b>:<br>
<br><b>L. Click</b>: Select atoms for next spin assignment<br>
<b>R. Click</b>: Undo previous spin assignments<br>
<br><b>Keyboard Controls</b>:
<br><br><b>Enter</b>: Assign Spins after selecting<br>
<b>t</b> : Toggle non-magnetic atoms<br>
<b>b</b> : Toggle bounding box<br>
<b>g</b> : Toggle plot grid<br>
<b>n</b> : Toggle ploted numbers on axes ticks<br>
<b>f</b>: Enter fullscreen mode<br>
<b>Escape</b>: Exit Program<br>
<b>CTRL +</b> / <b>CTRL -</b> : Zoom in or out<br>
<b>U / D Arrows</b>: Change atom size<br>
<b>R</b> / <b>L Arrows</b>: Change vector length"""


class DialogInstructions(wx.Dialog):
    '''"Instructions" Dialog: Shows instructions for magviewer'''

    def __init__(self, *args, **kwds):

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((600, 595))
        self.label_instructions = wx.StaticText(self, wx.ID_ANY, "")
        self.button_OK = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        # end wxGlade
        self.label_instructions.SetLabel(_instructions)

        self.Fit()
        return

    def __set_properties(self):
        self.SetTitle("Instructions")
        self.SetSize((600, 595))

    def __do_layout(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_instructions = wx.BoxSizer(wx.HORIZONTAL)
        sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        sizer_instructions.Add(self.label_instructions, 0, wx.RIGHT, 10)
        sizer_main.Add(sizer_instructions, 0, wx.EXPAND, 0)
        sizer_button.Add((20, 20), 1, wx.EXPAND, 0)
        sizer_button.Add(self.button_OK, 0, wx.RIGHT, 10)
        sizer_main.Add(sizer_button, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_main)
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class DialogInstructions

##### testing code ###########################################################

if __name__ == "__main__":
    app = wx.App()
    dialog = DialogInstructions(None, -1, "")
    dialog.ShowModal()
