# --------------------------------------------------------------------------- #
# PYAUI Library wxPython IMPLEMENTATION
#
# Original C++ Code From Kirix (wxAUI). You Can Find It At:
#
#    License: wxWidgets license
#
# http://www.kirix.com/en/community/opensource/wxaui/about_wxaui.html
#
# Current wxAUI Version Tracked: 0.9.2
#
#
# Python Code By:
#
# Andrea Gavana, @ 23 Dec 2005
# Latest Revision: 30 Jun 2006, 21.00 GMT
#
#
# PyAUI version 0.9.2 Adds:
#
# * Fixes For Display Glitches;
# * Fixes For Other Bugs Found In Previous Versions.
#
#
# TODO List/Caveats
#
# 1. Using The New Versions Of wxPython (2.6.2.1pre.20060106 Or Higher) There
#    Is A New Method Called wx.GetMouseState() That Gets Rid Of The Import Of
#    win32all or ctypes. Moreover, It Should Make PyAUI Working On All
#    Platforms (I Hope).
#
#
# Latest Patches:
#
# 1) Reduced Flicker While Drawing The Dock Hint
# 2) Made Impossoible To Drag The Sash Separator Outside The Main Frame
# 3) Improved Repaint When Using The Active Pane Option
# 4) Fixed The Mac Problem (Thanks To David Pratt) And Applied The wxGTK Patches
#    Suggested By Robin Dunn To Correctly Draw The Dock Hint
#
# For All Kind Of Problems, Requests Of Enhancements And Bug Reports, Please
# Write To Me At:
#
# andrea.gavana@agip.it
# andrea_gavan@tin.it
#
# Or, Obviously, To The wxPython Mailing List!!!
#
# with OS X support and refactoring implemented by Chris Mellon (arkanes@gmail.com) - 
#    contact me directly or on wxPython ML for more info
#
#
# End Of Comments
# --------------------------------------------------------------------------- #

"""
PyAUI is an Advanced User Interface library that aims to implement "cutting-edge"
interface usability and design features so developers can quickly and easily create
beautiful and usable application interfaces.

Vision and Design Principles

PyAUI attempts to encapsulate the following aspects of the user interface:

* Frame Management: Frame management provides the means to open, move and hide common
controls that are needed to interact with the document, and allow these configurations
to be saved into different perspectives and loaded at a later time. 

* Toolbars: Toolbars are a specialized subset of the frame management system and should
behave similarly to other docked components. However, they also require additional
functionality, such as "spring-loaded" rebar support, "chevron" buttons and end-user
customizability. 

* Modeless Controls: Modeless controls expose a tool palette or set of options that
float above the application content while allowing it to be accessed. Usually accessed
by the toolbar, these controls disappear when an option is selected, but may also be
"torn off" the toolbar into a floating frame of their own. 

* Look and Feel: Look and feel encompasses the way controls are drawn, both when shown
statically as well as when they are being moved. This aspect of user interface design
incorporates "special effects" such as transparent window dragging as well as frame animation. 

PyAUI adheres to the following principles:

- Use native floating frames to obtain a native look and feel for all platforms;
- Use existing wxPython code where possible, such as sizer implementation for frame management; 
- Use standard wxPython coding conventions.


Usage:

The following example shows a simple implementation that utilizes FrameManager to manage
three text controls in a frame window:

class MyFrame(wx.Frame):

    def __init__(self, parent, id=-1, title="PyAUI Test", pos=wx.DefaultPosition,
                 size=(800, 600), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = PyAUI.FrameManager()
        
        # notify PyAUI which frame to use
        self._mgr.SetFrame(self)

        # create several text controls
        text1 = wx.TextCtrl(self, -1, "Pane 1 - sample text",
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
                                           
        text2 = wx.TextCtrl(self, -1, "Pane 2 - sample text",
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
                                           
        text3 = wx.TextCtrl(self, -1, "Main content window",
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
        
        # add the panes to the manager
        self._mgr.AddPane(text1, wx.LEFT, "Pane Number One")
        self._mgr.AddPane(text2, wx.BOTTOM, "Pane Number Two")
        self._mgr.AddPane(text3, wx.CENTER)
                              
        # tell the manager to "commit" all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def OnClose(self, event):

        # deinitialize the frame manager
        self._mgr.UnInit()

        self.Destroy()        
        event.Skip()        


# our normal wxApp-derived class, as usual

app = wx.PySimpleApp()

frame = MyFrame(None)
app.SetTopWindow(frame)
frame.Show()

app.MainLoop()

What's New:

PyAUI version 0.9.2 Adds:

* Fixes For Display Glitches;
* Fixes For Other Bugs Found In Previous Versions.


License And Version:

PyAUI Library Is Freeware And Distributed Under The wxPython License. 

Latest Revision: Andrea Gavana @ 30 Jun 2006, 21.00 GMT
Version 0.9.2. 

"""

import wx
import cStringIO, zlib
import time

_libimported = None
_newversion = False

# Check For The New wxVersion: It Should Be > 2.6.2.1pre.20060102
# In Order To Let PyAUI Working On All Platforms

wxver = wx.VERSION_STRING

if hasattr(wx, "GetMouseState"):
    _newversion = True
    if wx.Platform == "__WXMSW__":
        try:
            import win32api
            import win32con
            import winxpgui
            _libimported = "MH"
        except:
            try:
                import ctypes
                _libimported = "ctypes"
            except:
                pass

else:
    if wx.Platform == "__WXMSW__":
        try:
            import win32api
            import win32con
            import winxpgui
            _libimported = "MH"
        except:
            try:
                import ctypes
                _libimported = "ctypes"
            except:
                raise "\nERROR: At Present, On Windows Machines, You Need To Install "\
                      "Mark Hammond's pywin32 Extensions Or The ctypes Module, Or Download" \
                      "The Latest wxPython Version."

    else:
        raise "\nSorry: I Still Don't Know How To Work On GTK/MAC Platforms... " \
              "Please Download The Latest wxPython Version."


if wx.Platform == "__WXMAC__":
    try:
        import ctypes
        _carbon_dll = ctypes.cdll.LoadLibrary(r'/System/Frameworks/Carbon.framework/Carbon')
    except:
        _carbon_dll = None

# Docking Styles
AUI_DOCK_NONE = 0
AUI_DOCK_TOP = 1
AUI_DOCK_RIGHT = 2
AUI_DOCK_BOTTOM = 3
AUI_DOCK_LEFT = 4
AUI_DOCK_CENTER = 5
AUI_DOCK_CENTRE = AUI_DOCK_CENTER

# Floating/Dragging Styles
AUI_MGR_ALLOW_FLOATING        = 1
AUI_MGR_ALLOW_ACTIVE_PANE     = 2
AUI_MGR_TRANSPARENT_DRAG      = 4
AUI_MGR_TRANSPARENT_HINT      = 8
AUI_MGR_TRANSPARENT_HINT_FADE = 16
    
AUI_MGR_DEFAULT = AUI_MGR_ALLOW_FLOATING | \
                  AUI_MGR_TRANSPARENT_HINT | \
                  AUI_MGR_TRANSPARENT_HINT_FADE | \
                  AUI_MGR_TRANSPARENT_DRAG

# Panes Customization
AUI_ART_SASH_SIZE = 0
AUI_ART_CAPTION_SIZE = 1
AUI_ART_GRIPPER_SIZE = 2
AUI_ART_PANE_BORDER_SIZE = 3
AUI_ART_PANE_BUTTON_SIZE = 4
AUI_ART_BACKGROUND_COLOUR = 5
AUI_ART_SASH_COLOUR = 6
AUI_ART_ACTIVE_CAPTION_COLOUR = 7
AUI_ART_ACTIVE_CAPTION_GRADIENT_COLOUR = 8
AUI_ART_INACTIVE_CAPTION_COLOUR = 9
AUI_ART_INACTIVE_CAPTION_GRADIENT_COLOUR = 10
AUI_ART_ACTIVE_CAPTION_TEXT_COLOUR = 11
AUI_ART_INACTIVE_CAPTION_TEXT_COLOUR = 12
AUI_ART_BORDER_COLOUR = 13
AUI_ART_GRIPPER_COLOUR = 14
AUI_ART_CAPTION_FONT = 15
AUI_ART_GRADIENT_TYPE = 16

# Caption Gradient Type
AUI_GRADIENT_NONE = 0
AUI_GRADIENT_VERTICAL = 1
AUI_GRADIENT_HORIZONTAL = 2

# Pane Button State    
AUI_BUTTON_STATE_NORMAL = 0
AUI_BUTTON_STATE_HOVER = 1
AUI_BUTTON_STATE_PRESSED = 2

# Pane Insert Level
AUI_INSERT_PANE = 0
AUI_INSERT_ROW = 1
AUI_INSERT_DOCK = 2

# some built in bitmaps
close_bits = '\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00' \
             '\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00' \
             '\xef\x00\x00\x00\xfb\x00\x00\x00\xcf\x00\x00\x00\xf9\x00\x00\x00' \
             '\x9f\x00\x00\x00\xfc\x00\x00\x00?\x00\x00\x00\xfe\x00\x00\x00?\x00' \
             '\x00\x00\xfe\x00\x00\x00\x9f\x00\x00\x00\xfc\x00\x00\x00\xcf\x00' \
             '\x00\x00\xf9\x00\x00\x00\xef\x00\x00\x00\xfb\x00\x00\x00\xff\x00' \
             '\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00' \
             '\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00'

pin_bits = '\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff' \
           '\x00\x00\x00\xff\x00\x00\x00\x1f\x00\x00\x00\xfc\x00\x00\x00\xdf\x00' \
           '\x00\x00\xfc\x00\x00\x00\xdf\x00\x00\x00\xfc\x00\x00\x00\xdf\x00\x00' \
           '\x00\xfc\x00\x00\x00\xdf\x00\x00\x00\xfc\x00\x00\x00\xdf\x00\x00\x00' \
           '\xfc\x00\x00\x00\x0f\x00\x00\x00\xf8\x00\x00\x00\x7f\x00\x00\x00\xff' \
           '\x00\x00\x00\x7f\x00\x00\x00\xff\x00\x00\x00\x7f\x00\x00\x00\xff\x00' \
           '\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00' \
           '\x00\xff\x00\x00\x00\xff\x00\x00\x00'

# PyAUI Event
wxEVT_AUI_PANEBUTTON = wx.NewEventType()
EVT_AUI_PANEBUTTON = wx.PyEventBinder(wxEVT_AUI_PANEBUTTON, 0)


def GetCloseData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4Gy\xba8\x86X\xf4\
\x9e\r:\xcd\xc7\xa0\xc0\xe1\xf5\xfb\xbf\xff\xbb\xc2\xacb6\xdbg\xaez\xb9|\x1c\
\x9a\x82kU\x99xW\x16K\xf5\xdccS\xdad\xe9\xf3\xe0\xa4\x0f\x0f\xaf\xcb\xea\x88\
\x8bV\xd7k\x1eoN\xdf\xb2\xdd\xc8\xd0\xe7Cw2{\xdd\\uf\xfd}3\x0f\xb0\xd4=\x0ff\
\xdfr$\\\xe5\xcf\xa9\xfd3\xfa\xcdu\xa4\x7fk\xa6\x89\x03ma\xf0t\xf5sY\xe7\x94\
\xd0\x04\x00\x1714z')


def GetCloseBitmap():
    return wx.BitmapFromImage(GetCloseImage())


def GetCloseImage():
    stream = cStringIO.StringIO(GetCloseData())
    return wx.ImageFromStream(stream)


def StepColour(c, percent):
    """
    StepColour() it a utility function that simply darkens
    a color by the specified percentage.
    """

    r = c.Red()
    g = c.Green()
    b = c.Blue()
    
    return wx.Colour(min((r*percent)/100, 255),
                     min((g*percent)/100, 255),
                     min((b*percent)/100, 255))


def LightContrastColour(c):

    amount = 120

    # if the color is especially dark, then
    # make the contrast even lighter
    if c.Red() < 128 and c.Green() < 128 and c.Blue() < 128:
        amount = 160

    return StepColour(c, amount)


def BitmapFromBits(color, type=0):
    """
    BitmapFromBits() is a utility function that creates a
    masked bitmap from raw bits (XBM format).
    """
    
    if type == 0:   # Close Bitmap
        img = GetCloseImage()
    else:
        # this should be GetClosePin()... but what the hell is a "pin"?
        img = GetCloseImage()
        
    img.Replace(255, 255, 255, 123, 123, 123)
    img.Replace(0, 0, 0, color.Red(), color.Green(), color.Blue())
    
    return img.ConvertToBitmap()


def DrawGradientRectangle(dc, rect, start_color, end_color, direction):

    rd = end_color.Red() - start_color.Red()
    gd = end_color.Green() - start_color.Green()
    bd = end_color.Blue() - start_color.Blue()

    if direction == AUI_GRADIENT_VERTICAL:
        high = rect.GetHeight() - 1
    else:
        high = rect.GetWidth() - 1

    for ii in xrange(high+1):
        r = start_color.Red() + ((ii*rd*100)/high)/100
        g = start_color.Green() + ((ii*gd*100)/high)/100
        b = start_color.Blue() + ((ii*bd*100)/high)/100

        p = wx.Pen(wx.Colour(r, g, b))
        dc.SetPen(p)

        if direction == AUI_GRADIENT_VERTICAL:
            dc.DrawLine(rect.x, rect.y+ii, rect.x+rect.width, rect.y+ii)
        else:
            dc.DrawLine(rect.x+ii, rect.y, rect.x+ii, rect.y+rect.height)


class DockInfo:

    def __init__(self):
        
        self.dock_direction = 0
        self.dock_layer = 0
        self.dock_row = 0
        self.size = 0
        self.min_size = 0
        self.resizable = True
        self.fixed = False
        self.toolbar = False
        self.rect = wx.Rect()
        self.panes = []


    def IsOk(self):

        return (self.dock_direction != 0 and [True] or [False])[0]

    
    def IsHorizontal(self):

        return ((self.dock_direction == AUI_DOCK_TOP or \
                self.dock_direction == AUI_DOCK_BOTTOM) and \
                [True] or [False])[0]


    def IsVertical(self):

        return ((self.dock_direction == AUI_DOCK_LEFT or \
                self.dock_direction == AUI_DOCK_RIGHT or \
                self.dock_direction == AUI_DOCK_CENTER) and [True] or [False])[0]
    

class DockUIPart:
    
    typeCaption = 0
    typeGripper = 1
    typeDock = 2
    typeDockSizer = 3
    typePane = 4
    typePaneSizer = 5
    typeBackground = 6
    typePaneBorder = 7
    typePaneButton = 8

    def __init__(self):

        self.orientation = wx.VERTICAL
        self.type = 0
        self.rect = wx.Rect()


class PaneButton:

    def __init__(self, button_id):    

        self.button_id = button_id


# event declarations/classes

class FrameManagerEvent(wx.PyCommandEvent):

    def __init__(self, eventType, id=1):

        wx.PyCommandEvent.__init__(self, eventType, id)
        
        self.pane = None
        self.button = 0


    def SetPane(self, p):
        
        self.pane = p

        
    def SetButton(self, b):
        
        self.button = b

        
    def GetPane(self):
        
        return self.pane


    def GetButton(self):

        return self.button


# -- DefaultDockArt class implementation --
#
# DefaultDockArt is an art provider class which does all of the drawing for
# FrameManager.  This allows the library caller to customize the dock art
# (probably by deriving from this class), or to completely replace all drawing
# with custom dock art. The active dock art class can be set via
# FrameManager.SetDockArt()

