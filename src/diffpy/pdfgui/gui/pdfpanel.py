#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow, Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

import wx

from diffpy.pdfgui.gui.errorwrapper import catchObjectErrors

class PDFPanel(object):
    """Mix-in class for all PDF gui panels.

    This method is meant to be a secondary parent class for classed derived from
    wx.Panel. It defines methods and member variables necessary to all panels in
    the PDFgui.
    """
    def __init__(self, *args, **kwds):
        self.mainFrame = None
        self.treeCtrlMain = None
        # The configuration parser for reading and writing to the
        # configuration file
        self.cP = None
        # key is used to determine the node type associated with the given panel.
        self.key = ""
        # Wrap all events so that the exceptions get handled.
        catchObjectErrors(self)
        return

    def refresh(self):
        """Refreshes wigets of the panel.

        This method must be overloaded in the derived class or else a
        NotImplementedError will be raised when this method is called.
        """
        raise NotImplementedError('refresh() must be implemented in subclass')

    def setToolTips(self, toolTips):
        '''Sets tooltips for controls

        @param toolTips: dictionary of the form {'controlname' : 'tooltip'}
        '''
        for (controlName, tooltip) in toolTips.items():
            control = getattr(self, controlName)
            if control.GetToolTip() is None:
                control.SetToolTip(wx.ToolTip(''))
            tt = control.GetToolTip()
            tt.SetTip(tooltip)
        return
