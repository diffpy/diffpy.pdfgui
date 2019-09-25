#!/usr/bin/env python
##############################################################################
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
##############################################################################

import random
import wx
import wx.lib.agw.hyperlink
from diffpy.pdfgui.gui.pdfguiglobals import iconpath
from diffpy.pdfgui.version import __version__, __date__


_acknowledgement =  '''\
This software was developed by the Billinge-group as part of the Distributed
Data Analysis of Neutron Scattering Experiments (DANSE) project funded by the US
National Science Foundation under grant DMR-0520547.  Developments of PDFfit2
were funded by NSF grant DMR-0304391 in the Billinge-group, and with support
from Michigan State University and Columbia University.  Any opinions, findings,
and conclusions or recommendations expressed in this material are those of the
author(s) and do not necessarily reflect the views of the respective funding
bodies.

If you use this program to do productive scientific research that leads to
publication, we ask that you acknowledge use of the program by citing the
following paper in your publication:

    C. L. Farrow, P. Juhas, J. W. Liu, D. Bryndin, E. S. Bozin,
    J. Bloch, Th. Proffen and S. J. L. Billinge, PDFfit2 and PDFgui:
    computer programs for studying nanostructure in crystals,
    J. Phys.: Condens. Matter 19, 335219 (2007).'''

_copyright = "(c) 2005-{year},".format(year= __date__[:4])

_homepage = "https://www.diffpy.org"

# authors list is shuffled randomly every time
_authors = ["S. J. L. Billinge", "E. S. Bozin", "D. Bryndin",
                "C. L. Farrow", "P. Juhas", "J. W. Liu"]
_paper = "https://stacks.iop.org/0953-8984/19/335219"
_license = ""


def launchBrowser(url):
    '''Launches browser and opens specified url

    In some cases may require BROWSER environment variable to be set up.

    @param url: URL to open
    '''
    import webbrowser
    webbrowser.open(url)