class DefaultDockArt:

    def __init__(self):

        base_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        darker1_color = StepColour(base_color, 85)
        darker2_color = StepColour(base_color, 70)
        darker3_color = StepColour(base_color, 60)
        darker4_color = StepColour(base_color, 50)
        darker5_color = StepColour(base_color, 40)

        self._active_caption_colour = LightContrastColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        self._active_caption_gradient_colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self._active_caption_text_colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        self._inactive_caption_colour = StepColour(darker1_color, 80)
        self._inactive_caption_gradient_colour = darker1_color
        self._inactive_caption_text_colour = wx.BLACK

        sash_color = base_color
        caption_color = darker1_color
        paneborder_color = darker2_color
        selectbutton_color = base_color
        selectbuttonpen_color = darker3_color

        self._sash_brush = wx.Brush(base_color)
        self._background_brush = wx.Brush(base_color)
        self._border_pen = wx.Pen(darker2_color)
        self._gripper_brush = wx.Brush(base_color)
        self._gripper_pen1 = wx.Pen(darker5_color)
        self._gripper_pen2 = wx.Pen(darker3_color)
        self._gripper_pen3 = wx.WHITE_PEN

        self._caption_font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)

        self._inactive_close_bitmap = BitmapFromBits(self._inactive_caption_text_colour, 0)
        self._inactive_pin_bitmap = BitmapFromBits(self._inactive_caption_text_colour, 1)
        self._active_close_bitmap = BitmapFromBits(self._active_caption_text_colour, 0)
        self._active_pin_bitmap = BitmapFromBits(self._active_caption_text_colour, 1)
        
        # default metric values
        self._sash_size = 4
        self._caption_size = 17
        self._border_size = 1
        self._button_size = 14
        self._gripper_size = 9
        self._gradient_type = AUI_GRADIENT_VERTICAL
        

    def GetMetric(self, id):

        if id == AUI_ART_SASH_SIZE:
            return self._sash_size
        elif id == AUI_ART_CAPTION_SIZE:
            return self._caption_size
        elif id == AUI_ART_GRIPPER_SIZE:
            return self._gripper_size
        elif id == AUI_ART_PANE_BORDER_SIZE:
            return self._border_size
        elif id == AUI_ART_PANE_BUTTON_SIZE:
            return self._button_size
        elif id == AUI_ART_GRADIENT_TYPE:
            return self._gradient_type
        else:
            raise "\nERROR: Invalid Metric Ordinal. "


    def SetMetric(self, id, new_val):

        if id == AUI_ART_SASH_SIZE:
            self._sash_size = new_val
        elif id == AUI_ART_CAPTION_SIZE:
            self._caption_size = new_val
        elif id == AUI_ART_GRIPPER_SIZE:
            self._gripper_size = new_val
        elif id == AUI_ART_PANE_BORDER_SIZE:
            self._border_size = new_val
        elif id == AUI_ART_PANE_BUTTON_SIZE:
            self._button_size = new_val
        elif id == AUI_ART_GRADIENT_TYPE:
            self._gradient_type = new_val
        else:
            raise "\nERROR: Invalid Metric Ordinal. "


    def GetColor(self, id):

        if id == AUI_ART_BACKGROUND_COLOUR:
            return self._background_brush.GetColour()
        elif id == AUI_ART_SASH_COLOUR:
            return self._sash_brush.GetColour()
        elif id == AUI_ART_INACTIVE_CAPTION_COLOUR:
            return self._inactive_caption_colour
        elif id == AUI_ART_INACTIVE_CAPTION_GRADIENT_COLOUR:
            return self._inactive_caption_gradient_colour
        elif id == AUI_ART_INACTIVE_CAPTION_TEXT_COLOUR:
            return self._inactive_caption_text_colour
        elif id == AUI_ART_ACTIVE_CAPTION_COLOUR:
            return self._active_caption_colour
        elif id == AUI_ART_ACTIVE_CAPTION_GRADIENT_COLOUR:
            return self._active_caption_gradient_colour
        elif id == AUI_ART_ACTIVE_CAPTION_TEXT_COLOUR:
            return self._active_caption_text_colour        
        elif id == AUI_ART_BORDER_COLOUR:
            return self._border_pen.GetColour()
        elif id == AUI_ART_GRIPPER_COLOUR:
            return self._gripper_brush.GetColour()
        else:
            raise "\nERROR: Invalid Metric Ordinal. "


    def SetColor(self, id, colour):

        if id == AUI_ART_BACKGROUND_COLOUR:
            self._background_brush.SetColour(colour)
        elif id == AUI_ART_SASH_COLOUR:
            self._sash_brush.SetColour(colour)
        elif id == AUI_ART_INACTIVE_CAPTION_COLOUR:
            self._inactive_caption_colour = colour
        elif id == AUI_ART_INACTIVE_CAPTION_GRADIENT_COLOUR:
            self._inactive_caption_gradient_colour = colour
        elif id == AUI_ART_INACTIVE_CAPTION_TEXT_COLOUR:
            self._inactive_caption_text_colour = colour
        elif id == AUI_ART_ACTIVE_CAPTION_COLOUR:
            self._active_caption_colour = colour
        elif id == AUI_ART_ACTIVE_CAPTION_GRADIENT_COLOUR:
            self._active_caption_gradient_colour = colour
        elif id == AUI_ART_ACTIVE_CAPTION_TEXT_COLOUR:
            self._active_caption_text_colour = colour
        elif id == AUI_ART_BORDER_COLOUR:
            self._border_pen.SetColour(colour)
        elif id == AUI_ART_GRIPPER_COLOUR:
            self._gripper_brush.SetColour(colour)
            self._gripper_pen1.SetColour(StepColour(colour, 40))
            self._gripper_pen2.SetColour(StepColour(colour, 60))
        else:
            raise "\nERROR: Invalid Metric Ordinal. "
        

    GetColour = GetColor
    SetColour = SetColor

    def SetFont(self, id, font):

        if id == AUI_ART_CAPTION_FONT:
            self._caption_font = font


    def GetFont(self, id):

        if id == AUI_ART_CAPTION_FONT:
            return self._caption_font
        
        return wx.NoneFont


    def DrawSash(self, dc, orient, rect):

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(self._sash_brush)
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)


    def DrawBackground(self, dc, orient, rect):

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(self._background_brush)
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)


    def DrawBorder(self, dc, rect, pane):

        drect = wx.Rect()
        drect.x = rect.x
        drect.y = rect.y
        drect.width = rect.width
        drect.height = rect.height
        
        dc.SetPen(self._border_pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        border_width = self.GetMetric(AUI_ART_PANE_BORDER_SIZE)

        if pane.IsToolbar():
        
            for ii in xrange(0, border_width):
            
                dc.SetPen(wx.WHITE_PEN)
                dc.DrawLine(drect.x, drect.y, drect.x+drect.width, drect.y)
                dc.DrawLine(drect.x, drect.y, drect.x, drect.y+drect.height)
                dc.SetPen(self._border_pen)       
                dc.DrawLine(drect.x, drect.y+drect.height-1,
                            drect.x+drect.width, drect.y+drect.height-1)
                dc.DrawLine(drect.x+drect.width-1, drect.y,
                            drect.x+drect.width-1, drect.y+drect.height)
                drect.Deflate(1, 1)
        
        else:
        
            for ii in xrange(0, border_width):
            
                dc.DrawRectangle(drect.x, drect.y, drect.width, drect.height)
                drect.Deflate(1, 1)
            

    def DrawCaptionBackground(self, dc, rect, active):

        if self._gradient_type == AUI_GRADIENT_NONE:
            if active:
                dc.SetBrush(wx.Brush(self._active_caption_colour))
            else:
                dc.SetBrush(wx.Brush(self._inactive_caption_colour))

            dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)        
        else:
            if active:
                DrawGradientRectangle(dc, rect, self._active_caption_colour,
                                      self._active_caption_gradient_colour,
                                      self._gradient_type)
            else:
                DrawGradientRectangle(dc, rect, self._inactive_caption_colour,
                                      self._inactive_caption_gradient_colour,
                                      self._gradient_type)


    def DrawCaption(self, dc, text, rect, pane):

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetFont(self._caption_font)

        self.DrawCaptionBackground(dc, rect, ((pane.state & PaneInfo.optionActive) and \
                                              [True] or [False])[0])

        if pane.state & PaneInfo.optionActive:
            dc.SetTextForeground(self._active_caption_text_colour)
        else:
            dc.SetTextForeground(self._inactive_caption_text_colour)

        w, h = dc.GetTextExtent("ABCDEFHXfgkj")

        dc.SetClippingRegion(rect.x, rect.y, rect.width, rect.height)
        dc.DrawText(text, rect.x+3, rect.y+(rect.height/2)-(h/2)-1)
        dc.DestroyClippingRegion()


    def DrawGripper(self, dc, rect, pane):

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(self._gripper_brush)

        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)

        if not pane.HasGripperTop():
            y = 5
            while 1:
                dc.SetPen(self._gripper_pen1)
                dc.DrawPoint(rect.x+3, rect.y+y) 
                dc.SetPen(self._gripper_pen2) 
                dc.DrawPoint(rect.x+3, rect.y+y+1) 
                dc.DrawPoint(rect.x+4, rect.y+y) 
                dc.SetPen(self._gripper_pen3) 
                dc.DrawPoint(rect.x+5, rect.y+y+1) 
                dc.DrawPoint(rect.x+5, rect.y+y+2) 
                dc.DrawPoint(rect.x+4, rect.y+y+2) 
                y = y + 4 
                if y > rect.GetHeight() - 5:
                    break
        else:
            x = 5
            while 1:
                dc.SetPen(self._gripper_pen1) 
                dc.DrawPoint(rect.x+x, rect.y+3) 
                dc.SetPen(self._gripper_pen2) 
                dc.DrawPoint(rect.x+x+1, rect.y+3) 
                dc.DrawPoint(rect.x+x, rect.y+4) 
                dc.SetPen(self._gripper_pen3) 
                dc.DrawPoint(rect.x+x+1, rect.y+5) 
                dc.DrawPoint(rect.x+x+2, rect.y+5) 
                dc.DrawPoint(rect.x+x+2, rect.y+4) 
                x = x + 4 
                if x > rect.GetWidth() - 5:
                    break 
        

    def DrawPaneButton(self, dc, button, button_state, rect, pane):

        drect = wx.Rect()
        drect.x = rect.x
        drect.y = rect.y
        drect.width = rect.width
        drect.height = rect.height
        
        if button_state == AUI_BUTTON_STATE_PRESSED:
        
            drect.x = drect.x + 1
            drect.y = drect.y + 1
        
        if button_state in [AUI_BUTTON_STATE_HOVER, AUI_BUTTON_STATE_PRESSED]:
        
            if pane.state & PaneInfo.optionActive:
                dc.SetBrush(wx.Brush(StepColour(self._active_caption_colour, 120)))
                dc.SetPen(wx.Pen(StepColour(self._active_caption_colour, 70)))
            else:
                dc.SetBrush(wx.Brush(StepColour(self._inactive_caption_colour, 120)))
                dc.SetPen(wx.Pen(StepColour(self._inactive_caption_colour, 70)))

            # draw the background behind the button
            dc.DrawRectangle(drect.x, drect.y, 15, 15)

        if button == PaneInfo.buttonClose:
            if pane.state & PaneInfo.optionActive:
                
                bmp = self._active_close_bitmap
            
            else:
                bmp = self._inactive_close_bitmap
        elif button == PaneInfo.buttonPin:
            if pane.state & PaneInfo.optionActive:
                
                bmp = self._active_pin_bitmap
            
            else:
                bmp = self._inactive_pin_bitmap

        # draw the button itself
        dc.DrawBitmap(bmp, drect.x, drect.y, True)


# -- PaneInfo class implementation --
#
# PaneInfo specifies all the parameters for a pane. These parameters specify where
# the pane is on the screen, whether it is docked or floating, or hidden. In addition,
# these parameters specify the pane's docked position, floating position, preferred
# size, minimum size, caption text among many other parameters. 

class PaneInfo:
    
    optionFloating        = 2**0
    optionHidden          = 2**1
    optionLeftDockable    = 2**2
    optionRightDockable   = 2**3
    optionTopDockable     = 2**4
    optionBottomDockable  = 2**5
    optionFloatable       = 2**6
    optionMovable         = 2**7
    optionResizable       = 2**8
    optionPaneBorder      = 2**9
    optionCaption         = 2**10
    optionGripper         = 2**11
    optionDestroyOnClose  = 2**12
    optionToolbar         = 2**13
    optionActive          = 2**14
    optionGripperTop      = 2**15

    buttonClose           = 2**24
    buttonMaximize        = 2**25
    buttonMinimize        = 2**26
    buttonPin             = 2**27
    buttonCustom1         = 2**28
    buttonCustom2         = 2**29
    buttonCustom3         = 2**30
    actionPane            = 2**31    # used internally

    def __init__(self):

        wx.DefaultSize = wx.Size(-1, -1)        
        self.window = None
        self.frame = None
        self.state = 0
        self.dock_direction = AUI_DOCK_LEFT
        self.dock_layer = 0
        self.dock_row = 0
        self.dock_pos = 0
        self.floating_pos = wx.Point(-1, -1)
        self.floating_size = wx.Size(-1, -1)
        self.best_size = wx.Size(-1, -1)
        self.min_size = wx.Size(-1, -1)
        self.max_size = wx.Size(-1, -1)
        self.dock_proportion = 0
        self.caption = ""
        self.buttons = []
        self.name = ""
        self.rect = wx.Rect()
        
        self.DefaultPane()
    

    def IsOk(self):
        """ IsOk() returns True if the PaneInfo structure is valid. """
        
        return (self.window != None and [True] or [False])[0]


    def IsFixed(self):
        """ IsFixed() returns True if the pane cannot be resized. """
        
        return not self.HasFlag(self.optionResizable)

    
    def IsResizable(self):
        """ IsResizeable() returns True if the pane can be resized. """
        
        return self.HasFlag(self.optionResizable)

    
    def IsShown(self):
        """ IsShown() returns True if the pane should be drawn on the screen. """
        
        return not self.HasFlag(self.optionHidden)

    
    def IsFloating(self):
        """ IsFloating() returns True if the pane is floating. """

        return self.HasFlag(self.optionFloating)

    
    def IsDocked(self):
        """ IsDocked() returns True if the pane is docked. """
        
        return not self.HasFlag(self.optionFloating)

    
    def IsToolbar(self):
        """ IsToolbar() returns True if the pane contains a toolbar. """

        return self.HasFlag(self.optionToolbar)

    
    def IsTopDockable(self):
        """
        IsTopDockable() returns True if the pane can be docked at the top
        of the managed frame.
        """
        
        return self.HasFlag(self.optionTopDockable)

    
    def IsBottomDockable(self):
        """
        IsBottomDockable() returns True if the pane can be docked at the bottom
        of the managed frame.
        """
        
        return self.HasFlag(self.optionBottomDockable)

    
    def IsLeftDockable(self):
        """
        IsLeftDockable() returns True if the pane can be docked at the left
        of the managed frame.
        """
        
        return self.HasFlag(self.optionLeftDockable) 


    def IsRightDockable(self):
        """
        IsRightDockable() returns True if the pane can be docked at the right
        of the managed frame.
        """
        
        return self.HasFlag(self.optionRightDockable)


    def IsDockable(self):
        """ IsDockable() returns True if the pane can be docked. """
        
        return self.IsTopDockable() or self.IsBottomDockable() or self.IsLeftDockable() or \
               self.IsRightDockable()
    
    
    def IsFloatable(self):
        """
        IsFloatable() returns True if the pane can be undocked and displayed as a
        floating window.
        """

        return self.HasFlag(self.optionFloatable)

    
    def IsMovable(self):
        """
        IsMoveable() returns True if the docked frame can be undocked or moved to
        another dock position.
        """
        
        return self.HasFlag(self.optionMovable)
    

    def HasCaption(self):
        """ HasCaption() returns True if the pane displays a caption. """
        
        return self.HasFlag(self.optionCaption)
    

    def HasGripper(self):
        """ HasGripper() returns True if the pane displays a gripper. """
        
        return self.HasFlag(self.optionGripper) 


    def HasBorder(self):
        """ HasBorder() returns True if the pane displays a border. """
        
        return self.HasFlag(self.optionPaneBorder)

    
    def HasCloseButton(self):
        """
        HasCloseButton() returns True if the pane displays a button to close
        the pane.
        """

        return self.HasFlag(self.buttonClose) 


    def HasMaximizeButton(self):
        """
        HasMaximizeButton() returns True if the pane displays a button to
        maximize the pane.
        """
        
        return self.HasFlag(self.buttonMaximize)

    
    def HasMinimizeButton(self):
        """
        HasMinimizeButton() returns True if the pane displays a button to
        minimize the pane.
        """
        
        return self.HasFlag(self.buttonMinimize) 


    def HasPinButton(self):
        """ HasPinButton() returns True if the pane displays a button to float the pane. """
        
        return self.HasFlag(self.buttonPin) 


    def HasGripperTop(self):

        return self.HasFlag(self.optionGripperTop)


    def Window(self, w):

        self.window = w
        return self

    
    def Name(self, n):
        """ Name() sets the name of the pane so it can be referenced in lookup functions. """

        self.name = n
        return self

    
    def Caption(self, c):
        """ Caption() sets the caption of the pane. """
        
        self.caption = c
        return self

    
    def Left(self):
        """ Left() sets the pane dock position to the left side of the frame. """
        
        self.dock_direction = AUI_DOCK_LEFT
        return self

    
    def Right(self):
        """ Right() sets the pane dock position to the right side of the frame. """
        
        self.dock_direction = AUI_DOCK_RIGHT
        return self

    
    def Top(self):
        """ Top() sets the pane dock position to the top of the frame. """

        self.dock_direction = AUI_DOCK_TOP
        return self

    
    def Bottom(self):
        """ Bottom() sets the pane dock position to the bottom of the frame. """

        self.dock_direction = AUI_DOCK_BOTTOM
        return self

    
    def Center(self):
        """ Center() sets the pane to the center position of the frame. """
        
        self.dock_direction = AUI_DOCK_CENTER
        return self

        
    def Centre(self):
        """ Centre() sets the pane to the center position of the frame. """
        
        self.dock_direction = AUI_DOCK_CENTRE
        return self

    
    def Direction(self, direction):
        """ Direction() determines the direction of the docked pane. """
        
        self.dock_direction = direction
        return self

    
    def Layer(self, layer):
        """ Layer() determines the layer of the docked pane. """
        
        self.dock_layer = layer
        return self

    
    def Row(self, row):
        """ Row() determines the row of the docked pane. """
        
        self.dock_row = row
        return self

    
    def Position(self, pos):
        """ Position() determines the position of the docked pane. """

        self.dock_pos = pos
        return self


    def MinSize(self, arg1=None, arg2=None):
        """ MinSize() sets the minimum size of the pane. """
        
        if isinstance(arg1, wx.Size):
            ret = self.MinSize1(arg1)
        else:
            ret = self.MinSize2(arg1, arg2)

        return ret

    
    def MinSize1(self, size):

        self.min_size = size
        return self


    def MinSize2(self, x, y):

        self.min_size.Set(x,y)
        return self


    def MaxSize(self, arg1=None, arg2=None):
        """ MaxSize() sets the maximum size of the pane. """
        
        if isinstance(arg1, wx.Size):
            ret = self.MaxSize1(arg1)
        else:
            ret = self.MaxSize2(arg1, arg2)

        return ret
    
    
    def MaxSize1(self, size):

        self.max_size = size
        return self


    def MaxSize2(self, x, y):

        self.max_size.Set(x,y)
        return self


    def BestSize(self, arg1=None, arg2=None):
        """ BestSize() sets the ideal size for the pane. """

        if isinstance(arg1, wx.Size):
            ret = self.BestSize1(arg1)
        else:
            ret = self.BestSize2(arg1, arg2)

        return ret
    
            
    def BestSize1(self, size):

        self.best_size = size
        return self

    
    def BestSize2(self, x, y):

        self.best_size.Set(x,y)
        return self
    
    
    def FloatingPosition(self, pos):
        """ FloatingPosition() sets the position of the floating pane. """
        
        self.floating_pos = pos
        return self

    
    def FloatingSize(self, size):
        """ FloatingSize() sets the size of the floating pane. """
        
        self.floating_size = size
        return self

    
    def Fixed(self):
        """ Fixed() forces a pane to be fixed size so that it cannot be resized. """
        
        return self.SetFlag(self.optionResizable, False)

    
    def Resizable(self, resizable=True):
        """
        Resizable() allows a pane to be resizable if resizable is True, and forces
        it to be a fixed size if resizeable is False.
        """
        
        return self.SetFlag(self.optionResizable, resizable)

    
    def Dock(self):
        """ Dock() indicates that a pane should be docked. """
        
        return self.SetFlag(self.optionFloating, False)

    
    def Float(self):
        """ Float() indicates that a pane should be floated. """
        
        return self.SetFlag(self.optionFloating, True)

    
    def Hide(self):
        """ Hide() indicates that a pane should be hidden. """
        
        return self.SetFlag(self.optionHidden, True)

    
    def Show(self, show=True):
        """ Show() indicates that a pane should be shown. """
        
        return self.SetFlag(self.optionHidden, not show)
    
    
    def CaptionVisible(self, visible=True):
        """ CaptionVisible() indicates that a pane caption should be visible. """
        
        return self.SetFlag(self.optionCaption, visible)

    
    def PaneBorder(self, visible=True):
        """ PaneBorder() indicates that a border should be drawn for the pane. """
        
        return self.SetFlag(self.optionPaneBorder, visible)

    
    def Gripper(self, visible=True):
        """ Gripper() indicates that a gripper should be drawn for the pane. """
        
        return self.SetFlag(self.optionGripper, visible)


    def GripperTop(self, attop=True):
        """ GripperTop() indicates that a gripper should be drawn for the pane. """
        
        return self.SetFlag(self.optionGripperTop, attop)

    
    def CloseButton(self, visible=True):
        """ CloseButton() indicates that a close button should be drawn for the pane. """
        
        return self.SetFlag(self.buttonClose, visible)

    
    def MaximizeButton(self, visible=True):
        """ MaximizeButton() indicates that a maximize button should be drawn for the pane. """
        
        return self.SetFlag(self.buttonMaximize, visible)

    
    def MinimizeButton(self, visible=True):
        """ MinimizeButton() indicates that a minimize button should be drawn for the pane. """
        
        return self.SetFlag(self.buttonMinimize, visible)

    
    def PinButton(self, visible=True):
        """ PinButton() indicates that a pin button should be drawn for the pane. """
        
        return self.SetFlag(self.buttonPin, visible)

    
    def DestroyOnClose(self, b=True):
        """ DestroyOnClose() indicates whether a pane should be destroyed when it is closed. """
        
        return self.SetFlag(self.optionDestroyOnClose, b)

    
    def TopDockable(self, b=True):
        """ TopDockable() indicates whether a pane can be docked at the top of the frame. """
        
        return self.SetFlag(self.optionTopDockable, b)

    
    def BottomDockable(self, b=True):
        """ BottomDockable() indicates whether a pane can be docked at the bottom of the frame. """
        
        return self.SetFlag(self.optionBottomDockable, b)

    
    def LeftDockable(self, b=True):
        """ LeftDockable() indicates whether a pane can be docked on the left of the frame. """

        return self.SetFlag(self.optionLeftDockable, b)

    
    def RightDockable(self, b=True):
        """ RightDockable() indicates whether a pane can be docked on the right of the frame. """
        
        return self.SetFlag(self.optionRightDockable, b)

    
    def Floatable(self, b=True):
        """ Floatable() indicates whether a frame can be floated. """
        
        return self.SetFlag(self.optionFloatable, b)

    
    def Movable(self, b=True):
        """ Movable() indicates whether a frame can be moved. """
        
        return self.SetFlag(self.optionMovable, b)

    
    def Dockable(self, b=True):
    
        return self.TopDockable(b).BottomDockable(b).LeftDockable(b).RightDockable(b)
    

    def DefaultPane(self):
        """ DefaultPane() specifies that the pane should adopt the default pane settings. """
        
        state = self.state    
        state |= self.optionTopDockable | self.optionBottomDockable | \
                 self.optionLeftDockable | self.optionRightDockable | \
                 self.optionFloatable | self.optionMovable | self.optionResizable | \
                 self.optionCaption | self.optionPaneBorder | self.buttonClose

        self.state = state
        
        return self
    
    
    def CentrePane(self):
        """ CentrePane() specifies that the pane should adopt the default center pane settings. """
        
        return self.CenterPane()

    
    def CenterPane(self):
        """ CenterPane() specifies that the pane should adopt the default center pane settings. """
        
        self.state = 0
        return self.Center().PaneBorder().Resizable()
    
     
    def ToolbarPane(self):
        """ ToolbarPane() specifies that the pane should adopt the default toolbar pane settings. """
        
        self.DefaultPane()
        state = self.state
        
        state |= (self.optionToolbar | self.optionGripper)
        state &= ~(self.optionResizable | self.optionCaption)
        
        if self.dock_layer == 0:
            self.dock_layer = 10

        self.state = state
        
        return self
    

    def SetFlag(self, flag, option_state):
        """ SetFlag() turns the property given by flag on or off with the option_state parameter. """
        
        state = self.state
        
        if option_state:
            state |= flag
        else:
            state &= ~flag

        self.state = state
        
        return self
    
    
    def HasFlag(self, flag):
        """ HasFlag() returns True if the the property specified by flag is active for the pane. """
        
        return (self.state & flag and [True] or [False])[0]
    

