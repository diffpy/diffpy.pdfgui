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

from diffpy.pdfgui.control.pdfcomponent import PDFComponent
from diffpy.pdfgui.control.controlerrors import ControlConfigError
from diffpy.pdfgui.control.controlerrors import ControlStatusError
from diffpy.pdfgui.gui.extendedplotframe import ExtendedPlotFrame

# Preset plotting style
colors = ("red","blue","magenta","cyan","green","yellow", #"black",
  "darkRed", "darkBlue","darkMagenta", "darkCyan", "darkGreen","darkYellow")
lines = ('solid','dash','dot','dashDot')
symbols = ("circle","square","triangle","diamond")#,"cross","xCross")

# this is to map 'r' to what it is supposed to be. For example, when user asks
# for plotting 'Gobs' against 'r', the real data objects are 'Gobs' and 'robs'
transdict = { 'Gobs':'robs',
        'Gcalc':'rcalc','Gdiff':'rcalc','Gtrunc':'rcalc','crw':'rcalc'}
baselineStyle = {'with':'lines','line':'solid','color':'black','width':1, 'legend':'_nolegend_'}

def _transName(name):
    '''translate name of y object

    This is mainly for plotting of parameters. GUI will pass in a integer to
    indicate which parameter to be plotted. However, in data storage the
    parameter is denoted as '@n'

    name -- name of data item
    '''
    if isinstance(name, int):
        rv = '@' + str(name)
    else:
        rv = str(name)
    return rv


def _fullName(dataId):
    '''construct full name'''
    from diffpy.pdfgui.control.fitting import Fitting
    if hasattr(dataId, 'owner') and isinstance(dataId.owner, Fitting):
        return _fullName(dataId.owner) + "/" + dataId.name
    else:
        return dataId.name

def _buildStyle(plotter, name, group, yNames):
    '''trying to figure out a good style

    1. generally we want line style for Gcalc, Gdiff, crw, symbol style for Gobs,
    and line-symbol style for the rest
    2. there is a preferred style for plotting a single PDF curve

    plotter -- A plotter instance
    name -- what is to be plotted (y name)
    group -- which group the curve is in (group = -1 means it is the only group)
    yNames -- all y to be plotted
    return: style dictionay
    '''
    if name in ('Gcalc', 'Gdiff', 'crw'):
        style = plotter.buildLineStyle()
        style['line']  = 'solid'
    elif name in ('Gobs', 'Gtrunc'):
        style = plotter.buildSymbolStyle()

        # Use open circle always
        style['symbolColor'] = 'white'
        style['symbol'] = 'circle'
        style['symbolSize'] = 6
    else:
        style = plotter.buildLineSymbolStyle()
        style['line'] = 'dash'
        style['symbol'] = 'circle'
        style['symbolSize'] = 8

    # We only care about how to arrange Gdiff Gobs Gcalc Gtrunc crw nicely
    if group < 0:
        # use fixed style for single PDFFit picture
        if name == 'Gcalc':
            style['color'] = 'red'
        elif name in ('Gobs', 'Gtrunc'):
            style['color'] = 'blue'
        elif name in ('Gdiff', 'crw'):
            style['color'] = 'green'
    else:
        # make sure Gdiff, Gtrunc, Gobs, crw are having same color
        if name in ('Gobs', 'Gtrunc', 'Gdiff', 'Gcalc', 'crw'):
            style['color'] = colors[group%len(colors)]
        if name == 'Gcalc':
            # for visual effect, change Gcalc to black if it's going to be plotted against Gobs/Gtrunc
            if 'Gobs' in yNames or 'Gtrunc' in yNames:
                style['color'] = 'black'

    return style

