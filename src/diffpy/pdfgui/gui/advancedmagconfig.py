#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Beric Bearnson
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
import wx
import wx.grid
from diffpy.pdfgui.gui.wxextensions.autowidthlabelsgrid import \
        AutoWidthLabelsGrid


class AdvancedFrame(wx.Frame):

    def __init__(self, title, mags, struc):
        wx.Frame.__init__(self, parent=None, title="Advanced Configuration Settings", size=(800,600))
        structure = struc
        self.magnetic_atoms = mags
        panel = AdvancedPanel(self, mags = self.magnetic_atoms, struc = structure)

        self.Show()

class AdvancedPanel(wx.Panel):
    def __init__(self, parent, mags, struc):
        wx.Panel.__init__(self,parent)
        self.structure = struc
        self.magnetic_atoms = mags
        self.advancedAtoms = AutoWidthLabelsGrid(self, wx.ID_ANY, size=(1,1))
        self.btn1 = wx.Button(self, wx.ID_ANY, "Ok")
        self.btn2 = wx.Button(self, wx.ID_ANY, "Cancel")

        self.btn1.Bind(wx.EVT_BUTTON, self.destroy)
        self.btn2.Bind(wx.EVT_BUTTON, self.destroy)
        #colFiveName = ("ξ{}".format("\N{U+0078,U+0031}") + "ξ{}".format("\N{U+0079,U+0032}") + "ξ{}".format("\N{U+007A}"))

        self.__set_properties()
        self.__do_layout()
        self.refresh()


    def __set_properties(self):
        self.advancedAtoms.CreateGrid(5, 7)
        self.advancedAtoms.EnableDragRowSize(0)
        self.advancedAtoms.SetColLabelValue(0, "elem(x,y,z)")
        self.advancedAtoms.SetColLabelValue(1, " g\u209B ")
        self.advancedAtoms.SetColLabelValue(2, " g\u2097 ")
        self.advancedAtoms.SetColLabelValue(3, "Q grid(min,max,step)")
        self.advancedAtoms.SetColLabelValue(4, "custom FF")
        self.advancedAtoms.SetColLabelValue(5, "colFiveName")
        self.advancedAtoms.SetColLabelValue(6, "damping pwr")


    def __do_layout(self):
        sizerMain = wx.BoxSizer(wx.VERTICAL)
        sizerAtoms = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizerAtoms.Add(sizer_1, 0, wx.EXPAND, 0)
        sizerAtoms.Add(self.advancedAtoms, 1, wx.EXPAND, 0)
        sizerMain.Add(sizerAtoms, 5, wx.EXPAND | wx.ALL, 20)
        self.advancedAtoms.AutosizeLabels()
        self.advancedAtoms.AutoSizeColumns()
        sizer_4.Add(2,1,1)
        sizer_4.Add(self.btn2, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        sizer_4.Add(self.btn1, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        sizerMain.Add(sizer_4, 0, wx.EXPAND, 0)
        self.SetSizer(sizerMain)
        sizerMain.Fit(self)
        self.Layout()

    def destroy(self, event):
        frame = self.GetParent()
        frame.Close()


    def refresh(self):
        """Refresh wigets on the panel."""
        if self.structure is None:
            raise ValueError("structure is not defined.")

        ### update the grid ###
        nmagatoms = len(self.magnetic_atoms)
        nrows = self.advancedAtoms.GetNumberRows()
        self.advancedAtoms.BeginBatch()
        # make sure grid has correct number of rows
        if nmagatoms > nrows:
            self.advancedAtoms.InsertRows(numRows = nmagatoms - nrows)
        elif nmagatoms < nrows:
            self.advancedAtoms.DeleteRows(numRows = nrows - nmagatoms)

        # start with clean grid
        self.advancedAtoms.ClearGrid()

        # fill the first 'elem' column with element symbols and x, y, z values if magnetic
        for row, atom in zip(range(natoms), self.structure):
            print(atom.element + " (" + str(atom.xyz[0]) + "," + str(atom.xyz[1]) + "," + str(atom.xyz[2]) + ")")
            print("magnetics", self.magnetics)
            if self.magnetics[row] == 1:
                atom_info = atom.element + " (" + str(atom.xyz[0]) + "," + str(atom.xyz[1]) + "," + str(atom.xyz[2]) + ")"
                self.advancedAtoms.SetCellValue(row, 0, atom_info)


        self.advancedAtoms.AutosizeLabels()
        self.advancedAtoms.AutoSizeColumns()
