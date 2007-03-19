#!/usr/bin/env python
########################################################################
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
########################################################################

from pdfcomponent import PDFComponent
from pdfgui.gui.extendedplotframe import ExtendedPlotFrame
from controlerrors import *

# Preset plotting style
colors = ("red","blue","black","magenta","cyan","green","yellow",
   "darkRed","darkBlue","darkMagenta", "darkCyan", "darkGreen","darkYellow")
lines = ('solid','dash','dot','dashDot')
symbols = ("circle","square","triangle","diamond")#,"cross","xCross")

# this is to map 'r' to what it is supposed to be. For example, when user asks 
# for plotting 'Gobs' against 'r', the real data objects are 'Gobs' and 'robs' 
transdict = { 'Gobs':'robs', 'Gcalc':'rcalc','Gdiff':'rcalc','Gtrunc':'rcalc'}
baselineStyle = {'with':'lines','line':'solid','color':'black','width':1, 'legend':'baseline'}
def _transName( name ):
    '''translate name of y object
    
    This is mainly for plotting of parameters. GUI will pass in a integer to 
    indicate which parameter to be plotted. However, in data storage the 
    parameter is denoted as '@n'
    
    name -- name of data item
    '''
    if isinstance(name, int):
        return '@'+str(name)
    else:
        return str(name)
        
def _buildStyle(plotter, name, group):
    '''trying to figure out a good style
    
    1. generally we want line style for Gcalc and Gdiff, symbol style for Gobs,
    and line-symbol style for the rest
    2. there is a preferred style for plotting a single PDF curve
    
    plotter -- A plotter instance
    name -- what is to be plotted ( y name)
    group -- which group the curve is in( group = -1 means it is the only group)
    return: style dictionay
    '''
    if name in ( 'Gcalc', 'Gdiff'): 
        style = plotter.buildLineStyle()
        style['line'] = 'solid'
    elif name in ('Gobs', 'Gtrunc'):
        style = plotter.buildSymbolStyle()
    else:
        style = plotter.buildLineSymbolStyle()
        style['line'] = 'dot'
        
    # We only care about how to arrange Gdiff Gobs Gcalc Gtrunc nicely
    if group < 0:
        # use fixed style for single PDFFit picture
        if name == 'Gcalc':
            style['color'] = 'red'
            style['line']  = 'solid'
        elif name in ('Gobs', 'Gtrunc'):
            style['color'] = 'blue'
            style['symbolColor'] = 'blue'
            style['symbol'] = 'circle'
        elif name == 'Gdiff':
            style['color'] = 'green'
            style['line']  = 'solid'
    else:
        # make sure Gcalc and Gobs are having same color
        if name in ('Gcalc', 'Gdiff', 'Gobs', 'Gtrunc'):
            color = colors[group%len(colors)]
            style['color'] = color
            style['symbolColor'] = color
        if name == 'Gdiff':
            style['line'] = 'dot'
            
    return style
        
