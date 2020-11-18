#!/usr/bin/env python
##############################################################################
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
##############################################################################

"""class Calculation for performing PDF simulation from model structure.
"""

import copy
import math

from diffpy.pdfgui.control.controlerrors import ControlConfigError
from diffpy.pdfgui.control.controlerrors import ControlKeyError
from diffpy.pdfgui.control.controlerrors import ControlValueError
from diffpy.pdfgui.control.pdfcomponent import PDFComponent
from diffpy.pdfgui.utils import safeCPickleDumps, pickle_loads


class Calculation(PDFComponent):
    """Perform a theoretical computation of PDF from model structure.

    Data members:

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
    spdiameter -- particle diameter for shape damping function.
              Note: this attribute has been moved to FitStructure and is
              maintained only for backward compatible reading of PDFgui
              project files.
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
        self.spdiameter = None
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
        rmax  -- new maximum rcalc, slightly adjusted to accommodate rstep

        No return value.
        Raise ControlValueError for invalid range specification.
        """
        if rmin is None:    rmin = self.rmin
        if rstep is None:   rstep = self.rstep
        if rmax is None:    rmax = self.rmax
        rstep = float(rstep)
        # check if arguments are valid
        if not rmin > 0:
            emsg = "Low range boundary must be positive."
            raise ControlValueError(emsg)
        if not rmin < rmax:
            emsg = "Invalid range boundaries."
            raise ControlValueError(emsg)
        if rstep <= 0.0:
            emsg = "Invalid value of rstep, rstep must be positive."
            raise ControlValueError(emsg)
        # find number of r bins
        nbins = int( math.ceil( (rmax - rmin)/rstep ) )
        # check for overshot due to round-off
        epsilonr = 1.0e-8 * rstep
        deltarmax = abs(rmin + (nbins - 1)*rstep - rmax)
        if nbins > 1 and deltarmax < epsilonr:
            nbins -= 1
        # All went well, let us go ahead and set the attributes.
        self.rmin = rmin
        self.rstep = rstep
        self.rmax = rmin + nbins*rstep
        self.rlen = nbins + 1
        return

    def start(self):
        """entry function for calculation"""
        from diffpy.pdfgui.control.fitting import getEngineExceptions,handleEngineException
        try:
            self.calculate()
        except getEngineExceptions() as error:
            gui = self.owner.controlCenter.gui
            handleEngineException(error, gui)

        # inform gui of change ( when engine calculation fails, it will update gui as well )
        gui = self.owner.controlCenter.gui
        if gui:
            gui.postEvent(gui.OUTPUT, None)
            gui.postEvent(gui.PLOTNOW, self)
        return

    def calculate(self):
        """do the real calculation
        """
        # clean up old results
        self.rcalc = []
        self.Gcalc = []

        # do the job
        if len(self.owner.strucs) == 0:
            raise ControlConfigError("No structure is given for calculation")

        # make sure parameters are initialized
        self.owner.updateParameters()
        from diffpy.pdffit2 import PdfFit
        server = PdfFit()

        # structure needs to be read before dataset allocation
        for struc in self.owner.strucs:
            server.read_struct_string(struc.writeStr('pdffit'))
            for key,var in struc.constraints.items():
                server.constrain(key, var.formula)

        # set up dataset
        server.alloc(self.stype, self.qmax, self.qdamp,
                self.rmin, self.rmax, self.rlen)
        server.setvar('qbroad', self.qbroad)
        server.setvar('dscale', self.dscale)

        # phase related variables
        # pair selection applies to current dataset,
        # therefore it has to be done after alloc
        for phaseidx0, struc in enumerate(self.owner.strucs):
            phaseidx1 = phaseidx0 + 1
            server.setphase(phaseidx1)
            server.setvar('pscale', struc.getvar('pscale'))
            server.setvar('spdiameter', struc.getvar('spdiameter'))
            struc.applyPairSelection(server, phaseidx1)

        # set up parameters
        for index, par in self.owner.parameters.items():
            server.setpar(index, par.initialValue()) # info[0] = init value
            # fix if fixed.  Note: all parameters are free after server.reset().
            if par.fixed:
                server.fixpar(index)

        # all ready here
        server.calc()

        # get results
        self.rcalc = server.getR()
        self.Gcalc = server.getpdf_fit()

    def write(self, filename):
        """write this calculated PDF to a file

        filename -- name of file to write to

        No return value.
        """
        txt = self.writeStr()
        f = open( filename, 'w' )
        f.write(txt)
        f.close()
        return

    def writeStr(self):
        """String representation of calculated PDF.

        Returns data string
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
        # dscale
        if self.dscale:
            lines.append('dscale=%g' % self.dscale)
        # qmax
        if self.qmax == 0:
            qmax_line = 'qmax=0   correction not applied'
        else:
            qmax_line = 'qmax=%.2f' % self.qmax
        lines.append(qmax_line)
        # qdamp
        if isinstance(self.qdamp, float):
            lines.append('qdamp=%g' % self.qdamp)
        # qbroad
        if self.qbroad:
            lines.append('qbroad=%g' % self.qbroad)
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
        config = pickle_loads(z.read(subpath + 'config'))
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
        self.spdiameter = config.get('spdiameter')
        self.dscale = config['dscale']
        return

    def save(self, z, subpath):
        """save data from a zipped project file

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        config = {
            'rmin' : self.rmin,
            'rstep' : self.rstep,
            'rmax' : self.rmax,
            'rlen' : self.rlen,
            'rcalc' : self.rcalc,
            'Gcalc' : self.Gcalc,
            'stype' : self.stype,
            'qmax' : self.qmax,
            'qdamp' : self.qdamp,
            'qbroad' : self.qbroad,
            'dscale' : self.dscale,
        }
        z.writestr(subpath + 'config', safeCPickleDumps(config))
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
                'qbroad', 'dscale', )
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
        return ['r', ]

    def getData(self, dataname, step=None):
        """get Calculation data member

        name -- data item name
        step -- ignored, just for compatibility with Organizer.getData()

        returns data object, be it a single number, a list, or a list of list
        """
        if dataname not in ['rcalc', 'Gcalc']:
            emsg = "%s is not valid dataname" % dataname
            raise ControlKeyError(emsg)
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

# End of file
