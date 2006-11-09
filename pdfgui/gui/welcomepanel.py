#!/usr/bin/env python
########################################################################
#
# PDFgui            by DANSE Diffraction group
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


import wx
import wx.lib.fancytext as fancytext
from pdfpanel import PDFPanel
from string import center

class WelcomePanel(wx.Panel, PDFPanel):
    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        # FIXME - there has to be a better way to do this.
        line1 = '<font family="swiss" color="dark green" size="48" weight="bold">'
        line2 = 'PDFgui\n'
        line3 = '</font>'
        line4 = '<font family="swiss" color="black" size="10">\n'
        line5 = \
"""
C. L. Farrow, P. Juhas, J. W. Liu, D. Bryndin, J. Bloch,
Th. Proffen and S. J. L. Billinge
PDFfit2 and PDFgui: Computer programs for studying 
nanostructures in crystals
Journal of Physics: Condensed Matter, in press
"""
        line6 = '</font>'
        
        # format the title text
        line2 = center(line2, 16)
        line5 = center(line5, 80)
        line5sp = line5.split('\n')
        line5 = '\n'.join( map(center, line5sp, [80]*len(line5sp)))
        line1 += line2 + line3 + line4 + line5 + line6

        self.labelWelcome = fancytext.StaticFancyText(self, -1, line1, style=wx.ALIGN_CENTRE)
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetSize((400, 300))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.labelWelcome, 1, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)

    # Methods overloaded from PDFPanel
    def refresh(self):
        return

# end of class WelcomePanel

__id__ = "$Id$"
