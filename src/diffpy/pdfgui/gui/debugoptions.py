#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""DebugOptions class for storing guess three time what

There should be exactly one instance of DebugOptions in pdfguiglobals module.
"""

class DebugOptions:
    """DebugOptions is a place to store various debugging options.
    There should be just one instance defined in pdfguiglobals module.
    It would be nice to have a simple way of setting them on command line

    Options in short and long forms:
        noed, noerrordialog  -- [False], disable exceptions catching and
                                display in ErrorReportDialog
        nocf, noconfirm      -- boolean (default False), exit without asking to
                                save modified project file
        pdb, pythondebugger  -- use python debugger to handle error exceptions
                                instead of ErrorReportDialog
    """
    # global list of all options
    alldebugoptions = (
            ('noed', 'noerrordialog'),
            ('nocf', 'noconfirm'),
            ('pdb', 'pythondebugger'),
    )
    # global dictionary for converting long options to short
    short2long = dict(alldebugoptions)

    def __init__(self):
        """Initialize DebugOptions, by default all of them are off.
        """
        self.noerrordialog = False
        self.noconfirm = False
        self.pythondebugger = False
        return

    def __setattr__(self, name, value):
        """Map short options to their long equivalents.
        """
        if name in DebugOptions.short2long:
            longname = DebugOptions.short2long[name]
        else:
            longname = name
        self.__dict__[longname] = value
        return

    def __getattr__(self, name):
        """Resolve values of short options.
        This is called only when normal lookup fails.

        returns value of short debug option
        """
        if name in DebugOptions.short2long:
            longname = DebugOptions.short2long[name]
            value = getattr(self, longname)
        else:
            raise AttributeError('An instance has no attribute %r' % name)
        return value

# End of class DebugOptions

# End of file
