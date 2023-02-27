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

from __future__ import print_function

import threading
import time

from diffpy.pdfgui.control.organizer import Organizer
from diffpy.pdfgui.control.controlerrors import ControlError
from diffpy.pdfgui.control.controlerrors import ControlStatusError
from diffpy.pdfgui.control.controlerrors import ControlValueError
from diffpy.pdfgui.utils import safeCPickleDumps, pickle_loads

# helper routines to deal with PDFfit2 exceptions

def getEngineExceptions():
    """Return a tuple of possible exceptions from diffpy.pdffit2.pdffit2.
    """
    from diffpy.pdffit2.pdffit2 import dataError, unassignedError, \
            constraintError, structureError, calculationError
    engine_exceptions = (
            dataError,
            unassignedError,
            constraintError,
            structureError,
            calculationError,
            )
    return engine_exceptions

def handleEngineException(error, gui=None):
    """Common handler of PDFfit2 engine exceptions.

    error -- instance of PDFfit2 exception
    gui   -- reference to GUI when active
    """
    errorInfo = "(%s)\n%s" % (error.__class__.__name__, str(error))
    # be more verbose for Singular matrix exception
    if "singular matrix" in errorInfo.lower():
        errorInfo += ("\n\n"
                "Common reasons are degeneracy in fit parameters,\n"
                "zero thermal factors or fit range starting at zero.")
    if gui:
        gui.postEvent(gui.ERROR, "<Engine exception> %s" % errorInfo)
    else:
        print("<Engine exception> %s" % errorInfo)
    return

