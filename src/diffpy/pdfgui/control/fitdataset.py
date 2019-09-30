#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""class FitDataSet for experimental PDF data and related fitting parameters
"""

import copy
import numpy

from diffpy.pdfgui.control.pdfdataset import PDFDataSet
from diffpy.pdfgui.control.parameter import Parameter
from diffpy.pdfgui.control.controlerrors import ControlStatusError

class FitDataSet(PDFDataSet):
    """FitDataSet stores experimental and calculated PDF data and related
    fitting parameters.  Inherited from PDFDataSet.

    Data members (in addition to those in PDFDataSet):

    fitrmin     -- lower boundary for data fitting, property
    fitrmax     -- upper boundary for data fitting, property
    fitrstep    -- r-step used for fitted data, property
    constraints -- dictionary of { var_string : Constraint_instance }
    initial     -- dictionary of initial values of refinable variables
    refined     -- dictionary of refined values of refinable variables

    Calculated members:

    rcalc       -- list of r points where Gcalc is calculated, cached property
    Gcalc       -- list of calculated G values, cached property
    dGcalc      -- list of standard deviations of Gcalc, cached property
    Gtrunc      -- Gobs resampled to rcalc grid, cached property
    dGtrunc     -- dGobs resampled to rcalc grid, cached property
    Gdiff       -- difference curve, Gdiff = Gtrunc - Gcalc, property
    crw         -- cumulative rw of the fit

    The data in rcalc, Gcalc, dGcalc, Gtrunc, dGtrunc are recalculated
    and cached when r-sampling changes.  Any change to fitrmin,
    fitrmax and fitrstep sets the _rcalc_changed flag.

    Refinable variables:  qdamp, qbroad, dscale
    Note: self.refvar is the same as self.initial[refvar].

    Class data:

    persistentItems -- list of attributes saved in project file
    """

    persistentItems = [ 'rcalc', 'Gcalc', 'dGcalc',
                        'fitrmin', 'fitrmax', 'fitrstep',
                        'initial', 'refined' ]

    def __init__(self, name):
        """Initialize FitDataSet.

        name -- name of the data set. It must be a unique identifier.
        """
        self.initial = {}
        self.refined = {}
        PDFDataSet.__init__(self, name)
        self.clear()
        return

    def __setattr__(self, name, value):
        """Assign refinable variables to self.initial.
        """
        if name in PDFDataSet.refinableVars:
            self.initial[name] = value
        else:
            PDFDataSet.__setattr__(self, name, value)
        return

    def __getattr__(self, name):
        """Obtain refinable variables from self.initial.
        This is called only when normal attribute lookup fails.
        """
        if name in PDFDataSet.refinableVars:
            value = self.initial[name]
        else:
            emsg = "A instance has no attribute '%s'" % name
            raise AttributeError(emsg)
        return value

    def _getStrId(self):
        """make a string identifier

        return value: string id
        """
        return "d_" + self.name

    def getYNames(self):
        """get names of data item which can be plotted as y

        returns list of strings
        """
        ynames = [ 'Gobs', 'Gcalc', 'Gdiff', 'Gtrunc', 'dGcalc', 'crw' ] + \
                 list(self.constraints.keys())
        return ynames

    def getXNames(self):
        """get names of data item which can be plotted as x

        returns list of strings
        """
        return ['r',]

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
        # data in below
        if name in self.metadata:
            return self.metadata[name]
        elif name in ( 'Gobs', 'Gcalc', 'Gtrunc', 'Gdiff', 'crw', 'robs', 'rcalc'):
            d = getattr(self, name)

            # for Gtrunc and rcalc, we can use Gobs and robs instead when they
            # are not ready.
            if not d :
                if name == 'Gtrunc':
                    return getattr(self, 'Gobs')
                if name == 'rcalc':
                    return getattr(self, 'robs')

            return d

        # otherwise fitting's repository is preferred
        return  self.owner._getData(self, name, step)

    def clear(self):
        """Reset all data members to initial empty values.
        """
        PDFDataSet.clear(self)
        self._rcalc_changed = True
        self._rcalc = []
        self._Gcalc = []
        self._dGcalc = []
        self._Gtrunc = []
        self._dGtrunc = []
        self._crw = []
        self._fitrmin = 0.5
        self._fitrmax = None
        self._fitrstep = None
        self.constraints = {}
        self.refined = {}
        return

    def clearRefined(self):
        """Clear all refinement results.
        """
        self.Gcalc = []
        self.dGcalc = []
        self.crw = []
        self.refined = {}
        return

    def obtainRefined(self, server, idataset):
        """Upload refined datataset from PdfFit server instance.

        server   -- instance of PdfFit server
        idataset -- index of this dataset in server
        """
        server.setdata(idataset)
        # obtain Gcalc, dGcalc and crw from the server
        self.Gcalc = server.getpdf_fit()
        self.dGcalc = server.getpdf_diff()
        self.crw = server.getcrw()
        # get variables from the server
        for var in PDFDataSet.refinableVars:
            self.refined[var] = server.getvar(var)
        return

    def read(self, filename):
        """Same as readObs().
        """
        return self.readObs(filename)

    def _updateRcalcRange(self):
        """Helper method for updating fitrmin, fitrmax and fitrstep
        just after reading observed values.

        No return value.
        """
        frmin = self.fitrmin or self.rmin
        self.fitrmin = max(frmin, self.rmin)
        frmax = self.fitrmax or self.rmax
        self.fitrmax = min(frmax, self.rmax)
        self.fitrstep = self.fitrstep or self.getObsSampling()
        return

    def readObs(self, filename):
        """Load experimental PDF data from PDFGetX2 or PDFGetN gr file.

        filename -- file to read from

        returns self
        """
        PDFDataSet.read(self, filename)
        self._updateRcalcRange()
        return self

    def readStr(self, datastring):
        """Same as readObsStr().
        """
        return self.readObsStr(datastring)

    def readObsStr(self, datastring):
        """Read experimental PDF data from a string

        datastring -- string of raw data

        returns self
        """
        PDFDataSet.readStr(self, datastring)
        self._updateRcalcRange()
        return self

    def write(self, filename):
        """Same as writeCalc().  Use writeObs() to save experimental PDF data.

        filename -- name of file to write to

        No return value.
        """
        self.writeCalc(filename)
        return

    def writeCalc(self, filename):
        """Write calculated PDF data to a file.

        filename -- name of file to write to

        No return value.
        """
        txt = self.writeCalcStr()
        f = open(filename, 'w')
        f.write(txt)
        f.close()
        return

    def writeStr(self):
        """Same as writeCalcStr.  Use writeObsStr() for experimental PDF.

        Return data string.
        """
        return self.writeCalcStr()

    def writeCalcStr(self):
        """String representation of calculated PDF data.

        Return data string.
        """
        if self.Gcalc == []:
            raise ControlStatusError("Gcalc not available")
        import time
        from getpass import getuser
        lines = []
        # write metadata
        lines.extend([
            'History written: ' + time.ctime(),
            'produced by ' + getuser(),
            '##### PDFgui fit' ])
        # stype
        if self.stype == 'X':
            lines.append('stype=X  x-ray scattering')
        elif self.stype == 'N':
            lines.append('stype=N  neutron scattering')
        # qmax
        if self.qmax:
            lines.append('qmax=%.2f' % self.qmax)
        # qdamp
        lines.append('qdamp=%g' % self.refined['qdamp'])
        # qbroad
        lines.append('qbroad=%g' % self.refined['qbroad'])
        # dscale
        lines.append('dscale=%g' % self.refined['dscale'])
        # fitrmin, fitrmax
        if self.fitrmin is not None and self.fitrmax is not None:
            lines.append('fitrmin=%g' % self.fitrmin)
            lines.append('fitrmax=%g' % self.fitrmax)
        # metadata
        if len(self.metadata) > 0:
            lines.append('# metadata')
            for k, v in self.metadata.items():
                lines.append( "%s=%s" % (k,v) )
        # write data:
        lines.append('##### start data')
        lines.append('#L r(A) G(r) d_r d_Gr Gdiff')
        # cache Gdiff here so it is not calculated many times
        Gdiff = self.Gdiff
        drcalc = 0.0
        for i in range(len(self.rcalc)):
            lines.append( '%g %g %.1f %g %g' % (self.rcalc[i],
                          self.Gcalc[i], drcalc, self.dGcalc[i], Gdiff[i]) )
        # lines are ready here
        datastring = "\n".join(lines) + "\n"
        return datastring

    def writeObs(self, filename):
        """Write observed PDF data to a file.

        filename -- name of file to write to

        No return value.
        """
        PDFDataSet.write(self, filename)
        return

    def writeObsStr(self):
        """String representation of observed PDF data.

        Return data string.
        """
        return PDFDataSet.writeStr(self)

    def _resampledPDFDataSet(self):
        """Return instance of PDFDataSet with resampled observed data.
        Helper method for writeResampledObs and writeResampledObsStr.
        """
        resampled = PDFDataSet(self.name)
        self.copy(resampled)
        resampled.robs = self.rcalc
        resampled.drobs = len(self.rcalc) * [0.0]
        resampled.Gobs = self.Gtrunc
        resampled.dGobs = self.dGtrunc
        return resampled

    def writeResampledObs(self, filename):
        """Write resampled PDF data in Gtrunc to a file.

        filename -- name of the file to write to

        No return value.
        """
        resampled = self._resampledPDFDataSet()
        resampled.write(filename)
        return

    def writeResampledObsStr(self):
        """String representation of resampled PDF data in Gtrunc.

        Return data string.
        """
        resampled = self._resampledPDFDataSet()
        s = resampled.writeStr()
        return s

    def findParameters(self):
        """Obtain dictionary of parameters used by self.constraints.
        The keys of returned dictionary are integer parameter indices, and
        their values Parameter instances, with guessed initial values.

        returns dictionary of indices and Parameter instances
        """
        foundpars = {}
        for var, con in self.constraints.items():
            con.guess(self.getvar(var))
            for pidx, pguess in con.parguess.items():
                # skip if already found
                if pidx in foundpars:
                    continue
                # insert to foundpars otherwise
                if pguess is not None:
                    foundpars[pidx] = Parameter(pidx, initial=pguess)
                else:
                    foundpars[pidx] = Parameter(pidx, initial=0.0)
        return foundpars

    def applyParameters(self, parameters):
        """Evaluate constraint formulas and adjust self.initial

        parameters -- dictionary of parameter indices with Parameter instances.
                      Dictionary may also have float-type values.
        """
        # convert values to floats
        parvalues = { }
        for pidx, par in parameters.items():
            if isinstance(par, Parameter):
                parvalues[pidx] = par.initialValue()
            else:
                parvalues[pidx] = float(par)
        # evaluate constraints
        for var, con in self.constraints.items():
            # __setattr__ assigns var in self.initial
            self.setvar(var, con.evalFormula(parvalues))
        return

    def changeParameterIndex(self, oldidx, newidx):
        """Change a parameter index to a new value.

        This will replace all instances of one parameter name with another in
        this fit.
        """
        import re
        for var in self.constraints:
            formula = self.constraints[var].formula
            pat = r"@%i\b" % oldidx
            newformula = re.sub(pat, "@%i" % newidx, formula)
            self.constraints[var].formula = newformula
        return

    def copy(self, other=None):
        """Copy self to other. if other is None, create new instance

        other -- ref to other object

        returns reference to copied object
        """
        # check arguments
        if other is None:
            other = FitDataSet(self.name)
        PDFDataSet.copy(self, other)
        if isinstance(other, FitDataSet):
            # assigned attributes
            other._fitrmin = self._fitrmin
            other._fitrmax = self._fitrmax
            other._fitrstep = self._fitrstep
            other._rcalc_changed = self._rcalc_changed
            # copied attributes
            other.constraints = copy.deepcopy(self.constraints)
            other.initial = copy.deepcopy(self.initial)
            other.refined = copy.deepcopy(self.refined)
            # must also update the sampling on the new object
            st = self.getFitSamplingType()
            other.setFitSamplingType(st, self.fitrstep)
        return other

    def load(self, z, subpath):
        """Load data from a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        from diffpy.pdfgui.utils import asunicode, pickle_loads
        self.clear()
        subs = subpath.split('/')
        rootDict = z.fileTree[subs[0]][subs[1]][subs[2]][subs[3]]
        # raw data
        obsdata = asunicode(z.read(subpath + 'obs'))
        self.readObsStr(obsdata)

        # data from calculation
        content = pickle_loads(z.read(subpath + 'calc'))
        for item in FitDataSet.persistentItems:
            # skip items which are not in the project file
            if item not in content: continue
            # update dictionaries so that old project files load fine
            if item == 'initial':
                self.initial.update(content[item])
            elif item == 'refined':
                self.refined.update(content[item])
            else:
                setattr(self, item, content[item])
        self._updateRcalcRange()

        # constraints
        if 'constraints' in rootDict:
            from diffpy.pdfgui.control.pdfguicontrol import CtrlUnpickler
            self.constraints = CtrlUnpickler.loads(z.read(subpath+'constraints'))
            # handle renamed variable from old project files
            translate = {'qsig' : 'qdamp',  'qalp' : 'qbroad'}
            for old, new in translate.items():
                if old in self.constraints:
                    self.constraints[new] = self.constraints.pop(old)

        return

    def save(self, z, subpath):
        """Save data to a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        from diffpy.pdfgui.utils import safeCPickleDumps
        # write raw data
        z.writestr(subpath + 'obs', self.writeObsStr())
        content = {}
        for item in FitDataSet.persistentItems:
            content[item] = getattr(self, item, None)
        spkl = safeCPickleDumps(content)
        z.writestr(subpath+'calc', spkl)

        # make a picklable dictionary of constraints
        if self.constraints:
            spkl = safeCPickleDumps(self.constraints)
            z.writestr(subpath + 'constraints', spkl)
        return

    # interface for data sampling

    def getFitSamplingType(self):
        """Description of r-sampling used in the fit.  This method
        compares self.fitrstep with r-sampling in the observed data
        and with Nyquist r step.

        Return a string, possible values are "data", "Nyquist" or "custom".
        """
        eps = 1e-8
        if abs(self.fitrstep - self.getObsSampling()) < eps:
            rv = "data"
        elif abs(self.fitrstep - self.getNyquistSampling()) < eps:
            rv = "Nyquist"
        else:
            rv = "custom"
        return rv

    def setFitSamplingType(self, tp, value=None):
        """GUI interface to set fitrstep, i.e., r-grid for fitting.

        tp    -- description of fit sampling type.  Possible values are
                 "data"    ... same as used in experimental PDF
                 "Nyquist" ... sampling at Nyquist spacing
                 "custom"  ... user specified value
        value -- new value of fitrstep, only used when tp is "custom".

        No return value.

        Raises ValueError for unknown tp string.
        """
        if tp == "data":
            self.fitrstep = self.getObsSampling()
        elif tp == "Nyquist":
            self.fitrstep = self.getNyquistSampling()
        elif tp == "custom":
            self.fitrstep = max(value, self.getObsSampling())
        else:
            emsg = "Invalid value for fit sampling type."
            raise ValueError(emsg)
        return

    def getObsSampling(self):
        """Return the average r-step used in robs or zero when not defined.
        """
        n = len(self.robs)
        if n > 1:   rv = (self.robs[-1] - self.robs[0])/(n - 1.0)
        else:       rv = 0.0
        return rv

    def getNyquistSampling(self):
        """Return r-step corresponding to Nyquist sampling at the qmax value.
        When qmax is zero, return r-step in the observed data.
        """
        if self.qmax > 0.0:
            rv = numpy.pi / self.qmax
        else:
            rv = self.getObsSampling()
        return rv

    # Property Attributes

    def _updateRcalcSampling(self):
        """Helper method for resampling rcalc and interpolating related data.
        This method interpolates Gcalc, dGcalc, Gtrunc, dGtrunc, crw to new r
        grid.

        No return value.
        """
        if not self._rcalc_changed:     return
        frmin, frmax = self.fitrmin, self.fitrmax
        frstep = float(self.fitrstep)
        # new rcalc must cover the whole [fitrmin, fitrmax] interval
        # otherwise pdffit2 would complain
        robs_below = [ri for ri in self.robs if ri < frmin]
        if robs_below:
            rcalcfirst = robs_below[-1]
        else:
            rcalcfirst = self.robs[0]
        nrcalc = numpy.round(1.0*(frmax - rcalcfirst)/frstep)
        if frmax - (rcalcfirst + nrcalc * frstep) > frstep * 1e-8:
            nrcalc += 1
        newrcalc = rcalcfirst + frstep * numpy.arange(nrcalc + 1)
        # Gcalc:
        if len(self._Gcalc) > 0:
            newGcalc = grid_interpolation(self._rcalc, self._Gcalc, newrcalc)
            self._Gcalc = list(newGcalc)
        # dGcalc
        if len(self._dGcalc) > 0:
            newdGcalc = grid_interpolation(self._rcalc, self._dGcalc, newrcalc)
            self._dGcalc = list(newdGcalc)
        # invalidate Gtrunc and dGtrunc
        self._Gtrunc = []
        self._dGtrunc = []
        # everything has been interpolated here, we can overwrite _rcalc
        self._rcalc = list(newrcalc)
        # and finally set flag for up to date cache
        self._rcalc_changed = False
        return

    # fitrmin

    def _get_fitrmin(self):
        return self._fitrmin

    def _set_fitrmin(self, value):
        self._rcalc_changed = True
        self._fitrmin = float(value)
        return

    fitrmin = property(_get_fitrmin, _set_fitrmin, doc =
            "Lower boundary for simulated PDF curve.")

    # fitrmax

    def _get_fitrmax(self):
        return self._fitrmax

    def _set_fitrmax(self, value):
        self._rcalc_changed = True
        self._fitrmax = float(value)
        return

    fitrmax = property(_get_fitrmax, _set_fitrmax, doc =
            "Upper boundary for simulated PDF curve.")

    # fitrstep

    def _get_fitrstep(self):
        return self._fitrstep

    def _set_fitrstep(self, value):
        self._rcalc_changed = True
        self._fitrstep = float(value)
        return

    fitrstep = property(_get_fitrstep, _set_fitrstep, doc =
            "R-step used for simulated PDF curve.")

    # rcalc

    def _get_rcalc(self):
        self._updateRcalcSampling()
        return self._rcalc

    def _set_rcalc(self, value):
        self._rcalc = value
        return

    rcalc = property(_get_rcalc, _set_rcalc, doc =
        """R-grid for refined data, read-only.
        Use fitrmin, fitrmax, fitrstep to change it""")

    # Gcalc

    def _get_Gcalc(self):
        self._updateRcalcSampling()
        return self._Gcalc

    def _set_Gcalc(self, value):
        self._Gcalc = value
        return

    Gcalc = property(_get_Gcalc, _set_Gcalc, doc =
        "List of calculate G values.")

    # dGcalc

    def _get_dGcalc(self):
        self._updateRcalcSampling()
        return self._dGcalc

    def _set_dGcalc(self, value):
        self._dGcalc = value
        return

    dGcalc = property(_get_dGcalc, _set_dGcalc, doc =
        "List of standard deviations of Gcalc.")

    # Gtrunc

    def _get_Gtrunc(self):
        self._updateRcalcSampling()
        if not self._Gtrunc:
            newGtrunc = grid_interpolation(self.robs, self.Gobs, self.rcalc)
            self._Gtrunc = list(newGtrunc)
        return self._Gtrunc

    def _set_Gtrunc(self, value):
        self._Gtrunc = value
        return

    Gtrunc = property(_get_Gtrunc, _set_Gtrunc, doc =
        "Gobs resampled to rcalc grid.")

    # dGtrunc

    def _get_dGtrunc(self):
        self._updateRcalcSampling()
        if not self._dGtrunc:
            # use sum to avoid index error for empty arrays
            newdGtrunc = grid_interpolation(self.robs, self.dGobs, self.rcalc,
                    youtleft=sum(self.dGobs[:1]),
                    youtright=sum(self.dGobs[-1:]))
            self._dGtrunc = list(newdGtrunc)
        return self._dGtrunc

    def _set_dGtrunc(self, value):
        self._dGtrunc = value
        return

    dGtrunc = property(_get_dGtrunc, _set_dGtrunc, doc =
        "dGobs resampled to rcalc grid.")

    # Gdiff

    def _get_Gdiff(self):
        if len(self.Gcalc):
            rv = [(yo - yc) for yo, yc in zip(self.Gtrunc, self.Gcalc)]
        else:
            rv = []
        return rv

    Gdiff = property(_get_Gdiff, doc =
            "Difference between observed and calculated PDF on rcalc grid.")

    # crw
    def _get_crw(self):
        # crw comes from the engine, so it doesn't need rescaling
        return self._crw

    def _set_crw(self, value):
        if len(value) != len(self.rcalc):
            self._crw = [0.0] * len(self.rcalc)
        else:
            self._crw = value[:]
        return

    crw = property(_get_crw, _set_crw, doc =
            "cumulative rw on rcalc grid")

    # End of Property Attributes


# End of class FitDataSet


##############################################################################
# helper functions
##############################################################################

def grid_interpolation(x0, y0, x1, youtleft=0.0, youtright=0.0):
    """Linear interpolation of x0, y0 values to a new grid x1.

    x0       -- original x-grid, must be equally spaced
    y0       -- original y values
    x1       -- new x-grid, it can have any spacing
    youtleft -- value for interpolated y1 for x1 below the x0 range
    youtright -- value for interpolated y1 for x1 above the x0 range

    Return numpy.array of interpolated y1 values.
    """
    x0 = numpy.array(x0, copy=False, dtype=float)
    y0 = numpy.array(y0, copy=False, dtype=float)
    n0 = len(x0)
    x1 = numpy.array(x1, copy=False, dtype=float)
    n1 = len(x1)
    y1 = youtright * numpy.ones(n1, dtype=float)
    if n0:
        y1[x1 < x0.min()] = youtleft
    # take care of special n0 lengths
    if n0 == 0:
        return y1
    elif n0 == 1:
        y1[x1 == x0[0]] = y0[0]
        return y1
    # here n0 > 1 so we can safely calculate dx0
    dx0 = (x0[-1] - x0[0]) / (n0 - 1.0)
    epsx = dx0 * 1e-8
    # find covered values in x1
    m1, = numpy.where(numpy.logical_and(x0[0] - epsx < x1, x1 < x0[-1] + epsx))
    ilo0 = numpy.floor((x1[m1] - x0[0])/dx0)
    ilo0 = numpy.array(ilo0, dtype=int)
    # ilo0 may be out of bounds for x1 close to the edge
    ilo0[ilo0 < 0] = 0
    ilo0[ilo0 > n0 - 2] = n0 - 2
    ihi0 = ilo0 + 1
    # make sure hi indices remain valid
    w0hi = (x1[m1] - x0[ilo0]) / dx0
    w0lo = 1.0 - w0hi
    y1[m1] = w0lo*y0[ilo0] + w0hi*y0[ihi0]
    return y1

# simple test code
if __name__ == "__main__":
    FitDataSet('name')

# End of file
