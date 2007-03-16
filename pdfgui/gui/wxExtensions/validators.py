########################################################################
#
# wxExtensions      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################

"""This module contains TextValidator, which is an input validator for the
wxTextCtrl. See the wxPython documentation for wxTextCtrl for more about text
validators. Three constants are defined for use in TextValidator: ALPHA_ONLY,
DIGIT_ONLY, and FLOAT_ONLY. See the TextValidator class for how these are used.
"""

# version
__id__ = "$Id$"

ALPHA_ONLY = 1
DIGIT_ONLY = 2
FLOAT_ONLY = 3
import wx
import string

class TextValidator(wx.PyValidator):
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
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.allowNeg = allowNeg
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return TextValidator(self.flag, self.allowNeg)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        
        if self.flag == ALPHA_ONLY:
            # Check for letters
            for x in val:
                if x not in string.letters:
                    return False

        elif self.flag == DIGIT_ONLY:

            # Check for an initial negative
            if self.allowNeg:
                if val[0] == '-':
                    # Clip the negative for the next check
                    if len(val) > 1:
                        val = val[1:]
                    else:
                        val = ""

            # Check the digits
            for x in val:
                if x not in string.digits:
                    return False

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

        if self.flag == DIGIT_ONLY: 
            if chr(key) in string.digits:
                event.Skip()
                return

            if self.allowNeg and chr(key) == '-':
                # Don't allow a '-' sign any place but at the beginning
                win = self.GetWindow()
                if win.GetInsertionPoint() == 0 and win.GetValue().count('-') == 0:
                    event.Skip()
                    return

        if self.flag == FLOAT_ONLY: 
            win = self.GetWindow()
            val = win.GetValue()
            i = win.GetInsertionPoint()
            newval = val[:i]+chr(key)+val[i:]
            try:
                x = float(newval+"1") # Catches "1e", a float to be
                if x < 0:
                    if self.allowNeg:
                        event.Skip()
                        return
                else:
                    event.Skip()
                    return

            except ValueError:
                pass

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even. Skip eats the event before it
        # gets to the text control
        return

# End of class TextValidator
