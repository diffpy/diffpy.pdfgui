#!/usr/bin/env python
##############################################################################
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
##############################################################################

"""This module contains a function wrapper and an object wrapper that catch
control errors and shows them in an error report dialog. This is used by
PDFPanel and MainFrame.
"""

import traceback
import sys

import wx

from diffpy.pdfgui.gui import pdfguiglobals
from diffpy.pdfgui.gui.errorreportdialog import ErrorReportDialog
from diffpy.pdfgui.control.controlerrors import ControlError

from diffpy.pdfgui.gui.errorreportdialog_control_fix import ErrorReportDialogControlFix
from diffpy.pdfgui.control.controlerrors import TempControlSelectError

# these methods will not be wrapped in catchFunctionErrors
_EXCLUDED_METHODS = dict.fromkeys(dir(wx.Panel) + dir(wx.Dialog))

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

    # default return value when exception is skipped:
    rvpass = wx.ID_CANCEL

    # otherwise wrap func within exceptions handler
    def _f(*args, **kwargs):

        hasmf = hasattr(obj, "mainFrame") and obj.mainFrame is not None

        try:
            return func(*args, **kwargs)

        #to be deleted. temporarily used for show the select-control error.
        except TempControlSelectError:
            dlg = ErrorReportDialogControlFix(obj.mainFrame)
            dlg.ShowModal()
            dlg.Destroy()

        # Display ControlError error messages in a dialog.
        except ControlError as e:
            if not hasmf:
                raise
            message = str(e)
            obj.mainFrame.showMessage(message, 'Oops!')
            return rvpass

        # Everything else
        except:
            if pdfguiglobals.dbopts.pythondebugger:
                import pdb
                tb = sys.exc_info()[2]
                pdb.post_mortem(tb)
                return rvpass
            if not hasmf:
                raise
            msglines = traceback.format_exception(*sys.exc_info())
            message = "".join(msglines)
            if obj.mainFrame.quitting:
                sys.stderr.write(message)
                sys.stderr.write('\n')
            else:
                dlg = ErrorReportDialog(obj.mainFrame)
                dlg.text_ctrl_log.SetValue(message)
                dlg.ShowModal()
                dlg.Destroy()
            return rvpass

        # we should never get here
        pass

    return _f


def catchObjectErrors(obj, exclude=None):
    """Wrap all functions of an object so that the exceptions are caught.

    obj --  Object containing the function. It is assumed that the object has an
            attribute named 'mainFrame', which is a reference to the MainFrame
            instance, which contains information about how and when to display
            errors.
    exclude  -- An iterable of additional function names to exclude.  These are
            excluded in addtion to names in _EXCLUDED_METHODS defined above.

    All functions starting with '_' are excluded.
    """
    if exclude:
        extra_excludes = dict.fromkeys(exclude)
    else:
        extra_excludes = {}

    funcNames = [item for item in dir(obj) if not item.startswith('_')
            and item not in _EXCLUDED_METHODS and item not in extra_excludes]

    for name in funcNames:
        if hasattr( getattr(obj, name), '__call__'):
            setattr(obj, name, catchFunctionErrors(obj, name))

    return
