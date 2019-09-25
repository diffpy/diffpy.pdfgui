#!/usr/bin/env python
##############################################################################
#
# wxextensions      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""This module contains AutoWidthListCtrl, a wxListCtrl object that
automatically adjusts the width of its columns.
"""


import wx
import wx.grid

class AutoWidthLabelsGrid(wx.grid.Grid):
    '''wx grid which allows lables auto sizing'''
#    def __init__(self, parent, state, size):
#        wx.grid.Grid.__init__(self, parent, state, size)

    def AutosizeLabels(self,rows=True,cols=False):
        # Common setup.
        devContext = wx.ScreenDC()
        devContext.SetFont(self.GetLabelFont())

        # First do row labels.
        if rows:
            maxWidth = 0
            curRow = self.GetNumberRows() - 1
            while curRow >= 0:
                curWidth = devContext.GetTextExtent("M%s"%(self.GetRowLabelValue(curRow)))[0]
                if curWidth > maxWidth:
                    maxWidth = curWidth
                curRow = curRow - 1
            self.SetRowLabelSize(maxWidth)

        # Then column labels.
        if cols:
            maxHeight = 0
            curCol = self.GetNumberCols() - 1
            while curCol >= 0:
                (w,h,d,l) = devContext.GetFullTextExtent(self.GetColLabelValue(curCol))
                curHeight = h + d + l + 4
                if curHeight > maxHeight:
                    maxHeight = curHeight
                curCol = curCol - 1
            self.SetColLabelSize(maxHeight)
        return

# End of class AutoWidthLabelsGrid
