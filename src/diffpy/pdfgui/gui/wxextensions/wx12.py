#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfgui     Complex Modeling Initiative
#                   (c) 2019 Brookhaven Science Associates,
#                   Brookhaven National Laboratory.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""\
Support for WX4-like methods and functions for WX3.

Notes
-----
This module should be removed after ending support for WX3.
Replace instances of its use with plain ``wx``.
"""

import types
import wx

WX3 = (wx.VERSION[0] == 3)
WX4 = (wx.VERSION[0] == 4)

# ----------------------------------------------------------------------------

class Menu(wx.Menu):

    def Append(self, *args, **kwargs):
        na = len(args)
        if isinstance(args[0], wx.MenuItem):
            return super(Menu, self).AppendItem(*args, **kwargs)
        if na > 2 and isinstance(args[2], wx.Menu):
            return super(Menu, self).AppendMenu(*args, **kwargs)
        plain_append = (
            isinstance(args[0], int) and
            (na > 1 and isinstance(args[1], str) or 'item' in kwargs))
        if plain_append:
            return super(Menu, self).Append(*args, **kwargs)
        assert False, "unexpected argument types"

if WX4:
    Menu = wx.Menu

# ----------------------------------------------------------------------------

class ListCtrl(wx.ListCtrl):

    InsertItem = wx.ListCtrl.InsertStringItem
    SetItem = wx.ListCtrl.SetStringItem

if WX4:
    ListCtrl = wx.ListCtrl

# ----------------------------------------------------------------------------

class TreeCtrl(wx.TreeCtrl):

    GetItemData = wx.TreeCtrl.GetPyData
    SetItemData = wx.TreeCtrl.SetPyData

if WX4:
    TreeCtrl = wx.TreeCtrl

# wx.ToolBar -----------------------------------------------------------------

def AddTool(self, *args, **kwargs):
    return super(wx.ToolBar, self).AddLabelTool(*args, **kwargs)


def patchToolBarMethods(toolbar):
    if WX3:
        toolbar.AddTool = types.MethodType(AddTool, toolbar)
    return

# Functions ------------------------------------------------------------------

IsMainThread = wx.Thread_IsMain if WX3 else wx.IsMainThread
NewIdRef = wx.NewIdRef if WX4 else wx.NewId

# Final checks ---------------------------------------------------------------

assert WX3 ^ (Menu is wx.Menu)
assert WX3 ^ (TreeCtrl is wx.TreeCtrl)
assert WX3 ^ (ListCtrl is wx.ListCtrl)