class Plotter(PDFComponent):
    """Plots a single graph. It can have multiple curves. """
    __plotWindowNumber = 1

    class Curve:
        """Curve stores the information for a curve in the plot

        There are three ways of forming x and y data lists.
        (1) r and g(r) from a single refinement are vectors by themselves
        (2) A scalar data item (any item other than r and g(r)) can form a
        vector if multiple timeSteps (refinement steps) are specified.
        (3) A scalar data item (any item other than r and g(r)) can form a
        vector if multiple refinement (multiple ids) are specified

        name  -- The curve name
        plotwnd -- The window where the curve is drawn
        xStr -- Data name (string) for x axis
        yStr -- Data name (string) for y axis
        steps -- refinement step list
        ids -- The list of object ids that the curve is related to
        offset -- curve displacement in y direction
        style --The drawing style of the curve
        xData, yData -- data to be plotted
        x, y -- original data for exporting (curve could be shifted)
        bMultiData -- if the curve data comes from multiple data objects
        bMultiStep -- if the curve data comes from multiple refinement step
        ref -- reference of curve in the plot window
        initialized -- if curve has been inserted
        dataChanged -- if curve data has changed
        """
        def __init__(self, name, plotwnd, xStr, yStr, steps, ids, offset, style):
            """initialize

            name  -- The curve name
            plotwnd -- The window where the curve is drawn
            xStr -- Data name (string) for x axis
            yStr -- Data name (string) for y axis
            steps -- refinement step list
            ids -- The list of object ids that the curve is related to
            offset -- curve displacement in y direction
            style --The drawing style of the curve
            """
            self.name = name
            self.plotwnd = plotwnd
            self.ids = ids
            self.steps = steps
            self.xStr = xStr
            self.yStr = yStr
            self.offset = offset
            self.style = style

            self.bMultiData = len(self.ids) > 1
            self.bMultiStep = False
            if self.steps is None or isinstance(self.steps, list):
                self.bMultiStep = True

            self.xData = None
            self.yData = None
            self.x = None
            self.y = None

            # Reference to the curve object in the  underlying plotting library
            self.ref = None
            self.initialized = False
            self.dataChanged = False

            #validate user's choice
            self.validate()

        def validate(self):
            """ validate(self) --> check if  the curve is valid. Validity
            is broken:
            (1) when xStr or yStr doesn't refer to a legal vector
            (2) when sizes of xStr and yStr don't match
            """
            bItemIsVector = False
            if self.xStr in ('r', 'rcalc', 'robs'):
                if self.yStr not in ('Gobs', 'Gcalc', 'Gdiff', 'Gtrunc','crw'):
                    emsg = "x={}, y={} don't match".format(self.xStr, self.yStr)
                    raise ControlConfigError(emsg)
                bItemIsVector = True
            elif self.xStr in ('Gobs', 'Gcalc', 'Gdiff', 'Gtrunc','crw'):
                raise ControlConfigError("%s can't be x axis" % self.xStr)
            elif self.yStr in ('Gobs', 'Gcalc', 'Gdiff', 'Gtrunc','crw'):
                # Get called when x is not r but y is not Gobs, Gtrunc Gdiff...
                raise ControlConfigError("%s can only be plotted against r" % self.yStr)

            # There are three booleans
            # (1) bItemIsVector
            # (2) self.ids has only one element
            # (3) self.allSteps
            # The logic below make sure only one of them can be true.
            if bItemIsVector:
                if  self.bMultiData or self.bMultiStep:
                    emsg = ("({}, {}) can't be plotted with multiple "
                            "refinements/steps").format(self.xStr, self.yStr)
                    raise ControlConfigError(emsg)
            else:
                if  not self.bMultiData and not self.bMultiStep:
                    raise ControlConfigError("(%s, %s) is a single point" % (self.xStr, self.yStr))
                elif self.bMultiData and self.bMultiStep:
                    emsg = ("({}, {}) can't be plotted with both multiple "
                            "refinements and multiple steps").format(self.xStr, self.yStr)
                    raise ControlConfigError(emsg)


        def notify(self, changedIds=None, plotwnd=None):
            """notify Curve object certain data is updated

            changedIds -- objects to which changed data is associated with
            """
            if plotwnd:
                self.plotwnd = plotwnd

            # in the case when changedIds are given explicitly, use it.
            if changedIds:
                affectedIds = []
                for id in self.ids:
                    for changedId in changedIds:
                        if id is changedId or id.owner is changedId:
                            affectedIds.append(id)
                            break

                #If the change doesn't affect any id, do nothing
                if not affectedIds:
                    return False
            else:
                affectedIds = self.ids

            # translation may be required
            xStr = self.xStr
            if xStr == 'r':
                xStr = transdict.get(self.yStr, xStr)

            if self.bMultiData:
                #Local list is maintained here
                if self.xData is None:
                    self.xData = [None] * len(self.ids)
                if self.yData is None:
                    self.yData = [None] * len(self.ids)
                for id in affectedIds:
                    i = self.ids.index(id)
                    self.yData[i] = id.getData(self.yStr, -1)
                    if xStr == 'step':
                        raise AssertionError("Can not plot against step")
                    elif xStr == 'index':
                        self.xData[i] = i
                    else:
                        self.xData[i] = id.getData(xStr, -1)
            else:
                # affectedIds has only one member
                if  self.bMultiStep:
                    steps = None # None to get the whole steps
                else:
                    steps = -1 #

                # plot multiple refinement steps for a single dataId
                # in deed, the reference is not gonna change
                self.yData = affectedIds[0].getData(self.yStr, steps)
                if xStr == 'step':
                    if self.yData is None:
                        self.xData = None
                    else:
                        self.xData = list(range(len(self.yData)))
                else:
                    self.xData = affectedIds[0].getData(xStr, steps)

                self.x = self.xData
                self.y = self.yData

                def _shift(y):
                    return y + self.offset

                if self.yData and self.offset: # not zero
                    self.yData = [_shift(yi) for yi in self.yData]

            if self.xData and self.yData: # not empty or None
                return self.draw()
            else:
                return False

        def draw(self):
            """draw the curve in the graph. It will make sure the data is OK,
            and plot to the screen.
            """
            if self.bMultiData:
                # xs and ys initialize here. They are actual data object to be
                # used for plotting
                xs = []
                ys = []
                plotData = sorted(zip(self.xData,self.yData))
                for x, y in plotData:
                    if x is not None and y is not None:
                        xs.append(x)
                        ys.append(y)
                self.x = xs
                self.y = ys
            else:
                xs = self.xData
                ys = self.yData

            if not xs or not ys:
                return False

            # If it can get here, data is ready now.
            if self.ref is None:
                self.ref = self.plotwnd.insertCurve(xs, ys, self.style)
                if self.yStr == 'Gdiff':
                    # add a baseline for any Gdiff
                    rs = self.ids[0].rcalc
                    if not rs:
                        rs = self.ids[0].robs
                    hMin = min(rs)
                    hMax = max(rs)

                    self.plotwnd.insertCurve([hMin, hMax], [self.offset, self.offset], baselineStyle)
            else:
                # update only
                self.plotwnd.updateData(self.ref, xs, ys)

            return True

    def __init__(self, name=None):
        """initialize

        name -- name of plot
        """
        if name is None:
            name = 'Plot [%i]' % Plotter.__plotWindowNumber

        PDFComponent.__init__(self, name)
        import threading
        self.lock = threading.RLock()
        self.curves = []
        self.window = None
        self.isShown = False
        from diffpy.pdfgui.control.pdfguicontrol import pdfguicontrol
        self.controlCenter = pdfguicontrol()

        # add some flavor by starting with random style
        import random
        self.symbolStyleIndex = random.randint(0,100)
        self.lineStyleIndex = random.randint(0,100)
        return

    def close(self, force=True):
        """close up the plot

        force -- if True, close forcibly
        """
        if self.window is not None:
            #self.window.Close(True)
            self.window.Destroy()
            self.window = None

    def onWindowClose(self):
        """get called when self.window is closed by user
        """
        self.window = None
        try:
            self.controlCenter.plots.remove(self)
        except ValueError:
            # if controlCenter doesn't know me, I'm just fine to bail out
            pass

    def buildSymbolStyle(self, index=-1):
        """generate a symbol style

        index -- plotting style index
        """
        # To build different symbol style, we first change color then the symbol
        i = index
        if i == -1:
            i = self.symbolStyleIndex
            self.symbolStyleIndex += 1

        symbolIndex = i % len(symbols)
        colorIndex = i % len(colors)
        return {'with':'points',
               'color':colors[colorIndex],
               'symbolColor':colors[colorIndex],
               'symbol':symbols[symbolIndex],
               'symbolSize':3}

    def buildLineStyle(self, index=-1):
        """generate a line style

        index -- plotting style index
        """
        # To build different line style, we first change color then the line
        i = index
        if i == -1:
            i = self.lineStyleIndex
            self.lineStyleIndex += 1

        lineIndex = i % len(lines)
        colorIndex = i % len(colors)
        return {'with':'lines',
               'color':colors[colorIndex],
               'line':lines[lineIndex],
               'width':2}

    def buildLineSymbolStyle(self, index=-1):
        """generate a linesymbol style

        index -- plotting style index
        """
        style = self.buildLineStyle(index)
        style.update(self.buildSymbolStyle(index))
        style['with'] = 'linespoints'
        return style

    def plot(self, xName, yNames, ids,  shift, dry):
        """Make a 2D plot

        xName --  x data item name
        yNames -- list of y data item names
        ids --    Objects where y data items are taken from
        shift -- y spacing for different ids
        dry -- dry run
        """
        def _addCurve(dataIds):
            # Identify the plot type. This is used to automatically modify
            # 'Gdiff' and 'crw' in certain types of plots.
            yset = set(yNames)
            if 'Gdiff' in yset: yset.remove('Gdiff')
            if 'crw' in yset: yset.remove('crw')

            # add yNames one by one for given dataIds
            for y in yNames:
                _offset = offset
                legend = None
                style = None
                if not dry:
                    if len(dataIds) == 1 and group != -1:
                        #legend = dataIds[0].name  + ": " + _transName(y)
                        legend = _fullName(dataIds[0]) + ": " + _transName(y)
                    else:
                        # 1.Group = -1, multiple ids give a single curve
                        # 2.there is only one dataId so that prefix unneeded
                        legend = _transName(y)

                    style = _buildStyle(self, y, group, yNames)
                    style['legend'] = legend

                    # automatically apply offset if we're plotting more than
                    # just 'Gdiff' and 'crw'
                    if y in ('Gdiff','crw') and group == -1 and len(yset) > 0:
                        _offset = shift
                #Create curve, get data for it and update it in the plot
                curve = Plotter.Curve(legend, self.window, xName, y,
                                      step, dataIds, _offset, style)
                self.curves.append(curve)
            return

        if not ids: # empty
            raise ControlConfigError("Plotter: No data is selected")
        if not yNames:
            raise ControlConfigError("Plotter: No y item is selected")

        # bSeparateID indicates if we want data from different ID to be
        # plotted in different curve or not
        bSeparateID = False
        if len(ids) > 1 and xName in ('r', 'rcalc', 'step'):
            # multi ID and within each ID we wants a vector, so curve can
            # only be plotted separately.
            bSeparateID = True

        # set up the step
        if xName == 'step':
            step = None
        else:
            step = -1

        self.curves = []

        if 'Gcalc' in yNames:
            yNames.remove('Gcalc')
            yNames.append('Gcalc')

        # default is no shift, single group.
        offset = 0.0
        group = -1
        if bSeparateID:
            for id in ids:
                group += 1
                _addCurve([id,])
                offset += shift
        else:
            _addCurve(ids)

        # clean up, it's only a dry run
        if dry:
            self.curves = []
            return

        # Real plot starts
        if self.window is None:
            # plotWindown may either not be ready or it has been closed
            self.window = ExtendedPlotFrame(self.controlCenter.gui)
            Plotter.__plotWindowNumber += 1
            self.window.plotter = self
        else:
            self.window.clear()

        for curve in self.curves:
            #Initial notification, don't plot immediately, wait for last line to be added
            #This is to optimize plotting multiple curves.
            curve.notify(plotwnd=self.window)

        # make the graph title, x, y label
        yStrs = [_transName(yName) for yName in yNames]
        if yStrs[0].startswith('G'):
            #then all are Gs
            yLabel = 'G'
        else:
            yLabel = ','.join(yStrs)
        title = ''
        if len(ids) == 1:
            title = ids[0].name + ': '
        title += yLabel
        self.window.setTitle(self.name+' '+title, title)
        self.window.setXLabel(_transName(xName))
        self.window.setYLabel(yLabel)

        # show the graph
        self.window.replot()
        self.show(True)


    def show(self, bShow=None) :
        """show the plot on screen

        bShow -- True to show, False to Hide. None to toggle
        return value: current status of window
        """
        if self.window is None:
            raise ControlStatusError("Plot: %s has no window" % self.name)
        if bShow is None:
            bShow = not self.isShown
        self.window.Show(bShow)
        if bShow: # True
            # further bring it to top
            self.window.Raise()
        self.isShown = bShow
        return self.isShown

    def notify(self, data):
        '''change of the data is notified

        data -- data object that has changed
        '''
        if not self.curves or self.window is None:
            return
        ret = False
        for curve in self.curves:
            ret |= (curve.notify(changedIds=[data,]))
        if ret:
            self.window.replot()

    def export(self, filename):
        '''export current data to external file

        filename -- the name of the file to save data
        '''
        # Check if any curve
        if len(self.curves) == 0:
            return
        import time, getpass
        outfile = open(filename, 'w')
        header = "# Generated on %s by %s.\n" % (time.ctime(), getpass.getuser())
        header += "# This file was created by PDFgui.\n"
        outfile.write(header)
        deblank = lambda s: ''.join(s.split())
        xylist = [(c.x, c.y) for c in self.curves]
        xynames = [(_transName(c.xStr), deblank(c.name))
                for c in self.curves]
        _exportCompactData(outfile, xylist, xynames)
        outfile.close()
        return

