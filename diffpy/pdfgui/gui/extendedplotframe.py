#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Jiwu Liu, Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""
The module contains extensions for GUI plot frame.
"""

import os.path

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavToolbar
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import _load_bitmap
from matplotlib.artist import setp
from matplotlib.font_manager import FontProperties
import wx


DATA_SAVE_ID  = wx.NewId()


class ExtendedToolbar(NavToolbar):
    """An extended plotting toolbar with a save and close button."""

    def __init__(self, canvas):
        NavToolbar.__init__(self, canvas)
        # Get rid of the configure subplots button
        if hasattr(self, 'wx_ids'):
            self.DeleteTool(self.wx_ids['Subplots'])
        else:
            self.DeleteToolByPos(6)
        # Add new buttons
        self.AddSimpleTool(wx.ID_PRINT,
               wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_TOOLBAR),
               'Print', 'print graph')
        self.AddSimpleTool(DATA_SAVE_ID,
               _load_bitmap('stock_save_as.xpm'),
               'Export plot data', 'Export plot data to file')
        self.AddSeparator()
        self.AddSimpleTool(wx.ID_CLOSE,
               _load_bitmap('stock_close.xpm'),
               'Close window', 'Close window')
        return

    def save(self, evt):
        # Fetch the required filename and file type.
        filetypes = self.canvas._get_imagesave_wildcards()
        exts = []
        # sortedtypes put png in the first
        sortedtypes = []
        import re
        types = filetypes[0].split('|')
        n = 0
        for ext in types[1::2]:
            # Extract only the file extension
            res = re.search(r'\*\.(\w+)', ext)
            pos = n*2
            if re.search(r'png', ext):
                pos = 0
            sortedtypes.insert(pos, ext)
            sortedtypes.insert(pos, types[n*2])
            if res:
                exts.insert(pos/2,res.groups()[0])
            n += 1

        # rejoin filetypes
        filetypes = '|'.join(sortedtypes)
        dlg =wx.FileDialog(self._parent, "Save to file", "", "", filetypes,
                           wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            dirname  = dlg.GetDirectory()
            filename = dlg.GetFilename()
            i = dlg.GetFilterIndex()
            dotext = '.' + exts[i]
            if os.path.splitext(filename)[-1] != dotext:
                filename = filename + dotext
            # matplotlib does not like UTF strings
            fullpath = str(os.path.join(dirname, filename))
            self.canvas.print_figure(fullpath)
        return

# End class ExtendedToolbar

class ExtendedPlotFrame(wx.Frame):
    """An extended plotting frame with a save and close button.

    The class has a matplotlib.figure.Figure data member named 'figure'.
    It also has a matplotlib.axes.Axes data member named 'axes'.
    The normal matplotlib plot manipulations can be performed with these two
    data members. See the matplotlib API at:
    http://matplotlib.sourceforge.net/classdocs.html
    """

    def __init__(self, parent = None, *args, **kwargs):
        """Initialize the CanvasFrame.

        The frame uses ExtendedToolbar as a toolbar, which has a save data
        button and a close button on the toolbar in addition to the normal
        buttons.

        args -- argument list
        kwargs -- keyword argument list
        """
        wx.Frame.__init__(self,parent,-1,'ExtendedPlotFrame',size=(550,350))

        # figsize in inches
        self.figure = Figure(figsize=(0.5,0.5), dpi=72)

        # we will manage view scale ourselves
        self.subplot = self.figure.add_subplot(111, autoscale_on=False)
        self.canvas = FigureCanvas(self, -1, self.figure)

        # Introspection data
        self.dirname = ''
        self.filename = ''

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP|wx.LEFT|wx.EXPAND)
        self.toolbar = ExtendedToolbar(self.canvas)
        self.toolbar.Realize()

        self.coordLabel = wx.StaticText(self,-1,style = wx.ALIGN_RIGHT|wx.NO_BORDER)
        # Place coordinates textbox in a horizontal sizer next to the toolbar.
        barSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(barSizer, 0, wx.EXPAND|wx.CENTER)
        barSizer.Add(self.toolbar, 0, wx.CENTER)
        barSizer.Add((20,10),0)
        barSizer.Add(self.coordLabel, 0, wx.CENTER)

        # update the axes menu on the toolbar
        self.toolbar.update()
        self.SetSizer(self.sizer)
        self.Fit()
        self.SetSize((600,400))
        # Use toolbar's color for coordinates label background.
        self.SetBackgroundColour(self.toolbar.GetBackgroundColour())
        # FIXME -- toolbar background color does not match on Mac OS X.
        # Use GIMP - picked color until a proper way is found.
        if wx.Platform == '__WXMAC__':
            self.SetBackgroundColour((200, 200, 200, 255))
        self.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_TOOL(self, DATA_SAVE_ID, self.savePlotData)
        wx.EVT_TOOL(self, wx.ID_CLOSE, self.onClose)
        wx.EVT_CLOSE(self, self.onClose)
        wx.EVT_TOOL(self, wx.ID_PRINT, self.onPrint)
        wx.EVT_TOOL(self, wx.ID_PRINT_SETUP, self.onPrintSetup)
        wx.EVT_TOOL(self, wx.ID_PREVIEW_PRINT, self.onPrintPreview)

        self.datalims = {}

    # CUSTOM METHODS ########################################################

    # EVENT CODE #############################################################
    def onClose(self, evt):
        """Close the frame."""
        if hasattr(self, 'plotter'):
            self.plotter.onWindowClose()
        self.Destroy()
        return

    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()

    def savePlotData(self, evt):
        """Save the data in the plot in columns."""
        d = wx.FileDialog(None, "Save as...", self.dirname, self.filename,
                "(*.dat)|*.dat|(*.txt)|*.txt|(*)|*", wx.SAVE|wx.OVERWRITE_PROMPT)
        if d.ShowModal() == wx.ID_OK:
            fullname = d.GetPath()
            self.dirname = os.path.dirname(fullname)
            self.filename =  os.path.basename(fullname)
            self.plotter.export(fullname)

        d.Destroy()
        return

    def onPrint(self, evt):
        '''handle print event'''
        self.canvas.Printer_Print(event=evt)

    def onPrintSetup(self,event=None):
        self.canvas.Printer_Setup(event=event)

    def onPrintPreview(self,event=None):
         self.canvas.Printer_Preview(event=event)

    def UpdateStatusBar(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            xystr = "x = %g, y = %g" % (x, y)
            self.coordLabel.SetLabel(xystr)

    def replot(self):
        """officially call function in matplotlib to do drawing
        """
        self.canvas.draw()

    def insertCurve(self, xData, yData, style):
        """insert a new curve to the plot

        xData, yData -- x, y data to used for the curve
        style -- the way curve should be plotted
        return:  internal reference to the newly added curve
        """
        stylestr,properties = self.__translateStyles(style)
        curveRef = self.subplot.plot(xData, yData, stylestr, **properties)[0]
        self.subplot.legend(**legendBoxProperties())
        try:
            self.datalims[curveRef] = (min(xData), max(xData), min(yData), max(yData))
        except ValueError:
            self.datalims[curveRef] = (0, 0, 0, 0)
        self.__updateViewLimits()
        return curveRef

    def updateData(self, curveRef, xData, yData):
        """update data for a existing curve

        curveRef -- internal reference to a curve
        xData, yData -- x, y data to used for the curve
        """
        curveRef.set_data(xData, yData)
        try:
            self.datalims[curveRef] = (min(xData), max(xData), min(yData), max(yData))
        except ValueError:
            self.datalims[curveRef] = (0, 0, 0, 0)
        self.__updateViewLimits()

    def changeStyle(self, curveRef, style):
        """change curve style

        curveRef -- internal reference to curves
        style -- style dictionary
        """
        stylestr, properties = self.__translateStyles(style)
        #FIXME: we discard stylestr because it seems there's no way
        # it can be changed afterwards.
        setp((curveRef,), **properties)
        self.subplot.legend(**legendBoxProperties())

    def removeCurve(self, curveRef):
        """remove curve from plot

        curveRef -- internal reference to curves
        """
        del self.datalims[curveRef]
        self.figure.gca().lines.remove(curveRef)
        self.subplot.legend(**legendBoxProperties())
        self.__updateViewLimits()

    def __updateViewLimits(self):
        """adjust the subplot range in order to show all curves correctly.
        """
        # NOTE:
        # we need to adjust view limits by ourselves because Matplotlib can't
        # set the legend nicely when there are multiple curves in the plot.
        # Beside, autoscale can not automatically respond to data change.
        if len(self.datalims) == 0 :
            return
        # ignore previous range
        self.subplot.dataLim.ignore(True)
        bounds = self.datalims.values()
        xmin = min([b[0] for b in bounds])
        xmax = max([b[1] for b in bounds])
        ymin = min([b[2] for b in bounds])
        ymax = max([b[3] for b in bounds])

        # If multiple curve, we need calculate new x limits because legend box
        # take up some space
        #NOTE: 3 and 0.33 is our best estimation for a good view
        # 2007-10-25 PJ: it is better to use full plot area
        # if len(self.datalims) > 3:
        #     # leave extra room for legend by shift the upper bound for x axis
        #     xmax += (xmax-xmin)*0.33
        if xmax > xmin:
            self.subplot.set_xlim(xmin, xmax)
        if ymax > ymin:
            self.subplot.set_ylim(ymin, ymax)

    def __translateStyles(self, style):
        """Private function to translate general probabilities to
        Matplotlib specific ones

        style -- general curve style dictionary (defined in demoplot)
        """
        #Translation dictionary
        lineStyleDict ={'solid':'-','dash':'--','dot':':','dashDot':'-.'}
        symbolDict ={'diamond':'d','square':'s','circle':'o',
        'cross':'+','xCross':'x','triangle':'^'}
        colorDict = {'blue':'b','green':'g','red':'r','cyan':'c',
        'magenta':'m','yellow':'y','black':'k','white':'w',
        'darkRed':'#8B0000', 'darkGreen':'#006400', 'darkCyan':'#008B8B',
        'darkYellow':'#FFD700','darkBlue':'#00008B','darkMagenta':'#8B008B'}

        properties = {}

        #NOTE: matplotlib takes additional string for plotting. It's
        # purpose is like 'with' in Gnuplot
        stylestr  = ''
        # color is universal for either lines, points or linepoints
        color = colorDict.get(style['color'], 'k')

        if style['with'] in ('points', 'linespoints'):
            # require symbol properties
            stylestr = '.'
            symbol = symbolDict.get(style['symbol'],'s') # prefer square
            symbolSize = style['symbolSize']
            symbolColor = colorDict.get(style['symbolColor'], 'k')
            properties.update({#'linewidth':0.0, # doesn't affect any
                               'markerfacecolor':symbolColor,
                              'markeredgecolor':color,
                             'marker':symbol,'markersize':symbolSize})
        if style['with'] != 'points':
            # not 'points', so line properties are required as well
            lineStyle = lineStyleDict.get(style['line'],'-') #prefer solid
            lineWidth = style['width']
            stylestr += lineStyle
            properties.update({'color':color,'linestyle':lineStyle,
                             'linewidth':lineWidth})

        if style.has_key('legend'):
            properties['label'] = style['legend']
        return stylestr, properties


    def setTitle(self, wt, gt):
        """set graph labels

        wt -- window title
        gt -- graph title
        """
        self.SetTitle(wt)
        self.figure.gca().set_title(gt)

    def setXLabel(self, x):
        """set label for x axis

        x -- x label
        """
        self.figure.gca().set_xlabel(x)

    def setYLabel(self, y):
        """set label for y axis

        y -- y label
        """
        self.figure.gca().set_ylabel(y)

    def clear(self):
        """erase all curves"""
        self.subplot.clear()
        self.curverefs =[]
        self.replot()

# End class ExtendedPlotFrame


def legendBoxProperties():
    """Legend properties dictionary with keys consistent with MPL version.

    The argument names have changed in matplotlib 0.98.5.
    Old arguments do not work with later versions of matplotlib.

    Return dictionary of legend properties.
    """
    global _lbp
    # return immediately if properties have already been cached
    if len(_lbp) > 0:   return _lbp
    #  figure out matplotlib version and appropriate names
    from pkg_resources import parse_version
    from matplotlib import __version__ as mplver
    if parse_version(mplver) >= parse_version('0.98.5'):
        _lbp = {
            'loc' : 'upper right',
            'numpoints' : 3,        # number of points in the legend line
            'borderpad' : 0.25,     # whitespace in the legend border
            'labelspacing' : 0,     # space between legend entries
            'handlelength' : 1.5,   # the length of the legend lines
            'handletextpad' : 0.5,  # separation between line and text
            'prop' : FontProperties(size='medium'),
        }
    else:
        _lbp = {
            'loc' : 'upper right',
            'numpoints' : 3,        # number of points in the legend line
            'pad' : 0.20,           # whitespace in the legend border
            'labelsep' : 0.005,     # space between legend entries
            'handlelen' : 0.03,     # the length of the legend lines
            'handletextsep' : 0.02, # separation between line and text
            'prop' : FontProperties(size='medium'),
        }
    return _lbp

_lbp = {}

# End of legendBoxProperties


if __name__ == "__main__":

    class MyApp(wx.App):
        def OnInit(self):
            from numpy import arange, sin, pi, cos
            'Create the main window and insert the custom frame'
            x = arange(0.0,3.0,0.01)
            s = sin(2*pi*x)
            c = cos(2*pi*x)
            t = sin(2*pi*x) + cos(2*pi*x)
            frame = ExtendedPlotFrame(None)
            style = {'with':'lines', 'color':'blue','line':'solid','width':2}
            style['legend'] = 'sin(x)'
            frame.insertCurve(x,s, style)
            style = {'with':'lines', 'color':'red','line':'solid','width':2}
            style['legend'] = 'cos(x)'
            frame.insertCurve(x,c, style)
            style = {'with':'lines', 'color':'black','line':'solid','width':2}
            #style['legend'] = 'sin(x)+cos(x)'
            frame.insertCurve(x,t, style)
            frame.Show(True)
            return True

    app = MyApp(0)
    app.MainLoop()


# End of file
