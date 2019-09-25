#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##############################################################################
#
# wxextensions      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2009 trustees of Columbia University in the City of
#                   New York.
#                   All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""This module contains utilities that can be used with wxTextCtrls."""


import wx

def textCtrlAsGridCell(panel, event):
    """Process a textCtrl key event as if the textCtrl was a grid cell.

    This catches ESC and ENTER events in textCtrls and processes them as if the
    textCtrl were a grid cell. This method can be bound to the wx.EVT_KEY_DOWN
    event of any textCtrl. See phaseconfigurepanel.py in diffpy.pdfgui.gui for
    an example.

    ESC     --  Cancel the edit and highlight the text. This requires that
                panel has a _focusedText attribute that stores the previous
                value.
    ENTER   --  Confirm the edit and move to the next cell (the default TAB
                behavior).
    """
    key = event.GetKeyCode()

    textctrl = event.GetEventObject()

    # ESC - cancel the edit
    if key == 27:
        # Restore the original value
        textctrl.ChangeValue(panel._focusedText)
        # Now reselect the text
        wx.CallAfter(textctrl.SetSelection, -1, -1)
    # ENTER - Act like TAB
    elif key == 13:
        wx.CallAfter(textctrl.Navigate)
    else:
        event.Skip()
    return