# End of class Plotter


def _exportCompactData(fp, xylist, xynames=None):
    '''Write the xylist data in a text format to the file object fp.
    The curves with the same x are groupped in the same datasets.
    The datasets are marked with "#S 1", "#S 2", etc. labels according
    to the spec format http://www.certif.com/cplot_manual/ch0c_C_11_3.html

    fp       -- file type object that is writable
    xylist   -- list of (x, y) tuples of x and y arrays.  Items with
                empty x or empty y are ignored.
    xynames  -- list of tuples of (xname, yname) strings.  These are
                used as a header in the dataset blocks.

    No return value.
    '''
    dataformat = '%g'
    # build the default xynames:
    if xynames is None:
        xynames = [('x%i' % i, 'y%i' % i) for i in range(len(xylist))]
    datasets = []
    datanames = []
    xt2idx = {}
    for ((x, y), (xn, yn)) in zip(xylist, xynames):
        if x is None or not len(x):  continue
        if y is None or not len(y):  continue
        xt = tuple(x)
        i = xt2idx.setdefault(xt, len(xt2idx))
        if not i < len(datasets):
            datasets.append([])
            datanames.append([])
        ds = datasets[i]
        dn = datanames[i]
        if not ds:
            ds.append(x)
            dn.append(xn)
        ds.append(y)
        dn.append(yn)
    for i, (ds, dn) in enumerate(zip(datasets, datanames)):
        # separate datasets with a blank line:
        if i > 0:
            fp.write('\n')
        fp.write('#S %i\n' % (i + 1))
        fp.write('#L %s\n' % ('  '.join(dn)))
        ncols = len(ds)
        fmt = ' '.join(ncols * [dataformat]) + '\n'
        for cols in zip(*ds):
            line = fmt % cols
            fp.write(line)
    return

# End of file