NonePaneInfo = PaneInfo()

# -- FloatingPane class implementation --
#
# FloatingPane implements a frame class with some special functionality
# which allows the library to sense when the frame move starts, is active,
# and completes.  Note that it contains it's own FrameManager instance,
# which, in the future, would allow for nested managed frames.
# For now, with wxMSW, the wx.MiniFrame window is used, but on wxGTK, wx.Frame

if wx.Platform == "__WXGTK__":
    
    class FloatingPaneBaseClass(wx.Frame):
        def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                     size=wx.DefaultSize, style=0):
            wx.Frame.__init__(self, parent, id, title, pos, size, style)

else:

    class FloatingPaneBaseClass(wx.MiniFrame):
        def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                     size=wx.DefaultSize, style=0):
            wx.MiniFrame.__init__(self, parent, id, title, pos, size, style)
            if wx.Platform == "__WXMAC__":
                self.MacSetMetalAppearance(True)
            

class FloatingPane(FloatingPaneBaseClass):

    def __init__(self, parent, owner_mgr, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION |
                                            wx.CLOSE_BOX | wx.FRAME_NO_TASKBAR |
                                            wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN,
                 resizeborder=0):

        if not resizeborder:
            style = style & ~wx.RESIZE_BORDER
            
        FloatingPaneBaseClass.__init__(self, parent, id, title, pos, size, style)
        self._owner_mgr = owner_mgr
        self._moving = False
        self._last_rect = wx.Rect()
        self._mgr = FrameManager(None)
        self._mgr.SetFrame(self)
        self._mousedown = False
        self.SetExtraStyle(wx.WS_EX_PROCESS_IDLE)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOVE, self.OnMoveEvent)
        self.Bind(wx.EVT_MOVING, self.OnMoveEvent)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        

    def CopyAttributes(self, pane, contained_pane):

        contained_pane.name = pane.name
        contained_pane.caption = pane.caption
        contained_pane.window = pane.window
        contained_pane.frame = pane.frame
        contained_pane.state = pane.state
        contained_pane.dock_direction = pane.dock_direction
        contained_pane.dock_layer = pane.dock_layer
        contained_pane.dock_row = pane.dock_row
        contained_pane.dock_pos = pane.dock_pos
        contained_pane.best_size = pane.best_size
        contained_pane.min_size = pane.min_size
        contained_pane.max_size = pane.max_size
        contained_pane.floating_pos = pane.floating_pos
        contained_pane.floating_size = pane.floating_size
        contained_pane.dock_proportion = pane.dock_proportion
        contained_pane.buttons = pane.buttons
        contained_pane.rect = pane.rect

        return contained_pane
    

    def SetPaneWindow(self, pane):

        self._pane_window = pane.window
        self._pane_window.Reparent(self)
        
        contained_pane = PaneInfo()

        contained_pane = self.CopyAttributes(pane, contained_pane)        
        
        contained_pane.Dock().Center().Show(). \
                       CaptionVisible(False). \
                       PaneBorder(False). \
                       Layer(0).Row(0).Position(0)

        indx = self._owner_mgr._panes.index(pane)
        self._owner_mgr._panes[indx] = pane
                                              
        self._mgr.AddPane(self._pane_window, contained_pane)
        self._mgr.Update()           

        if pane.min_size.IsFullySpecified():
            tmp = self.GetSize()
            self.GetSizer().SetSizeHints(self)
            self.SetSize(tmp)
        
        self.SetTitle(pane.caption)

        if pane.floating_size != wx.DefaultSize:
            self.SetSize(pane.floating_size)
            self._owner_mgr._panes[indx] = pane
        else:
            size = pane.best_size
            if size == wx.DefaultSize:
                size = pane.min_size
            if size == wx.DefaultSize:
                size = self._pane_window.GetSize()
            if pane.HasGripper():
                if pane.HasGripperTop():
                    size.y += self._owner_mgr._art.GetMetric(AUI_ART_GRIPPER_SIZE)
                else:
                    size.x += self._owner_mgr._art.GetMetric(AUI_ART_GRIPPER_SIZE)

            pane.floating_size = size
            self._owner_mgr._panes[indx] = pane
            self.SetClientSize(size)

    
    def OnSize(self, event):

        self._owner_mgr.OnFloatingPaneResized(self._pane_window, event.GetSize())
        
    
    def OnClose(self, event):
    
        self._owner_mgr.OnFloatingPaneClosed(self._pane_window)
        self.Destroy()
        
        self._mgr.UnInit()

        # Eventually to be added to handle wx.EVT_CLOSE events
        # commenting ALL the above 3 lines
        #
        # e = FrameManagerEvent(wxEVT_AUI_PANEBUTTON)
        # e.SetPane(self._owner_mgr.GetPane(self._pane_window))
        # e.SetButton(PaneInfo.buttonClose)
        # self._owner_mgr.ProcessMgrEvent(e)
    

    def OnMoveEvent(self, event):

        win_rect = self.GetRect()

        # skip the first move event
        if self._last_rect.IsEmpty():
            self._last_rect = win_rect
            return

        # prevent frame redocking during resize
        if self._last_rect.GetSize() != win_rect.GetSize():
            self._last_rect = win_rect
            return
        
        self._last_rect = win_rect

        if not self.IsMouseDown():
            return

        if not self._moving:
            self.OnMoveStart()
            self._moving = True
        
        self.OnMoving(event.GetRect())


    def IsMouseDown(self):

        if _newversion:
            ms = wx.GetMouseState()
            return ms.leftDown
        else:
            if wx.Platform == "__WXMSW__":
                if _libimported == "MH":
                    return ((win32api.GetKeyState(win32con.VK_LBUTTON) & (1<<15))\
                            and [True] or [False])[0]
                elif _libimported == "ctypes":
                    return ((ctypes.windll.user32.GetKeyState(1) & (1<<15)) and \
                            [True] or [False])[0]
            
    
    def OnIdle(self, event):
    
        if self._moving:
            if not self.IsMouseDown():
                self._moving = False
                self.OnMoveFinished()
            else:
                event.RequestMore()

        event.Skip()

        
    def OnMoveStart(self):
    
        # notify the owner manager that the pane has started to move
        self._owner_mgr.OnFloatingPaneMoveStart(self._pane_window)
    

    def OnMoving(self, window_rect):
    
        # notify the owner manager that the pane is moving
        self._owner_mgr.OnFloatingPaneMoving(self._pane_window)

    
    def OnMoveFinished(self):
    
        # notify the owner manager that the pane has finished moving
        self._owner_mgr.OnFloatingPaneMoved(self._pane_window)
    

    def OnActivate(self, event):

        if event.GetActive():
            self._owner_mgr.OnFloatingPaneActivated(self._pane_window)

    
# -- static utility functions --

def PaneCreateStippleBitmap():

    data = [0, 0, 0, 192, 192, 192, 192, 192, 192, 0, 0, 0]
    img = wx.EmptyImage(2, 2)
    counter = 0
    
    for ii in xrange(2):
        for jj in xrange(2):
            img.SetRGB(ii, jj, data[counter], data[counter+1], data[counter+2])
            counter = counter + 3
    
    return img.ConvertToBitmap()


def DrawResizeHint(dc, rect):
        
    stipple = PaneCreateStippleBitmap()
    brush = wx.BrushFromBitmap(stipple)
    dc.SetBrush(brush)
    dc.SetPen(wx.TRANSPARENT_PEN)

    dc.SetLogicalFunction(wx.XOR)
    dc.DrawRectangleRect(rect)    


def CopyDocksAndPanes(src_docks, src_panes):
    """
    CopyDocksAndPanes() - this utility function creates shallow copies of
    the dock and pane info.  DockInfo's usually contain pointers
    to PaneInfo classes, thus this function is necessary to reliably
    reconstruct that relationship in the new dock info and pane info arrays.
    """
    
    dest_docks = src_docks
    dest_panes = src_panes

    for ii in xrange(len(dest_docks)):
        dock = dest_docks[ii]
        for jj in xrange(len(dock.panes)):
            for kk in xrange(len(src_panes)):
                if dock.panes[jj] == src_panes[kk]:
                    dock.panes[jj] = dest_panes[kk]

    return dest_docks, dest_panes


def CopyDocksAndPanes2(src_docks, src_panes):
    """
    CopyDocksAndPanes2() - this utility function creates full copies of
    the dock and pane info.  DockInfo's usually contain pointers
    to PaneInfo classes, thus this function is necessary to reliably
    reconstruct that relationship in the new dock info and pane info arrays.
    """
    
    dest_docks = []

    for ii in xrange(len(src_docks)):
        dest_docks.append(DockInfo())
        dest_docks[ii].dock_direction = src_docks[ii].dock_direction
        dest_docks[ii].dock_layer = src_docks[ii].dock_layer
        dest_docks[ii].dock_row = src_docks[ii].dock_row
        dest_docks[ii].size = src_docks[ii].size
        dest_docks[ii].min_size = src_docks[ii].min_size
        dest_docks[ii].resizable = src_docks[ii].resizable
        dest_docks[ii].fixed = src_docks[ii].fixed
        dest_docks[ii].toolbar = src_docks[ii].toolbar
        dest_docks[ii].panes = src_docks[ii].panes
        dest_docks[ii].rect = src_docks[ii].rect

    dest_panes = []

    for ii in xrange(len(src_panes)):
        dest_panes.append(PaneInfo())
        dest_panes[ii].name = src_panes[ii].name
        dest_panes[ii].caption = src_panes[ii].caption
        dest_panes[ii].window = src_panes[ii].window
        dest_panes[ii].frame = src_panes[ii].frame
        dest_panes[ii].state = src_panes[ii].state
        dest_panes[ii].dock_direction = src_panes[ii].dock_direction
        dest_panes[ii].dock_layer = src_panes[ii].dock_layer
        dest_panes[ii].dock_row = src_panes[ii].dock_row
        dest_panes[ii].dock_pos = src_panes[ii].dock_pos
        dest_panes[ii].best_size = src_panes[ii].best_size
        dest_panes[ii].min_size = src_panes[ii].min_size
        dest_panes[ii].max_size = src_panes[ii].max_size
        dest_panes[ii].floating_pos = src_panes[ii].floating_pos
        dest_panes[ii].floating_size = src_panes[ii].floating_size
        dest_panes[ii].dock_proportion = src_panes[ii].dock_proportion
        dest_panes[ii].buttons = src_panes[ii].buttons
        dest_panes[ii].rect = src_panes[ii].rect

    for ii in xrange(len(dest_docks)):
        dock = dest_docks[ii]
        for jj in xrange(len(dock.panes)):
            for kk in xrange(len(src_panes)):
                if dock.panes[jj] == src_panes[kk]:
                    dock.panes[jj] = dest_panes[kk]

        dest_docks[ii] = dock
        
    return dest_docks, dest_panes


def GetMaxLayer(docks, dock_direction):
    """
    GetMaxLayer() is an internal function which returns
    the highest layer inside the specified dock.
    """
    
    max_layer = 0

    for dock in docks:
        if dock.dock_direction == dock_direction and dock.dock_layer > max_layer and not dock.fixed:
            max_layer = dock.dock_layer
    
    return max_layer


def GetMaxRow(panes, direction, layer):
    """
    GetMaxRow() is an internal function which returns
    the highest layer inside the specified dock.
    """
    
    max_row = 0

    for pane in panes:
        if pane.dock_direction == direction and pane.dock_layer == layer and \
           pane.dock_row > max_row:
            max_row = pane.dock_row
    
    return max_row


def DoInsertDockLayer(panes, dock_direction, dock_layer):
    """
    DoInsertDockLayer() is an internal function that inserts a new dock
    layer by incrementing all existing dock layer values by one.
    """
    
    for ii in xrange(len(panes)):
        pane = panes[ii]
        if not pane.IsFloating() and pane.dock_direction == dock_direction and pane.dock_layer >= dock_layer:
            pane.dock_layer = pane.dock_layer + 1

        panes[ii] = pane

    return panes


def DoInsertDockRow(panes, dock_direction, dock_layer, dock_row):
    """
    DoInsertDockRow() is an internal function that inserts a new dock
    row by incrementing all existing dock row values by one.
    """
    
    for ii in xrange(len(panes)):
        pane = panes[ii]
        if not pane.IsFloating() and pane.dock_direction == dock_direction and \
           pane.dock_layer == dock_layer and pane.dock_row >= dock_row:
            pane.dock_row = pane.dock_row + 1

        panes[ii] = pane

    return panes

    
def DoInsertPane(panes, dock_direction, dock_layer, dock_row, dock_pos):

    for ii in xrange(len(panes)):
        pane = panes[ii]
        if not pane.IsFloating() and pane.dock_direction == dock_direction and \
           pane.dock_layer == dock_layer and  pane.dock_row == dock_row and \
           pane.dock_pos >= dock_pos:
            pane.dock_pos = pane.dock_pos + 1

        panes[ii] = pane

    return panes


def FindDocks(docks, dock_direction, dock_layer=-1, dock_row=-1, arr=[]):
    """
    FindDocks() is an internal function that returns a list of docks which meet
    the specified conditions in the parameters and returns a sorted array
    (sorted by layer and then row).
    """
    
    begin_layer = dock_layer
    end_layer = dock_layer
    begin_row = dock_row
    end_row = dock_row
    dock_count = len(docks)
    max_row = 0
    max_layer = 0
    
    # discover the maximum dock layer and the max row
    for ii in xrange(dock_count):
        max_row = max(max_row, docks[ii].dock_row)
        max_layer = max(max_layer, docks[ii].dock_layer)
    
    # if no dock layer was specified, search all dock layers
    if dock_layer == -1:
        begin_layer = 0
        end_layer = max_layer
    
    # if no dock row was specified, search all dock row
    if dock_row == -1:
        begin_row = 0
        end_row = max_row

    arr = []

    for layer in xrange(begin_layer, end_layer+1):
        for row in xrange(begin_row, end_row+1):
            for ii in xrange(dock_count):
                d = docks[ii]
                if dock_direction == -1 or dock_direction == d.dock_direction:
                    if d.dock_layer == layer and d.dock_row == row:
                        arr.append(d)

    return arr


def FindPaneInDock(dock, window):
    """
    FindPaneInDock() looks up a specified window pointer inside a dock.
    If found, the corresponding PaneInfo pointer is returned, otherwise None.
    """

    for p in dock.panes:
        if p.window == window:
            return p
    
    return None


def RemovePaneFromDocks(docks, pane, exc=None):
    """
    RemovePaneFromDocks() removes a pane window from all docks
    with a possible exception specified by parameter "except".
    """
    
    for ii in xrange(len(docks)):
        d = docks[ii]
        if d == exc:
            continue
        pi = FindPaneInDock(d, pane.window)
        if pi:
            d.panes.remove(pi)

        docks[ii] = d            

    return docks


def RenumberDockRows(docks):
    """
    RenumberDockRows() takes a dock and assigns sequential numbers
    to existing rows.  Basically it takes out the gaps so if a
    dock has rows with numbers 0, 2, 5, they will become 0, 1, 2.
    """
    
    for ii in xrange(len(docks)):
        dock = docks[ii]
        dock.dock_row = ii
        for jj in xrange(len(dock.panes)):
            dock.panes[jj].dock_row = ii

        docks[ii] = dock
        
    return docks


def SetActivePane(panes, active_pane):
    
    for ii in xrange(len(panes)):
        pane = panes[ii]
        pane.state &= ~PaneInfo.optionActive

        if pane.window == active_pane:
            pane.state |= PaneInfo.optionActive

        panes[ii] = pane
        
    return panes


def PaneSortFunc(p1, p2):
    """ This function is used to sort panes by dock position. """
    
    return (p1.dock_pos < p2.dock_pos and [-1] or [1])[0]


def EscapeDelimiters(s):
    """
    EscapeDelimiters() changes "" into "\" and "|" into "\|"
    in the input string.  This is an internal functions which is
    used for saving perspectives.
    """
    
    result = s.replace(";", "\\")
    result = result.replace("|", "|\\")
    
    return result


actionNone = 0
actionResize = 1
actionClickButton = 2
actionClickCaption = 3
actionDragToolbarPane = 4
actionDragFloatingPane = 5    

auiInsertRowPixels = 10
auiNewRowPixels = 40
auiLayerInsertPixels = 40
auiLayerInsertOffset = 5