##############################################################################
class Fitting(Organizer):
    """Fitting is the class to control a PdfFit process running locally.
    Fitting will start a new thread to interact with the PdfFit server.

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

    class Worker(threading.Thread):
        """Worker is the daemon thread of fitting"""
        def __init__( self, fitting ):
            """Worker ( self, fitting) --> initialize

            fitting -- fitting object
            """
            threading.Thread.__init__(self)
            self.fitting = fitting

        def run(self):
            """overload function from Thread """
            try:
                self.fitting.run()
            except ControlError as error:
                gui = self.fitting.controlCenter.gui
                if gui:
                    gui.postEvent(gui.ERROR, "<Fitting exception> %s" % error.info)
                else:
                    print("<Fitting exception> %s" % error.info)
            except getEngineExceptions() as error:
                gui = self.fitting.controlCenter.gui
                handleEngineException(error, gui)
            return

    def __init__(self, name):
        """initialize

        name -- name of this fitting
        """
        Organizer.__init__(self, name)

        # Thread, status, and control variables
        self.thread = None
        self.pauseEvent = threading.Event()
        self.fitStatus = Fitting.INITIALIZED
        self.jobStatus = Fitting.VOID
        self.stopped = False
        self.paused = False

        # the PDFfit2 server instance.
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

    def __changeStatus(self, fitStatus=None, jobStatus=None):
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

    def _release(self):
        """release resources"""
        if self.server: # server has been allocated, we need free the memory
            self.server.reset()

    def _getStrId(self):
        """make a string identifier

        return value: string id
        """
        return "f_" + self.name

    def copy(self, other=None):
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

    def load(self, z, subpath):
        """load data from a zipped project file

        z -- zipped project file
        subpath -- path to its own storage within project file

        returns a tree of internal hierachy
        """
        # subpath = projName/fitName/
        subs = subpath.split('/')
        rootDict = z.fileTree[subs[0]][subs[1]]

        if 'parameters' in rootDict:
            from diffpy.pdfgui.control.pdfguicontrol import CtrlUnpickler
            self.parameters = CtrlUnpickler.loads(z.read(subpath+'parameters'))
        if 'steps' in rootDict:
            self.itemIndex, self.dataNameDict, self.snapshots = \
                    pickle_loads(z.read(subpath+'steps'))
        if 'result' in rootDict:
            self.rw, self.res = pickle_loads(z.read(subpath+'result'))

        return Organizer.load(self, z, subpath)

    def save(self, z, subpath):
        """save data from a zipped project file

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        if self.parameters:
            spkl = safeCPickleDumps(self.parameters)
            z.writestr(subpath + 'parameters', spkl)
        if self.res:
            spkl = safeCPickleDumps((self.rw, self.res))
            z.writestr(subpath + 'result', spkl)
        if self.snapshots:
            spkl = safeCPickleDumps(
                    (self.itemIndex, self.dataNameDict, self.snapshots) )
            z.writestr(subpath + 'steps', spkl)
        Organizer.save(self, z, subpath)
        return

    def stripped(self):
        """Make a copy stripped of all unpickleable data members.
        The copy should be suitable for pickling and has the
        following data members removed:
            controlCenter, lock, pauseEvent, thread

        returns reference to stripped copy
        """
        unpickleables = ('controlCenter', 'lock', 'pauseEvent', 'thread')
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
            for idx, par in struc.findParameters().items():
                if idx not in cpars:
                    cpars[idx] = par
        for dataset in self.datasets:
            for idx, par in dataset.findParameters().items():
                if idx not in cpars:
                    cpars[idx] = par
        # add new parameters
        for idx, par in cpars.items():
            if idx not in self.parameters:
                self.parameters[idx] = par
        # remove unused parameters
        unused = [idx for idx in self.parameters if idx not in cpars]
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

        from diffpy.pdfgui.control.pdfguicontrol import pdfguicontrol
        fits = pdfguicontrol().fits
        for fit in fits:
            parameters = fit.parameters
            for par in parameters.values():
                if par.initialStr() == fiteq:
                    par.setInitial(newfiteq)

        return

    def queue(self, enter=True):
        """queue or dequeue self

        enter -- True to queue, False to dequeue
        """
        if enter:
            if self.jobStatus == Fitting.VOID:
                self.__changeStatus(jobStatus=Fitting.QUEUED)
        else:
            if self.jobStatus == Fitting.QUEUED:
                self.__changeStatus(jobStatus=Fitting.VOID)

    def getServer(self):
        """get a PDFfit2 instance either locally or remotely
        """
        if self.fitStatus != Fitting.INITIALIZED:
            return
        # create a new instance of calculation server
        from diffpy.pdffit2 import PdfFit
        self.server = PdfFit()
        self.__changeStatus(fitStatus=Fitting.CONNECTED)


    def configure(self):
        """configure fitting"""
        if self.fitStatus != Fitting.CONNECTED:
            return

        # make sure parameters are initialized
        self.updateParameters()
        self.server.reset()
        for struc in self.strucs:
            struc.clearRefined()
            self.server.read_struct_string(struc.initial.writeStr("pdffit") )
            for key, var in struc.constraints.items():
                self.server.constrain(key, var.formula)

        # phase paramters configured

        for dataset in self.datasets:
            dataset.clearRefined()
            self.server.read_data_string(dataset.writeResampledObsStr(),
                                         dataset.stype,
                                         dataset.qmax,
                                         dataset.qdamp)
            self.server.setvar('qbroad', dataset.qbroad)
            for key,var in dataset.constraints.items():
                self.server.constrain(key, var.formula)
            # Removed call to pdfrange call, because data were already
            # resampled to at fit range.
            #
            # Pair selection applies only to the current dataset,
            # therefore it has to be done here.
            nstrucs = len(self.strucs)
            for phaseidx, struc in zip(range(1, nstrucs + 1), self.strucs):
                struc.applyPairSelection(self.server, phaseidx)

        for index, par in self.parameters.items():
            # clean any refined value
            par.refined = None
            self.server.setpar(index, par.initialValue()) # info[0] = init value
            # fix if fixed.  Note: all parameters are free after self.server.reset().
            if par.fixed:
                self.server.fixpar(index)

        # build name dict
        self.buildNameDict()

        self.__changeStatus(fitStatus=Fitting.CONFIGURED)
        return


    def resetStatus(self):
        """reset status back to initialized"""
        self.snapshots = []
        self.step = 0
        if self.fitStatus == Fitting.INITIALIZED:
            return  # already reset

        # This status will mandate allocation of a new PdfFit instance
        self.__changeStatus(fitStatus=Fitting.INITIALIZED)

    def run(self):
        """function to be run in daemon thread.
        """
        # Begin
        self.__changeStatus(jobStatus=Fitting.RUNNING)
        try:
            for calc in self.calcs:
                calc.start()

            while not self.stopped and self.datasets:
                if not self.paused:
                    # quick check to make sure status is right
                    # will do nothing if status is CONFIGURED
                    self.getServer()
                    self.configure()

                    # if self.refine_step return True, fitting is finished
                    if self.refine_step():
                        break
                else:
                    #Wait on an event, pause for a while
                    self.__changeStatus(jobStatus=Fitting.PAUSED)
                    self.pauseEvent.wait()

                    # Recover from pause now
                    self.__changeStatus(jobStatus=Fitting.RUNNING)

        finally:
            # whatever happened, resource should be released.
            self._release()

            # job status should be changed because of thread exit
            self.__changeStatus ( jobStatus = Fitting.VOID)
        return

    def _configureBondCalculation(self, struc):
        """Prepare server for bond angle or bond length calculation.

        struc   -- instance of PDFStructure

        No return value.
        """
        # struc can be handle to FitStructure.initial
        # let's make sure it is synchronized with current parameters
        self.applyParameters()
        self.getServer()
        self.server.reset()
        strucstr = struc.writeStr("pdffit")
        self.server.read_struct_string(strucstr)
        return


    def outputBondAngle(self, struc, i, j, k):
        """Output bond angle defined by atoms i, j, k.
        The angle is calculated using the shortest lengths ji and jk with
        respect to periodic boundary conditions.

        struc   -- instance of PDFStructure
        i, j, k -- atom indices starting at 1

        No return value.  The result should be automatically added to
        the Output Window, because all server output is sent there.

        Raise ControlValueError for invalid indices i, j, k.
        """
        try:
            self._configureBondCalculation(struc)
            self.server.bang(i, j, k)
            self._release()
        except getEngineExceptions() as error:
            gui = self.controlCenter.gui
            handleEngineException(error, gui)
        except ValueError as error:
            raise ControlValueError(str(error))
        return


    def outputBondLengthAtoms(self, struc, i, j):
        """Output shortest bond between atoms i, j.
        Periodic boundary conditions are applied to find the shortest bond.

        struc   -- instance of PDFStructure
        i, j    -- atom indices starting at 1

        No return value.  The result should be automatically added to
        the Output Window, because all server output is sent there.

        Raise ControlValueError for invalid indices i, j.
        """
        try:
            self._configureBondCalculation(struc)
            self.server.blen(i, j)
            self._release()
        except getEngineExceptions() as error:
            gui = self.controlCenter.gui
            handleEngineException(error, gui)
        except ValueError as error:
            raise ControlValueError(str(error))
        return


    def outputBondLengthTypes(self, struc, a1, a2, lb, ub):
        """Output all a1-a2 bond lenghts within specified range.

        struc  -- instance of PDFStructure
        a1     -- symbol of the first element in pair or "ALL"
        a2     -- symbol of the second element in pair or "ALL"
        lb     -- lower bond length boundary
        ub     -- upper bond length boundary

        No return value.  The result should be automatically added to
        the Output Window, because all server output is sent there.

        Raise ControlValueError for invalid element symbols.
        """
        try:
            self._configureBondCalculation(struc)
            self.server.blen(a1, a2, lb, ub)
            self._release()
        except getEngineExceptions() as error:
            gui = self.controlCenter.gui
            handleEngineException(error, gui)
        except ValueError as error:
            raise ControlValueError(str(error))
        return


    def pause(self, bPause=None):
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

    def start(self):
        """start fitting"""
        # check if paused
        if self.jobStatus == Fitting.PAUSED:
            self.pause(False)
            return

        # clean up control variable
        self.stopped = False
        self.paused = False
        self.resetStatus()

        # Restart fitting require another thread instance.
        self.thread = Fitting.Worker(self)
        self.thread.start()

    def stop(self):
        """stop the fitting"""
        self.stopped = True

        # wake up daemon thread if it is paused
        if self.jobStatus == Fitting.PAUSED:
            self.pause(False)

    def isThreadRunning(self):
        """check if fitting thread is running

        return: True if running, False otherwise
        """
        return self.thread is not None and self.thread.is_alive()

    def join(self):
        """wait for current fitting to finish"""
        if self.thread:
            self.thread.join()
            self.thread = None

    def close(self, force=False):
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
                raise ControlStatusError("Fitting: Fitting %s is still running"%self.name)
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
            for itemName in list(dataset.constraints.keys()) + ['Gcalc','crw']:
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

    def appendStep(self, source):
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
            snapshot[nameDict['crw']] = dataset.crw
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
        for idx, par in self.parameters.items():
            par.refined = self.server.getpar(idx)

        self.rw = self.server.getrw()

        self.step += 1
        self.appendStep(self.server)

        #update plots and structure renderer
        gui = self.controlCenter.gui
        if gui:
            gui.postEvent(gui.OUTPUT, None)
            gui.postEvent(gui.PLOTNOW, self)

        if finished:
            self.res = "* %s\n\n"%time.ctime()+ self.server.save_res_string()
            self.__changeStatus(fitStatus = Fitting.DONE)

        return finished

    def getYNames(self):
        """get names of data item which can be plotted as y

        returns a name str list
        """
        names = list(self.parameters.keys())
        names.append('rw')
        return names

    def getXNames(self):
        """get names of data item which can be plotted as x

        returns a name str list
        """
        return []

    def getData(self, name, step=-1):
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
        data = self.getMetaData(name)
        if data is not None:
            return data

        return self._getData(self, name, step)

    def getMetaDataNames(self):
        """return all applicable meta data names
        """
        names = []
        for dataset in self.datasets:
            # build up the name list
            if not names:
                names = list(dataset.metadata.keys())
            else:
                for name in names[:]:
                    if name not in dataset.metadata:
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

    def _getData(self, id, name, step=-1):
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

# End of file