class Plotter(PDFComponent):
    """Plots a single graph. It can have multiple curves. """
    UniqueSequence = 0

    class Curve:
        """Curve stores the information for a curve in the plot
        
        There are three ways of forming x and y data lists.
        (1) r and g(r) from a single refinement are vectors by themselves
        (2) A scalar data item ( any item other than r and g(r) ) can form a 
        vector if multiple timeSteps (refinement steps) are specified.
        (3) A scalar data item ( any item other than r and g(r) ) can form a 
        vector if multiple refinement ( multiple ids ) are specified 
        
        name  -- The curve name
        plotwnd -- The window where the curve is drawn
        xStr -- Data name (string) for x axis
        yStr -- Data name (string) for y axis
        steps -- refinement step list
        ids -- The list of object ids that the curve is related to
        shift -- curve displacement in y direction
        style --The drawing style of the curve        
        xData, yData -- data to be plotted
        x, y -- original data for exporting ( curve could be shifted)
        bMultiData -- if the curve data comes from multiple data objects
        bMultiStep -- if the curve data comes from multiple refinement step
        ref -- reference of curve in the plot window
        initialized -- if curve has been inserted
        dataChanged -- if curve data has changed
        """
        def __init__(self, name, plotwnd, xStr, yStr, steps, ids, shift, style):
            """initialize
            
            name  -- The curve name
            plotwnd -- The window where the curve is drawn
            xStr -- Data name (string) for x axis
            yStr -- Data name (string) for y axis
            steps -- refinement step list
            ids -- The list of object ids that the curve is related to
            shift -- curve displacement in y direction
            style --The drawing style of the curve
            """
            self.name = name
            self.plotwnd = plotwnd
            self.ids = ids
            self.steps = steps
            self.xStr = xStr
            self.yStr = yStr
            self.shift = shift
            self.style = style
            
            self.bMultiData = len ( self.ids ) > 1
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
            
        def validate (self ):
            """ validate (self ) --> check if  the curve is valid. Validity 
            is broken:
            (1) when xStr or yStr doesn't refer to a legal vector 
            (2) when sizes of xStr and yStr don't match
            """
            bItemIsVector = False
            if self.xStr in ( 'r', 'rcalc', 'robs'):
                if self.yStr not in ('Gobs', 'Gcalc', 'Gdiff', 'Gtrunc'):
                    raise  ControlConfigError, "x=%s, y=%s don't match"\
                           %(self.xStr, self.yStr)
                bItemIsVector = True
            elif self.xStr in ('Gobs', 'Gcalc', 'Gdiff', 'Gtrunc'):
                raise ControlConfigError, "%s can't be x axis"\
                        %self.xStr
            elif self.yStr in ('Gobs', 'Gcalc', 'Gdiff', 'Gtrunc'):
                # Get called when x is not r but y is not Gobs, Gtrunc Gdiff...
                raise ControlConfigError, "%s can only be plotted against r"\
                    %self.yStr
            
            # There are three booleans
            # (1) bItemIsVector 
            # (2) self.ids has only one element
            # (3) self.allSteps 
            # The logic below make sure only one of them can be true.
            if bItemIsVector:
                if  self.bMultiData or self.bMultiStep:
                    raise ControlConfigError,\
                "(%s, %s) can't be plotted with mulitple refinements/steps"%\
                (self.xStr, self.yStr)
            else:
                if  not self.bMultiData and not self.bMultiStep:
                    raise ControlConfigError,\
                "(%s, %s) is a single point"%(self.xStr, self.yStr)
                elif self.bMultiData and self.bMultiStep:
                    raise ControlConfigError,\
                "(%s, %s) can't be plotted with both multiple refinements and multiple steps"%\
                (self.xStr, self.yStr)
                    
        def register (self ):
            """Register self as dataListener in control center
            """
            self.controlCenter = controlCenter 
            for id in self.ids:
                #self.plot.name -- the name of listener object
                #self.name      -- the data for listener object
                #controlCenter.registerListener(dataId,self.plot.name,self.name)
                pass
                
        def notify( self, changedIds, bUpdate = True):
            """notify Curve object certain data is updated
            
            changedIds -- objects to which changed data is associated with
            bUpdate -- if update the plot immediately. If set to false, change 
                       will not be plotted until user call replot() function of 
                       plot window explicitly.
            """             
            # find affected ids
            affectedIds = []
            for id in self.ids:
                for changedId in changedIds:
                    if  ( id  is changedId ) or ( id.owner is changedId ): 
                        affectedIds.append(id)
                        break
                        
            #If the change doesn't affect any id, do nothing
            if not affectedIds:
                return
            
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
                        raise AssertionError, "Can not plot against step"
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
                        self.xData = range(len(self.yData))
                else:
                    self.xData = affectedIds[0].getData(xStr, steps)
                    
                self.x = self.xData
                self.y = self.yData
    
                def _shift ( y ):
                    return y + self.shift
    
                if self.yData and self.shift: # not zero
                    self.yData = map ( _shift, self.yData)

            if self.xData and self.yData: # not empty or None
                self.draw(bUpdate)
                        
        def draw(self, bUpdate):
            """draw the curve in the graph. It will make sure the data is OK, 
            and plot to the screen.
            
            bUpdate -- if update the plot immediately 
            """
            if self.bMultiData:
                # xs and ys initialize here. They are actual data object to be 
                # used for plotting
                xs = []
                ys = []
                plotData = zip(self.xData,self.yData)
                plotData.sort()
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
                return
        
            # If it can get here, data is ready now.
            if not self.initialized:
                # need insert a curve first.
                self.initialized = True
                self.ref = self.plotwnd.insertCurve(xs, ys, self.style, bUpdate)
            else:
                # update only
                self.plotwnd.updateData(self.ref, xs, ys)

    def __init__(self, name = None):
        """initialize
        
        name -- name of plot
        """
        if name is None:
            name = 'Plot[%i]'%Plotter.UniqueSequence
            Plotter.UniqueSequence += 1
            
        PDFComponent.__init__(self, name)
        import threading
        self.lock = threading.RLock()
        self.curves = []
        self.window = None
        self.isShown = False
        from pdfguicontrol import pdfguicontrol
        self.controlCenter = pdfguicontrol()
        
        # add some flavor by starting with random style
        import random
        self.symbolStyleIndex = random.randint(0,100)
        self.lineStyleIndex = random.randint(0,100)
        return
    
    def close ( self, force = True ):
        """close up the plot
        
        force -- if True, close forcibly
        """
        # NOTE: Not gonna be called because gui has no way of doing this
        if self.window is not None:
            #self.window.Close(True)
            #self.window.Destroy()
            pass
            
    def onWindowClose(self):
        """get called when self.window is closed by user
        """
        self.window = None
        try:
            self.controlCenter.plots.remove(self)
        except ValueError:
            # if controlCenter doesn't know me, I'm just fine to bail out
            pass 
            
    def buildSymbolStyle (self, index = -1 ):
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
               
    def buildLineStyle (self, index = -1 ):
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
                   
    def buildLineSymbolStyle ( self, index = -1):
        """generate a linesymbol style
        
        index -- plotting style index
        """
        style = self.buildLineStyle(index)
        style.update(self.buildSymbolStyle(index))
        style['with'] = 'linespoints'
        return style
        
    def plot ( self, xName, yNames, ids,  spacing = 1.0):
        """Make a 2D plot
        
        xName --  x data item name
        yNames -- list of y data item names
        ids --    Objects where y data items are taken from
        spacing -- y spacing for different ids
        """
        def _addCurve(dataIds):
            # add yNames one by one for given dataIds
            
            # firstly we don't want to change global shift
            _shift = shift 
            for y in yNames:
                if len(dataIds) == 1 and group != -1:
                    legend = dataIds[0].name  + ": " + _transName(y)
                else:
                    # curve point is taken from multidata, no prefix applicable 
                    # or there is only one dataIds so that prefix unneeded
                    legend = _transName(y)
                
                style = _buildStyle(self, y, group)
                style['legend'] = legend
               
                #NOTE: to deal with user's request
                if y == 'Gdiff' and group == -1 and len(yNames) != 1: 
                    # add a baseline
                    rs = dataIds[0].rcalc
                    if not rs:
                        rs = dataIds[0].robs
                    hMin = min(rs)
                    hMax = max(rs)

                    # Find the value of the baseline
                    GobsMin = min(dataIds[0].Gobs)
                    GcalcMin = min(dataIds[0].Gcalc)
                    GMin = min(GobsMin, GcalcMin)
                    GdiffMax = max(dataIds[0].Gdiff)
                    vMin = 1.1*(GMin - GdiffMax)
                    
                    self.window.insertCurve([hMin, hMax], [vMin, vMin], baselineStyle)
                    _shift = vMin
                    
                #Create curve, get data for it and update it in the plot
                curve = Plotter.Curve(legend, self.window, xName, y,
                                      step, dataIds, _shift, style)
                #Initial notification, at this moment don't plot immediately. 
                #This is to optimize plotting multiple curves.
                curve.notify(dataIds, False)
                self.curves.append(curve)
            return 
            
        if not ids: # empty
            raise ControlConfigError, "Plotter: No data is selected"
        if not yNames:
            raise ControlConfigError, "Plotter: No y item is selected"
        
        # bSeparateID indicates if we want data from different ID to be 
        # plotted in different curve or not
        bSeparateID = False
        if len(ids) > 1 and xName in ( 'r', 'rcalc', 'step' ):
            # multi ID and within each ID we wants a vector, so curve can
            # only be plotted separately.
            bSeparateID = True
            
        # set up the step
        if xName == 'step':
            step = None
        else:
            step = -1
                
        try:
            self.lock.acquire()
            self.curves = []
            
            if self.window is None:
                # plotWindown may either not be ready or it has been closed
                self.window = ExtendedPlotFrame(self.controlCenter.gui)
                self.window.plotter = self
            else:
                self.window.clear()
            
            # default is no shift, single group.
            shift = 0.0
            group = -1
            if bSeparateID:
                for id in ids:
                    group += 1
                    _addCurve([id,])
                    shift += spacing
            else:
                _addCurve(ids)
            
            # make the graph title, x, y label
            yLabel = ','.join([_transName(yName) for yName in yNames])
            title = ''
            if len(ids) == 1:
                title += ' '+ ids[0].name + ':' 
            title += yLabel
            self.window.setTitle(self.name+' '+title, title)
            self.window.setXLabel( _transName(xName) )
            self.window.setYLabel( yLabel )
            
            # show the graph
            self.window.replot()
            self.show(True)
            
        finally:
            self.lock.release()

    def show ( self, bShow = None) :
        """show the plot on screen
        
        bShow -- True to show, False to Hide. None to toggle
        return value: current status of window
        """
        try:
            self.lock.acquire()
            if self.window is None:
                raise ControlStatusError, "Plot: %s has no window"%self.name
            if bShow is None:
                bShow = not self.isShown
            self.window.Show(bShow)
            if bShow: # True 
                # further bring it to top
                self.window.Raise()
            self.isShown = bShow        
            return self.isShown
        finally:
            self.lock.release()
        
    def notify ( self , data ):
        '''change of the data is notified
        
        data -- data object that has changed
        '''
        try:
            self.lock.acquire()
            if not self.curves or self.window is None:
                return   
            for curve in self.curves:
                curve.notify([data,])
        finally:
            self.lock.release()

    def export( self, filename):
        '''export current data to external file
        
        filename -- the name of the file to save data
        '''
        # Check if any curve
        if len(self.curves) == 0:
            return
        import time,getpass
        outfile = open(filename, 'w')
        header = "# Generated on %s by %s.\n" % (time.ctime(), getpass.getuser())
        header += "# This file generated by PDFgui.\n"
        outfile.write(header)
        
        # write curve data one by one
        for curve in self.curves:
            if curve.x and curve.y:
                description = "#L " + curve.xStr + " " + curve.yStr + "\n"
                outfile.write(description)
                for a,b in zip(curve.x,curve.y):
                    line =  "%10.8f %10.8f\n"%(a,b)
                    outfile.write(line)
                # additional newline to separate different curve data
                outfile.write('\n')
                
        outfile.close()        
# version
__id__ = "$Id$"

# End of file