# -- FrameManager class implementation --
#
# FrameManager manages the panes associated with it for a particular wx.Frame,
# using a pane's PaneInfo information to determine each pane's docking and
# floating behavior. FrameManager uses wxPython's sizer mechanism to plan the
# layout of each frame. It uses a replaceable dock art class to do all drawing,
# so all drawing is localized in one area, and may be customized depending on an
# applications' specific needs.
#
# FrameManager works as follows: The programmer adds panes to the class, or makes
# changes to existing pane properties (dock position, floating state, show state, etc.).
# To apply these changes, FrameManager's Update() function is called. This batch
# processing can be used to avoid flicker, by modifying more than one pane at a time,
# and then "committing" all of the changes at once by calling Update().
#
# Panes can be added quite easily:
#
#   text1 = wx.TextCtrl(self, -1)
#   text2 = wx.TextCtrl(self, -1)
#   self._mgr.AddPane(text1, wx.LEFT, "Pane Caption")
#   self._mgr.AddPane(text2, wx.BOTTOM, "Pane Caption")
#   self._mgr.Update()
#
# Later on, the positions can be modified easily. The following will float an
# existing pane in a tool window:

#   self._mgr.GetPane(text1).Float()

# Layers, Rows and Directions, Positions
# Inside PyAUI, the docking layout is figured out by checking several pane parameters.
# Four of these are important for determining where a pane will end up.
#
# Direction - Each docked pane has a direction, Top, Bottom, Left, Right, or Center.
# This is fairly self-explanatory. The pane will be placed in the location specified
# by this variable.
#
# Position - More than one pane can be placed inside of a "dock." Imagine to panes
# being docked on the left side of a window. One pane can be placed over another.
# In proportionally managed docks, the pane position indicates it's sequential position,
# starting with zero. So, in our scenario with two panes docked on the left side, the
# top pane in the dock would have position 0, and the second one would occupy position 1. 
#
# Row - A row can allow for two docks to be placed next to each other. One of the most
# common places for this to happen is in the toolbar. Multiple toolbar rows are allowed,
# the first row being in row 0, and the second in row 1. Rows can also be used on
# vertically docked panes. 
#
# Layer - A layer is akin to an onion. Layer 0 is the very center of the managed pane.
# Thus, if a pane is in layer 0, it will be closest to the center window (also sometimes
# known as the "content window"). Increasing layers "swallow up" all layers of a lower
# value. This can look very similar to multiple rows, but is different because all panes
# in a lower level yield to panes in higher levels. The best way to understand layers
# is by running the PyAUI sample (PyAUIDemo.py).

class FrameManager(wx.EvtHandler):

    def __init__(self, frame=None, flags=None):
        """
        Default Class Constructor. frame specifies the wx.Frame which should be managed.
        flags specifies options which allow the frame management behavior to be modified.
        """

        wx.EvtHandler.__init__(self)
        self._action = actionNone
        self._last_mouse_move = wx.Point()
        self._hover_button = None
        self._art = DefaultDockArt()
        self._hint_wnd = None
        self._action_window = None
        self._last_hint = wx.Rect()
        self._hint_fadetimer = wx.Timer()
        self._hintshown = False
        
        if flags is None:
            flags = AUI_MGR_DEFAULT
            
        self._flags = flags
        self._active_pane = None

        if frame:
            self.SetFrame(frame)

        self._panes = []
        self._docks = []
        self._uiparts = []

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_SET_CURSOR, self.OnSetCursor)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_TIMER, self.OnHintFadeTimer)
        self.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
        self.Bind(EVT_AUI_PANEBUTTON, self.OnPaneButton)


    def GetPaneByWidget(self, window):
        """
        This version of GetPane() looks up a pane based on a
        'pane window', see below comment for more info.
        """

        for p in self._panes:
            if p.window == window:
                return p

        return NonePaneInfo


    def GetPaneByName(self, name):
        """
        This version of GetPane() looks up a pane based on a
        'pane name', see below comment for more info.
        """
        
        for p in self._panes:
            if p.name == name:
                return p
        
        return NonePaneInfo


    def GetPane(self, item):
        """
        GetPane() looks up a PaneInfo structure based
        on the supplied window pointer.  Upon failure, GetPane()
        returns an empty PaneInfo, a condition which can be checked
        by calling PaneInfo.IsOk().

        The pane info's structure may then be modified.  Once a pane's
        info is modified, FrameManager.Update() must be called to
        realize the changes in the UI.

        AG: Added To Handle 2 Different Versions Of GetPane() For
        wxPython/Python.         
        """

        if isinstance(item, type("")):
            return self.GetPaneByName(item)
        else:
            return self.GetPaneByWidget(item)


    def GetAllPanes(self):
        """ GetAllPanes() returns a reference to all the pane info structures. """
        
        return self._panes


    def HitTest(self, x, y):
        """
        HitTest() is an internal function which determines
        which UI item the specified coordinates are over
        (x,y) specify a position in client coordinates.
        """

        result = None

        for item in self._uiparts:
            # we are not interested in typeDock, because this space 
            # isn't used to draw anything, just for measurements
            # besides, the entire dock area is covered with other
            # rectangles, which we are interested in.
            if item.type == DockUIPart.typeDock:
                continue

            # if we already have a hit on a more specific item, we are not
            # interested in a pane hit.  If, however, we don't already have
            # a hit, returning a pane hit is necessary for some operations
            if (item.type == DockUIPart.typePane or \
                item.type == DockUIPart.typePaneBorder) and result:
                continue
        
            # if the point is inside the rectangle, we have a hit
            if item.rect.Inside((x, y)):
                result = item
        
        return result


    # SetFlags() and GetFlags() allow the owner to set various
    # options which are global to FrameManager

    def SetFlags(self, flags):
        """
        SetFlags() is used to specify FrameManager's settings flags. flags specifies
        options which allow the frame management behavior to be modified.
        """
        
        self._flags = flags


    def GetFlags(self):
        """ GetFlags() returns the current manager's flags. """
        
        return self._flags


    def SetFrame(self, frame):
        """
        SetFrame() is usually called once when the frame
        manager class is being initialized.  "frame" specifies
        the frame which should be managed by the frame manager.
        """

        if not frame:
            raise "\nERROR: Specified Frame Must Be Non-Null. "
        
        self._frame = frame
        self._frame.PushEventHandler(self)

        # if the owner is going to manage an MDI parent frame,
        # we need to add the MDI client window as the default
        # center pane
        if isinstance(frame, wx.MDIParentFrame):
            mdi_frame = frame
            client_window = mdi_frame.GetClientWindow()
            
            if not client_window:
                raise "\nERROR: MDI Client Window Is Null. "

            self.AddPane(client_window, PaneInfo().Name("mdiclient").
                         CenterPane().PaneBorder(False))
        

    def GetFrame(self):
        """ GetFrame() returns the frame pointer being managed by FrameManager. """
        
        return self._frame


    def UnInit(self):
        """
        UnInit() must be called, usually in the destructor
        of the frame class.   If it is not called, usually this
        will result in a crash upon program exit.
        """
        
        self._frame.RemoveEventHandler(self)


    def GetArtProvider(self):
        """ GetArtProvider() returns the current art provider being used. """
        
        return self._art


    def ProcessMgrEvent(self, event):

        # first, give the owner frame a chance to override
        if self._frame:
            if self._frame.ProcessEvent(event):
                return
        
        self.ProcessEvent(event)

    
    def CanMakeWindowsTransparent(self):
        if wx.Platform == "__WXMSW__":
            version = wx.GetOsDescription()
            found = version.find("XP") >= 0 or version.find("2000") >= 0 or version.find("NT") >= 0
            return found and _libimported
        elif wx.Platform == "__WXMAC__" and _carbon_dll:
            return True
        else:
            return False

