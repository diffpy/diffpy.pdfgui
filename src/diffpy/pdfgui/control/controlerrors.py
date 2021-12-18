#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Jiwu Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

class ControlError(Exception):
    """Basic PDFGuiControl exception class"""
    def __init__(self, info):
        """initialize

        info -- description string
        """
        Exception.__init__(self)
        self.info = info

    def __str__(self):
        return self.info


class ControlConfigError(ControlError):
    """PDFGuiControl exception class -- object config is invalid"""
    pass


class ControlFileError(ControlError):
    """PDFGuiControl exception class -- object config is invalid"""
    pass


class ControlKeyError(ControlError):
    """PDFGuiControl exception class -- requested object can't be found"""
    pass


class ControlValueError(ControlError):
    """PDFGuiControl exception class -- Invalid value"""
    pass


class ControlTypeError(ControlError):
    """PDFGuiControl exception class -- Type mismatch"""
    pass


class ControlStatusError(ControlError):
    """PDFGuiControl exception class -- Fitting status doesn't match"""
    pass


class ControlRuntimeError(ControlError):
    """PDFGuiControl exception class -- various irrecoverable runtime error"""
    pass


class ControlIndexError(ControlError):
    """PDFGuiControl exception class -- index out of bound """
    pass


class ControlSyntaxError(ControlError):
    """PDFGuiControl exception class -- invalid syntax of constraint formula
    """
    pass

class TempControlSelectError(ControlError):
    """Temporary define this error to identify the select-control error in python3
    """
    pass

# End of file
