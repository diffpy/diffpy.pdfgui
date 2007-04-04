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

from organizer import Organizer
from threading import Event, Thread
from controlerrors import *
from pdfstructure import PDFStructure
from pdfdataset import PDFDataSet

class Fitting(Organizer):
    """Fitting is the class to control a PdfFit process, which can be either 
    running on a remote machine or locally. Fitting will start a thread to 
    interact with the PdfFit server using ssh2 and XMLRPC protocol. 
    
    rw:         fitness parameter
    tolerancy:  accurancy requirement
    step:       current refinement step
    res:        fitting result string
    parameters: parameter dictionary
    """
    #Fit status -- mask 0xff
    INITIALIZED = 1
    CONNECTED   = 1<<1
    CONFIGURED  = 1<<2
    DONE        = 1<<3
    
    #JOB Status -- mask 0xff00
    VOID        = 1<<8
    QUEUED      = 1<<9
    RUNNING     = 1<<10
    PAUSED      = 1<<11

    class Worker ( Thread ):
        """Worker is the daemon thread of fitting"""
        def __init__( self, fitting ):
            """Worker ( self, fitting) --> initialize
            
            fitting -- fitting object
            """
            Thread.__init__(self)
            self.fitting = fitting
            
        def run ( self ):
            """overload function from Thread """
            from diffpy.pdffit2.pdffit2 import dataError, unassignedError,\
                constraintError, structureError, calculationError
            try:
                self.fitting.run()
            except ControlError,error:
                gui = self.fitting.controlCenter.gui
                if gui:
                    gui.postEvent(gui.ERROR, "<Fitting exception> %s"%error.info)
                else:
                    print "<Fitting exception> %s"%error.info
            except (dataError,unassignedError,constraintError,
                     structureError, calculationError), error:
                gui = self.fitting.controlCenter.gui
                errorInfo = "(%s)%s"%(error.__class__.__name__, str(error))
                if gui:
                    gui.postEvent(gui.ERROR, "<Engine exception> %s"%errorInfo)
                else:
                    print "<Engine exception> %s"%errorInfo
                
    def __init__(self, name):
        """initialize
        
        name -- name of this fitting
        """
        Organizer.__init__(self, name)
                
        # Thread, status, and control variables 
        self.thread = None
        self.pauseEvent = Event()
        self.fitStatus = Fitting.INITIALIZED
        self.jobStatus = Fitting.VOID
        self.stopped = False
        self.paused = False
                    
        # rpc memeber
        self.host = None
        self.server = None 
        
        # public data members
        self.step = 0
        self.parameters = {}
        self.rw = 1.0
        self.tolerancy = 0.001
        self.res = ''
        self.snapshots = []
        self.res = ''

        # All the calculated data are to be stored in a list.
        # Such flat storage require unique index for each data item
        # self.dataNameDict translate named data to an index
        self.dataNameDict = {}
        self.itemIndex = 0
        
    def __changeStatus(self, fitStatus = None, jobStatus = None):
        """change current status of fitting
        
        fitStatus -- new  fitting status
        jobStatus -- new thread status
        """
        self.fitStatus = fitStatus or self.fitStatus
        self.jobStatus = jobStatus or self.jobStatus
        if fitStatus or jobStatus: # either of them is not None
            gui = self.controlCenter.gui
            if gui:
                gui.postEvent(gui.UPDATE, self)
                gui.postEvent(gui.OUTPUT, None)
                
    def __release(self):
        """release resources"""
        if self.host: # is not None (running on a remote server)
            self.host.releaseServer(self.server)
            self.host = None
        
    def _getStrId(self):
        """make a string identifier
        
        return value: string id
        """
        return "f_" + self.name

    def copy(self, other = None):
        """copy self to other. if other is None, create an instance
        
        other -- ref to other object
        return value: reference to copied object
        """
        if other is None:
            other = Fitting(self.name)
        import copy
        Organizer.copy(self, other)
        other.parameters = copy.deepcopy(self.parameters)
        other.snapshots = copy.deepcopy(self.snapshots)
        other.res = copy.deepcopy(self.res)
        other.dataNameDict = copy.deepcopy(self.dataNameDict)
        other.itemIndex = self.itemIndex
        return other

    def load ( self, z, subpath):
        """load data from a zipped project file

        z -- zipped project file
        subpath -- path to its own storage within project file

        returns a tree of internal hierachy
        """
        # subpath = projName/fitName/
        subs = subpath.split('/')
        rootDict = z.fileTree[subs[0]][subs[1]]

        import cPickle
        if rootDict.has_key('parameters'):
            from pdfguicontrol import CtrlUnpickler
            self.parameters = CtrlUnpickler.loads(z.read(subpath+'parameters'))
        if rootDict.has_key('steps'):
            self.itemIndex, self.dataNameDict, self.snapshots = \
                    cPickle.loads(z.read(subpath+'steps'))
        if rootDict.has_key('result'):
            self.rw, self.res = cPickle.loads(z.read(subpath+'result'))

        return Organizer.load(self, z, subpath)

    def save ( self, z, subpath ):
        """save data from a zipped project file

        z -- zipped project file
        subpath -- path to its own storage within project file
        """
        import cPickle
        if self.parameters:
            bytes = cPickle.dumps(self.parameters, cPickle.HIGHEST_PROTOCOL)
            z.writestr(subpath + 'parameters', bytes)
        if self.res:
            bytes = cPickle.dumps((self.rw, self.res), cPickle.HIGHEST_PROTOCOL)
            z.writestr(subpath + 'result', bytes)
        if self.snapshots:
            bytes = cPickle.dumps((self.itemIndex, self.dataNameDict,
                               self.snapshots), cPickle.HIGHEST_PROTOCOL)
            z.writestr(subpath + 'steps', bytes)
        Organizer.save(self, z, subpath)
        return

    def stripped(self):
        """Make a copy stripped of all unpickleable data members.
        The copy should be suitable for pickling and has the
        following data members removed:
            controlCenter, lock, pauseEvent, thread
        
        returns reference to stripped copy
        """
        unpickleables = ( 'controlCenter', 'lock', 'pauseEvent', 'thread' )
        naked = self.copy()
        for a in unpickleables:
            if a in self.__dict__:
                delattr(naked, a)
        return naked

    def updateParameters(self):
        """Update parameters dictionary from active constraints.

        returns self.parameters
        """
        # create dictionary of parameters used in constraints
        cpars = {}
        for struc in self.strucs:
            for idx, par in struc.findParameters().iteritems():
                if idx not in cpars:
                    cpars[idx] = par
        for dataset in self.datasets:
            for idx, par in dataset.findParameters().iteritems():
                if idx not in cpars:
                    cpars[idx] = par
        # add new parameters
        for idx, par in cpars.iteritems():
            if idx not in self.parameters:
                self.parameters[idx] = par
        # remove unused parameters
        unused = [ idx for idx in self.parameters if idx not in cpars ]
        for idx in unused:
            del self.parameters[idx]
        return self.parameters

    def applyParameters(self):
        """Evaluate all constrained variables using current parameters.
        """
        for struc in self.strucs:
            struc.applyParameters(self.parameters)
        for dataset in self.datasets:
            dataset.applyParameters(self.parameters)
        return

    def changeParameterIndex(self, oldidx, newidx):
        """Change a parameter index to a new value.

        This will replace all instances of one parameter name with another in
        the containing fit.
        """
        # Change the index in the current structure
        for struc in self.strucs:
            struc.changeParameterIndex(oldidx, newidx)
        for dataset in self.datasets:
            dataset.changeParameterIndex(oldidx, newidx)

        # Change the index if appears in linking equation initial values, e.g.
        # '=thisfitname:oldidx' -> '=thisfitname:newidx'
        fiteq = "=%s:%i" % (self.name, oldidx)
        newfiteq = "=%s:%i" % (self.name, newidx)

        from pdfguicontrol import pdfguicontrol
        fits = pdfguicontrol().fits
        for fit in fits:
            parameters = fit.parameters
            for par in parameters.itervalues():
                if par.initialStr() == fiteq:
                    par.setInitial(newfiteq)

        return
          
    def queue(self, enter = True ):
        """queue or dequeue self
        
        enter -- True to queue, False to dequeue
        """
        if enter:
            if self.jobStatus == Fitting.VOID:
                self.__changeStatus(jobStatus=Fitting.QUEUED)
        else:
            if self.jobStatus == Fitting.QUEUED:
                self.__changeStatus(jobStatus=Fitting.VOID)
        
    def connect(self):
        """start PDFServer.py process and connect to it.  PDFServer.py must
        be on the PATH of the host machine.
        """
        if self.fitStatus != Fitting.INITIALIZED:
            return 
           
        self.host = self.controlCenter.getHost()
        if self.host is None:
            # import directly from local host
            from diffpy.pdffit2.PdfFit import PdfFit
            self.server = PdfFit()
        else:
            # get server without waiting.
            self.server = self.host.getServer()
                
        self.__changeStatus(fitStatus=Fitting.CONNECTED)
                                    
    def configure(self):
        """run configuration for fitting"""        
        if self.fitStatus != Fitting.CONNECTED:
            return
        
        # make sure parameters are initialized
        self.updateParameters()
        self.server.reset()
        for struc in self.strucs:
            struc.clearRefined()
            self.server.read_struct_string(struc.initial.writeStr("pdffit") )
            for key,var in struc.constraints.items():
                self.server.constrain(key.encode('ascii'), var.formula.encode('ascii'))
        
        seq = 1
        for dataset in self.datasets:
            dataset.clearRefined()
            self.server.read_data_string(dataset.writeObsStr(), 
                                         dataset.stype.encode('ascii'), 
                                         dataset.qmax, 
                                         dataset.qsig)
            self.server.setvar('qalp', dataset.qalp)
            self.server.setvar('spdiameter', dataset.spdiameter)
            for key,var in dataset.constraints.items():
                self.server.constrain(key.encode('ascii'), var.formula.encode('ascii'))
            self.server.pdfrange(seq, dataset.fitrmin, dataset.fitrmax)
            seq += 1

        for index, par in self.parameters.items():
            # clean any refined value
            par.refined = None
            self.server.setpar(index, par.initialValue()) # info[0] = init value
            # fix if fixed.  Note: all parameters are free after server.reset().
            if par.fixed:
                self.server.fixpar(index)
                
        # build name dict
        self.buildNameDict()
    
        self.__changeStatus(fitStatus=Fitting.CONFIGURED)

    def calculate(self, calc):
        """calculate speicified calculation
        
        calc -- a calculation object
        """
        try:
            self.connect()
            self.configure()
            calc._calculate()
            
            #NOTE: for reliability, next calculation/fitting should start all over
            self.__changeStatus(fitStatus=Fitting.INITIALIZED)
        finally:
            self.__release()
            
    def resetStatus ( self ):
        """reset status back to initialized"""
        self.snapshots = []
        self.step = 0
        if self.fitStatus == Fitting.INITIALIZED:
            return  # already reset
        self.__changeStatus(fitStatus=Fitting.INITIALIZED)
        
    def run ( self ):
        """function to be run in daemon thread.
        """
        # Begin
        self.__changeStatus ( jobStatus = Fitting.RUNNING )
        try:
            for calc in self.calcs:
                self.calculate(calc)
                
            while not self.stopped:
                if not self.paused:
                    # quick check to make sure status is right
                    # will do nothing if status is CONFIGURED
                    self.connect()
                    self.configure()
                    
                    # if self.refine_step return True, fitting is finished
                    if self.refine_step():
                        break
                else:
                    #Wait on an event, pause for a while
                    self.__changeStatus(jobStatus = Fitting.PAUSED)
                    self.pauseEvent.wait() 
                    
                    # Recover from pause now
                    self.__changeStatus ( jobStatus = Fitting.RUNNING )
                    
        finally:
            # whatever happened, resource should be released.
            self.__release()
        
            # job status should be changed because of thread exit
            self.__changeStatus ( jobStatus = Fitting.VOID)
        
    def pause ( self,  bPause = None ):
        """pause ( self, bPause = None ) --> pause a fitting process
        
        bPause -- True to pause, False to restart. If None, it will figure out 
                by itself.
        """
        if bPause is None:
            bPause = self.jobStatus == Fitting.RUNNING
            
        if bPause:
            self.paused = True
        else:
            self.paused = False
            self.pauseEvent.set()
            
    def start ( self ):
        """start fitting thread """
        # check if paused
        if self.jobStatus == Fitting.PAUSED:
            self.pause(False)
            return 
            
        # Otherwise it should be a new run, in this case firstly cleanup 
        # when user called this function, it must be true that the status 
        # of current thread is not Fitting.RUNNING
        if self.thread is not None:
            self.thread.join()
        
        # clean up control variable
        self.stopped = False
        self.paused = False
        self.resetStatus()
        
        # Restart fitting require another thread instance.
        self.thread = Fitting.Worker(self)
        self.thread.start()
        
    def stop ( self ):
        """stop the fitting process"""        
        self.stopped = True
        
        # wake up daemon thread if it is paused
        if self.jobStatus == Fitting.PAUSED:
            self.pause(False)
            
    def isThreadRunning ( self ):
        """check if fitting thread is running
        
        return: True if running, False otherwise
        """
        return self.thread is not None and self.thread.isAlive()
            
    def close ( self, force = False ):
        """close up the fitting in order to exit

        force -- if force to exit
        """        
        if force:
            if self.isThreadRunning():
                self.stop()
                #NOTE: Not waiting for thread to stop. There's no graceful
                #      way while user choose to stop forcefully
        else:
            if self.isThreadRunning():
                raise ControlStatusError,\
                "Fitting: Fitting %s is still running"%self.name
            if self.thread is not None:    
                self.thread.join()        

    def buildNameDict(self):
        """build up a data name dictionary, which will map data name to a
        unique index
        
        The private dataNameDict has such strcture:
        { 'd_data1':{'Gobs':12, 'Gcalc':11, ....},
          'd_data2':{'Gobs':10, 'Gcalc':9, ....},
          ...
          'p_ph1':{'lat(1)':1,'lat(2)':2, .....},
          'p_ph1':{'lat(1)':3,'lat(2)':4, .....},
          ...
          'f_fit':{'rw':100, 1:101, 2:102}
        }
        
        The value of each sub-dict is the corresponding index of this data
        item in the snapshot.
        The prefix d_ p_ f_ make dataset,struc,fitname unique within the 
        shared name space of dictionary
        """
        self.itemIndex = 0
        dataNameDict = {}
        
        #dataNameDict for datasets
        for dataset in self.datasets:
            id = dataset._getStrId()
            dataNameDict[id] = {}
            for itemName in dataset.constraints.keys() + ['Gcalc',]:
                dataNameDict[id][itemName] = self.itemIndex
                self.itemIndex += 1
        
        # dataNameDict for strucs
        for struc in self.strucs:
            id = struc._getStrId()
            dataNameDict[id] = {}
            for itemName in struc.constraints.keys():
                dataNameDict[id][itemName] = self.itemIndex
                self.itemIndex += 1

        # dataNameDict for self
        id = self._getStrId()
        dataNameDict[id] = {}
        dataNameDict[id]['rw'] = self.itemIndex
        self.itemIndex += 1
        for parameter in self.parameters.keys():
            dataNameDict[id][parameter] = self.itemIndex
            self.itemIndex += 1
    
        # assign to self
        self.dataNameDict = dataNameDict

    def appendStep (self, source):
        """after a refinement step is done, append all data from self to the 
        historical storage, i.e., self.snapshots        
        
        source -- where to get the fitted data, in deed it's a PdfFit2 instance
        """
        # self.itemIndex should store total number of items
        snapshot = [None] * self.itemIndex
        
        # update datasets
        seq = 1 
        for dataset in self.datasets:
            id = dataset._getStrId()
            # set current dataset
            source.setdata(seq)
            # use nameDict for current dataset
            nameDict = self.dataNameDict[id]
            # get values for constrained variables
            for name in dataset.constraints.keys():
                snapshot[nameDict[name]] = source.getvar(name)
            
            snapshot[nameDict['Gcalc']] = dataset.Gcalc
            seq += 1
        
        # udpate strucs
        seq = 1
        for struc in self.strucs:
            id = struc._getStrId()
            #set current struc
            source.setphase(seq)
            # use nameDict for current struc
            nameDict = self.dataNameDict[id]
            # get values for constrained variables
            for name in struc.constraints.keys():
                snapshot[nameDict[name]] = source.getvar(name)
            seq += 1
            
        # update global data
        id = self._getStrId()
        nameDict = self.dataNameDict[id]
        snapshot[nameDict['rw']] = self.rw
        for parameter in self.parameters.keys():
            snapshot[nameDict[parameter]] = source.getpar(parameter)
            
        self.snapshots.append(snapshot)

    def refine_step(self):
        """Run a single step of the fit.

        return value: True if refinement is finished, otherwise False 
        """
        if self.fitStatus == Fitting.DONE:
            # do nothing but return finished
            return True
        
        finished =  self.server.refine_step(self.tolerancy)
        
        # get fitted data 
        idataset = 1
        for dataset in self.datasets:
            dataset.obtainRefined(self.server, idataset)
            idataset += 1
        
        # get refined structure
        istruc = 1
        for struc in self.strucs:
            struc.obtainRefined(self.server, istruc)
            istruc += 1

        # update parameters
        for idx, par in self.parameters.iteritems():
            par.refined = self.server.getpar(idx)
        
        self.rw = self.server.getrw()
       
        self.step += 1
        self.appendStep(self.server)
        
        #update plots and structure renderer
        gui = self.controlCenter.gui
        if gui:
            gui.postEvent(gui.OUTPUT, None)
        try:
            if gui:
                gui.lock()
            for plot in self.controlCenter.plots:
                plot.notify(self)
        finally:
            if gui:
                gui.unlock()
        
        if finished:
            import time
            self.res = "* %s\n\n"%time.ctime()+ self.server.save_res_string()
            self.__changeStatus(fitStatus = Fitting.DONE)
            
        return finished

    def getYNames(self):
        """get names of data item which can be plotted as y
        
        returns a name str list
        """
        names = self.parameters.keys()
        names.append('rw')
        return names
    
    def getXNames(self):
        """get names of data item which can be plotted as x
        
        returns a name str list
        """
        return []

    def getData(self, name, step = -1 ):
        """get self's data member

        name -- data item name
        step -- step info, it can be:
                (1) a number ( -1 means latest step ): for single step
                (2) a list of numbers: for multiple steps
                (3) None: for all steps

        returns data object, be it a single number, a list, or a list of list
        """
        # FIXME: for next plot interface, we need find how many steps the 
        # plotter is requiring for and make exact same number of copies of 
        # data by name
        data = self.getMetaData ( name )
        if data is not None:
            return data
            
        return self._getData(self, name, step )
    
    def getMetaDataNames(self):
        """return all applicable meta data names
        """
        names = []
        for dataset in self.datasets:
            # build up the name list
            if not names:
                names = dataset.metadata.keys()
            else:
                for name in names[:]: 
                    if name not in dataset.metadata.keys():
                        names.remove(name)
        return names
        
    def getMetaData(self, name):
        """get meta data value
        
        name -- meta data name
        returns meta data value
        """
        try:
            return self.datasets[0].metadata[name]
        except (KeyError, IndexError):
            return None

    def _getData ( self, id, name, step = -1 ):
        """get any data member from snapshots

        id   -- reference to a Fitting/Calculation/Phase/DataSet object
        name -- data item name
        step -- step info, it can be:
                (1) a number ( -1 means latest step ): for single step
                (2) a list of numbers: for multiple steps
                (3) None: for all steps

        returns data object, be it a single number, a list, or a list of list
        """
        # find the unique index
        if len(self.snapshots) == 0:
           return None 
        try:
            # if it is a 'int', it must be parameter. So only fitting has its value.
            if isinstance(name, int): id = self
            nameDict = self.dataNameDict[id._getStrId()]
            index = nameDict[name]
        except KeyError:
            return None # data is not ready

        if step is None:
            return [ snapshot[index] for snapshot in self.snapshots ]
        elif isinstance( step, list):
            return [ self.snapshots[i][index] for i in step ]
        else:
            return self.snapshots[step][index]

# version
__id__ = "$Id$"

# End of file 
