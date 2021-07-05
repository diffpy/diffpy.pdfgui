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
from diffpy.pdfgui.gui.phasepanelutils import float2str
from diffpy.pdfgui.gui.wxextensions.autowidthlabelsgrid import \
        AutoWidthLabelsGrid
import numpy as np


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
        self.gridAtoms = AutoWidthLabelsGrid(self, wx.ID_ANY, size=(1,1))
        self.btn1 = wx.Button(self, wx.ID_ANY, "Ok")
        self.btn2 = wx.Button(self, wx.ID_ANY, "Cancel")

        self.btn1.Bind(wx.EVT_BUTTON, self.destroy)
        self.btn2.Bind(wx.EVT_BUTTON, self.destroy)
        #colFiveName = ("ξ{}".format("\N{U+0078,U+0031}") + "ξ{}".format("\N{U+0079,U+0032}") + "ξ{}".format("\N{U+007A}"))

        self.__set_properties()
        self.__do_layout()
        self.refresh()


    def __set_properties(self):
        self.gridAtoms.CreateGrid(5, 7)
        self.gridAtoms.EnableDragRowSize(0)
        self.gridAtoms.SetColLabelValue(0, "elem(x,y,z)")
        self.gridAtoms.SetColLabelValue(1, " g\u209B ")
        self.gridAtoms.SetColLabelValue(2, " g\u2097 ")
        self.gridAtoms.SetColLabelValue(3, "Q grid(min,max,step)")
        self.gridAtoms.SetColLabelValue(4, "custom FF")
        self.gridAtoms.SetColLabelValue(5, "colFiveName")
        self.gridAtoms.SetColLabelValue(6, "damping pwr")


    def __do_layout(self):
        sizerMain = wx.BoxSizer(wx.VERTICAL)
        sizerAtoms = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizerAtoms.Add(sizer_1, 0, wx.EXPAND, 0)
        sizerAtoms.Add(self.gridAtoms, 1, wx.EXPAND, 0)
        sizerMain.Add(sizerAtoms, 5, wx.EXPAND | wx.ALL, 20)
        self.gridAtoms.AutosizeLabels()
        self.gridAtoms.AutoSizeColumns()
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

    def arrayToStr(self, arr):
        """returns basis and kvec numpy arrays in str format
        Ex. [[1 2 3],[4 5 6]] -> (1, 2, 3),(4, 5, 6)"""
        if arr is None or type(arr) != np.ndarray:
            return
        ret = str(arr.astype(float).tolist())[1:-1]
        ret = ret.replace("[","(")
        ret = ret.replace("]",")")
        return ret

    def refresh(self):
        """Refresh wigets on the panel."""
        if self.structure is None:
            raise ValueError("structure is not defined.")

        ### update the grid ###
        nmagatoms = 0
        for m in self.structure.magnetic_atoms:
            if m[0] == 1:
                nmagatoms += 1
        nrows = self.gridAtoms.GetNumberRows()
        self.gridAtoms.BeginBatch()
        # make sure grid has correct number of rows
        if nmagatoms > nrows:
            self.gridAtoms.InsertRows(numRows = nmagatoms - nrows)
        elif nmagatoms < nrows:
            self.gridAtoms.DeleteRows(numRows = nrows - nmagatoms)

        # start with clean grid
        self.gridAtoms.ClearGrid()

        # fill the first 'elem' column with element symbols and x, y, z values if magnetic
        count = 0
        for row, atom in zip(range(len(self.structure)), self.structure):
            if self.structure.magnetic_atoms[row][0] == 1:
                self.gridAtoms.SetRowLabelValue(count, str(row+1))
                atom_info = atom.element + " (" + float2str(atom.xyz[0]) + "," + float2str(atom.xyz[1]) + "," + float2str(atom.xyz[2]) + ")"
                self.gridAtoms.SetCellValue(count, 0, atom_info)

                magSpecies = self.structure.magStructure.species[self.structure.magnetic_atoms[row][1]]
                gS = '0.0' if magSpecies.gL is None else str(magSpecies.gS)
                self.gridAtoms.SetCellValue(count, 1, gS)
                gL = '0.0' if magSpecies.gS is None else str(magSpecies.gL)
                self.gridAtoms.SetCellValue(count, 2, gL)
                ffkey = 'None' if magSpecies.ffparamkey is None else magSpecies.ffparamkey
                self.gridAtoms.SetCellValue(count, 3, ffkey)
                count += 1


        self.gridAtoms.AutosizeLabels()
        self.gridAtoms.AutoSizeColumns()

        return
