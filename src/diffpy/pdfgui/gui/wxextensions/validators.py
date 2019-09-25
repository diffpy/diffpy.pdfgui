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

"""This module contains TextValidator, which is an input validator for the
wxTextCtrl. See the wxPython documentation for wxTextCtrl for more about text
validators. Three constants are defined for use in TextValidator: ALPHA_ONLY,
DIGIT_ONLY, and FLOAT_ONLY. See the TextValidator class for how these are used.
"""

ALPHA_ONLY = 1
DIGIT_ONLY = 2
FLOAT_ONLY = 3

import wx
import string

class TextValidator(wx.Validator):
    """This validator is designed to check text input for wxTextCtrls. (It might
    have uses in other widgets.) It can validate for letters only, digits only,
    floats only, and can allow for a negative at the beginning of a digit string
    or a negative float.
    """

    def __init__(self, flag=DIGIT_ONLY, allowNeg=False):
        """Initialize the validator.

        flag        --  DIGIT_ONLY, allow only digits (default)
                        ALPHA_ONLY, allow only letters
                        FLOAT_ONLY, allow only floats

        allowNeg    --  Allow a negative sign in front of DIGIT_ONLY, or
                        FLOAT_ONLY text. (default False)
        """
        wx.Validator.__init__(self)
        self.flag = flag
        self.allowNeg = allowNeg
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return TextValidator(self.flag, self.allowNeg)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        if self.flag == ALPHA_ONLY:
            return val.isalpha()

        elif self.flag == DIGIT_ONLY:
            if self.allowNeg:
                val1 = val[:1].lstrip('-') + val[1:]
            else:
                val1 = val
            return val1.isdigit()

        elif self.flag == FLOAT_ONLY:
            try:
                x = float(val)
                if x < 0 and not self.allowNeg:
                    return False
            except ValueError:
                return False

        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == ALPHA_ONLY and chr(key) in string.letters:
            event.Skip()
            return

        # resolve the new value here
        win = self.GetWindow()
        val = win.GetValue()
        insertion = win.GetInsertionPoint()
        first, last = win.GetSelection()
        if first != last:
            val = val[:first] + val[last:]
            insertion = first
        newval = val[:insertion] + chr(key) + val[insertion:]

        if self.flag == DIGIT_ONLY:
            newval1 = newval
            if self.allowNeg:
                newval1 = newval[:1].lstrip('-') + newval[1:]
            if newval1.isdigit():
                event.Skip()
                return

        if self.flag == FLOAT_ONLY:
            try:
                x = float(newval+"1") # Catches "1e", a float to be
                if x >= 0 or self.allowNeg:
                    event.Skip()
                    return

            except ValueError:
                pass

        if not wx.Validator.IsSilent():
            wx.Bell()

        # Returning without calling even. Skip eats the event before it
        # gets to the text control
        return

    # These are needed so the validator can work in dialogs.
    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

# End of class TextValidator
