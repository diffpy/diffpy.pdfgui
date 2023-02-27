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

import sys
import os
import threading
import time
import six
import six.moves.cPickle as pickle

from diffpy.pdfgui.control.pdflist import PDFList
from diffpy.pdfgui.control.fitting import Fitting
from diffpy.pdfgui.control.calculation import Calculation
from diffpy.pdfgui.control.fitdataset import FitDataSet
from diffpy.pdfgui.control.organizer import Organizer
from diffpy.pdfgui.control.fitstructure import FitStructure
from diffpy.pdfgui.control.controlerrors import ControlError
from diffpy.pdfgui.control.controlerrors import ControlFileError
from diffpy.pdfgui.control.controlerrors import ControlTypeError
from diffpy.pdfgui.utils import asunicode, quote_plain


class PDFGuiControl:
    """PDFGuiControl holds all the data GUI needs to access or change
    It has a container of Calculation and Fitting instances.
    Each Calculation and Fitting has a unique name.
    """
    def __init__(self, gui=None):
        """initialize

        gui: main panel of GUI
        """
        self.lock = threading.RLock()
        self.gui = gui

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
    class QueueManager(threading.Thread):
        def __init__(self, control):
            threading.Thread.__init__(self)
            self.control = control
            self.running = True

        def run(self):
            while self.running:
                try:
                    self.control.checkQueue()
                except ControlError as error:
                    gui = self.control.gui
                    if gui:
                        gui.postEvent(gui.ERROR, "<Queue exception> %s"%error.info)
                    else:
                        print("<Queue exception> %s"%error.info)
                # another check before go to sleep
                if not self.running: break
                time.sleep(1)

    def startQueue(self):
        """start queue manager"""
        self.queueManager.setDaemon(True)
        self.queueManager.start()

    def checkQueue(self):
        """find next fitting in the queue and start it"""
        if self.currentFitting:
            # wait for currentFitting
            self.currentFitting.join()

        # No fitting in the queue is running.
        try:
            self.lock.acquire()
            if len(self.fittingQueue) > 0 :
                self.currentFitting = self.fittingQueue.pop(0)
            else:
                self.currentFitting = None
                return
        finally:
            self.lock.release()

        self.currentFitting.start()

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

    def close(self, force = True):
        """close a project

        force -- if exit forciably
        """
        self.stop()
        for plot in self.plots:
            plot.close(force)
        for fit in self.fits:
            fit.close(force)

        self.reset()

    def exit(self):
        """exit when program finished
        """
        self.close()
        if self.queueManager.is_alive():
            self.queueManager.running = False

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
        calculation = Calculation(name)
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
            raise ControlTypeError("Can't add %s to list" % self.__class__.__name__)
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
                raise ControlTypeError("Object %s doesn't exit in the list" % ID.name)

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
                    if x not in pathDict:
                        pathDict[x] = {}
                    pathDict = pathDict[x]

                # check if the entry is a leaf(file, not folder)
                if subs[-1] != '':
                    pathDict[subs[-1]] = None
            return fileTree

        self.projfile = projfile
        organizations = []
        import zipfile

        # IOError can be raised when reading invalid zipfile
        # check for file existence here.
        if not os.path.isfile(projfile):
            emsg = "Project file %s does not exist." % projfile
            raise ControlFileError(emsg)

        emsg_invalid_file = "Invalid or corrupted project %s." % projfile
        z = None
        try:
            z = zipfile.ZipFile(projfile, 'r')
            z.fileTree = _nameParser(z.namelist())

            if len(z.fileTree) == 0:
                raise ControlFileError(emsg_invalid_file)
            # The first layer has only one folder
            rootDict = next(iter(z.fileTree.values()))
            projName = next(iter(z.fileTree.keys()))

            if 'journal' in rootDict:
                self.journal = asunicode(z.read(projName + '/journal'))

            # all the fitting and calculations
            #NOTE: It doesn't hurt to keep backward compatibility
            # old test project may not have file 'fits'
            if 'fits' in rootDict:
                ftxt = asunicode(z.read(projName + '/fits'))
                fitnames = ftxt.splitlines()
            else:
                fitnames = [ x for x in rootDict.keys() if rootDict[x] is not None]

            for name in fitnames:
                if not name: # empty string
                    continue
                fit = Fitting(name)
                # fitting name stored in rootDict should be quoted
                rdname = quote_plain(name)
                # but let's also handle old project files
                if rdname not in rootDict:
                    rdname = name
                if rdname in rootDict:
                    org = fit.load(z, projName + '/' + rdname + '/')
                else:
                    # it's simply a blank fitting, has no info in proj file yet
                    org = fit.organization()
                organizations.append(org)
                self.add(fit)

        except (IOError, zipfile.error, pickle.PickleError):
            raise ControlFileError(emsg_invalid_file)

        # close input file if opened
        finally:
            if z:  z.close()

        return organizations


    def save(self, projfile=None):
        """Save project to projfile, default projfile is self.projfile

        This method first writes to a temporary file and only when
        successful, it overwrites projfile with the temporary file content.
        These steps prevent corruption of existing projects should
        something go wrong in the middle of save.  As an added benefit,
        all permissions and ownership flags in an existing projfile
        are preserved.
        """
        if projfile is not None:
            self.projfile = projfile

        # self.projfile is unset here only due to a bug.
        assert self.projfile is not None

        import zipfile
        import shutil
        import tempfile

        projbase = os.path.basename(self.projfile)
        projName = os.path.splitext(projbase)[0]
        # prepare to write
        fitnames = []
        z = None
        tmpfilename = None
        try :
            tmpfd, tmpfilename = tempfile.mkstemp()
            os.close(tmpfd)
            z = zipfile.ZipFile(tmpfilename, 'w', zipfile.ZIP_DEFLATED)
            # fits also contain calculations
            for fit in self.fits:
                name = fit.name
                fit.save(z, projName + '/' + quote_plain(fit.name) + '/')
                fitnames.append(name)
            if self.journal:
                z.writestr(projName + '/journal', asunicode(self.journal))
            ftxt = '\n'.join(fitnames)
            z.writestr(projName + '/fits', asunicode(ftxt))
            z.close()
            shutil.copyfile(tmpfilename, self.projfile)

        except (IOError, pickle.PickleError):
            emsg = "Error when writing to %s" % self.projfile
            raise ControlFileError(emsg)

        finally:
            if z is not None:
                z.close()
            if tmpfilename is not None:
                os.remove(tmpfilename)

        return


    def plot (self, xItem, yItems, Ids, shift = 1.0, dry=False):
        """Make a 2D plot

        xItem --  x data item name
        yItems -- list of y data item names
        Ids --    Objects where y data items are taken from
        shift -- y displacement for each curve
        dry -- not a real plot, only check if plot is valid
        """
        from diffpy.pdfgui.control.plotter import Plotter
        plotter = Plotter()
        plotter.plot(xItem, yItems, Ids, shift, dry)
        self.plots.append(plotter)

    def start(self, IDlist):
        """execute Calculations and Fittings in IDlist.
        """
        self.redirectStdout()
        fits = [ ID for ID in IDlist if isinstance(ID, Fitting) ]
        # only add calcs which is not in fits, because fits will automatically run calcs under it anyway
        calcs = [ ID for ID in IDlist if isinstance(ID, Calculation) and ID.owner not in fits]
        for calc in calcs:
            calc.start()
        self.enqueue(fits)

    def stop(self):
        """stop all Fittings
        """
        self.enqueue(self.fits, False)
        for id in self.fits:
            if isinstance(id, Fitting):
                id.stop()

    def __validateType(self, targetID):
        """check if targetID is a Fitting class"""
        if not isinstance(targetID, Organizer):
            raise ControlTypeError("Can't insert to %s" % self.__class__.__name__)

    def redirectStdout(self):
        """Redirect standard out.

        This redirect engine output to StringIO if not done yet.
        """
        from diffpy.pdffit2 import redirect_stdout, output
        if output.stdout is sys.stdout:
            redirect_stdout(six.StringIO())
        return

    def getEngineOutput(self):
        """Get the output from the engine."""
        from diffpy.pdffit2 import output, redirect_stdout
        txt = output.stdout.getvalue()
        output.stdout.close()
        redirect_stdout(six.StringIO())
        return txt