# on supported windows systems (Win2000 and greater), this function
# will make a frame window transparent by a certain amount
    def MakeWindowTransparent(self, wnd, amount):

        if wnd.GetSize() == (0, 0):
            return

        # this API call is not in all SDKs, only the newer ones, so
        # we will runtime bind this
        if wx.Platform == "__WXMSW__":
            hwnd = wnd.GetHandle()
    
            if not hasattr(self, "_winlib"):
                if _libimported == "MH":
                    self._winlib = win32api.LoadLibrary("user32")
                elif _libimported == "ctypes":
                    self._winlib = ctypes.windll.user32
                    
            if _libimported == "MH":
                pSetLayeredWindowAttributes = win32api.GetProcAddress(self._winlib,
                                                                      "SetLayeredWindowAttributes")
                
                if pSetLayeredWindowAttributes == None:
                    return
                    
                exstyle = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if 0 == (exstyle & 0x80000):
                    win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle | 0x80000)  
                         
                winxpgui.SetLayeredWindowAttributes(hwnd, 0, amount, 2)
    
            elif _libimported == "ctypes":
                style = self._winlib.GetWindowLongA(hwnd, 0xffffffecL)
                style |= 0x00080000
                self._winlib.SetWindowLongA(hwnd, 0xffffffecL, style)
                self._winlib.SetLayeredWindowAttributes(hwnd, 0, amount, 2)
                
        elif wx.Platform == "__WXMAC__" and _carbon_dll:
            handle = _carbon_dll.GetControlOwner(wnd.GetHandle())
            if amount == 0:
                amnt = float(0)
            else:
                amnt = float(amount)/255.0  #convert from the 0-255 amount to the float that Carbon wants
            _carbon_dll.SetWindowAlpha(handle, ctypes.c_float(amnt))
        else:
            #shouldn't be called, but just in case...
            return
    
    
    def SetArtProvider(self, art_provider):
        """
        SetArtProvider() instructs FrameManager to use the
        specified art provider for all drawing calls.  This allows
        plugable look-and-feel features.
        """

        # delete the last art provider, if any
        del self._art
        
        # assign the new art provider
        self._art = art_provider


    def AddPane(self, window, arg1=None, arg2=None):
        """
        AddPane() tells the frame manager to start managing a child window. There
        are two versions of this function. The first verison allows the full spectrum
        of pane parameter possibilities (AddPane1). The second version is used for
        simpler user interfaces which do not require as much configuration (AddPane2).
        In wxPython, simply call AddPane.
        """

        if type(arg1) == type(1):
            # This Is Addpane2
            if arg1 is None:
                arg1 = wx.LEFT
            if arg2 is None:
                arg2 = ""
            return self.AddPane2(window, arg1, arg2)
        else:
            return self.AddPane1(window, arg1)
        

    def AddPane1(self, window, pane_info):

        # check if the pane has a valid window
        if not window:
            return False

        # check if the pane already exists
        if self.GetPane(pane_info.window).IsOk():
            return False

        if isinstance(window, wx.ToolBar):
            window.SetBestFittingSize()
            
        self._panes.append(pane_info)

        pinfo = self._panes[-1]

        # set the pane window
        pinfo.window = window
        
        # if the pane's name identifier is blank, create a random string
        if len(pinfo.name) == 0 or pinfo.name == "":
            pinfo.name = ("%s%08x%08x%08x")%(pinfo.window.GetName(), time.time(),
                                             time.clock(), len(self._panes))
        
        # set initial proportion (if not already set)
        if pinfo.dock_proportion == 0:
            pinfo.dock_proportion = 100000

        if pinfo.HasCloseButton() and len(pinfo.buttons) == 0:
            button = PaneButton(None)
            button.button_id = PaneInfo.buttonClose
            pinfo.buttons.append(button)
        
        if pinfo.best_size == wx.DefaultSize and pinfo.window:
            pinfo.best_size = pinfo.window.GetClientSize()
            
            if isinstance(pinfo.window, wx.ToolBar):
                # GetClientSize() doesn't get the best size for
                # a toolbar under some newer versions of wxWidgets,
                # so use GetBestSize()
                pinfo.best_size = pinfo.window.GetBestSize()
                        
                # for some reason, wxToolBar::GetBestSize() is returning
                # a size that is a pixel shy of the correct amount.
                # I believe this to be the correct action, until
                # wxToolBar::GetBestSize() is fixed.  Is this assumption
                # correct?
                pinfo.best_size.y = pinfo.best_size.y + 1

                # this is needed for Win2000 to correctly fill toolbar backround
                # it should probably be repeated once system colour change happens
                if wx.Platform == "__WXMSW__" and pinfo.window.UseBgCol():
                    pinfo.window.SetBackgroundColour(self.GetArtProvider().GetColour(AUI_ART_BACKGROUND_COLOUR))

            if pinfo.min_size != wx.DefaultSize:
                if pinfo.best_size.x < pinfo.min_size.x:
                    pinfo.best_size.x = pinfo.min_size.x
                if pinfo.best_size.y < pinfo.min_size.y:
                    pinfo.best_size.y = pinfo.min_size.y

        self._panes[-1] = pinfo
        
        return True


    def AddPane2(self, window, direction, caption):

        pinfo = PaneInfo()
        pinfo.Caption(caption)
        
        if direction == wx.TOP:
            pinfo.Top()
        elif direction == wx.BOTTOM:
            pinfo.Bottom()
        elif direction == wx.LEFT:
            pinfo.Left()
        elif direction == wx.RIGHT:
            pinfo.Right()
        elif direction == wx.CENTER:
            pinfo.CenterPane()
        
        return self.AddPane(window, pinfo)


    def InsertPane(self, window, pane_info, insert_level=AUI_INSERT_PANE):
        """
        InsertPane() is used to insert either a previously unmanaged pane window
        into the frame manager, or to insert a currently managed pane somewhere else.
        InsertPane() will push all panes, rows, or docks aside and insert the window
        into the position specified by insert_location. Because insert_location can
        specify either a pane, dock row, or dock layer, the insert_level parameter is
        used to disambiguate this. The parameter insert_level can take a value of
        AUI_INSERT_PANE, AUI_INSERT_ROW or AUI_INSERT_DOCK.
        """

        # shift the panes around, depending on the insert level
        if insert_level == AUI_INSERT_PANE:
            self._panes = DoInsertPane(self._panes, pane_info.dock_direction,
                                       pane_info.dock_layer, pane_info.dock_row,
                                       pane_info.dock_pos)

        elif insert_level == AUI_INSERT_ROW:
            self._panes = DoInsertDockRow(self._panes, pane_info.dock_direction,
                                          pane_info.dock_layer, pane_info.dock_row)

        elif insert_level == AUI_INSERT_DOCK:
            self._panes = DoInsertDockLayer(self._panes, pane_info.dock_direction,
                                            pane_info.dock_layer)
        
        # if the window already exists, we are basically just moving/inserting the
        # existing window.  If it doesn't exist, we need to add it and insert it
        existing_pane = self.GetPane(window)
        indx = self._panes.index(existing_pane)
        
        if not existing_pane.IsOk():
        
            return self.AddPane(window, pane_info)
        
        else:
        
            if pane_info.IsFloating():
                existing_pane.Float()
                if pane_info.floating_pos != wx.DefaultPosition:
                    existing_pane.FloatingPosition(pane_info.floating_pos)
                if pane_info.floating_size != wx.DefaultSize:
                    existing_pane.FloatingSize(pane_info.floating_size)
            else:
                existing_pane.Direction(pane_info.dock_direction)
                existing_pane.Layer(pane_info.dock_layer)
                existing_pane.Row(pane_info.dock_row)
                existing_pane.Position(pane_info.dock_pos)

            self._panes[indx] = existing_pane                
            
        return True

    
    def DetachPane(self, window):
        """
        DetachPane() tells the FrameManager to stop managing the pane specified
        by window. The window, if in a floated frame, is reparented to the frame
        managed by FrameManager.
        """
        
        for p in self._panes:
            if p.window == window:
                if p.frame:
                    # we have a floating frame which is being detached. We need to
                    # reparent it to m_frame and destroy the floating frame

                    # reduce flicker
                    p.window.SetSize(1,1)
                    p.frame.Show(False)

                    # reparent to self._frame and destroy the pane
                    p.window.Reparent(self._frame)
                    p.frame.SetSizer(None)
                    p.frame.Destroy()
                    p.frame = None

                self._panes.remove(p)
                return True
        
        return False


    def SavePerspective(self):
        """
        SavePerspective() saves all pane information as a single string.
        This string may later be fed into LoadPerspective() to restore
        all pane settings.  This save and load mechanism allows an
        exact pane configuration to be saved and restored at a later time.
        """

        result = "layout1|"
        pane_count = len(self._panes)

        for pane_i in xrange(pane_count):
            pane = self._panes[pane_i]
            result = result + "name=" + EscapeDelimiters(pane.name) + ";"
            result = result + "caption=" + EscapeDelimiters(pane.caption) + ";"
            result = result + "state=%u;"%pane.state
            result = result + "dir=%d;"%pane.dock_direction
            result = result + "layer=%d;"%pane.dock_layer
            result = result + "row=%d;"%pane.dock_row
            result = result + "pos=%d;"%pane.dock_pos
            result = result + "prop=%d;"%pane.dock_proportion
            result = result + "bestw=%d;"%pane.best_size.x
            result = result + "besth=%d;"%pane.best_size.y
            result = result + "minw=%d;"%pane.min_size.x
            result = result + "minh=%d;"%pane.min_size.y
            result = result + "maxw=%d;"%pane.max_size.x
            result = result + "maxh=%d;"%pane.max_size.y
            result = result + "floatx=%d;"%pane.floating_pos.x
            result = result + "floaty=%d;"%pane.floating_pos.y
            result = result + "floatw=%d;"%pane.floating_size.x
            result = result + "floath=%d"%pane.floating_size.y
            result = result + "|"
        
        dock_count = len(self._docks)

        for dock_i in xrange(dock_count):
            dock = self._docks[dock_i]
            result = result + ("dock_size(%d,%d,%d)=%d|")%(dock.dock_direction,
                                                           dock.dock_layer,
                                                           dock.dock_row,
                                                           dock.size)
            
        return result


    def LoadPerspective(self, layout, update=True):
        """
        LoadPerspective() loads a layout which was saved with SavePerspective()
        If the "update" flag parameter is True, the GUI will immediately be updated.
        """

        input = layout
        # check layout string version
        indx = input.index("|")
        part = input[0:indx]
        input = input[indx+1:]
        part = part.strip()

        if part != "layout1":
            return False

        olddocks = self._docks[:]
        oldpanes = self._panes[:]
        
        # mark all panes currently managed as docked and hidden
        pane_count = len(self._panes)
        for pane_i in xrange(pane_count):
            pane = self._panes[pane_i]
            pane.Dock().Hide()
            self._panes[pane_i] = pane

        # clear out the dock array this will be reconstructed
        self._docks = []
        
        # replace escaped characters so we can
        # split up the string easily
        input = input.replace("\\|", "\a")
        input = input.replace("\\", "\b")

        input = input.split("|")    

        for line in input:
            
            if line.startswith("dock_size"):
                
                indx = line.index("=")
                size = int(line[indx+1:])
                indx1 = line.index("(")
                indx2 = line.index(")")
                line2 = line[indx1+1:indx2]
                vals = line2.split(",")
                dir = int(vals[0])
                layer = int(vals[1])
                row = int(vals[2])
                dock = DockInfo()
                dock.dock_direction = dir
                dock.dock_layer = layer
                dock.dock_row = row
                dock.size = size
                
                self._docks.append(dock)
                
            elif line.startswith("name"):

                newline = line.split(";")
                pane = PaneInfo()
                
                for newl in newline:
                    myline = newl.strip()
                    vals = myline.split("=")
                    val_name = vals[0]
                    value = vals[1]
                    if val_name == "name":
                        pane.name = value
                    elif val_name == "caption":
                        pane.caption = value
                    elif val_name == "state":
                        pane.state = int(value)
                    elif val_name == "dir":
                        pane.dock_direction = int(value)
                    elif val_name == "layer":
                        pane.dock_layer = int(value)
                    elif val_name == "row":
                        pane.dock_row = int(value)
                    elif val_name == "pos":
                        pane.dock_pos = int(value)
                    elif val_name == "prop":
                        pane.dock_proportion = int(value)
                    elif val_name == "bestw":
                        pane.best_size.x = int(value)
                    elif val_name == "besth":
                        pane.best_size.y = int(value)
                        pane.best_size = wx.Size(pane.best_size.x, pane.best_size.y)
                    elif val_name == "minw":
                        pane.min_size.x = int(value)
                    elif val_name == "minh":
                        pane.min_size.y = int(value)
                        pane.min_size = wx.Size(pane.min_size.x, pane.min_size.y)
                    elif val_name == "maxw":
                        pane.max_size.x = int(value)
                    elif val_name == "maxh":
                        pane.max_size.y = int(value)
                        pane.max_size = wx.Size(pane.max_size.x, pane.max_size.y)
                    elif val_name == "floatx":
                        pane.floating_pos.x = int(value)
                    elif val_name == "floaty":
                        pane.floating_pos.y = int(value)
                        pane.floating_pos = wx.Point(pane.floating_pos.x, pane.floating_pos.y)
                    elif val_name == "floatw":
                        pane.floating_size.x = int(value)
                    elif val_name == "floath":
                        pane.floating_size.y = int(value)
                        pane.floating_size = wx.Size(pane.floating_size.x, pane.floating_size.y)
                    else: 
                        raise "\nERROR: Bad Perspective String."

                # replace escaped characters so we can
                # split up the string easily
                pane.name = pane.name.replace("\a", "|")
                pane.name = pane.name.replace("\b", ";")
                pane.caption = pane.caption.replace("\a", "|")
                pane.caption = pane.caption.replace("\b", ";")
                
                p = self.GetPane(pane.name)
                if not p.IsOk():
                    # the pane window couldn't be found
                    # in the existing layout
                    return False

                indx = self._panes.index(p)            
                pane.window = p.window
                pane.frame = p.frame
                pane.buttons = p.buttons
                self._panes[indx] = pane

        if update:
            self.Update()

        return True


    def GetPanePositionsAndSizes(self, dock):
        """ Returns all the panes positions and sizes. """
        
        caption_size = self._art.GetMetric(AUI_ART_CAPTION_SIZE)
        pane_border_size = self._art.GetMetric(AUI_ART_PANE_BORDER_SIZE)
        gripper_size = self._art.GetMetric(AUI_ART_GRIPPER_SIZE)

        positions = []
        sizes = []

        action_pane = -1
        pane_count = len(dock.panes)

        # find the pane marked as our action pane
        for pane_i in xrange(pane_count):
            pane = dock.panes[pane_i]
            if pane.state & PaneInfo.actionPane:
                action_pane = pane_i
            
        # set up each panes default position, and
        # determine the size (width or height, depending
        # on the dock's orientation) of each pane
        for pane in dock.panes:
            positions.append(pane.dock_pos)
            size = 0
            
            if pane.HasBorder():
                size  = size + pane_border_size*2
                    
            if dock.IsHorizontal():
                if pane.HasGripper() and not pane.HasGripperTop():
                    size = size + gripper_size
                    
                size = size + pane.best_size.x
                 
            else:
                if pane.HasGripper() and pane.HasGripperTop():
                    size = size + gripper_size

                if pane.HasCaption():
                    size = size + caption_size
                    
                size = size + pane.best_size.y
       
            sizes.append(size)

        # if there is no action pane, just return the default
        # positions (as specified in pane.pane_pos)
        if action_pane == -1:
            return positions, sizes

        offset = 0
        for pane_i in xrange(action_pane-1, -1, -1):
            amount = positions[pane_i+1] - (positions[pane_i] + sizes[pane_i])
            if amount >= 0:
                offset = offset + amount
            else:
                positions[pane_i] -= -amount

            offset = offset + sizes[pane_i]
        
        # if the dock mode is fixed, make sure none of the panes
        # overlap we will bump panes that overlap
        offset = 0
        for pane_i in xrange(action_pane, pane_count):
            amount = positions[pane_i] - offset
            if amount >= 0:
                offset = offset + amount
            else:
                positions[pane_i] += -amount

            offset = offset + sizes[pane_i]

        return positions, sizes
    

    def LayoutAddPane(self, cont, dock, pane, uiparts, spacer_only):
        
        sizer_item = wx.SizerItem()
        caption_size = self._art.GetMetric(AUI_ART_CAPTION_SIZE)
        gripper_size = self._art.GetMetric(AUI_ART_GRIPPER_SIZE)
        pane_border_size = self._art.GetMetric(AUI_ART_PANE_BORDER_SIZE)
        pane_button_size = self._art.GetMetric(AUI_ART_PANE_BUTTON_SIZE)

        # find out the orientation of the item (orientation for panes
        # is the same as the dock's orientation)

        if dock.IsHorizontal():
            orientation = wx.HORIZONTAL
        else:
            orientation = wx.VERTICAL

        # this variable will store the proportion
        # value that the pane will receive
        pane_proportion = pane.dock_proportion

        horz_pane_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vert_pane_sizer = wx.BoxSizer(wx.VERTICAL)

        if pane.HasGripper():
            
            part = DockUIPart()
            if pane.HasGripperTop():
                sizer_item = vert_pane_sizer.Add((1, gripper_size), 0, wx.EXPAND)
            else:
                sizer_item = horz_pane_sizer.Add((gripper_size, 1), 0, wx.EXPAND)

            part.type = DockUIPart.typeGripper
            part.dock = dock
            part.pane = pane
            part.button = None
            part.orientation = orientation
            part.cont_sizer = horz_pane_sizer
            part.sizer_item = sizer_item
            uiparts.append(part)
        
        if pane.HasCaption():
        
            # create the caption sizer
            part = DockUIPart()
            caption_sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer_item = caption_sizer.Add((1, caption_size), 1, wx.EXPAND)
            part.type = DockUIPart.typeCaption
            part.dock = dock
            part.pane = pane
            part.button = None
            part.orientation = orientation
            part.cont_sizer = vert_pane_sizer
            part.sizer_item = sizer_item
            caption_part_idx = len(uiparts)
            uiparts.append(part)

            # add pane buttons to the caption
            for button in pane.buttons:
                sizer_item = caption_sizer.Add((pane_button_size,
                                               caption_size),
                                               0, wx.EXPAND)
                part = DockUIPart()
                part.type = DockUIPart.typePaneButton
                part.dock = dock
                part.pane = pane
                part.button = button
                part.orientation = orientation
                part.cont_sizer = caption_sizer
                part.sizer_item = sizer_item
                uiparts.append(part)
            
            # add the caption sizer
            sizer_item = vert_pane_sizer.Add(caption_sizer, 0, wx.EXPAND)
            uiparts[caption_part_idx].sizer_item = sizer_item
                
        # add the pane window itself
        if spacer_only:
            sizer_item = vert_pane_sizer.Add((1, 1), 1, wx.EXPAND)
        else:
            sizer_item = vert_pane_sizer.Add(pane.window, 1, wx.EXPAND)
            vert_pane_sizer.SetItemMinSize(pane.window, (1, 1))

        part = DockUIPart()        
        part.type = DockUIPart.typePane
        part.dock = dock
        part.pane = pane
        part.button = None
        part.orientation = orientation
        part.cont_sizer = vert_pane_sizer
        part.sizer_item = sizer_item
        uiparts.append(part)

        # determine if the pane should have a minimum size if the pane is
        # non-resizable (fixed) then we must set a minimum size. Alternitavely,
        # if the pane.min_size is set, we must use that value as well
        
        min_size = pane.min_size
        if pane.IsFixed():
            if min_size == wx.DefaultSize:
                min_size = pane.best_size
                pane_proportion = 0
            
        if min_size != wx.DefaultSize:
            vert_pane_sizer.SetItemMinSize(
                len(vert_pane_sizer.GetChildren())-1, (min_size.x, min_size.y))
        
        # add the verticle sizer (caption, pane window) to the
        # horizontal sizer (gripper, verticle sizer)
        horz_pane_sizer.Add(vert_pane_sizer, 1, wx.EXPAND)

        # finally, add the pane sizer to the dock sizer
        if pane.HasBorder():
            # allowing space for the pane's border
            sizer_item = cont.Add(horz_pane_sizer, pane_proportion,
                                  wx.EXPAND | wx.ALL, pane_border_size)
            part = DockUIPart()
            part.type = DockUIPart.typePaneBorder
            part.dock = dock
            part.pane = pane
            part.button = None
            part.orientation = orientation
            part.cont_sizer = cont
            part.sizer_item = sizer_item
            uiparts.append(part)
        else:
            sizer_item = cont.Add(horz_pane_sizer, pane_proportion, wx.EXPAND)
        
        return uiparts
        
        
    def LayoutAddDock(self, cont, dock, uiparts, spacer_only):

        sizer_item = wx.SizerItem()
        part = DockUIPart()

        sash_size = self._art.GetMetric(AUI_ART_SASH_SIZE)
        orientation = (dock.IsHorizontal() and [wx.HORIZONTAL] or [wx.VERTICAL])[0]

        # resizable bottom and right docks have a sash before them
        if not dock.fixed and (dock.dock_direction == AUI_DOCK_BOTTOM or \
                               dock.dock_direction == AUI_DOCK_RIGHT):
        
            sizer_item = cont.Add((sash_size, sash_size), 0, wx.EXPAND)

            part.type = DockUIPart.typeDockSizer
            part.orientation = orientation
            part.dock = dock
            part.pane = None
            part.button = None
            part.cont_sizer = cont
            part.sizer_item = sizer_item
            uiparts.append(part)
        
        # create the sizer for the dock
        dock_sizer = wx.BoxSizer(orientation)

        # add each pane to the dock
        pane_count = len(dock.panes)

        if dock.fixed:
        
            # figure out the real pane positions we will
            # use, without modifying the each pane's pane_pos member
            pane_positions, pane_sizes = self.GetPanePositionsAndSizes(dock)

            offset = 0
            for pane_i in xrange(pane_count):
            
                pane = dock.panes[pane_i]
                pane_pos = pane_positions[pane_i]

                amount = pane_pos - offset
                if amount > 0:
                
                    if dock.IsVertical():
                        sizer_item = dock_sizer.Add((1, amount), 0, wx.EXPAND)
                    else:
                        sizer_item = dock_sizer.Add((amount, 1), 0, wx.EXPAND)

                    part = DockUIPart()
                    part.type = DockUIPart.typeBackground
                    part.dock = dock
                    part.pane = None
                    part.button = None
                    part.orientation = (orientation==wx.HORIZONTAL and \
                                        [wx.VERTICAL] or [wx.HORIZONTAL])[0]
                    part.cont_sizer = dock_sizer
                    part.sizer_item = sizer_item
                    uiparts.append(part)

                    offset = offset + amount
                
                uiparts = self.LayoutAddPane(dock_sizer, dock, pane, uiparts, spacer_only)

                offset = offset + pane_sizes[pane_i]
            
            # at the end add a very small stretchable background area
            sizer_item = dock_sizer.Add((1, 1), 1, wx.EXPAND)
            part = DockUIPart()
            part.type = DockUIPart.typeBackground
            part.dock = dock
            part.pane = None
            part.button = None
            part.orientation = orientation
            part.cont_sizer = dock_sizer
            part.sizer_item = sizer_item
            uiparts.append(part)
        
        else:
        
            for pane_i in xrange(pane_count):
            
                pane = dock.panes[pane_i]

                # if this is not the first pane being added,
                # we need to add a pane sizer
                if pane_i > 0:
                    sizer_item = dock_sizer.Add((sash_size, sash_size), 0, wx.EXPAND)
                    part = DockUIPart()
                    part.type = DockUIPart.typePaneSizer
                    part.dock = dock
                    part.pane = dock.panes[pane_i-1]
                    part.button = None
                    part.orientation = (orientation==wx.HORIZONTAL and \
                                        [wx.VERTICAL] or [wx.HORIZONTAL])[0]
                    part.cont_sizer = dock_sizer
                    part.sizer_item = sizer_item
                    uiparts.append(part)
                
                uiparts = self.LayoutAddPane(dock_sizer, dock, pane, uiparts, spacer_only)
            
        if dock.dock_direction == AUI_DOCK_CENTER:
            sizer_item = cont.Add(dock_sizer, 1, wx.EXPAND)
        else:
            sizer_item = cont.Add(dock_sizer, 0, wx.EXPAND)

        part = DockUIPart()
        part.type = DockUIPart.typeDock
        part.dock = dock
        part.pane = None
        part.button = None
        part.orientation = orientation
        part.cont_sizer = cont
        part.sizer_item = sizer_item
        uiparts.append(part)

        if dock.IsHorizontal():
            cont.SetItemMinSize(dock_sizer, (0, dock.size))
        else:
            cont.SetItemMinSize(dock_sizer, (dock.size, 0))

        #  top and left docks have a sash after them
        if not dock.fixed and (dock.dock_direction == AUI_DOCK_TOP or \
                               dock.dock_direction == AUI_DOCK_LEFT):
        
            sizer_item = cont.Add((sash_size, sash_size), 0, wx.EXPAND)

            part = DockUIPart()
            part.type = DockUIPart.typeDockSizer
            part.dock = dock
            part.pane = None
            part.button = None
            part.orientation = orientation
            part.cont_sizer = cont
            part.sizer_item = sizer_item
            uiparts.append(part)
        
        return uiparts
    

    def LayoutAll(self, panes, docks, uiparts, spacer_only=False, oncheck=True):

        container = wx.BoxSizer(wx.VERTICAL)

        pane_border_size = self._art.GetMetric(AUI_ART_PANE_BORDER_SIZE)
        caption_size = self._art.GetMetric(AUI_ART_CAPTION_SIZE)
        cli_size = self._frame.GetClientSize()
        
        # empty all docks out
        for ii in xrange(len(docks)):
            docks[ii].panes = []

        dock_count = len(docks)
        
        # iterate through all known panes, filing each
        # of them into the appropriate dock. If the
        # pane does not exist in the dock, add it
        for p in panes:

            # find any docks in this layer
            arr = FindDocks(docks, p.dock_direction, p.dock_layer, p.dock_row)

            if len(arr) > 0:
                dock = arr[0]
            else:
                # dock was not found, so we need to create a new one
                d = DockInfo()
                d.dock_direction = p.dock_direction
                d.dock_layer = p.dock_layer
                d.dock_row = p.dock_row
                docks.append(d)
                dock = docks[-1]

            if p.IsDocked() and p.IsShown():
                # remove the pane from any existing docks except this one
                docks = RemovePaneFromDocks(docks, p, dock)

                # pane needs to be added to the dock,
                # if it doesn't already exist 
                if not FindPaneInDock(dock, p.window):
                    dock.panes.append(p)
            else:
                # remove the pane from any existing docks
                docks = RemovePaneFromDocks(docks, p)
            
        # remove any empty docks
        for ii in xrange(len(docks)-1, -1, -1):
            if len(docks[ii].panes) == 0:
                docks.pop(ii)

        dock_count = len(docks)        
        # configure the docks further
        for ii in xrange(len(docks)):
            dock = docks[ii]
            dock_pane_count = len(dock.panes)
            
            # sort the dock pane array by the pane's
            # dock position (dock_pos), in ascending order
            dock.panes.sort(PaneSortFunc)

            # for newly created docks, set up their initial size
            if dock.size == 0:
                size = 0
                for jj in xrange(dock_pane_count):
                    pane = dock.panes[jj]
                    pane_size = pane.best_size
                    if pane_size == wx.DefaultSize:
                        pane_size = pane.min_size
                    if pane_size == wx.DefaultSize:
                        pane_size = pane.window.GetSize()
                    
                    if dock.IsHorizontal():
                        size = max(pane_size.y, size)
                    else:
                        size = max(pane_size.x, size)
                
                # add space for the border (two times), but only
                # if at least one pane inside the dock has a pane border
                for jj in xrange(dock_pane_count):
                    if dock.panes[jj].HasBorder():
                        size = size + pane_border_size*2
                        break
                    
                # if pane is on the top or bottom, add the caption height,
                # but only if at least one pane inside the dock has a caption
                if dock.IsHorizontal():
                    for jj in xrange(dock_pane_count):
                        if dock.panes[jj].HasCaption():
                            size = size + caption_size
                            break
                    
                # new dock's size may not be more than 1/3 of the frame size
                if dock.IsHorizontal():
                    size = min(size, cli_size.y/3)
                else:
                    size = min(size, cli_size.x/3)

                if size < 10:
                    size = 10
                    
                dock.size = size

            # determine the dock's minimum size
            plus_border = False
            plus_caption = False
            dock_min_size = 0
            for jj in xrange(dock_pane_count):
                pane = dock.panes[jj]
                if pane.min_size != wx.DefaultSize:
                    if pane.HasBorder():
                        plus_border = True
                    if pane.HasCaption():
                        plus_caption = True
                    if dock.IsHorizontal():
                        if pane.min_size.y > dock_min_size:
                            dock_min_size = pane.min_size.y
                    else:
                        if pane.min_size.x > dock_min_size:
                            dock_min_size = pane.min_size.x
                    
            if plus_border:
                dock_min_size = dock_min_size + pane_border_size*2
            if plus_caption and dock.IsHorizontal():
                dock_min_size = dock_min_size + caption_size
               
            dock.min_size = dock_min_size
            
            # if the pane's current size is less than it's
            # minimum, increase the dock's size to it's minimum
            if dock.size < dock.min_size:
                dock.size = dock.min_size

            # determine the dock's mode (fixed or proportional)
            # determine whether the dock has only toolbars
            action_pane_marked = False
            dock.fixed = True
            dock.toolbar = True
            for jj in xrange(dock_pane_count):
                pane = dock.panes[jj]
                if not pane.IsFixed():
                    dock.fixed = False
                if not pane.IsToolbar():
                    dock.toolbar = False
                if pane.state & PaneInfo.actionPane:
                    action_pane_marked = True

            # if the dock mode is proportional and not fixed-pixel,
            # reassign the dock_pos to the sequential 0, 1, 2, 3
            # e.g. remove gaps like 1, 2, 30, 500
            if not dock.fixed:
                for jj in xrange(dock_pane_count):
                    pane = dock.panes[jj]
                    pane.dock_pos = jj
                    dock.panes[jj] = pane
                
            # if the dock mode is fixed, and none of the panes
            # are being moved right now, make sure the panes
            # do not overlap each other.  If they do, we will
            # adjust the panes' positions
            if dock.fixed and not action_pane_marked:
                pane_positions, pane_sizes = self.GetPanePositionsAndSizes(dock)
                offset = 0
                for jj in xrange(dock_pane_count):
                    pane = dock.panes[jj]
                    pane.dock_pos = pane_positions[jj]
                    amount = pane.dock_pos - offset
                    if amount >= 0:
                        offset = offset + amount
                    else:
                        pane.dock_pos += -amount

                    offset = offset + pane_sizes[jj]
                    dock.panes[jj] = pane

            if oncheck:
                self._docks[ii] = dock                    
        
        # discover the maximum dock layer
        max_layer = 0
        
        for ii in xrange(dock_count):
            max_layer = max(max_layer, docks[ii].dock_layer)

        # clear out uiparts
        uiparts = []

        # create a bunch of box sizers,
        # from the innermost level outwards.
        cont = None
        middle = None

        if oncheck:
            docks = self._docks
        
        for layer in xrange(max_layer+1):
            # find any docks in this layer
            arr = FindDocks(docks, -1, layer, -1)
            # if there aren't any, skip to the next layer
            if len(arr) == 0:
                continue

            old_cont = cont

            # create a container which will hold this layer's
            # docks (top, bottom, left, right)
            cont = wx.BoxSizer(wx.VERTICAL)

            # find any top docks in this layer
            arr = FindDocks(docks, AUI_DOCK_TOP, layer, -1, arr)
            arr = RenumberDockRows(arr)
            if len(arr) > 0:
                for row in xrange(len(arr)):
                    uiparts = self.LayoutAddDock(cont, arr[row], uiparts, spacer_only)
            
            # fill out the middle layer (which consists
            # of left docks, content area and right docks)
            
            middle = wx.BoxSizer(wx.HORIZONTAL)

            # find any left docks in this layer
            arr = FindDocks(docks, AUI_DOCK_LEFT, layer, -1, arr)
            arr = RenumberDockRows(arr)
            if len(arr) > 0:
                for row in xrange(len(arr)):
                    uiparts = self.LayoutAddDock(middle, arr[row], uiparts, spacer_only)
            
            # add content dock (or previous layer's sizer
            # to the middle
            if not old_cont:
                # find any center docks
                arr = FindDocks(docks, AUI_DOCK_CENTER, -1, -1, arr)
                if len(arr) > 0:
                    for row in xrange(len(arr)):
                       uiparts = self.LayoutAddDock(middle, arr[row], uiparts, spacer_only)
                else:                
                    # there are no center docks, add a background area
                    sizer_item = middle.Add((1, 1), 1, wx.EXPAND)
                    part = DockUIPart()
                    part.type = DockUIPart.typeBackground
                    part.pane = None
                    part.dock = None
                    part.button = None
                    part.cont_sizer = middle
                    part.sizer_item = sizer_item
                    uiparts.append(part)
            else:
                middle.Add(old_cont, 1, wx.EXPAND)
            
            # find any right docks in this layer
            arr = FindDocks(docks, AUI_DOCK_RIGHT, layer, -1, arr)
            arr = RenumberDockRows(arr)
            if len(arr) > 0:
                for row in xrange(len(arr)-1, -1, -1):
                    uiparts = self.LayoutAddDock(middle, arr[row], uiparts, spacer_only)
            
            cont.Add(middle, 1, wx.EXPAND)

            # find any bottom docks in this layer
            arr = FindDocks(docks, AUI_DOCK_BOTTOM, layer, -1, arr)
            arr = RenumberDockRows(arr)
            if len(arr) > 0:
                for row in xrange(len(arr)-1, -1, -1):
                    uiparts = self.LayoutAddDock(cont, arr[row], uiparts, spacer_only)

        if not cont:
            # no sizer available, because there are no docks,
            # therefore we will create a simple background area
            cont = wx.BoxSizer(wx.VERTICAL)
            sizer_item = cont.Add((1, 1), 1, wx.EXPAND)
            part = DockUIPart()
            part.type = DockUIPart.typeBackground
            part.pane = None
            part.dock = None
            part.button = None
            part.cont_sizer = middle
            part.sizer_item = sizer_item
            uiparts.append(part)

        if oncheck:
            self._uiparts = uiparts
            self._docks = docks

        container.Add(cont, 1, wx.EXPAND)

        if oncheck:
            return container
        else:
            return container, panes, docks, uiparts


    def Update(self):
        """
        Update() updates the layout.  Whenever changes are made to
        one or more panes, this function should be called.  It is the
        external entry point for running the layout engine.
        """
    
        pane_count = len(self._panes)
        # delete old sizer first
        self._frame.SetSizer(None)

        # destroy floating panes which have been
        # redocked or are becoming non-floating
        for ii in xrange(pane_count):
            p = self._panes[ii]
            if not p.IsFloating() and p.frame:
                # because the pane is no longer in a floating, we need to
                # reparent it to self._frame and destroy the floating frame
                # reduce flicker
                p.window.SetSize((1, 1))
                p.frame.Show(False)
                           
                # reparent to self._frame and destroy the pane
                p.window.Reparent(self._frame)
                p.frame.SetSizer(None)
                p.frame.Destroy()
                p.frame = None

            self._panes[ii] = p
            
        # create a layout for all of the panes
        sizer = self.LayoutAll(self._panes, self._docks, self._uiparts, False)

        # hide or show panes as necessary,
        # and float panes as necessary
        
        pane_count = len(self._panes)
        
        for ii in xrange(pane_count):
            p = self._panes[ii]
            if p.IsFloating():
                if p.frame == None:
                    # we need to create a frame for this
                    # pane, which has recently been floated
                    resizeborder = 1
                    if p.IsFixed():
                        resizeborder = 0
                        
                    frame = FloatingPane(self._frame, self, -1, "", p.floating_pos,
                                         p.floating_size, resizeborder=resizeborder)
                                    
                    # on MSW, if the owner desires transparent dragging, and
                    # the dragging is happening right now, then the floating
                    # window should have this style by default                  
                    
                    if self._action == actionDragFloatingPane and self.UseTransparentDrag():
                        self.MakeWindowTransparent(frame, 150)
                    
                    frame.SetPaneWindow(p)
                    p.frame = frame
                    if p.IsShown():
                        frame.Show()
                else:
                
                    # frame already exists, make sure it's position
                    # and size reflect the information in PaneInfo
                    if p.frame.GetPosition() != p.floating_pos:
                        p.frame.SetDimensions(p.floating_pos.x, p.floating_pos.y,
                                        -1, -1, wx.SIZE_USE_EXISTING)
                    p.frame.Show(p.IsShown())
            else:
            
                p.window.Show(p.IsShown())

            # if "active panes" are no longer allowed, clear
            # any optionActive values from the pane states
            if self._flags & AUI_MGR_ALLOW_ACTIVE_PANE == 0:
                p.state &= ~PaneInfo.optionActive

            self._panes[ii] = p


        old_pane_rects = []
        
        for ii in xrange(pane_count):
            r = wx.Rect()
            p = self._panes[ii]

            if p.window and p.IsShown() and p.IsDocked():
                r = p.rect

            old_pane_rects.append(r)    
            
        # apply the new sizer
        self._frame.SetSizer(sizer)
        self._frame.SetAutoLayout(False)
        self.DoFrameLayout()
        
        # now that the frame layout is done, we need to check
        # the new pane rectangles against the old rectangles that
        # we saved a few lines above here.  If the rectangles have
        # changed, the corresponding panes must also be updated
        for ii in xrange(pane_count):
            p = self._panes[ii]
            if p.window and p.IsShown() and p.IsDocked():
                if p.rect != old_pane_rects[ii]:
                    p.window.Refresh()
                    p.window.Update()
        
        self.Repaint()

        
    def DoFrameLayout(self):
        """
        DoFrameLayout() is an internal function which invokes wxSizer.Layout
        on the frame's main sizer, then measures all the various UI items
        and updates their internal rectangles.  This should always be called
        instead of calling self._frame.Layout() directly
        """

        self._frame.Layout()
        
        for ii in xrange(len(self._uiparts)):
            part = self._uiparts[ii]
            
            # get the rectangle of the UI part
            # originally, this code looked like this:
            #    part.rect = wx.Rect(part.sizer_item.GetPosition(),
            #                       part.sizer_item.GetSize())
            # this worked quite well, with one exception: the mdi
            # client window had a "deferred" size variable 
            # that returned the wrong size.  It looks like
            # a bug in wx, because the former size of the window
            # was being returned.  So, we will retrieve the part's
            # rectangle via other means

            part.rect = part.sizer_item.GetRect()
            flag = part.sizer_item.GetFlag()
            border = part.sizer_item.GetBorder()
            
            if flag & wx.TOP:
                part.rect.y -= border
                part.rect.height += border
            if flag & wx.LEFT:
                part.rect.x -= border
                part.rect.width += border
            if flag & wx.BOTTOM:
                part.rect.height += border
            if flag & wx.RIGHT:
                part.rect.width += border

            if part.type == DockUIPart.typeDock:
                part.dock.rect = part.rect
            if part.type == DockUIPart.typePane:
                part.pane.rect = part.rect

            self._uiparts[ii] = part


    def GetPanePart(self, wnd):
        """
        GetPanePart() looks up the pane border UI part of the
        pane specified.  This allows the caller to get the exact rectangle
        of the pane in question, including decorations like caption and border.
        """

        for ii in xrange(len(self._uiparts)):
            part = self._uiparts[ii]
            if part.type == DockUIPart.typePaneBorder and \
               part.pane and part.pane.window == wnd:
                return part

        for ii in xrange(len(self._uiparts)):
            part = self._uiparts[ii]
            if part.type == DockUIPart.typePane and \
               part.pane and part.pane.window == wnd:
                return part
    
        return None


    def GetDockPixelOffset(self, test):
        """
        GetDockPixelOffset() is an internal function which returns
        a dock's offset in pixels from the left side of the window
        (for horizontal docks) or from the top of the window (for
        vertical docks).  This value is necessary for calculating
        fixel-pane/toolbar offsets when they are dragged.
        """

        # the only way to accurately calculate the dock's
        # offset is to actually run a theoretical layout

        docks, panes = CopyDocksAndPanes2(self._docks, self._panes)
        panes.append(test)

        sizer, panes, docks, uiparts = self.LayoutAll(panes, docks, [], True, False)
        client_size = self._frame.GetClientSize()
        sizer.SetDimension(0, 0, client_size.x, client_size.y)
        sizer.Layout()

        for ii in xrange(len(uiparts)):
            part = uiparts[ii]
            pos = part.sizer_item.GetPosition()
            size = part.sizer_item.GetSize()
            part.rect = wx.Rect(pos[0], pos[1], size[0], size[1])
            if part.type == DockUIPart.typeDock:
                part.dock.rect = part.rect

        sizer.Destroy()

        for ii in xrange(len(docks)):
            dock = docks[ii]
            if test.dock_direction == dock.dock_direction and \
               test.dock_layer == dock.dock_layer and  \
               test.dock_row == dock.dock_row:
            
                if dock.IsVertical():
                    return dock.rect.y
                else:
                    return dock.rect.x
            
        return 0


    def ProcessDockResult(self, target, new_pos):
        """
        ProcessDockResult() is a utility function used by DoDrop() - it checks
        if a dock operation is allowed, the new dock position is copied into
        the target info.  If the operation was allowed, the function returns True.
        """

        allowed = False
        if new_pos.dock_direction == AUI_DOCK_TOP:
            allowed = target.IsTopDockable()
        elif new_pos.dock_direction == AUI_DOCK_BOTTOM:
            allowed = target.IsBottomDockable()
        elif new_pos.dock_direction == AUI_DOCK_LEFT:
            allowed = target.IsLeftDockable()
        elif new_pos.dock_direction == AUI_DOCK_RIGHT:
            allowed = target.IsRightDockable()
        
        if allowed:
            target = new_pos

        return allowed, target


    def DoDrop(self, docks, panes, target, pt, offset=wx.Point(0,0)):
        """
        DoDrop() is an important function.  It basically takes a mouse position,
        and determines where the panes new position would be.  If the pane is to be
        dropped, it performs the drop operation using the specified dock and pane
        arrays.  By specifying copy dock and pane arrays when calling, a "what-if"
        scenario can be performed, giving precise coordinates for drop hints.
        """

        cli_size = self._frame.GetClientSize()

        drop = PaneInfo()
        drop.name = target.name
        drop.caption = target.caption
        drop.window = target.window
        drop.frame = target.frame
        drop.state = target.state
        drop.dock_direction = target.dock_direction
        drop.dock_layer = target.dock_layer
        drop.dock_row = target.dock_row
        drop.dock_pos = target.dock_pos
        drop.best_size = target.best_size
        drop.min_size = target.min_size
        drop.max_size = target.max_size
        drop.floating_pos = target.floating_pos
        drop.floating_size = target.floating_size
        drop.dock_proportion = target.dock_proportion
        drop.buttons = target.buttons
        drop.rect = target.rect

        # The result should always be shown
        drop.Show()

        # Check to see if the pane has been dragged outside of the window
        # (or near to the outside of the window), if so, dock it along the edge

        layer_insert_offset = auiLayerInsertOffset
        
        if target.IsToolbar():
            layer_insert_offset = 0

        if pt.x < layer_insert_offset and \
           pt.x > layer_insert_offset-auiLayerInsertPixels:
            new_layer = max(max(GetMaxLayer(docks, AUI_DOCK_LEFT),
                                GetMaxLayer(docks, AUI_DOCK_BOTTOM)), 
                            GetMaxLayer(docks, AUI_DOCK_TOP)) + 1
            
            drop.Dock().Left().Layer(new_layer).Row(0). \
                 Position(pt.y - self.GetDockPixelOffset(drop) - offset.y)

            return self.ProcessDockResult(target, drop)
        
        elif pt.y < layer_insert_offset and \
              pt.y > layer_insert_offset-auiLayerInsertPixels:
            new_layer = max(max(GetMaxLayer(docks, AUI_DOCK_TOP),
                                GetMaxLayer(docks, AUI_DOCK_LEFT)),
                            GetMaxLayer(docks, AUI_DOCK_RIGHT)) + 1
            
            drop.Dock().Top().Layer(new_layer).Row(0). \
                 Position(pt.x - self.GetDockPixelOffset(drop) - offset.x)
            
            return self.ProcessDockResult(target, drop)
        
        elif pt.x >= cli_size.x - layer_insert_offset and \
              pt.x < cli_size.x - layer_insert_offset + auiLayerInsertPixels:
        
            new_layer = max(max(GetMaxLayer(docks, AUI_DOCK_RIGHT),
                                GetMaxLayer(docks, AUI_DOCK_TOP)),
                            GetMaxLayer(docks, AUI_DOCK_BOTTOM)) + 1
            
            drop.Dock().Right().Layer(new_layer).Row(0). \
                 Position(pt.y - self.GetDockPixelOffset(drop) - offset.y)
            
            return self.ProcessDockResult(target, drop)
        
        elif pt.y >= cli_size.y - layer_insert_offset and \
             pt.y < cli_size.y - layer_insert_offset + auiLayerInsertPixels:
        
            new_layer = max(max(GetMaxLayer(docks, AUI_DOCK_BOTTOM),
                                GetMaxLayer(docks, AUI_DOCK_LEFT)),
                            GetMaxLayer(docks, AUI_DOCK_RIGHT)) + 1
            
            drop.Dock().Bottom().Layer(new_layer).Row(0). \
                 Position(pt.x - self.GetDockPixelOffset(drop) - offset.x)
            
            return self.ProcessDockResult(target, drop)
        
        part = self.HitTest(pt.x, pt.y)

        if drop.IsToolbar():
            if not part or not part.dock:
                return False, target
            
            # calculate the offset from where the dock begins
            # to the point where the user dropped the pane
            dock_drop_offset = 0
            if part.dock.IsHorizontal():
                dock_drop_offset = pt.x - part.dock.rect.x - offset.x
            else:
                dock_drop_offset = pt.y - part.dock.rect.y - offset.y

            # toolbars may only be moved in and to fixed-pane docks,
            # otherwise we will try to float the pane.  Also, the pane
            # should float if being dragged over center pane windows
            if not part.dock.fixed or part.dock.dock_direction == AUI_DOCK_CENTER:
                if (self._flags & AUI_MGR_ALLOW_FLOATING) and (drop.IsFloatable() or (\
                    part.dock.dock_direction != AUI_DOCK_CENTER and \
                    part.dock.dock_direction != AUI_DOCK_NONE)):

                    drop.Float()
                    
                return self.ProcessDockResult(target, drop)
            
            drop.Dock(). \
                 Direction(part.dock.dock_direction). \
                 Layer(part.dock.dock_layer). \
                 Row(part.dock.dock_row). \
                 Position(dock_drop_offset)

            if pt.y < part.dock.rect.y + 2 and len(part.dock.panes) > 1:
                row = drop.dock_row
                panes = DoInsertDockRow(panes, part.dock.dock_direction,
                                        part.dock.dock_layer,
                                        part.dock.dock_row)
                drop.dock_row = row            
                
            if pt.y > part.dock.rect.y + part.dock.rect.height - 2 and \
               len(part.dock.panes) > 1:
                panes = DoInsertDockRow(panes, part.dock.dock_direction,
                                        part.dock.dock_layer,
                                        part.dock.dock_row+1)
                drop.dock_row = part.dock.dock_row + 1
                
            return self.ProcessDockResult(target, drop)
        
        if not part:
            return False, target

        if part.type == DockUIPart.typePaneBorder or \
            part.type == DockUIPart.typeCaption or \
            part.type == DockUIPart.typeGripper or \
            part.type == DockUIPart.typePaneButton or \
            part.type == DockUIPart.typePane or \
            part.type == DockUIPart.typePaneSizer or \
            part.type == DockUIPart.typeDockSizer or \
            part.type == DockUIPart.typeBackground:
        
            if part.type == DockUIPart.typeDockSizer:
                if len(part.dock.panes) != 1:
                    return False, target
                
                part = self.GetPanePart(part.dock.panes[0].window)
                
                if not part:
                    return False, target

            # If a normal frame is being dragged over a toolbar, insert it
            # along the edge under the toolbar, but over all other panes.
            # (this could be done much better, but somehow factoring this
            # calculation with the one at the beginning of this function)
            if part.dock and (hasattr(part.dock, "toolbar") and part.dock.toolbar):
                layer = 0

                if part.dock.dock_direction == AUI_DOCK_LEFT:
                    layer = max(max(GetMaxLayer(docks, AUI_DOCK_LEFT),
                                    GetMaxLayer(docks, AUI_DOCK_BOTTOM)),
                                GetMaxLayer(docks, AUI_DOCK_TOP))
                elif part.dock.dock_direction == AUI_DOCK_TOP:
                    layer = max(max(GetMaxLayer(docks, AUI_DOCK_TOP),
                                    GetMaxLayer(docks, AUI_DOCK_LEFT)),
                                GetMaxLayer(docks, AUI_DOCK_RIGHT))
                elif part.dock.dock_direction == AUI_DOCK_RIGHT:
                    layer = max(max(GetMaxLayer(docks, AUI_DOCK_RIGHT),
                                    GetMaxLayer(docks, AUI_DOCK_TOP)),
                                GetMaxLayer(docks, AUI_DOCK_BOTTOM))
                elif part.dock.dock_direction == AUI_DOCK_BOTTOM:
                    layer = max(max(GetMaxLayer(docks, AUI_DOCK_BOTTOM),
                                    GetMaxLayer(docks, AUI_DOCK_LEFT)),
                                GetMaxLayer(docks, AUI_DOCK_RIGHT))                

                panes = DoInsertDockRow(panes, part.dock.dock_direction,
                                        layer, 0)
                drop.Dock(). \
                     Direction(part.dock.dock_direction). \
                     Layer(layer).Row(0).Position(0)

                return self.ProcessDockResult(target, drop)
            
            if not part.pane:
                return False, target

            part = self.GetPanePart(part.pane.window)
            if not part:
                return False, target
                
            insert_dock_row = False
            insert_row = part.pane.dock_row
            insert_dir = part.pane.dock_direction
            insert_layer = part.pane.dock_layer
            
            if part.pane.dock_direction == AUI_DOCK_TOP:
                if pt.y >= part.rect.y and \
                   pt.y < part.rect.y+auiInsertRowPixels:
                    insert_dock_row = True

            elif part.pane.dock_direction == AUI_DOCK_BOTTOM:
                if pt.y > part.rect.y+part.rect.height-auiInsertRowPixels and \
                   pt.y <= part.rect.y + part.rect.height:
                    insert_dock_row = True

            elif part.pane.dock_direction == AUI_DOCK_LEFT:
                if pt.x >= part.rect.x and \
                   pt.x < part.rect.x+auiInsertRowPixels:
                    insert_dock_row = True

            elif part.pane.dock_direction == AUI_DOCK_RIGHT:
                if pt.x > part.rect.x+part.rect.width-auiInsertRowPixels and \
                   pt.x <= part.rect.x+part.rect.width:
                    insert_dock_row = True

            elif part.pane.dock_direction == AUI_DOCK_CENTER:
                # "new row pixels" will be set to the default, but
                # must never exceed 20% of the window size
                new_row_pixels_x = auiNewRowPixels
                new_row_pixels_y = auiNewRowPixels

                if new_row_pixels_x > part.rect.width*20/100:
                    new_row_pixels_x = part.rect.width*20/100

                if new_row_pixels_y > part.rect.height*20/100:
                    new_row_pixels_y = part.rect.height*20/100

                    # determine if the mouse pointer is in a location that
                    # will cause a new row to be inserted.  The hot spot positions
                    # are along the borders of the center pane

                    insert_layer = 0
                    insert_dock_row = True
                                        
                    if pt.x >= part.rect.x and \
                       pt.x < part.rect.x+new_row_pixels_x:
                        insert_dir = AUI_DOCK_LEFT
                    elif pt.y >= part.rect.y and \
                         pt.y < part.rect.y+new_row_pixels_y:
                        insert_dir = AUI_DOCK_TOP
                    elif pt.x >= part.rect.x + part.rect.width-new_row_pixels_x and \
                         pt.x < part.rect.x + part.rect.width:
                        insert_dir = AUI_DOCK_RIGHT
                    elif pt.y >= part.rect.y+ part.rect.height-new_row_pixels_y and \
                         pt.y < part.rect.y + part.rect.height:
                        insert_dir = AUI_DOCK_BOTTOM
                    else:
                        return False, target
                    
                    insert_row = GetMaxRow(panes, insert_dir, insert_layer) + 1

            if insert_dock_row:
             
                panes = DoInsertDockRow(panes, insert_dir, insert_layer,
                                        insert_row)
                drop.Dock().Direction(insert_dir). \
                            Layer(insert_layer). \
                            Row(insert_row). \
                            Position(0)

                return self.ProcessDockResult(target, drop)
            
            # determine the mouse offset and the pane size, both in the
            # direction of the dock itself, and perpendicular to the dock
            
            if part.orientation == wx.VERTICAL:
            
                offset = pt.y - part.rect.y
                size = part.rect.GetHeight() 
            
            else:
            
                offset = pt.x - part.rect.x
                size = part.rect.GetWidth()
            
            drop_position = part.pane.dock_pos
            
            # if we are in the top/left part of the pane,
            # insert the pane before the pane being hovered over
            if offset <= size/2:
            
                drop_position = part.pane.dock_pos
                panes = DoInsertPane(panes,
                                     part.pane.dock_direction,
                                     part.pane.dock_layer,
                                     part.pane.dock_row,
                                     part.pane.dock_pos)
            
            # if we are in the bottom/right part of the pane,
            # insert the pane before the pane being hovered over
            if offset > size/2:
            
                drop_position = part.pane.dock_pos+1
                panes = DoInsertPane(panes,
                                     part.pane.dock_direction,
                                     part.pane.dock_layer,
                                     part.pane.dock_row,
                                     part.pane.dock_pos+1)

            drop.Dock(). \
                 Direction(part.dock.dock_direction). \
                 Layer(part.dock.dock_layer). \
                 Row(part.dock.dock_row). \
                 Position(drop_position)
                        
            return self.ProcessDockResult(target, drop)
        
        return False, target


    def UseTransparentHint(self):
        return (self._flags & AUI_MGR_TRANSPARENT_HINT) and self.CanMakeWindowsTransparent()

    def OnHintFadeTimer(self, event):
        #sanity check
        if not self.UseTransparentHint():
            return
            
        if not self._hint_wnd or self._hint_fadeamt >= 50:
            self._hint_fadetimer.Stop()
            return
        
        self._hint_fadeamt = self._hint_fadeamt + 5
        self.MakeWindowTransparent(self._hint_wnd, self._hint_fadeamt)


    def ShowHint(self, rect):
        self._hintshown = True
        if self.UseTransparentHint():
            if wx.Platform == "__WXMSW__":                    
                if self._last_hint == rect:
                    return
                self._last_hint = rect
                
                initial_fade = 50
                
                if self._flags & AUI_MGR_TRANSPARENT_HINT_FADE:
                    initial_fade = 0
                    
                if self._hint_wnd == None:
                
                    pt = rect.GetPosition()
                    size = rect.GetSize()
                    self._hint_wnd = wx.Frame(self._frame, -1, "", pt, size,
                                              wx.FRAME_TOOL_WINDOW |
                                              wx.FRAME_FLOAT_ON_PARENT |
                                              wx.FRAME_NO_TASKBAR |
                                              wx.NO_BORDER)

                    self.MakeWindowTransparent(self._hint_wnd, initial_fade)
                    self._hint_wnd.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION))
                    self._hint_wnd.Show()

                    # if we are dragging a floating pane, set the focus
                    
                    # back to that floating pane (otherwise it becomes unfocused)
                    
                    if self._action == actionDragFloatingPane and self._action_window:
                        self._action_window.SetFocus()
                
                else:
                
                    pt = rect.GetPosition()
                    size = rect.GetSize()
                    self.MakeWindowTransparent(self._hint_wnd, initial_fade)
                    self._hint_wnd.SetDimensions(pt.x, pt.y, rect.width, rect.height)
                
                if self._flags & AUI_MGR_TRANSPARENT_HINT_FADE:
                    # start fade in timer
                    self._hint_fadeamt = 0
                    self._hint_fadetimer.SetOwner(self, 101)
                    self._hint_fadetimer.Start(5)
                return
            elif wx.Platform == "__WXMAC__":
                if self._last_hint == rect:
                    return  #same rect, already shown, no-op
                if self._flags & AUI_MGR_TRANSPARENT_HINT_FADE:
                    initial_fade = 0
                else:
                    initial_fade = 80
   
                if not self._hint_wnd:
                    self._hint_wnd = wx.MiniFrame(self._frame,
                        style=wx.FRAME_FLOAT_ON_PARENT|wx.FRAME_TOOL_WINDOW
                        |wx.CAPTION#|wx.FRAME_SHAPED
                        #without wxCAPTION + wx.FRAME_TOOL_WINDOW, the hint window
                        #gets focus & dims the main frames toolbar, which is both wrong
                        #and distracting.
                        #wx.CAPTION + wx.FRAME_TOOL_WINDOW cures the focus problem,
                        #but then it draws the caption. Adding wx.FRAME_SHAPED takes
                        #care of that, but then SetRect doesn't work to size - need to 
                        #create a bitmap or mask or something.
                        )
                    #can't set the background of a wx.Frame in OSX
                    p = wx.Panel(self._hint_wnd)
                    
                    #the caption color is a light silver thats really hard to see
                    #especially transparent. See if theres some other system
                    #setting that is more appropriate, or just extend the art provider
                    #to cover this
                    #p.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION))
                    p.SetBackgroundColour(wx.BLUE)
                    
                self.MakeWindowTransparent(self._hint_wnd, initial_fade)
                self._hint_wnd.SetRect(rect)
                self._hint_wnd.Show()
                
                if self._action == actionDragFloatingPane and self._action_window:
                   self._action_window.SetFocus()

                if self._flags & AUI_MGR_TRANSPARENT_HINT_FADE:
                    # start fade in timer
                    self._hint_fadeamt = 0
                    self._hint_fadetimer.SetOwner(self, 101)
                    self._hint_fadetimer.Start(5)
                return

            
        if self._last_hint != rect:
            # remove the last hint rectangle
            self._last_hint = rect
            self._frame.Refresh()
            self._frame.Update()


        
        screendc = wx.ScreenDC()
        clip = wx.Region(1, 1, 10000, 10000)

        # clip all floating windows, so we don't draw over them
        for pane in self._panes:
            if pane.IsFloating() and pane.frame.IsShown():
                recta = pane.frame.GetRect()
                if wx.Platform == "__WXGTK__":
                    # wxGTK returns the client size, not the whole frame size
                    width, height = pane.frame.ClientToScreen((0,0)) - pane.frame.GetPosition()
                    recta.width = recta.width + width
                    recta.height = recta.height + height
                    recta.Inflate(5, 5)
                    #endif

                clip.SubtractRect(recta)

        screendc.SetClippingRegionAsRegion(clip)

        screendc.SetBrush(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION)))
        screendc.SetPen(wx.TRANSPARENT_PEN)

        screendc.DrawRectangle(rect.x, rect.y, 5, rect.height)
        screendc.DrawRectangle(rect.x+5, rect.y, rect.width-10, 5)
        screendc.DrawRectangle(rect.x+rect.width-5, rect.y, 5, rect.height)
        screendc.DrawRectangle(rect.x+5, rect.y+rect.height-5, rect.width-10, 5)  


    def HideHint(self):

        self._hintshown = False
        
        # hides a transparent window hint (currently wxMSW only)
        if self.UseTransparentHint():
            if self._hint_wnd:
                self._hint_fadetimer.Stop()
                #self._hint_wnd.Destroy()
                self.MakeWindowTransparent(self._hint_wnd, 0)
                self._last_hint = wx.Rect()
                
            return
        
        # hides a painted hint by redrawing the frame window
        if not self._last_hint.IsEmpty():
            self._frame.Refresh()
            self._frame.Update()
            self._last_hint = wx.Rect()
        

    def DrawHintRect(self, pane_window, pt, offset):
        """
        DrawHintRect() draws a drop hint rectangle. First calls DoDrop() to
        determine the exact position the pane would be at were if dropped.  If
        the pame would indeed become docked at the specified drop point,
        DrawHintRect() then calls ShowHint() to indicate this drop rectangle.
        "pane_window" is the window pointer of the pane being dragged, pt is
        the mouse position, in client coordinates.
        """
        
        # we need to paint a hint rectangle to find out the exact hint rectangle,
        # we will create a new temporary layout and then measure the resulting
        # rectangle we will create a copy of the docking structures (self._docks)
        # so that we don't modify the real thing on screen

        rect = wx.Rect()
        pane = self.GetPane(pane_window)
        
        attrs = self.GetAttributes(pane)
        hint = PaneInfo()
        hint = self.SetAttributes(hint, attrs)
        
        if hint.name != "__HINT__":
            self._oldname = hint.name
            
        hint.name = "__HINT__"

        if not hint.IsOk():
            hint.name = self._oldname
            return

        docks, panes = CopyDocksAndPanes2(self._docks, self._panes)

        # remove any pane already there which bears the same window
        # this happens when you are moving a pane around in a dock
        for ii in xrange(len(panes)):
            if panes[ii].window == pane_window:
                docks = RemovePaneFromDocks(docks, panes[ii])
                panes.pop(ii)
                break

        # find out where the new pane would be
        allow, hint = self.DoDrop(docks, panes, hint, pt, offset)

        if not allow:
            self.HideHint()
            return
        
        panes.append(hint)

        sizer, panes, docks, uiparts = self.LayoutAll(panes, docks, [], True, False)
        client_size = self._frame.GetClientSize()
        sizer.SetDimension(0, 0, client_size.x, client_size.y)
        sizer.Layout()

        for ii in xrange(len(uiparts)):
            part = uiparts[ii]
            if part.type == DockUIPart.typePaneBorder and \
               part.pane and part.pane.name == "__HINT__":
                pos = part.sizer_item.GetPosition()
                size = part.sizer_item.GetSize()
                rect = wx.Rect(pos[0], pos[1], size[0], size[1])
                break
            
        sizer.Destroy()

        if rect.IsEmpty():
            self.HideHint()
            return

        # actually show the hint rectangle on the screen
        rect.x, rect.y = self._frame.ClientToScreen((rect.x, rect.y))
        self.ShowHint(rect)


    def GetAttributes(self, pane):

        attrs = []
        attrs.extend([pane.window, pane.frame, pane.state, pane.dock_direction,
                     pane.dock_layer, pane.dock_pos, pane.dock_row, pane.dock_proportion,
                     pane.floating_pos, pane.floating_size, pane.best_size,
                     pane.min_size, pane.max_size, pane.caption, pane.name,
                     pane.buttons, pane.rect])

        return attrs
    

    def SetAttributes(self, pane, attrs):

        pane.window = attrs[0]
        pane.frame = attrs[1]
        pane.state = attrs[2]
        pane.dock_direction = attrs[3]
        pane.dock_layer = attrs[4]
        pane.dock_pos = attrs[5]
        pane.dock_row = attrs[6]
        pane.dock_proportion = attrs[7]
        pane.floating_pos = attrs[8]
        pane.floating_size = attrs[9]
        pane.best_size = attrs[10]
        pane.min_size = attrs[11]
        pane.max_size = attrs[12]
        pane.caption = attrs[13]
        pane.name = attrs[14]
        pane.buttons = attrs[15]
        pane.rect = attrs[16]

        return pane
    
    def UseTransparentDrag(self):
        
        if self._flags & AUI_MGR_TRANSPARENT_DRAG:
            return self.CanMakeWindowsTransparent()
        else:
            return False
        
 
    def OnFloatingPaneMoveStart(self, wnd):

        # try to find the pane
        pane = self.GetPane(wnd)
        if not pane.IsOk():
            raise "\nERROR: Pane Window Not Found"
        if self.UseTransparentDrag() and pane.IsDockable():
            self.MakeWindowTransparent(pane.frame, 150)


    def OnFloatingPaneMoving(self, wnd):

        # try to find the pane
        pane = self.GetPane(wnd)

        if not pane.IsOk():
            raise "\nERROR: Pane Window Not Found"
        
        pt = wx.GetMousePosition()
        client_pt = self._frame.ScreenToClient(pt)
        
        # calculate the offset from the upper left-hand corner
        # of the frame to the mouse pointer
        frame_pos = pane.frame.GetPosition()
        action_offset = wx.Point(pt[0]-frame_pos.x, pt[1]-frame_pos.y)

