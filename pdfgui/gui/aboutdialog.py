#!/usr/bin/env python
########################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################

# version
__id__ = "$Id$"
__revision__ = "$Revision$"

__acknowledgement__ = """
This software was developed by the Billinge-group as part of the
Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
project funded by the US National Science Foundation under grant
DMR-0520547.  Developments of PDFfit2 were funded by NSF grant
DMR-0304391 in the Billinge-group, and with support from Michigan State
University.  Any opinions, findings, and conclusions or recommendations
expressed in this material are those of the author(s) and do not
necessarily reflect the views of the respective funding bodies.
""".strip().replace('\n', ' ')

import wx
import wx.lib.hyperlink
import random
import os.path
from pdfguiglobals import iconsDir

from diffpy.pdfgui.version import __version__

class DialogAbout(wx.Dialog):
    '''"About" Dialog
    
    Shows product name, current version, authors, and link to the product page.
    Current version is taken from version.py
    
    self.authors  - is a list of all authors, which is shuffled randomly
    self.homepage - link to the project web page
    '''
    
    def __init__(self, *args, **kwds):

        self.authors = ["Simon Billinge", "Emil Bozin", "Dmitriy Bryndin",
                "Chris Farrow", "Pavol Juhas", "Jiwu Liu"]
        self.homepage = "http://danse.us/trac/diffraction"
        
        # begin wxGlade: DialogAbout.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.bitmap_logo = wx.StaticBitmap(self, -1, wx.Bitmap(os.path.join(iconsDir,"logo.png")))
        self.label_title = wx.StaticText(self, -1, "PDFgui")
        self.label_version = wx.StaticText(self, -1, "")
        self.label_build = wx.StaticText(self, -1, "Build:")
        self.label_svnrevision = wx.StaticText(self, -1, "")
        self.label_copyright = wx.StaticText(self, -1, "(c) 2005-2006,")
        self.label_author = wx.StaticText(self, -1, "author")
        self.hyperlink = wx.lib.hyperlink.HyperLinkCtrl(self, -1, self.homepage, URL=self.homepage)
        self.static_line_1 = wx.StaticLine(self, -1)
        self.text_ctrl_acknowledgement = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER)
        self.static_line_2 = wx.StaticLine(self, -1)
        self.bitmap_button_nsf = wx.BitmapButton(self, -1, wx.NullBitmap)
        self.bitmap_button_danse = wx.BitmapButton(self, -1, wx.NullBitmap)
        self.bitmap_button_msu = wx.BitmapButton(self, -1, wx.NullBitmap)
        self.static_line_3 = wx.StaticLine(self, -1)
        self.button_OK = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onNsfLogo, self.bitmap_button_nsf)
        self.Bind(wx.EVT_BUTTON, self.onDanseLogo, self.bitmap_button_danse)
        self.Bind(wx.EVT_BUTTON, self.onMsuLogo, self.bitmap_button_msu)
        # end wxGlade
        
        # fill in acknowledgements
        self.text_ctrl_acknowledgement.SetValue(__acknowledgement__)

        # randomly shuffle authors' names
        random.shuffle(self.authors)
        strLabel = ", ".join(self.authors)
        
        # display version and svn revison numbers
        verwords = __version__.split('.')
        version = '.'.join(verwords[:-1])
        revision = verwords[-1]
        
        self.label_author.SetLabel(strLabel)
        self.label_version.SetLabel(version)
        self.label_svnrevision.SetLabel(revision)
        
        # set bitmaps for logo buttons
        logo = wx.Bitmap(os.path.join(iconsDir,"nsf_logo.png"))
        self.bitmap_button_nsf.SetBitmapLabel(logo)
        logo = wx.Bitmap(os.path.join(iconsDir,"danse_logo.png"))
        self.bitmap_button_danse.SetBitmapLabel(logo)
        logo = wx.Bitmap(os.path.join(iconsDir,"msu_logo.png"))
        self.bitmap_button_msu.SetBitmapLabel(logo)
        
        # resize dialog window to fit version number nicely
        size = [self.GetEffectiveMinSize()[0], self.GetSize()[1]]
        self.SetSize(size)
        

    def __set_properties(self):
        # begin wxGlade: DialogAbout.__set_properties
        self.SetTitle("About")
        self.SetSize((600, 370))
        self.label_title.SetFont(wx.Font(26, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_version.SetFont(wx.Font(26, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.text_ctrl_acknowledgement.Enable(False)
        self.bitmap_button_nsf.SetSize(self.bitmap_button_nsf.GetBestSize())
        self.bitmap_button_danse.SetSize(self.bitmap_button_danse.GetBestSize())
        self.bitmap_button_msu.SetSize(self.bitmap_button_msu.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: DialogAbout.__do_layout
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        sizer_logos = wx.BoxSizer(wx.HORIZONTAL)
        sizer_header = wx.BoxSizer(wx.HORIZONTAL)
        sizer_titles = wx.BoxSizer(wx.VERTICAL)
        sizer_build = wx.BoxSizer(wx.HORIZONTAL)
        sizer_title = wx.BoxSizer(wx.HORIZONTAL)
        sizer_header.Add(self.bitmap_logo, 0, wx.EXPAND, 0)
        sizer_title.Add(self.label_title, 0, wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 20)
        sizer_title.Add((20, 20), 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_title.Add(self.label_version, 0, wx.RIGHT|wx.ALIGN_BOTTOM|wx.ADJUST_MINSIZE, 10)
        sizer_titles.Add(sizer_title, 0, wx.EXPAND, 0)
        sizer_build.Add(self.label_build, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_build.Add(self.label_svnrevision, 0, wx.ADJUST_MINSIZE, 0)
        sizer_titles.Add(sizer_build, 0, wx.TOP|wx.EXPAND, 5)
        sizer_titles.Add(self.label_copyright, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ADJUST_MINSIZE, 10)
        sizer_titles.Add(self.label_author, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_titles.Add(self.hyperlink, 0, wx.LEFT|wx.RIGHT, 10)
        sizer_header.Add(sizer_titles, 0, wx.EXPAND, 0)
        sizer_main.Add(sizer_header, 0, wx.BOTTOM|wx.EXPAND, 3)
        sizer_main.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_main.Add(self.text_ctrl_acknowledgement, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_main.Add(self.static_line_2, 0, wx.EXPAND, 0)
        sizer_logos.Add(self.bitmap_button_nsf, 0, wx.LEFT|wx.ADJUST_MINSIZE, 2)
        sizer_logos.Add(self.bitmap_button_danse, 0, wx.LEFT|wx.ADJUST_MINSIZE, 2)
        sizer_logos.Add(self.bitmap_button_msu, 0, wx.LEFT|wx.ADJUST_MINSIZE, 2)
        sizer_logos.Add((50, 50), 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_logos, 0, wx.EXPAND, 0)
        sizer_main.Add(self.static_line_3, 0, wx.EXPAND, 0)
        sizer_button.Add((20, 20), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_button.Add(self.button_OK, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_main.Add(sizer_button, 0, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_main)
        self.Layout()
        self.Centre()
        # end wxGlade

    def _launchBrowser(self, url):
        import webbrowser
        webbrowser.open(url)

    def onNsfLogo(self, event): # wxGlade: DialogAbout.<event_handler>
        self._launchBrowser("http://www.nsf.gov")
        event.Skip()

    def onDanseLogo(self, event): # wxGlade: DialogAbout.<event_handler>
        self._launchBrowser("http://wiki.cacr.caltech.edu/danse")
        event.Skip()

    def onMsuLogo(self, event): # wxGlade: DialogAbout.<event_handler>
        self._launchBrowser("http://www.msu.edu")
        event.Skip()

# end of class DialogAbout

##### testing code ############################################################
class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        dialog = DialogAbout(None, -1, "")
        self.SetTopWindow(dialog)
        dialog.ShowModal()
        dialog.Destroy()
        return 1

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
    
##### end of testing code #####################################################    
