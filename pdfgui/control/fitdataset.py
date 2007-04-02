#!/usr/bin/env python
########################################################################
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
########################################################################

"""class FitDataSet for experimental PDF data and related fitting parameters
"""

import copy, re
from pdfdataset import PDFDataSet
from parameter import Parameter
from constraint import Constraint
from controlerrors import ControlStatusError

class FitDataSet(PDFDataSet):
    """FitDataSet stores experimental and calculated PDF data and related
    fitting parameters.  Inherited from PDFDataSet.

    Data members (in addition to those in PDFDataSet):
        rcalc       -- list of r points where Gcalc is calculated
        Gcalc       -- list of calculated G values
        dGcalc      -- list of standard deviations of Gcalc
        fitrmin     -- lower boundary for data fitting
        fitrmax     -- upper boundary for data fitting
        constraints -- dictionary of { var_string : Constraint_instance }
        initial     -- dictionary of initial values of refinable variables
        refined     -- dictionary of refined values of refinable variables
    Calculated members:
        Gtrunc      -- truncated Gobs from fitmin to fitmax
        Gdiff       -- difference curve, Gdiff = Gtrunc - Gcalc

    Refinable variables:  qsig, qalp, dscale
    Note: self.refvar is the same as self.initial[refvar].

    Global member:
        persistentItems -- list of attributes saved in project file
    """

    persistentItems = [ 'rcalc', 'Gcalc', 'dGcalc', 'fitrmin', 'fitrmax',
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
        """Assign qsig, qalp, dscale assign in self.initial.
        """
        if name in ('qsig', 'qalp', 'dscale'):
            self.initial[name] = value
        elif name in ("Gtrunc", "Gdiff"):
            pass
        else:
            self.__dict__[name] = value
        return

    def __getattr__(self, name):
        """Obtain qsig, qalp, dscale values from self.initial.
        This is called only when normal attribute lookup fails.
        """
        if name in ('qsig', 'qalp', 'dscale'):
            value = self.initial[name]
        elif name == "Gtrunc":
            if self.Gcalc == []:
                return []
            # start:stop is a slice of Gobs corresponding to Gcalc
            start = len([1 for r in self.robs if r < self.fitrmin])
            stop  = start + len(self.Gcalc)
            return self.Gobs[start:stop]
        elif name == "Gdiff":
            # this returns [] when Gcalc is not available
            import operator
            return map(operator.sub, self.Gtrunc, self.Gcalc)
        else:
            raise AttributeError, "A instance has no attribute '%s'" % name
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
        ynames = [ 'Gobs', 'Gcalc', 'Gdiff', 'Gtrunc', 'dGcalc' ] + \
                 self.constraints.keys()
        return ynames
    
    def getXNames(self):
        """get names of data item which can be plotted as x
        
        returns list of strings
        """
        return self.metadata.keys() + ['r',]

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
        elif name in ( 'Gobs', 'Gcalc', 'Gtrunc', 'Gdiff', 'robs', 'rcalc'):
            return getattr(self, name)
                    
        # fitting's repository is preferred
        return  self.owner._getData(self, name, step)
        
    def clear(self):
        """Reset all data members to initial empty values.
        """
        PDFDataSet.clear(self)
        self.rcalc = []
        self.Gcalc = []
        self.dGcalc = []
        self.fitrmin = None
        self.fitrmax = None
        self.constraints = {}
        self.refined = {}
        return

    def clearRefined(self):
        """Clear all refinement results.
        """
        self.rcalc = []
        self.Gcalc = []
        self.dGcalc = []
        self.refined = {}
        return

    def obtainRefined(self, server, idataset):
        """Upload refined datataset from PdfFit server instance.

        server   -- instance of PdfFit server
        idataset -- index of this dataset in server
        """
        server.setdata(idataset)
        if not self.rcalc:
            # only need to update once
            self.rcalc = server.getR()
    
        self.Gcalc = server.getpdf_fit()
        # we need to replace this with direct interface to dGcalc
        self.dGcalc = []
        spdf = server.save_pdf_string(idataset).strip()
        for line in spdf.split('\n'):
            sdGcalc = line.split()[3]
            self.dGcalc.append(float(sdGcalc))
        # dGcalc done here
        for var in ('qsig', 'qalp', 'dscale'):
            self.refined[var] = server.getvar(var)
        return

    def read(self, filename):
        """Same as readObs().
        """
        return self.readObs(filename)

    def readObs(self, filename):
        """Load experimental PDF data from PDFGetX2 or PDFGetN gr file.
        
        filename -- file to read from

        returns self
        """
        PDFDataSet.read(self, filename)
        if self.fitrmin is None:
            self.fitrmin = self.rmin
        else:
            self.fitrmin = max(self.rmin, self.fitrmin)
        if self.fitrmax is None:
            self.fitrmax = self.rmax
        else:
            self.fitrmax = min(self.rmax, self.fitrmax)
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
        return self

    def write(self, filename):
        """Same as writeCalc().  Use writeObs() to save experimental PDF data.
        """
        return self.writeCalc(filename)

    def writeCalc(self, filename):
        """Write calculated PDF data to a file.
        
        filename -- name of file to write to
        """
        bytes = self.writeCalcStr()
        f = open( filename, 'w' )
        f.write(bytes)
        f.close()
        return

    def writeStr(self):
        """Same as writeCalcStr.  Use writeObsStr() for experimental PDF.
        """
        return self.writeCalcStr()

    def writeCalcStr(self):
        """String representation of calculated PDF data.
        
        returns data string
        """
        if self.Gcalc == []:
            raise ControlStatusError, "Gcalc not available"
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
        # qsig
        lines.append('qsig=%g' % self.refined['qsig'])
        # qalp
        lines.append('qalp=%g' % self.refined['qalp'])
        # dscale
        lines.append('dscale=%g' % self.refined['dscale'])
        # fitrmin, fitrmax
        if self.fitrmin is not None and self.fitrmax is not None:
            lines.append('fitrmin=%g' % self.fitrmin)
            lines.append('fitrmax=%g' % self.fitrmax)
        # metadata
        if len(self.metadata) > 0:
            lines.append('# metadata')
            for k, v in self.metadata.iteritems():
                lines.append( "%s=%s" % (k,v) )
        # write data:
        lines.append('##### start data')
        lines.append('#L r(A) G(r) d_r d_Gr Gdiff')
        # evaluate Gdiff here so it is not calculated many times
        Gdiff = self.Gdiff
        for i in range(len(self.rcalc)):
            lines.append( '%g %g %.1f %g %g' % (self.rcalc[i],
                          self.Gcalc[i], 0.0, self.dGcalc[i], Gdiff[i]) )
        # lines are ready here
        datastring = "\n".join(lines) + "\n"
        return datastring

    def writeObs(self, filename):
        """Write observed PDF data to a file.
        
        filename -- name of file to write to
        """
        return PDFDataSet.write(self, filename)

    def writeObsStr(self):
        """String representation of observed PDF data.
        
        returns data string
        """
        return PDFDataSet.writeStr(self)

    def findParameters(self):
        """Obtain dictionary of parameters used by self.constraints.
        The keys of returned dictionary are integer parameter indices, and
        their values Parameter instances, with guessed initial values.

        returns dictionary of indices and Parameter instances
        """
        foundpars = {}
        for var, con in self.constraints.iteritems():
            con.guess(self.getvar(var))
            for pidx, pguess in con.parguess.iteritems():
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
        for pidx, par in parameters.iteritems():
            if isinstance(par, Parameter):
                parvalues[pidx] = par.initialValue()
            else:
                parvalues[pidx] = float(par)
        # evaluate constraints
        for var, con in self.constraints.iteritems():
            # __setattr__ assigns var in self.initial
            self.setvar(var, con.evalFormula(parvalues))
        return

    def changeParameterIndex(self, oldidx, newidx):
        """Change a parameter index to a new value.

        This will replace all instances of one parameter name with another in
        this fit.
        """
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
            assign_attributes = ('fitrmin', 'fitrmax')
            copy_attributes = ('constraints', 'initial', 'refined')
            for a in assign_attributes:
                setattr(other, a, getattr(self, a))
            for a in copy_attributes:
                setattr(other, a, copy.deepcopy(getattr(self, a)))
        return other

    def load(self, z, subpath):
        """Load data from a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        #subpath = projname/fitname/dataset/myname/
        subs = subpath.split('/')
        rootDict = z.fileTree[subs[0]][subs[1]][subs[2]][subs[3]]
        import cPickle
        # raw data
        self.readObsStr(z.read(subpath+'obs'))
        
        # data from calculation
        content = cPickle.loads(z.read(subpath+'calc'))
        for item in self.persistentItems:
            setattr(self, item, content.get(item, None))
           
        # constraints
        if rootDict.has_key('constraints'):
            from pdfguicontrol import CtrlUnpickler
            self.constraints = CtrlUnpickler.loads(z.read(subpath+'constraints'))
            #for k,v in constraints.items():
            #    self.constraints[k] = Constraint(v)

        return
        
    def save(self, z, subpath):
        """Save data to a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        import cPickle
        # write raw data
        z.writestr(subpath + 'obs', self.writeObsStr())
        content = {}
        for item in self.persistentItems:
            content[item] = getattr(self, item, None)
        bytes = cPickle.dumps(content, cPickle.HIGHEST_PROTOCOL)
        z.writestr(subpath+'calc', bytes)
        
        # make a picklable dictionary of constraints
        if self.constraints:
            # make a picklable dictionary of constraints
            #constraints = {}
            #for k,v in self.constraints.items():
            #    constraints[k] = v.formula
            bytes = cPickle.dumps(self.constraints, cPickle.HIGHEST_PROTOCOL)
            z.writestr(subpath+'constraints', bytes)
        return

# End of class FitDataSet

# simple test code
if __name__ == "__main__":
    FitDataSet('name')

# version
__id__ = "$Id$"

# End of file
