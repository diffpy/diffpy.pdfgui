########################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################

# version
__id__ = "$Id$"

"""This module contains a function wrapper and an object wrapper that catch
control errors and shows them in an error report dialog. This is used by
PDFPanel and MainFrame.
"""

import traceback
import sys
import os

import wx

import diffpy.pdfgui.gui.pdfguiglobals as pdfguiglobals
from diffpy.pdfgui.gui.errorreportdialog import ErrorReportDialog
from diffpy.pdfgui.control.controlerrors import ControlError

excluded = list(dir(wx.Panel))
excluded.extend(list(dir(wx.Dialog)))
excluded = dict.fromkeys(excluded).keys()

def catchFunctionErrors(obj, funcName):
    """Wrap a function so its errors get transferred to a dialog.

    obj         --  Object containing the function. It is assumed that the
                    object has an attribute named 'mainFrame', which is a
                    reference to the MainFrame instance, which contains
                    information about how and when to display errors.
    funcName    --  Name of a function to wrap.

    Returns the wrapped function
    """
    func = getattr(obj, funcName)

    # do not catch anything when requested in pdfguigloabals.dbopts
    if pdfguiglobals.dbopts.noerrordialog:  
        return func

    # otherwise wrap func within exceptions handler
    def _f(*args, **kwargs):

        hasmf = hasattr(obj, "mainFrame") and obj.mainFrame is not None

        try:
            return func(*args, **kwargs)
        except ControlError, e:
            message = str(e)
            if hasmf and not obj.mainFrame.quitting:
                obj.mainFrame.showMessage(message, 'Oops!')
            else:
                raise
        except: # Everything else
            msglines = traceback.format_exception(*sys.exc_info())
            message = "".join(msglines)
            if hasmf and not obj.mainFrame.quitting:
                dlg = ErrorReportDialog(obj.mainFrame)
                dlg.text_ctrl_log.SetValue(message)
                dlg.ShowModal()
                dlg.Destroy()        
            else:
                raise
        return wx.ID_CANCEL  # Not sure this is needed

    return _f


def catchObjectErrors(obj, ex = []):
    """Wrap all functions of an object so that the exceptions are caught.

    obj --  Object containing the function. It is assumed that the object has an
            attribute named 'mainFrame', which is a reference to the MainFrame
            instance, which contains information about how and when to display
            errors.
    ex  --  A list of function names to exclude. These are excluded in addition
            to the 'excluded' list defined in the method.
    
    All functions starting with '_' are excluded.
    """
    ex.extend(excluded)

    funcNames = [item for item in dir(obj) if not item.startswith('_') 
            and item not in ex]

    for name in funcNames:
        if hasattr( getattr(obj, name), '__call__'):
            setattr(obj, name, catchFunctionErrors(obj, name))

    return

