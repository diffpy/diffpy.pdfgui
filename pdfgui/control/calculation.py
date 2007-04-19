#!/usr/bin/env python
########################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas, Jiwu Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################

"""class Calculation for performing PDF simulation from model structure.
"""

import copy
import math
import types
from controlerrors import *
from fitstructure import FitStructure
from pdfcomponent import PDFComponent

class Calculation(PDFComponent):
    """Perform a theoretical computation of PDF from model structure.

    Data members:

    serverFactory -- class used for creating PdfFit engine server
    serverFactoryArgs -- tuple of arguments passed to serverFactory
    rmin   -- read-only lower boundary of rcalc, change with setRGrid()
    rstep  -- read-only r-grid step, use setRGrid() to change it
    rmax   -- read-only upper boundary of rcalc, change with setRGrid()
    rlen   -- read-only number of r points, set by setRGrid().
              To be used in PdfFit.alloc()
    rcalc  -- list of r values, this is set after calculation is finished
    Gcalc  -- list of calculated G values
    stype  -- scattering type, 'X' or 'N'
    qmax   -- maximum value of Q in inverse Angstroms.  Termination ripples
              are ignored for qmax=0.
    qdamp  -- specifies width of Gaussian damping factor in pdf_obs due
              to imperfect Q resolution
    qbroad -- quadratic peak broadening factor related to dataset
    spdiameter -- particle diameter for shape damping function
    dscale -- total scale factor
    """

    def __init__(self, name):
        """initialize Calculation

        name -- calculation name
        """
        PDFComponent.__init__(self, name)

        # rmin, rstep, rmax, rlen, rcalc
        self.setRGrid(rmin=0.1, rstep=0.01, rmax=10.0)
        self.rcalc = []
        self.Gcalc = []
        self.stype = 'X'
        # user must specify qmax to get termination ripples
        self.qmax = 0.0
        self.qdamp = 0.001
        self.qbroad = 0.0
        self.spdiameter = 0.0
        self.dscale = 1.0
        return
        
    def _getStrId(self):
        """make a string identifier
        
        return value: string id
        """
        return "c_" + self.name


    def setRGrid(self, rmin=None, rstep=None, rmax=None):
        """Change specified r-grid parameters (rmin, rstep, rmax).
        Adjust rmax for integer number of steps.

        rmin  -- new low rcalc boundary
        rstep -- new r-grid step
        rmax  -- new maximum rcalc, slightly adjusted to accomodate rstep
        """
        if rmin is not None:    self.rmin = float(rmin)
        if rstep is not None:   self.rstep = float(rstep)
        if rmax is not None:    self.rmax = float(rmax)
        if self.rstep <= 0.0:
            raise ControlRuntimeError, \
                    "Invalid value of rstep, rstep must be positive"
        self.rlen = int(math.ceil( (self.rmax - self.rmin)/self.rstep )) + 1
        self.rmax = self.rmin + self.rstep*(self.rlen - 1)
        return

    def start(self):
        """entry function for calculation"""
        self.owner.calculate(self)
        
    def _calculate(self):
        """do the real calculation"""
        server = self.owner.server

        # server is up, clean up old results
        self.rcalc = []
        self.Gcalc = []
        # do the job
        if len(self.owner.strucs) == 0:
            raise ControlConfigError, "No structure is given for calculation"
        # dataset related variables
        server.alloc(self.stype, self.qmax, self.qdamp,
                self.rmin, self.rmax, self.rlen)
        server.setvar('qbroad', self.qbroad)
        server.setvar('spdiameter', self.spdiameter)
        # phase related variables
        # pair selection applies to current dataset, 
        # therefore it has to be done after alloc
        nstrucs = len(self.owner.strucs)
        for phaseidx, struc in zip(range(1, nstrucs + 1), self.owner.strucs):
            server.read_struct_string(struc.writeStr('pdffit'))
            server.setvar('pscale', struc.getvar('pscale'))
            struc.applyPairSelection(server, phaseidx)
        # all ready here
        server.calc()
        
        # get results
        self.rcalc = server.getR()
        self.Gcalc = server.getpdf_fit()
       
        # inform gui of change
        gui = self.owner.controlCenter.gui
        if gui:
            #gui.postEvent(gui.UPDATE, self)
            try:
                gui.lock()
                for plot in self.owner.controlCenter.plots:
                    plot.notify(self)
            finally:
                gui.unlock()        
        return

    def write(self, filename):
        """write this calculated PDF to a file
        
        filename -- name of file to write to
        """
        bytes = self.writeStr()
        f = open( filename, 'w' )
        f.write(bytes)
        f.close()
        return
        
    def writeStr(self):
        """string representation of calculated PDF
        
        returns data string
        """
        import time
        from getpass import getuser
        lines = []
        # write metadata
        lines.extend([
            'History written: ' + time.ctime(),
            'produced by ' + getuser(),
            '##### PDFgui calculation' ])
        # stype
        if self.stype == 'X':
            lines.append('stype=X  x-ray scattering')
        elif self.stype == 'N':
            lines.append('stype=N  neutron scattering')
        # qmax
        if self.qmax:
            lines.append('qmax=%.2f' % self.qmax)
        # qdamp
        if type(self.qdamp) is types.FloatType:
            lines.append('qdamp=%g' % self.qdamp)
        # qbroad
        if self.qbroad:
            lines.append('qbroad=%g' % self.qbroad)
        # spdiameter
        if self.spdiameter:
            lines.append('spdiameter=%g' % self.spdiameter)
        # write data:
        lines.append('##### start data')
        lines.append('#L r(A) G(r)')
        for i in range(len(self.rcalc)):
            lines.append( '%g %g' % (self.rcalc[i], self.Gcalc[i]) )
        # lines are ready here
        datastring = '\n'.join(lines) + '\n'
        return datastring

    def load(self, z, subpath):
        """load data from a zipped project file

        z       -- zipped project file
        subpath -- path to its own storage within project file
        
        returns a tree of internal hierachy
        """
        import cPickle
        config = cPickle.loads(z.read(subpath+'config'))
        self.rmin = config['rmin']
        self.rstep = config['rstep']
        self.rmax = config['rmax']
        self.rlen = config['rlen']
        self.rcalc = config['rcalc']
        self.Gcalc = config['Gcalc']
        self.stype = config['stype']
        self.qmax = config['qmax']
        self.qdamp = config.get('qdamp', config.get('qsig'))
        self.qbroad = config.get('qbroad', config.get('qalp', 0.0))
        self.spdiameter = config.get('spdiameter', 0.0)
        self.dscale = config['dscale']
        return 

    def save(self, z, subpath):
        """save data from a zipped project file

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        import cPickle
        config = {
            'rmin'       : self.rmin,
            'rstep'      : self.rstep,
            'rmax'       : self.rmax,
            'rlen'       : self.rlen,
            'rcalc'      : self.rcalc,
            'Gcalc'      : self.Gcalc,
            'stype'      : self.stype,
            'qmax'       : self.qmax,
            'qdamp'      : self.qdamp,
            'qbroad'     : self.qbroad,
            'spdiameter' : self.spdiameter,
            'dscale'     : self.dscale,
        }
        z.writestr( subpath+'config',
                    cPickle.dumps(config, cPickle.HIGHEST_PROTOCOL) )
        return

    def copy(self, other=None):
        """copy self to other. if other is None, create new instance

        other -- reference to other object

        returns reference to copied object
        """
        if other is None:
            other = Calculation(self.name)

        # rcalc and Gcalc may be assigned, they get replaced by new lists
        # after every calculation
        assign_attributes = ( 'rmin', 'rstep', 'rmax', 'rlen',
                'rcalc', 'Gcalc', 'stype', 'qmax', 'qdamp', 
                'qbroad', 'spdiameter', 'dscale', )
        copy_attributes = ( )
        for a in assign_attributes:
            setattr(other, a, getattr(self, a))
        for a in copy_attributes:
            setattr(other, a, copy.copy(getattr(self, a)))
        return other

    def getYNames(self):
        """get names of data item which can be plotted as y
        
        returns a name str list
        """
        return ['Gcalc',]

    def getXNames(self):
        """get names of data item which can be plotted as x
        
        returns a name str list
        """
        return ['rcalc', ]

    def getData(self, dataname, step=None):
        """get Calculation data member

        name -- data item name
        step -- ignored, just for compatibility with Organizer.getData()

        returns data object, be it a single number, a list, or a list of list
        """
        if dataname not in ['rcalc', 'Gcalc']:
            raise ControlKeyError, "%s is not valid dataname" % dataname
        return self.__dict__[dataname]
        
    def getMetaDataNames(self):
        """return all applicable meta data names
        """
        # FIXME: Currently we haven't thought about this
        return []
        
    def getMetaData(self, name):
        """get meta data value
        
        name -- meta data name
        returns meta data value
        """
        return None

# End of class Calculation

# simple test code
if __name__ == "__main__":
    Calculation('name')

# version
__id__ = "$Id$"

# End of file
