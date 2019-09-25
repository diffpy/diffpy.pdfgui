#!/usr/bin/env python
##############################################################################
#
# wxextensions      by DANSE Diffraction group
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

"""This module contains custom wxListCtrl subclasses.
AutoWidthListCtrl  - A wxListCtrl object that automatically adjusts the width of
its columns.
ColumnSortListCtrl - An AutoWidthListCtrl that sorts its entries when the column
header is clicked.
KeyEventsListCtrl  - A ColumnSortListCtrl that selects and item as you type its
name.
"""


import wx
import wx.lib.mixins.listctrl as listmix
from diffpy.pdfgui.gui.wxextensions import wx12


class AutoWidthListCtrl(wx12.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    """wxListCtrl subclass that automatically adjusts its column width."""
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, *args, **kwargs):
        wx12.ListCtrl.__init__(self, parent, ID, pos, size, style, *args, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def clearSelections(self):
        """Clear all selections in the list."""
        for item in range( self.GetItemCount() ):
            self.Select(item, on=0)
        return

    def setSelection(self, itemtext = None):
        """Convenience function for simple selection of a list item by label.

        itemtext    --  The label of the item to select. If itemtext is None
                        (default) then all items will be deselected.
        """
        # Clear all selections
        self.clearSelections()

        # Set the selected item
        item = 0
        if itemtext:
            item = self.FindItem(-1, itemtext)
            self.Select(item)
            self.Focus(item)
        return item
# end AutoWidthListCtrl

class ColumnSortListCtrl(AutoWidthListCtrl, listmix.ColumnSorterMixin):
    """AutoWidthListCtrl subclass that sorts its columns when the column header
    is pressed.

    This ListCtrl requires an itemDataMap member dictionary to be initialized
    before the sorting capabilites can be realized. This dictionary simply references
    the ListCtrl's entries by a unique number. This number must be stored as the
    ItemData (with SetItemData) of the entry.  The member data must be in the
    form of a tuple, where the tuple has a number of entries as the ListCtrl has
    columns. The sorting routine sorts the items in the ListCtrl by the entries
    in this tuple.
    """
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, *args, **kwargs):
        AutoWidthListCtrl.__init__(self, parent, ID, pos, size, style,
                *args, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def GetListCtrl(self):
        """This method is required by the sorter mixin."""
        return self

    def initializeSorter(self):
        """Initialize the column sorter mixin after the ListCtrl is filled.

        This method must be called whenever the itemDataMap is altered.
        """
        numcol = self.GetColumnCount()
        listmix.ColumnSorterMixin.__init__(self, numcol)
        return

    def makeIDM(self):
        """This method automatically sets up the itemDataMap.

        The itemDataMap gets filled with the current ListCtrl entries. The
        itemDataMap does not update automatically when the list is changed. To
        update the itemDataMap this method must be called again.
        initializeSorter should be called after a call to this method.
        """
        numcol = self.GetColumnCount()
        numrow = self.GetItemCount()
        self.itemDataMap = {}
        for i in range(numrow):
            infolist = []
            for j in range(numcol):
                infolist.append( self.GetItem(i,j).GetText() )
            self.itemDataMap[i+1] = tuple(infolist)
            self.SetItemData(i, i+1)
        return

# end ColumnSortListCtrl

class KeyEventsListCtrl(ColumnSortListCtrl):
    """ColumnSortListCtrl that catches key events and selects the item that
    matches.

    It only searches for items in the first column.
    """
    def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=0, *args, **kwargs):
        ColumnSortListCtrl.__init__(self, parent, id, pos, size, style, *args,
                **kwargs)
        self.typedText = ''
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)

    def findPrefix(self, prefix):
        if prefix:
            prefix = prefix.lower()
            length = len(prefix)

            for x in range(self.GetItemCount()):
                text = self.GetItemText(x)
                text = text.lower()

                if text[:length] == prefix:
                    return x

        return -1


    def OnKey(self, evt):
        key = evt.GetKeyCode()

        # Select All - Ctrl+A
        if evt.ControlDown() and key == 65:
            for item in range(self.GetItemCount()):
                self.Select(item)
            return

        # Search for name
        if key >= 32 and key <= 127:
            self.typedText = self.typedText + chr(key)
            item = self.findPrefix(self.typedText)

            if item != -1:
                itemtext = self.GetItemText(item)
                self.setSelection(itemtext)

        elif key == wx.WXK_BACK:
            self.typedText = self.typedText[:-1]

            if not self.typedText:
                itemtext = self.GetItemText(0)
                self.setSelection(itemtext)
            else:
                item = self.findPrefix(self.typedText)

                if item != -1:
                    itemtext = self.GetItemText(item)
                    self.setSelection(itemtext)

        else:
            self.typedText = ''
            evt.Skip()

    def OnKeyDown(self, evt):
        pass

# End of class KeyEventsListCtrl

# verify inheritance of all ListCtrl classes
assert issubclass(AutoWidthListCtrl, wx12.ListCtrl)
assert issubclass(ColumnSortListCtrl, wx12.ListCtrl)
assert issubclass(KeyEventsListCtrl, wx12.ListCtrl)
