#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006-2024 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

# generated by wxGlade 0.4 on Tue Feb 21 12:00:30 2006

import wx

# from diffpy.pdfgui.gui.mainframe import MainPanel
# from diffpy.pdfgui.gui.journalpanel import JournalPanel
# from diffpy.pdfgui.gui.datasetconfigurepanel import DataSetConfigurePanel
# from diffpy.pdfgui.gui.fitnotebookpanel import FitNotebookPanel
# from diffpy.pdfgui.gui.rseriespanel import RSeriesPanel
from diffpy.pdfgui.gui.temperatureseriespanel import TemperatureSeriesPanel


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        # self.window_1 = MainPanel(self, -1)
        # self.window_1 = JournalPanel(self, -1)
        # self.window_1 = DataSetConfigurePanel(self, -1)
        # self.window_1 = FitNotebookPanel(self, -1)
        # self.window_1 = RSeriesPanel(self, -1)
        self.window_1 = TemperatureSeriesPanel(self, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("panel test")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(self.window_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        sizer_3.SetSizeHints(self)
        self.Layout()
        # end wxGlade
        self.SetSize((700, 120))


# end of class MyFrame


class MyApp(wx.App):
    def OnInit(self):
        frame_1 = MyFrame(None, -1, "")
        self.SetTopWindow(frame_1)
        frame_1.Show()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