##        # no hint for toolbar floating windows
##        if pane.IsToolbar() and self._action == actionDragFloatingPane:
##
##            oldname = pane.name
##            indx = self._panes.index(pane)
##            hint = pane
##            docks, panes = CopyDocksAndPanes2(self._docks, self._panes)
##
##            # find out where the new pane would be
##            ret, hint = self.DoDrop(docks, panes, hint, client_pt)
##            
##            if not ret:
##                return
##
##            if hint.IsFloating():
##                return
##
##            pane = hint
##            pane.name = oldname
##            
##            self._panes[indx] = pane
##            self._action = actionDragToolbarPane
##            self._action_window = pane.window
##            
##            self.Update()
##            
##            return

        # if a key modifier is pressed while dragging the frame,
        # don't dock the window
        if wx.GetKeyState(wx.WXK_CONTROL) or wx.GetKeyState(wx.WXK_ALT):
            self.HideHint()
            return

        if pane.IsDockable():
            self.DrawHintRect(wnd, client_pt, action_offset)
        
        # reduces flicker
        self._frame.Update()
        

    def OnFloatingPaneMoved(self, wnd):

        # try to find the pane
        pane = self.GetPane(wnd)

        if not pane.IsOk():
            raise "\nERROR: Pane Window Not Found"
        
        pt = wx.GetMousePosition()
        client_pt = self._frame.ScreenToClient(pt)

        indx = self._panes.index(pane)
        
        # calculate the offset from the upper left-hand corner
        # of the frame to the mouse pointer
        frame_pos = pane.frame.GetPosition()
        action_offset = wx.Point(pt[0]-frame_pos.x, pt[1]-frame_pos.y)

        # if a key modifier is pressed while dragging the frame,
        # don't dock the window
        if wx.GetKeyState(wx.WXK_CONTROL) or wx.GetKeyState(wx.WXK_ALT):
            self.HideHint()
            return

        if not pane.IsToolbar() and pane.IsDockable() and not self._hintshown:
            if not pane.IsFloating():
                pane.Float()
                pane.floating_pos = pane.frame.GetPosition()
                self._panes[indx] = pane
                if self.UseTransparentDrag():
                    self.MakeWindowTransparent(pane.frame, 255)
            
        # do the drop calculation
        allow, pane = self.DoDrop(self._docks, self._panes, pane, client_pt, action_offset)

        # if the pane is still floating, update it's floating
        # position (that we store)
        if pane.IsFloating():
            pane.floating_pos = pane.frame.GetPosition()
            if self.UseTransparentDrag():
                self.MakeWindowTransparent(pane.frame, 255)

        if not pane.IsToolbar() and pane.IsDockable():
            pane.name = self._oldname
            
        self._panes[indx] = pane
            
        self.Update()
        self.HideHint()


    def OnFloatingPaneResized(self, wnd, size):

        # try to find the pane
        pane = self.GetPane(wnd)
        if not pane.IsOk():
            raise "\nERROR: Pane Window Not Found"

        indx = self._panes.index(pane)    
        pane.floating_size = size
        self._panes[indx] = pane


    def OnFloatingPaneClosed(self, wnd):

        # try to find the pane
        pane = self.GetPane(wnd)
        if not pane.IsOk():
            raise "\nERROR: Pane Window Not Found"

        indx = self._panes.index(pane)
        # reparent the pane window back to us and
        # prepare the frame window for destruction
        pane.window.Show(False)
        pane.window.Reparent(self._frame)
        pane.frame = None
        pane.Hide()
        
        self._panes[indx] = pane


    def OnFloatingPaneActivated(self, wnd):

        if self.GetFlags() & AUI_MGR_ALLOW_ACTIVE_PANE:
            # try to find the pane
            pane = self.GetPane(wnd)
            if not pane.IsOk():
                raise "\nERROR: Pane Window Not Found"

            self._panes = SetActivePane(self._panes, wnd)
            self.Repaint()
            

    def Render(self, dc):
        """
        Render() draws all of the pane captions, sashes,
        backgrounds, captions, grippers, pane borders and buttons.
        It renders the entire user interface.
        """

        for part in self._uiparts:

            # don't draw hidden pane items
            if part.sizer_item and not part.sizer_item.IsShown():
                continue
            
            if part.type == DockUIPart.typeDockSizer or \
               part.type == DockUIPart.typePaneSizer:
                self._art.DrawSash(dc, part.orientation, part.rect)
            elif part.type == DockUIPart.typeBackground:
                self._art.DrawBackground(dc, part.orientation, part.rect)
            elif part.type == DockUIPart.typeCaption:
                self._art.DrawCaption(dc, part.pane.caption, part.rect, part.pane)
            elif part.type == DockUIPart.typeGripper:
                self._art.DrawGripper(dc, part.rect, part.pane)
            elif part.type == DockUIPart.typePaneBorder:
                self._art.DrawBorder(dc, part.rect, part.pane)
            elif part.type == DockUIPart.typePaneButton:
                self._art.DrawPaneButton(dc, part.button.button_id,
                                         AUI_BUTTON_STATE_NORMAL, part.rect, part.pane)
                

    def Repaint(self, dc=None):

        w, h = self._frame.GetClientSize()
        # figure out which dc to use if one
        # has been specified, use it, otherwise
        # make a client dc
        client_dc = None
        
        if not dc:
            client_dc = wx.ClientDC(self._frame)
            dc = client_dc
        
        # if the frame has a toolbar, the client area
        # origin will not be (0,0).
        pt = self._frame.GetClientAreaOrigin()
        if pt.x != 0 or pt.y != 0:
            dc.SetDeviceOrigin(pt.x, pt.y)

        # render all the items
        self.Render(dc)

        # if we created a client_dc, delete it
        if client_dc:
            del client_dc
        

    def OnPaint(self, event):
        
        dc = wx.PaintDC(self._frame)
        
        if wx.Platform == "__WXMAC__":
            #Macs paint optimizations clip the area we need to paint a log
            #of the time, this is a dirty hack to always paint everything
            self.Repaint(None)
        else:
            self.Repaint(dc)


    def OnEraseBackground(self, event):

        if wx.Platform == "__WXMAC__":
            event.Skip()        


    def OnSize(self, event):

        if self._frame:
            
            self.DoFrameLayout()
            wx.CallAfter(self.Repaint)
            
            if not isinstance(self._frame, wx.MDIParentFrame):
                event.Skip()
        

    def OnSetCursor(self, event):

        # determine cursor
        part = self.HitTest(event.GetX(), event.GetY())
        cursor = None

        if part:
            if part.type == DockUIPart.typeDockSizer or \
               part.type == DockUIPart.typePaneSizer:

                # a dock may not be resized if it has a single
                # pane which is not resizable
                if part.type == DockUIPart.typeDockSizer and part.dock and \
                   len(part.dock.panes) == 1 and part.dock.panes[0].IsFixed():
                    return

                # panes that may not be resized do not get a sizing cursor
                if part.pane and part.pane.IsFixed():
                    return

                if part.orientation == wx.VERTICAL:
                    cursor = wx.StockCursor(wx.CURSOR_SIZEWE)
                else:
                    cursor = wx.StockCursor(wx.CURSOR_SIZENS)
            
            elif part.type == DockUIPart.typeGripper:
                cursor = wx.StockCursor(wx.CURSOR_SIZING)

        if cursor is not None:
            event.SetCursor(cursor)


    def UpdateButtonOnScreen(self, button_ui_part, event):

        hit_test = self.HitTest(event.GetX(), event.GetY())
        state = AUI_BUTTON_STATE_NORMAL
        
        if hit_test == button_ui_part:
            if event.LeftDown():
                state = AUI_BUTTON_STATE_PRESSED
            else:
                state = AUI_BUTTON_STATE_HOVER
        else:
            if event.LeftDown():
                state = AUI_BUTTON_STATE_HOVER
        
        # now repaint the button with hover state
        cdc = wx.ClientDC(self._frame)

        # if the frame has a toolbar, the client area
        # origin will not be (0,0).
        pt = self._frame.GetClientAreaOrigin()
        if pt.x != 0 or pt.y != 0:
            cdc.SetDeviceOrigin(pt.x, pt.y)

        self._art.DrawPaneButton(cdc,
                  button_ui_part.button.button_id,
                  state,
                  button_ui_part.rect, hit_test.pane)


    def OnLeftDown(self, event):

        part = self.HitTest(event.GetX(), event.GetY())

        if part:
            if part.dock and part.dock.dock_direction == AUI_DOCK_CENTER:
                return

            if part.type == DockUIPart.typeDockSizer or \
               part.type == DockUIPart.typePaneSizer:
            
                # a dock may not be resized if it has a single
                # pane which is not resizable
                if part.type == DockUIPart.typeDockSizer and part.dock and \
                   len(part.dock.panes) == 1 and part.dock.panes[0].IsFixed():
                    return

                # panes that may not be resized should be ignored here
                if part.pane and part.pane.IsFixed():
                    return

                self._action = actionResize
                self._action_part = part
                self._action_hintrect = wx.Rect()
                self._action_start = wx.Point(event.GetX(), event.GetY())
                self._action_offset = wx.Point(event.GetX() - part.rect.x,
                                               event.GetY() - part.rect.y)
                self._frame.CaptureMouse()
            
            elif part.type == DockUIPart.typePaneButton:
            
                self._action = actionClickButton
                self._action_part = part
                self._action_start = wx.Point(event.GetX(), event.GetY())
                self._frame.CaptureMouse()

                self.UpdateButtonOnScreen(part, event)
            
            elif part.type == DockUIPart.typeCaption or \
                  part.type == DockUIPart.typeGripper:

                if self.GetFlags() & AUI_MGR_ALLOW_ACTIVE_PANE:
                    # set the caption as active
                    self._panes = SetActivePane(self._panes, part.pane.window)
                    self.Repaint()
            
                self._action = actionClickCaption
                self._action_part = part
                self._action_start = wx.Point(event.GetX(), event.GetY())
                self._action_offset = wx.Point(event.GetX() - part.rect.x,
                                               event.GetY() - part.rect.y)
                self._frame.CaptureMouse()

        if wx.Platform != "__WXMAC__":
            event.Skip()


    def OnLeftUp(self, event):

        if self._action == actionResize:

            self._frame.ReleaseMouse()

            # get rid of the hint rectangle
            dc = wx.ScreenDC()
            DrawResizeHint(dc, self._action_hintrect)

            # resize the dock or the pane
            if self._action_part and self._action_part.type == DockUIPart.typeDockSizer:
                rect = self._action_part.dock.rect
                new_pos = wx.Point(event.GetX() - self._action_offset.x,
                                   event.GetY() - self._action_offset.y)

                if self._action_part.dock.dock_direction == AUI_DOCK_LEFT:
                    self._action_part.dock.size = new_pos.x - rect.x
                elif self._action_part.dock.dock_direction == AUI_DOCK_TOP:
                    self._action_part.dock.size = new_pos.y - rect.y
                elif self._action_part.dock.dock_direction == AUI_DOCK_RIGHT:
                    self._action_part.dock.size = rect.x + rect.width - \
                                                  new_pos.x - \
                                                  self._action_part.rect.GetWidth()
                elif self._action_part.dock.dock_direction == AUI_DOCK_BOTTOM:
                    self._action_part.dock.size = rect.y + rect.height - \
                                                  new_pos.y - \
                                                  self._action_part.rect.GetHeight()

                self.Update()
                self.Repaint(None)
            
            elif self._action_part and \
                 self._action_part.type == DockUIPart.typePaneSizer:
            
                dock = self._action_part.dock
                pane = self._action_part.pane

                total_proportion = 0
                dock_pixels = 0
                new_pixsize = 0

                caption_size = self._art.GetMetric(AUI_ART_CAPTION_SIZE)
                pane_border_size = self._art.GetMetric(AUI_ART_PANE_BORDER_SIZE)
                sash_size = self._art.GetMetric(AUI_ART_SASH_SIZE)

                new_pos = wx.Point(event.GetX() - self._action_offset.x,
                                   event.GetY() - self._action_offset.y)

                # determine the pane rectangle by getting the pane part
                pane_part = self.GetPanePart(pane.window)
                if not pane_part:
                    raise "\nERROR: Pane border part not found -- shouldn't happen"

                # determine the new pixel size that the user wants
                # this will help us recalculate the pane's proportion
                if dock.IsHorizontal():
                    new_pixsize = new_pos.x - pane_part.rect.x
                else:
                    new_pixsize = new_pos.y - pane_part.rect.y

                # determine the size of the dock, based on orientation
                if dock.IsHorizontal():
                    dock_pixels = dock.rect.GetWidth()
                else:
                    dock_pixels = dock.rect.GetHeight()

                # determine the total proportion of all resizable panes,
                # and the total size of the dock minus the size of all
                # the fixed panes
                dock_pane_count = len(dock.panes)
                pane_position = -1
                
                for ii in xrange(dock_pane_count):
                    p = dock.panes[ii]
                    if p.window == pane.window:
                        pane_position = ii
                    
                    # while we're at it, subtract the pane sash
                    # width from the dock width, because this would
                    # skew our proportion calculations
                    if ii > 0:
                        dock_pixels = dock_pixels - sash_size
                 
                    # also, the whole size (including decorations) of
                    # all fixed panes must also be subtracted, because they
                    # are not part of the proportion calculation
                    if p.IsFixed():
                        if dock.IsHorizontal():
                            dock_pixels = dock_pixels - p.best_size.x
                        else:
                            dock_pixels = dock_pixels - p.best_size.y
                    else:
                        total_proportion = total_proportion + p.dock_proportion
                    
                # find a pane in our dock to 'steal' space from or to 'give'
                # space to -- this is essentially what is done when a pane is
                # resized the pane should usually be the first non-fixed pane
                # to the right of the action pane
                borrow_pane = -1
                
                for ii in xrange(pane_position+1, dock_pane_count):
                    p = dock.panes[ii]
                    if not p.IsFixed():
                        borrow_pane = ii
                        break
                
                # demand that the pane being resized is found in this dock
                # (this assert really never should be raised)
                if pane_position == -1:
                    raise "\nERROR: Pane not found in dock"
                
                # prevent division by zero
                if dock_pixels == 0 or total_proportion == 0 or borrow_pane == -1:
                    self._action = actionNone
                    return
                
                # calculate the new proportion of the pane
                new_proportion = new_pixsize*total_proportion/dock_pixels
                
                # default minimum size
                min_size = 0
                
                # check against the pane's minimum size, if specified. please note
                # that this is not enough to ensure that the minimum size will
                # not be violated, because the whole frame might later be shrunk,
                # causing the size of the pane to violate it's minimum size
                if pane.min_size.IsFullySpecified():
                    min_size = 0
                    if pane.HasBorder():
                        min_size = min_size + pane_border_size*2

                    # calculate minimum size with decorations (border,caption)
                    if pane_part.orientation == wx.VERTICAL:
                        min_size = min_size + pane.min_size.y
                        if pane.HasCaption():
                            min_size = min_size + caption_size
                    else:
                        min_size = min_size + pane.min_size.x
                    
                # for some reason, an arithmatic error somewhere is causing
                # the proportion calculations to always be off by 1 pixel
                # for now we will add the 1 pixel on, but we really should
                # determine what's causing this.
                min_size = min_size + 1
                
                min_proportion = min_size*total_proportion/dock_pixels
                    
                if new_proportion < min_proportion:
                    new_proportion = min_proportion
                
                prop_diff = new_proportion - pane.dock_proportion

                # borrow the space from our neighbor pane to the
                # right or bottom (depending on orientation)
                dock.panes[borrow_pane].dock_proportion -= prop_diff
                pane.dock_proportion = new_proportion

                indxd = self._docks.index(dock)
                indxp = self._panes.index(pane)

                self._docks[indxd] = dock
                self._panes[indxp] = pane
                
                # repaint
                self.Update()
                self.Repaint(None)
        
        elif self._action == actionClickButton:
        
            self._hover_button = None
            self._frame.ReleaseMouse()     
            self.UpdateButtonOnScreen(self._action_part, event)

            # make sure we're still over the item that was originally clicked
            if self._action_part == self.HitTest(event.GetX(), event.GetY()):
                # fire button-click event  
                e = FrameManagerEvent(wxEVT_AUI_PANEBUTTON)
                e.SetPane(self._action_part.pane)
                e.SetButton(self._action_part.button.button_id)
                self.ProcessMgrEvent(e)
        
        elif self._action == actionClickCaption:
        
            self._frame.ReleaseMouse()
        
        elif self._action == actionDragFloatingPane:
            
            self._frame.ReleaseMouse()
        
        elif self._action == actionDragToolbarPane:

            self._frame.ReleaseMouse()

            pane = self.GetPane(self._action_window)
            if not pane.IsOk():
                raise "\nERROR: Pane Window Not Found"
        
            # save the new positions
            docks = FindDocks(self._docks, pane.dock_direction,
                              pane.dock_layer, pane.dock_row)

            if len(docks) == 1:
                dock = docks[0]
                pane_positions, pane_sizes = self.GetPanePositionsAndSizes(dock)
                
                dock_pane_count = len(dock.panes)
                for ii in xrange(dock_pane_count):
                    dock.panes[ii].dock_pos = pane_positions[ii]
            
            pane.state &= ~PaneInfo.actionPane
            indx = self._panes.index(pane)
            self._panes[indx] = pane
            
            self.Update()

        else:

            event.Skip()

        self._action = actionNone
        self._last_mouse_move = wx.Point() # see comment in OnMotion()


    def OnMotion(self, event):

        # sometimes when Update() is called from inside this method,
        # a spurious mouse move event is generated this check will make
        # sure that only real mouse moves will get anywhere in this method
        # this appears to be a bug somewhere, and I don't know where the
        # mouse move event is being generated.  only verified on MSW
        
        mouse_pos = event.GetPosition()
        if self._last_mouse_move == mouse_pos:
            return
        
        self._last_mouse_move = mouse_pos

        if self._action == actionResize:
            pos = self._action_part.rect.GetPosition()
            if self._action_part.orientation == wx.HORIZONTAL:
                pos.y = max(0, mouse_pos.y - self._action_offset.y)
                pos.y = min(pos.y, self._frame.GetClientSize().y - self._action_part.rect.GetSize().y)
            else:
                pos.x = max(0, mouse_pos.x - self._action_offset.x)
                pos.x = min(pos.x, self._frame.GetClientSize().x - self._action_part.rect.GetSize().x)

            mypos = self._frame.ClientToScreen(pos)
            mysize = self._action_part.rect.GetSize()
            rect = wx.Rect(mypos[0], mypos[1], mysize[0], mysize[1])

            # is it the same as the old rectangle?
            if self._action_hintrect == rect:
                # heck, yes, no need to draw again, it will only bring about flicker
                event.Skip()
                return

            # otherwise draw the hint

            dc = wx.ScreenDC()
            
            if not self._action_hintrect.IsEmpty() and self._action_hintrect != rect:
                DrawResizeHint(dc, self._action_hintrect)
                
            DrawResizeHint(dc, rect)
            self._action_hintrect = rect
        
        elif self._action == actionClickCaption:
        
            drag_x_threshold = wx.SystemSettings_GetMetric(wx.SYS_DRAG_X)
            drag_y_threshold = wx.SystemSettings_GetMetric(wx.SYS_DRAG_Y)
            
            # caption has been clicked.  we need to check if the mouse
            # is now being dragged. if it is, we need to change the
            # mouse action to 'drag'
            if abs(mouse_pos.x - self._action_start.x) > drag_x_threshold or \
               abs(mouse_pos.y - self._action_start.y) > drag_y_threshold:

                pane_info = self._action_part.pane
                indx = self._panes.index(pane_info)

                if not pane_info.IsToolbar():
                
                    if self._flags & AUI_MGR_ALLOW_FLOATING and \
                       pane_info.IsFloatable():
                    
                        self._action = actionDragFloatingPane

                        # set initial float position
                        pt = self._frame.ClientToScreen(event.GetPosition())
                        pane_info.floating_pos = wx.Point(pt.x - self._action_offset.x,
                                                          pt.y - self._action_offset.y)
                        # float the window
                        pane_info.Float()
                        self._panes[indx] = pane_info
                        
                        self.Update()

                        self._action_window = pane_info.frame
                        
                        # action offset is used here to make it feel "natural" to the user
                        # to drag a docked pane and suddenly have it become a floating frame.
                        # Sometimes, however, the offset where the user clicked on the docked
                        # caption is bigger than the width of the floating frame itself, so
                        # in that case we need to set the action offset to a sensible value
                        frame_size = self._action_window.GetSize()
                        if frame_size.x <= self._action_offset.x:
                            self._action_offset.x = 30
                    
                else:
                
                    self._action = actionDragToolbarPane
                    self._action_window = pane_info.window
                
        elif self._action == actionDragFloatingPane:
        
            pt = self._frame.ClientToScreen(event.GetPosition())
            if self._action_window:
                self._action_window.Move((pt.x - self._action_offset.x,
                                         pt.y - self._action_offset.y))
        
        elif self._action == actionDragToolbarPane:

            pane = self.GetPane(self._action_window)
            if not pane.IsOk():
                raise "\nERROR: Pane Window Not Found"

            indx = self._panes.index(pane)            
            pane.state |= PaneInfo.actionPane
        
            pt = event.GetPosition()
            ret, pane = self.DoDrop(self._docks, self._panes, pane, pt, self._action_offset)

            if not ret:
                return
            
            # if DoDrop() decided to float the pane, set up
            # the floating pane's initial position
            if pane.IsFloating():
            
                pt = self._frame.ClientToScreen(event.GetPosition())
                pane.floating_pos = wx.Point(pt.x - self._action_offset.x,
                                             pt.y - self._action_offset.y)

            self._panes[indx] = pane
            
            # this will do the actiual move operation
            # in the case that the pane has been floated,
            # this call will create the floating pane
            # and do the reparenting
            self.Update()
            
            # if the pane has been floated, change the mouse
            # action actionDragFloatingPane so that subsequent
            # EVT_MOTION() events will move the floating pane
            if pane.IsFloating():
            
                pane.state &= ~PaneInfo.actionPane
                self._action = actionDragFloatingPane
                self._action_window = pane.frame

            self._panes[indx] = pane                
            
        else:
        
            part = self.HitTest(event.GetX(), event.GetY())
            if part and part.type == DockUIPart.typePaneButton:
                if part != self._hover_button:
                    # make the old button normal
                    if self._hover_button:
                        self.UpdateButtonOnScreen(self._hover_button, event)

                    # mouse is over a button, so repaint the
                    # button in hover mode
                    self.UpdateButtonOnScreen(part, event)
                    self._hover_button = part
            else:            
                if self._hover_button:
                
                    self._hover_button = None
                    self.Repaint()

                else:

                    event.Skip()
                    
                
    def OnLeaveWindow(self, event):

        if self._hover_button:
            self._hover_button = None
            self.Repaint()


    def OnChildFocus(self, event):

        # when a child pane has it's focus set, we should change the 
        # pane's active state to reflect this. (this is only true if 
        # active panes are allowed by the owner)
        if self.GetFlags() & AUI_MGR_ALLOW_ACTIVE_PANE:
            if self.GetPane(event.GetWindow()).IsOk():
                self._panes = SetActivePane(self._panes, event.GetWindow())
                self._frame.Refresh()
    
        event.Skip()
        

    def OnPaneButton(self, event):
        """
        OnPaneButton() is an event handler that is called
        when a pane button has been pressed.
        """

        pane = event.pane
        indx = self._panes.index(pane)
        
        if event.button == PaneInfo.buttonClose:
            pane.Hide()
            self._panes[indx] = pane
            self.Update()
        
        elif event.button == PaneInfo.buttonPin:
        
            if self._flags & AUI_MGR_ALLOW_FLOATING and pane.IsFloatable():
                pane.Float()

            self._panes[indx] = pane                
            self.Update()