class DialogAbout(wx.Dialog):
    '''"About" Dialog

    Shows product name, current version, authors, and link to the product page.
    Current version is taken from version.py
    '''

    def __init__(self, *args, **kwds):

        # begin wxGlade: DialogAbout.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((600, 595))
        self.bitmap_logo = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(iconpath("logo.png")))
        self.label_title = wx.StaticText(self, wx.ID_ANY, "PDFgui")
        self.label_version = wx.StaticText(self, wx.ID_ANY, "")
        self.label_build = wx.StaticText(self, wx.ID_ANY, "Build:")
        self.label_svnrevision = wx.StaticText(self, wx.ID_ANY, "")
        self.label_copyright = wx.StaticText(self, wx.ID_ANY, "")
        self.label_author = wx.StaticText(self, wx.ID_ANY, "author")
        self.hyperlink = wx.lib.agw.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, _homepage, URL=_homepage)
        self.hyperlink_license = wx.lib.agw.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, _license, URL=_license)
        self.static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.label_acknowledgement = wx.StaticText(self, wx.ID_ANY, "")
        self.hyperlink_paper = wx.lib.agw.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, _paper, URL=_paper)
        self.static_line_2 = wx.StaticLine(self, wx.ID_ANY)
        self.bitmap_button_nsf = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, style=wx.BU_AUTODRAW)
        self.bitmap_button_danse = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, style=wx.BU_AUTODRAW)
        self.bitmap_button_msu = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, style=wx.BU_AUTODRAW)
        self.bitmap_button_columbia = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, style=wx.BU_AUTODRAW)
        self.static_line_3 = wx.StaticLine(self, wx.ID_ANY)
        self.button_OK = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onNsfLogo, self.bitmap_button_nsf)
        self.Bind(wx.EVT_BUTTON, self.onDanseLogo, self.bitmap_button_danse)
        self.Bind(wx.EVT_BUTTON, self.onMsuLogo, self.bitmap_button_msu)
        self.Bind(wx.EVT_BUTTON, self.onColumbiaLogo, self.bitmap_button_columbia)
        # end wxGlade

        # randomly shuffle authors' names
        random.shuffle(_authors)
        strLabel = ", ".join(_authors)
        self.label_author.SetLabel(strLabel)
        # setup acknowledgement and copyright text labels
        self.label_acknowledgement.SetLabel(_acknowledgement)
        self.label_copyright.SetLabel(_copyright)
        # display version and svn revison numbers
        verwords = __version__.split('.post', 1)
        version = verwords[0]
        revision = '0' if len(verwords) == 1 else verwords[1]
        self.label_version.SetLabel(version)
        self.label_svnrevision.SetLabel(revision)

        # set bitmaps for logo buttons
        logo = wx.Bitmap(iconpath("nsf_logo.png"))
        self.bitmap_button_nsf.SetBitmapLabel(logo)
        logo = wx.Bitmap(iconpath("danse_logo.png"))
        self.bitmap_button_danse.SetBitmapLabel(logo)
        logo = wx.Bitmap(iconpath("msu_logo.png"))
        self.bitmap_button_msu.SetBitmapLabel(logo)
        logo = wx.Bitmap(iconpath("columbia_logo.png"))
        self.bitmap_button_columbia.SetBitmapLabel(logo)

        # resize dialog window to fit version number nicely
        self.Fit()
        return


    def __set_properties(self):
        # begin wxGlade: DialogAbout.__set_properties
        self.SetTitle("About")
        self.SetSize((600, 595))
        self.label_title.SetFont(wx.Font(26, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.label_version.SetFont(wx.Font(26, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.hyperlink_license.Enable(False)
        self.hyperlink_license.Hide()
        self.bitmap_button_nsf.SetSize(self.bitmap_button_nsf.GetBestSize())
        self.bitmap_button_danse.SetSize(self.bitmap_button_danse.GetBestSize())
        self.bitmap_button_msu.SetSize(self.bitmap_button_msu.GetBestSize())
        self.bitmap_button_columbia.SetSize(self.bitmap_button_columbia.GetBestSize())
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
        sizer_title.Add(self.label_title, 0, wx.EXPAND | wx.LEFT | wx.TOP, 10)
        sizer_title.Add((20, 20), 0, wx.EXPAND, 0)
        sizer_title.Add(self.label_version, 0, wx.ALIGN_BOTTOM | wx.RIGHT, 10)
        sizer_titles.Add(sizer_title, 0, wx.EXPAND, 0)
        sizer_build.Add(self.label_build, 0, wx.LEFT | wx.RIGHT, 10)
        sizer_build.Add(self.label_svnrevision, 0, 0, 0)
        sizer_titles.Add(sizer_build, 0, wx.EXPAND | wx.TOP, 5)
        sizer_titles.Add(self.label_copyright, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer_titles.Add(self.label_author, 0, wx.LEFT | wx.RIGHT, 10)
        sizer_titles.Add(self.hyperlink, 0, wx.LEFT | wx.RIGHT, 10)
        sizer_titles.Add((20, 20), 0, 0, 0)
        sizer_titles.Add(self.hyperlink_license, 0, wx.LEFT | wx.RIGHT, 10)
        sizer_header.Add(sizer_titles, 0, wx.EXPAND, 0)
        sizer_main.Add(sizer_header, 0, wx.BOTTOM | wx.EXPAND, 3)
        sizer_main.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_main.Add(self.label_acknowledgement, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 7)
        sizer_main.Add(self.hyperlink_paper, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 7)
        sizer_main.Add(self.static_line_2, 0, wx.EXPAND, 0)
        sizer_logos.Add(self.bitmap_button_nsf, 0, wx.LEFT, 2)
        sizer_logos.Add(self.bitmap_button_danse, 0, wx.LEFT, 2)
        sizer_logos.Add(self.bitmap_button_msu, 0, wx.LEFT, 2)
        sizer_logos.Add(self.bitmap_button_columbia, 0, wx.LEFT, 2)
        sizer_logos.Add((50, 50), 0, 0, 0)
        sizer_main.Add(sizer_logos, 0, wx.EXPAND, 0)
        sizer_main.Add(self.static_line_3, 0, wx.EXPAND, 0)
        sizer_button.Add((20, 20), 1, wx.EXPAND, 0)
        sizer_button.Add(self.button_OK, 0, wx.RIGHT, 10)
        sizer_main.Add(sizer_button, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_main)
        self.Layout()
        self.Centre()
        # end wxGlade

    def onNsfLogo(self, event): # wxGlade: DialogAbout.<event_handler>
        launchBrowser("https://www.nsf.gov")
        event.Skip()

    def onDanseLogo(self, event): # wxGlade: DialogAbout.<event_handler>
        launchBrowser("http://danse.us")
        event.Skip()

    def onMsuLogo(self, event): # wxGlade: DialogAbout.<event_handler>
        launchBrowser("https://www.msu.edu")
        event.Skip()

    def onColumbiaLogo(self, event): # wxGlade: DialogAbout.<event_handler>
        launchBrowser("https://www.columbia.edu")
        event.Skip()

# end of class DialogAbout

##### testing code ###########################################################

if __name__ == "__main__":
    app = wx.App()
    dialog = DialogAbout(None, -1, "")
    dialog.ShowModal()
