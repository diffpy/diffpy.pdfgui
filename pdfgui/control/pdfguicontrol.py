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

import sys
import os

from pdflist import PDFList
from fitting import Fitting
from calculation import Calculation
from fitdataset import FitDataSet
from organizer import Organizer
from fitstructure import FitStructure
from serverhost import ServerHost
from threading import Thread
from controlerrors import *

class PDFGuiControl:
    """PDFGuiControl holds all the data GUI needs to access or change
    It has a container of Calculation and Fitting instances.
    Each Calculation and Fitting has a unique name.
    """
    def __init__(self, gui=None):
        """initialize
        
        gui: main panel of GUI
        """        
        # Lock , Gui and host machine
        import threading
        self.lock = threading.RLock()
        self.gui = gui
        self.host = None
        
        # clean up local data
        self.reset()
        
        # Queue stuff
        self.fittingQueue = []
        self.currentFitting = None
        self.queueManager = PDFGuiControl.QueueManager(self)
        ##self.startQueue()
        
    def reset(self):
        """clean up for a new project"""
        self.fits = PDFList()
        self.plots = PDFList()
        self.journal = ''
                    
        self.projfile = None
        #self.saved = False
        
    # a simple thread to handle fitting queue
    class QueueManager(Thread):
        def __init__(self, control):
            Thread.__init__(self)
            self.control = control
            self.running = True
            
        def run(self):
            import time
            while self.running:
                try:
                    self.control.checkQueue()
                except ControlError, error:
                    gui = self.control.gui
                    if gui:
                        gui.postEvent(gui.ERROR, "<Queue exception> %s"%error.info)
                    else:
                        print "<Queue exception> %s"%error.info
                time.sleep(1)

    def startQueue(self):
        """start queue manager"""
        ##self.queueManager.setDaemon(True)
        self.queueManager.start()
        
    def checkQueue(self):
        """find next fitting in the queue and start it"""
        if self.currentFitting and self.currentFitting.isThreadRunning():
            return 
        
        # No fitting in the queue is running.
        try:
            self.lock.acquire()
            if len(self.fittingQueue) > 0 :
                fit = self.fittingQueue.pop(0)
            else:
                return
        finally:
            self.lock.release()
        
        self.currentFitting = fit
        fit.start()
            
    def enqueue(self, fits, enter = True):
        """enqueue or dequeue fittings
        
        fits -- list of fittings to be queued/dequeued
        enter -- True to queue, False to dequeue
        """
        try:
            self.lock.acquire()
            for fit in fits:
                if enter:
                    try: 
                        self.fittingQueue.index(fit)
                        # if no exception, then it already in the queue, 
                        # continue to next
                        continue
                    except ValueError:
                        # not in the queue
                        self.fittingQueue.append(fit)
                else:
                    try:
                        # try to remove even if it may not be in the queue
                        self.fittingQueue.remove(fit)
                    except ValueError:
                        # do nothing if it's not in the queue, continue to next.
                        continue
                
                # When this is called, GUI lock is in possess for sure, so
                # no dead lock can happen.
                fit.queue(enter)
        finally:
            self.lock.release()

    def close ( self, force = True ):
        """close a project
        
        force -- if exit forciably
        """
        for plot in self.plots:
            plot.close(force)
        for fit in self.fits:
            fit.close(force)
        
        self.reset()

    def exit ( self ):
        """exit when program finished
        """
        self.close()
        
        if self.host:
            self.host.close()
        
        #stop queuemanager,wait for queue thread 
        if self.queueManager.isAlive():
            self.queueManager.running = False            
            self.queueManager.join()
        
    def newFitting(self, name, position=None):
        """insert a new instance of Fitting
        
        name      --  unique name for this Fitting
        position  --  where Fitting is inserted, default is last place

        return: Fitting reference
        """
        fitting = Fitting(name)
        self.add(fitting, position)
        return fitting
        
    def newCalculation(self, targetID, name, position=None):
        """insert a new instance of Calculation to a Fitting
        
        targetID  --  reference to Fitting
        name      --  unique name for this Calculation
        position  --  where Calculation is inserted, default is last place

        return: Calculation reference
        """
        calculation = Calculation ( name )
        targetID.add(calculation, position)
            
        return calculation

    def newStructure(self, targetID, name, position=None):
        """add blank structure to a Fitting

        targetID  --  reference to Fitting
        name      --  name of the new Structure
        position  --  where the structure is to be inserted, default is last

        return: Structure reference
        """
        self.__validateType(targetID)
        
        # insert to target
        struct = FitStructure(name)
        targetID.add(struct, position)
        return struct

    def loadStructure(self, targetID, filename, name = None, position=None):
        """add blank structure to a Fitting
        
        targetID  --  reference to Fitting
        name      --  name of the new Structure, default is file basename

        return: Structure reference
        """
        self.__validateType(targetID)
        if name is None:
            name = os.path.basename(filename)

        # insert to target
        struct = FitStructure(name)
        struct.initial.read(filename)
        targetID.add(struct, position)
        return struct

    def loadDataset(self, targetID, filename, name = None, position=None):
        """load Dataset from a file to a Fitting

        targetID  --  reference to Fitting
        name      --  name of the new Dataset, default is file basename
        position  --  where the dataset is to be inserted, default is last

        return: Dataset reference
        """
        self.__validateType(targetID)
        
        if name is None:
            name = os.path.basename(filename)

        #insert to target
        dataset = FitDataSet(name)
        dataset.readObs(filename)
        targetID.add(dataset, position)
        return dataset
    
    def add(self, ID, position = None):
        """add fitting/calculation to internal list
        
        Id -- reference to the object to be inserted
        position  --  where the object is to be inserted, default is last
        """
        if not isinstance(ID, Fitting) and \
           not isinstance(ID, Calculation):
            raise ControlTypeError, "Can't add %s to list"%\
                  self.__class__.__name__
        if position is not None:
            self.fits.insert(position, ID)
        else:
            self.fits.append(ID)
        # added successfully
        ID.owner = self
        return ID
    
    def __findOwner(self, ID):
        """find where the ID belongs
        
        ID -- object which can be Fitting,Calculation,FitDataSet or FitStructure
        return: a PDFList holding that object
        """
        if isinstance(ID, Organizer):
            return self.fits
        else:
            try:
                return ID.owner
            except AttributeError:
                raise ControlTypeError, "Object %s doesn't exit in the list"\
                                        %ID.name

    def rename(self, ID, new_name):
        """rename Fitting, Calculation, Dataset or Structure
        identified by ID
        
        ID:       reference to the object to be renamed
        new_name: new name to be given to the object 
        """
        container = self.__findOwner(ID)
        container.rename(ID, new_name)

    def remove(self, ID):
        """remove Fitting, Calculation, Dataset or Structure
        identified by ID
        
        ID:     reference to the object to be removed
        return: removed object
        """
        container = self.__findOwner(ID)
        container.remove(ID)
        return ID

    def index(self, ID):
        """return position index of an object in its owner list
        
        ID  --  ID of object
        return: index
        """
        container = self.__findOwner(ID)
        return container.index(ID)

    def copy(self, src):
        """copy src object 
        
        src -- reference to the source object
        return: reference to the copy
        """
        newObject = src.copy()
        return newObject
        
    def paste(self, dup, target=None, new_name=None, position=None):
        """paste copied object to target under new_name, the default new_name
        will be name of src
        
        dup -- reference to the copied object
        target -- target object where the copy should be inserted
        new_name -- new name to be given to the copy
        position -- where in the target object should the copy be inserted

        return: reference to the pasted object
        """
        if target is None:
            target = self
        else:
            self.__validateType(target)
            
        o = dup.copy()
        if new_name is not None:
            o.name = new_name
        target.add(o, position)
        return o

    def importPdffit2Script(self, scriptfile, args=[]):
        """add fits and calculations from pdffit2 script

        scriptfile -- path to old pdffit2 script
        args       -- optional arguments passed to scriptfile

        returns list of imported fits
        """
        pyexe = sys.executable
        from pdfgui.gui.pdfguiglobals import controlDir
        dumpscript = os.path.join(controlDir, 'dumppdffit2script.py')
        # this should take care of proper shell quoting
        cmdwords = [pyexe, dumpscript, scriptfile] + args
        cmd = " ".join([repr(w.encode('ascii')) for w in cmdwords])
        (i, o, e) = os.popen3(cmd)
        # close child standard input
        i.close()
        err = e.read()
        e.close()
        out = o.read()
        o.close()
        status = os.wait()[1]
        if os.WEXITSTATUS(status) != 0:
            raise ControlRuntimeError, \
                "Import of pdffit2 script failed:\n" + err
        # seems that everything worked fine here
        import cPickle
        impfits = cPickle.loads(out)
        orgnames = [ f.name for f in impfits ]
        usednames = dict.fromkeys([ f.name for f in self.fits ])
        basename, ext = os.path.splitext(os.path.basename(scriptfile))
        start = 0
        while True:
            start = start + 1
            newnames = [ basename + str(i) \
                         for i in range(start, start+len(impfits)) ]
            anyused = [ n for n in newnames if n in usednames ]
            if not anyused:
                break
        # here we have correct new names
        # build a dictionary with name translations
        old2new = dict(zip(orgnames, newnames))
        for fit in impfits:
            # items in impfits were stripped, we need to insert normal copy
            clothed = fit.copy()
            clothed.name = old2new[fit.name]
            # take care of linked parameters:
            if isinstance(clothed, Fitting):
                for idx, par in clothed.parameters.iteritems():
                    inistr = par.initialStr()
                    if inistr[:1] == "=":
                        name_idx = inistr[1:].rsplit(':', 1)
                        ininame = name_idx[0]
                        if len(name_idx) > 1:   srcparidx = name_idx[1]
                        else:                   srcparidx = str(idx)
                        newlinkedname = old2new[ininame]
                        par.setInitial("=%s:%s" % (newlinkedname, srcparidx))
            # finally we can put it in
            self.add(clothed)
        newfits = self.fits[len(self.fits)-len(impfits):]
        return [obj.organization() for obj in newfits]

    def load(self, projfile):
        """load project from projfile.
        
        projfile -- a zip file of everything
        """
        def _nameParser(namelist):
            """parse the zipfile name list to get a file tree"""
            fileTree = {}
            for name in namelist:
                subs = name.split('/')
                pathDict = fileTree
                for x in subs[:-1]:
                    # if no node has been created
                    if not pathDict.has_key(x):
                        pathDict[x] = {}
                    pathDict = pathDict[x]
                
                # check if the entry is a leaf ( file, not folder)
                if subs[-1] != '':
                    pathDict[subs[-1]] = None
            return fileTree

        self.projfile = projfile
        organizations = []
        import zipfile
        try:
            z = zipfile.ZipFile(projfile, 'r')
            z.fileTree = _nameParser(z.namelist())
            
            # The first layer has only one folder
            rootDict = z.fileTree.values()[0]
            projName = z.fileTree.keys()[0]
            
            if rootDict.has_key('journal'):
                self.journal = z.read(projName+'/journal')

            # all the fitting and calculations
            #NOTE: It doesn't hurt to keep backward compatibility 
            # old test project may not have file 'fits'
            fitnames = z.read(projName+'/fits').splitlines()
            
            for name in fitnames:
                if not name: # empty string
                    continue
                fit = Fitting(name)
                if rootDict.has_key(name):
                    org = fit.load(z, projName + '/' + name + '/')
                else:
                    # it's simply a blank fitting, has no info in proj file yet
                    org = fit.organization()
                organizations.append(org)
                self.add(fit)
                          
            z.close()
            return organizations
        
        except IOError:
            raise ControlFileError, "%s is invalid project file"%projfile

    def save(self, projfile=None):
        """save project to projfile, default projfile is self.projfile
        """
        if projfile is not None:
            self.projfile = projfile.encode('ascii')
        
        if self.projfile is None:
            raise ControlFileError, "No project file specifier"
        
        projName = os.path.basename(self.projfile).split('.')[0]
        # prepare to write
        import zipfile
        fitnames = []
        calcnames = []
        try :
            z = zipfile.ZipFile(self.projfile, 'w', zipfile.ZIP_DEFLATED)
            for fit in self.fits: # also calculations
                name = fit.name.encode('ascii')
                fit.save(z, projName + '/' + name + '/')
                fitnames.append(name)
            if self.journal:
                z.writestr(projName +'/journal', self.journal)
            z.writestr(projName + '/fits','\n'.join(fitnames))
            z.close()
        except IOError:
            raise ControlFileError, "Error when writing to %s"%self.projfile
    
    def plot (self, xItem, yItems, Ids, shift = 1.0):
        """Make a 2D plot
        
        xItem --  x data item name
        yItems -- list of y data item names
        Ids --    Objects where y data items are taken from
        shift -- y displacement for each curve
        """
        from plotter import Plotter
        plotter = Plotter()
        plotter.plot(xItem, yItems, Ids, shift)
        self.plots.append(plotter)

    def start(self, IDlist):
        """execute Calculations and Fittings in IDlist.
        """
        for ID in IDlist:
            if isinstance(ID, Calculation):
                ID.start()
            else:
                self.enqueue([ID,])

    def stop(self):
        """stop all Fittings
        """
        self.enqueue(self.fits, False)
        for id in self.fits:
            if isinstance(id, Fitting):
                id.stop()
    
    def setHost(self, hostCfg):
        """set the host machine to be used for fitting
        
        hostCfg -- configuration dictionary of remote host. If it is blank or None,
                   self.host will be set to None.
        """
        if not hostCfg:
            # set self.host to None in order to use local host
            self.host = None
        else:
            # create a host
            self.host = ServerHost(hostCfg['name'], hostCfg)
        
    def getHost(self):
        """get current host to be used. It can be None if we choose
        localhost
        
        return value: proxy instance
        """            
        return self.host
        
    def __validateType(self, targetID):
        """check if targetID is a Fitting class"""
        if not isinstance(targetID, Organizer):
            raise ControlTypeError, "Can't insert to %s"%\
                  self.__class__.__name__
   

_pdfguicontrol = None
def pdfguicontrol(*args, **kwargs):
    """This function will return the single instance of class PDFGuiControl"""
    global _pdfguicontrol
    if _pdfguicontrol is None:
        _pdfguicontrol = PDFGuiControl(*args, **kwargs)
    return _pdfguicontrol
    
# version
__id__ = "$Id$"

# End of file
