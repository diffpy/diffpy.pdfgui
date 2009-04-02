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
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)

class ControlFileError(ControlError):
    """PDFGuiControl exception class -- object config is invalid"""
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)
        
class ControlKeyError(ControlError):
    """PDFGuiControl exception class -- requested object can't be found"""
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)
        
class ControlValueError(ControlError):
    """PDFGuiControl exception class -- Invalid value"""
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)    
        
class ControlTypeError(ControlError):
    """PDFGuiControl exception class -- Type mismatch"""
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)    
        
class ControlStatusError(ControlError):
    """PDFGuiControl exception class -- Fitting status doesn't match"""
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)

class ControlRuntimeError(ControlError):
    """PDFGuiControl exception class -- various irrecoverable runtime error"""
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)

class ControlConnectError(ControlError):
    """PDFGuiControl exception class -- network connection error"""
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)
        
class ControlAuthError(ControlError):
    """PDFGuiControl exception class -- authentication failed """
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)
        
class ControlIndexError(ControlError):
    """PDFGuiControl exception class -- index out of bound """
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)

class ControlSyntaxError(ControlError):
    """PDFGuiControl exception class -- invalid syntax of constraint formula
    """
    def __init__(self, info):
        """initialize
        
        info -- description string
        """
        ControlError.__init__(self, info)

# version
__id__ = "$Id$"

# End of file 