_pdfguicontrol = None
def pdfguicontrol(*args, **kwargs):
    """This function will return the single instance of class PDFGuiControl"""
    global _pdfguicontrol
    if _pdfguicontrol is None:
        _pdfguicontrol = PDFGuiControl(*args, **kwargs)
    return _pdfguicontrol

def _importByName(mname, name):
    try:
        module = __import__(mname, globals(), locals(), [name])
    except ImportError:
        return None
    return getattr(module, name)

def _find_global(moduleName, clsName):
    #from diffpy.pdfgui.control.parameter import Parameter
    moduleName = 'diffpy.pdfgui.control.' + moduleName.split('.')[-1]
    m = _importByName(moduleName,clsName)
    return m


class CtrlUnpickler:
    '''Occasionally the project file may be generated on a platform where
    PYTHONPATH is not correctly set up. CtrlUnpickler will transform the
    module path in the project file to be relative to diffpy so that it can
    be safely loaded. Only constraints and parameters need this class to un-
    pickle.
    '''
    @staticmethod
    def loads(s):
        try:
            return pickle.loads(s)
        except ImportError as err:
            missedModule = str(err).split(' ')[-1]
            if missedModule.find('pdfgui.control') == -1:
                raise err
            f = six.StringIO(s)
            unpickler = pickle.Unpickler(f)
            unpickler.find_global = _find_global
            return unpickler.load()

# End of file
