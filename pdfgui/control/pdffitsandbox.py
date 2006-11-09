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

"""PdfFit class for fitting pdf data to a model."""

import sys
import os
import copy

from calculation import Calculation
from fitting import Fitting
from fitstructure import FitStructure
from fitdataset import FitDataSet
from controlerrors import ControlRuntimeError
from controlerrors import ControlKeyError
from parameter import Parameter
from constraint import Constraint

class PdfFitSandbox:
    """PdfFit sandbox for importing pdffit2 scripts.

    Data members:
        _fits       -- list of Fitting instances
        _curphase   -- 0 based index of selected phase
        _curdataset -- 0 based index of selected datased
    """

    
    # constants and enumerators from pdffit.h:
    # selection of all atoms
    _atomselect = { 'ALL' : -1 }
    # constraint type identifiers
    _FCON = { 'IDENT' : 1, 'FCOMP' : 2, 'FSQR' : 3 }
    # scattering type identifiers
    _Sctp = { 'X' : 0, 'N' : 1 }
    # dataset variables
    _dataset_vars = ( 'qsig', 'qalp', 'dscale' )

    def __init__(self):
        self._fits = [ Fitting('0').stripped() ]
        # initialize _curdataset and _curphase to invalid values
        self._curdataset = None
        self._curphase = None
        aliases = self._atomselect.keys() + self._FCON.keys() + \
                  self._Sctp.keys()
        for a in aliases:
            setattr(self, a, a)
        return

    def allfits(self):
        """Get resulting list of Fitting and Calculations
        """
        return self._fits[0:-1]

    def sandbox(self):
        """Create sandbox dictionary suitable for script evaluation

        returns sandbox dictionary
        """
        import inspect
        box  = {}
        for a, v in inspect.getmembers(self):
            # keep private parts and sandbox out of sandbox
            if a[:1] == "_" or a in ("allfits", "sandbox", "loadscript"):
                continue
            box[a] = v
        return box

    def loadscript(self, scriptfile):
        """Execute scriptfile in this sandbox.  Before it is executed, change
        to script directory and shadow pdffit and pdffit2 modules
        
        scriptfile  --  path to the script to be loaded
        """
        # go to script directory
        orgdir = os.getcwd()
        scriptdir = os.path.dirname(scriptfile) or "."
        scriptbase = os.path.basename(scriptfile)
        os.chdir(scriptdir)
        # shadow pdffit and pdffit2 modules
        savemodules = { }
        for modname in [ 'pdffit', 'pdffit2' ]:
            if modname in sys.modules:
                savemodules[modname] = sys.modules[modname]
        import new
        sys.modules['pdffit'] = new.module('pdffit')
        sys.modules['pdffit2'] = pdffit2 = new.module('pdffit2')
        # shadow PdfFit class
        pdffit2.PdfFit = None
        # execute the file
        execfile(scriptbase, self.sandbox())
        # restore modules
        del sys.modules['pdffit']
        del sys.modules['pdffit2']
        for modname, mod in savemodules.iteritems():
            sys.modules[modname] = mod
        # get to the original directory
        os.chdir(orgdir)
        return

    def read_struct(self, filename):
        """Read structure from file into memory.
        
        filename  -- name of file from which to read structure
        
        Raises:
            pdffit2.calculationError when a lattice cannot be created from the
            given structure
            pdffit2.structureError when a structure file is malformed
            IOError when the file cannot be read from the disk
        """
        curfit = self._fits[-1]
        name, ext = os.path.splitext(os.path.basename(filename))
        fs = FitStructure(name).read(filename, 'pdffit')
        curfit.add(fs)
        self._curphase = len(curfit.strucs) - 1
        return

    def read_struct_string(self, s, name=""):
        """Read structure from a string into memory.
        
        s    -- string containing the contents of the structure file
        name -- tag with which to label structure
        
        Raises:
            pdffit2.calculationError when a lattice cannot be created from the
            given structure
            pdffit2.structureError when a structure file is malformed
        """
        curfit = self._fits[-1]
        fs = FitStructure(name).readStr(s, 'pdffit')
        curfit.add(fs)
        self._curphase = len(curfit.strucs) - 1
        return

    def read_data(self, filename, stype, qmax, qsig):
        """Read pdf data from file into memory.
 
        filename -- name of file from which to read data
        stype    -- 'X' (xray) or 'N' (neutron)
        qmax     -- maximum q value
        qsig     -- instrumental q-resolution factor
        
        Raises:
            IOError when the file cannot be read from disk
        """
        curfit = self._fits[-1]
        name, ext = os.path.splitext(os.path.basename(filename))
        fd = FitDataSet(name).read(filename)
        fd.stype = stype
        fd.qmax = qmax
        fd.qsig = qsig
        curfit.add(fd)
        self._curdataset = len(curfit.datasets) - 1
        return

    def read_data_string(self, s, stype, qmax, qsig, name=""):
        """Read pdf data from a string into memory.

        s       -- string containing the contents of the data file
        stype   -- 'X' (xray) or 'N' (neutron)
        qmax    -- maximum q value
        qsig    -- instrumental q-resolution factor
        name    -- tag with which to label data
        """
        curfit = self._fits[-1]
        fd = FitDataSet(name).readStr(s)
        fd.stype = stype
        fd.qmax = qmax
        fd.qsig = qsig
        curfit.add(fd)
        self._curdataset = len(curfit.datasets) - 1
        return

    def read_data_lists(self, stype, qmax, qsig, r_data, Gr_data,
            dGr_data = None, name = "list"):
        """Read pdf data into memory from lists.
        
        All lists must be of the same length.
        stype       -- 'X' (xray) or 'N' (neutron)
        qmax        -- maximum q value
        qsig        -- instrumental q-resolution factor
        r_data      -- list of r-values
        Gr_data     -- list of G(r) values
        dGr_data    -- list of G(r) uncertainty values
        name        -- tag with which to label data
        
        Raises:
            NotImplementedError
        """
        raise NotImplementedError, "ok, somebody needs read_data_lists()"
        return

    def pdfrange(self, iset, rmin, rmax):
        """Set the range of the fit in specified dataset.
        
        iset    -- data set to consider, indexed from 1 or 'ALL'
        rmin    -- minimum r-value of fit
        rmax    -- maximum r-value of fit
        """
        import types
        if not rmin < rmax:
            raise ControlRuntimeError, 'Invalid pdfrange limits.'
        if type(iset) is types.StringType and iset.upper() == 'ALL':
            seldatasets = self._fits[-1].datasets
        else:
            seldatasets = self._fits[-1].datasets[iset-1:iset]
        for dataset in seldatasets:
            if rmin < dataset.rmin:
                raise ControlRuntimeError, \
                        'Invalid pdfrange, rmin is too low.'
            dataset.fitrmin = float(rmin)
            if rmax > dataset.rmax:
                raise ControlRuntimeError, \
                        'Invalid pdfrange, rmax is too large.'
            dataset.fitrmax = float(rmax)
        return

    def reset(self):
        """Clear the last fit.
        """
        lastidx = len(self._fits) - 1
        self._fits[-1] = Fitting(str(lastidx)).stripped()
        self._curdataset = None
        self._curphase = None
        return

    def alloc(self, stype, qmax, qsig, rmin, rmax, rlen):
        """Allocate space for a PDF calculation.
        
        The structure from which to calculate the PDF must first be imported with
        the read_struct() or read_struct_string() method.
        stype   -- 'X' (xray) or 'N' (neutron)
        qmax    -- maximum q value
        qsig    -- instrumental q-resolution factor
        rmin    -- minimum r-value of calculation
        rmax    -- maximum r-value of calculation
        rlen    -- number of data points in calculation
        """
        # convert last fit to calculation
        lastidx = len(self._fits) - 1
        last = self._fits[-1]
        newcalc = Calculation(last.name)
        newcalc.strucs = last.strucs
        newcalc.stype = stype
        newcalc.qmax = qmax
        newcalc.qsig = qsig
        newcalc.rmin = rmin
        newcalc.rmax = rmax
        newcalc.rlen = rlen
        newcalc.rstep = (rmax - rmin)/(rlen - 1)
        self._fits[-1] = newcalc
        return


    def calc(self):
        """Calculate the PDF of the imported structure.
        
        Space for the calculation must first be allocated with the alloc()
        method.
        
        Raises:
            ControlRuntimeError when space for calculation has not been
            allocated
        """
        last = self._fits[-1]
        if not isinstance(last, Calculation):
            raise ControlRuntimeError, "calculation has to be allocated"
        newidx = len(self._fits)
        self._fits.append( Fitting(str(newidx)).stripped() )
        self._curdataset = None
        self._curphase = None
        return

    def refine(self, toler=0.00000001):
        """Fit the theory to the imported data.

        toler   --  tolerance of the fit, ignored for now
        """
        last = self._fits[-1]
        newname = str(len(self._fits))
        if isinstance(last, Fitting):
            newfitting = last.copy().stripped()
            newfitting.name = newname
            # link parameters to last fitting
            for idx, par in last.parameters.iteritems():
                linkedpar = copy.copy(par)
                linkedpar.setInitial("="+last.name)
                newfitting.parameters[idx] = linkedpar
        else:
            newfitting = Fitting(newname).stripped()
        self._fits.append(newfitting)
        return

    def refine_step(self, toler = 0.00000001):
        """Run a single step of the fit.
        
        toler   --  tolerance of the fit

        Raises:
            NotImplementedError - I am not importing such beast
        """
        raise NotImplementedError, \
                "Go and figure how to import refine_step() yourself!"
        return 1

    def save_pdf(self, iset, fname):
        """Save calculated or fitted PDF to file.  Ignored.
        """
        return

    def save_pdf_string(self, iset):
        """Save calculated or fitted PDF to string.
        
        iset    -- data set to save, indexed from 1

        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "save_pdf_string() is not supported."
        return ""

    def save_dif(self, iset, fname):
        """Save data and fitted PDF difference to file.  Ignored.
        
        iset    -- data set to save
        fname   -- file to write to
        """
        return

    def save_dif_string(self, iset):
        """Save data and fitted PDF difference to string.
        
        iset    -- data set to save
        
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "save_dif_string() is not supported."
        return ""

    def save_res(self, fname):
        """Save fit-specific data to file.  Ignored.
        """
        return

    def save_res_string(self):
        """save_res_string() --> Save fit-specific data to a string.
        
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "save_res_string() is not supported."
        return ""

    def save_struct(self, ip, fname):
        """Save structure resulting from fit to file.  Ignored.
        
        ip    -- phase to save
        """
        return

    def save_struct_string(self, ip):
        """Save structure resulting from fit to string.
        
        ip    -- phase to save
        
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "save_struct_string() is not supported."
        return ""

    def show_struct(self, ip):
        """Print structure resulting from fit.  Ignored.
        
        ip    -- phase to display
        """
        return

    def constrain(self, var, par, fcon=None):
        """Constrain a variable to a parameter.
        
        A variable can be constrained to a number or equation string.
        var     -- variable to constrain, such as x(1)
        par     -- parameter which to constrain the variable. This can be
                   an integer or an equation string containing a reference
                   to another parameter. Equation strings use standard c++
                   syntax. The value of a constrained parameter is accessed
                   as @p in an equation string, where p is the parameter.
                   e.g.
                   >>>  constrain(x(1), 1)
                   >>>  constrain(x(2), "0.5+@1")
        fcon    -- 'IDENT', 'FCOMP', or 'FSQR', old-style constraint formulas:
                       'IDENT'  @par
                       'FCOMP'  1.0-@par
                       'FSQR'   @par*@par
        """
        import types
        curfit = self._fits[-1]
        if isinstance(curfit, Calculation):
            raise ControlRuntimeError, \
                "Cannot define constrain for calculation."
        if type(var) is types.MethodType:
            var = var()
        if fcon is not None:
            if fcon == "IDENT":
                formula = "@%i" % par
            elif fcon == 'FCOMP':
                formula = "1.0-@%i" % par
            elif fcon == 'FSQR':
                formula = "@%i*@%i" % (par, par)
            else:
                raise ControlRuntimeError, "invalid value of fcon %r" % fcon
        elif type(par) is types.IntType:
            formula = "@%i" % par
        else:
            formula = par
        if var in PdfFitSandbox._dataset_vars:
            curdataset = curfit.datasets[self._curdataset]
            curdataset.constraints[var] = Constraint(formula)
        else:
            curphase = curfit.strucs[self._curphase]
            curphase.constraints[var] = Constraint(formula)
        return

    def setpar(self, idx, val):
        """Set value of constrained parameter.
        
        idx     --  parameter index
        val     --  Either a numerical value or a reference to variable
        
        Raises:
            KeyError when parameter is yet to be constrained
        """
        # people do not use parenthesis, e.g., "setpar(3, qsig)"
        # in such case val is a reference to PdfFit method
        import types
        curfit = self._fits[-1]
        if type(val) is types.MethodType:
            val = val()
        # here val can be either number or variable string
        if type(val) in (types.IntType, types.FloatType):
            value = float(val)
        # it is string of either dataset variable
        elif val in PdfFitSandbox._dataset_vars:
            curdataset = curfit.datasets[self._curdataset]
            value = curdataset.getvar(val)
        # or phase variable otherwise
        else:
            curphase = curfit.strucs[self._curphase]
            value = curphase.getvar(val)
        # here we can set the parameter
        curfit.parameters[idx] = Parameter(idx, initial=value)
        return

    def getpar(self, idx):
        """Get value of parameter.

        idx     --  parameter index
        
        Raises:
            KeyError if parameter does not exists
        """
        curfit = self._fits[-1]
        return curfit.parameters[idx].initialValue()

    def fixpar(self, idx):
        """Fix a parameter.

        idx     --  parameter index
        
        Fixed parameters are not fitted in a refinement. Passed parameter can be
        'ALL', in which case all parameters are fixed.

        Raises:
            ControlKeyError if parameter does not exists
        """
        curfit = self._fits[-1]
        import types
        if type(idx) is types.StringType and idx.upper() == 'ALL':
            for p in curfit.parameters.values():
                p.fixed = True
        else:
            try:
                p = curfit.parameters[idx]
            except KeyError:
                raise ControlKeyError, "parameter %i does not exist" % idx
            p.fixed = True
        return

    def freepar(self, idx):
        """Free a parameter.
        
        idx     --  parameter index

        Freed parameters are fitted in a refinement. Passed parameter can be
        ALL, in which case all parameters are freed.

        Raises:
            ControlKeyError if parameter does not exists
        """
        curfit = self._fits[-1]
        import types
        if type(idx) is types.StringType and idx.upper() == 'ALL':
            for p in curfit.parameters.values():
                p.fixed = False
        else:
            try:
                p = curfit.parameters[idx]
            except KeyError:
                raise ControlKeyError, "parameter %i does not exist" % idx
            p.fixed = False
        return

    def setvar(self, var, val):
        """Set the value of a variable.
        
        Raises:
            ControlKeyError if variable does not yet exist
        """
        import types
        curfit = self._fits[-1]
        if type(var) is types.MethodType:
            var = var()
        # here var is string of either dataset variable
        if var in PdfFitSandbox._dataset_vars:
            curdataset = curfit.datasets[self._curdataset]
            curdataset.setvar(var, val)
        else:
        # or phase variable otherwise
            curphase = curfit.strucs[self._curphase]
            curphase.setvar(var, val)
        return

    def getvar(self, var):
        """Get stored value of a variable.
        
        Raises:
            ControlKeyError if variable index does not exist

        returns value of variable var.
        """
        import types
        curfit = self._fits[-1]
        if type(var) is types.MethodType:
            var = var()
        # here var is string of either dataset variable
        if var in PdfFitSandbox._dataset_vars:
            curdataset = curfit.datasets[self._curdataset]
            value = curdataset.getvar(var)
        else:
        # or phase variable otherwise
            curphase = curfit.strucs[self._curphase]
            value = curphase.getvar(var)
        return value

    def getrw(self):
        """Get goodness of fit value, rw.
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "getrw() is not supported"
        return 0.0

    def getR(self):
        """Get r-points used in the fit.
        
        This function should only be called after data has been loaded or
        calculated. Before a refinement, the list of r-points will reflect the
        data. Afterwords, they will reflect the fit range.
        
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "getR() is not supported"
        return []

    def getpdf_fit(self):
        """Get fitted PDF.
        
        This function should only be called after a refinement or refinement
        step has been done.
        
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "getpdf_fit() is not supported"
        return []

    def getpdf_obs(self):
        """Get observed PDF.
        
        This function should only be called after data has been loaded or
        calculated. Before a refinement, the list of r-points will reflect the
        data. Afterwords, they will reflect the fit range.
        
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "getpdf_obs() is not supported"
        return []

    def get_atoms(self):
        """Get atoms in the structure.
        
        This function should only be called after a structure has been loaded.
        
        Raises:
            NotImplementedError - we cannot return anything without engine.
        """
        raise NotImplementedError, "get_atoms() is not supported"
        return []

    def setphase(self, ip):
        """Switch to phase ip.

        ip  --  phase index starting from 1
        
        All parameters assigned after this method is called refer only to the
        current phase.
        
        Raises:
            IndexError if phase ip does not exist
        """
        # check if we have valid index
        curphase = self._fits[-1].strucs[ip - 1]
        # if we get here, it is OK
        self._curphase = ip - 1
        return

    def setdata(self, iset):
        """Set specified dataset in focus.
        
        iset  --  dataset index starting from 1

        Raises:
            IndexError if dataset iset does not exist
        """
        # check if we have valid index
        curdataset = self._fits[-1].datasets[iset - 1]
        # if we get here, it is OK
        self._curdataset = iset - 1
        return

    def psel(self, ip):
        """Associate the current data set with phase ip.

        ip -- phase index starting from 1
        
        Raises:
            NotImplementedError
        """
        raise NotImplementedError, "psel() is not supported"
        return

    def pdesel(self, ip):
        """Unassociate the current data set with phase ip.
        
        ip -- phase index starting from 1

        Raises:
            NotImplementedError
        """
        raise NotImplementedError, "pdesel() is not supported"
        return

    def isel(self, ip, i):
        """Select atoms for calculating partial PDF
        
        ip  --  phase index starting from 1, if set to 'ALL' isel applies
                to all phases
        i  --   atom index starting from 1, if set to 'ALL', select all atoms
        
        Raises: 
            NotImplementedError
        """
        raise NotImplementedError, "isel() is not supported"
        return

    def idesel(self, ip, i):
        """Deselect atoms for calculating partial PDF
        
        ip  --  phase index starting from 1, if set to 'ALL' isel applies
                to all phases
        i  --   atom index starting from 1, if set to 'ALL', select all atoms
        
        Raises: 
            NotImplementedError
        """
        raise NotImplementedError, "idesel() is not supported"
        return

    def jsel(self, ip, i):
        """Select atoms for calculating partial PDF
        
        ip  --  phase index starting from 1, if set to 'ALL' jsel applies
                to all phases
        i  --   atom index starting from 1, if set to 'ALL', select all atoms
        
        Raises: 
            NotImplementedError
        """
        raise NotImplementedError, "jsel() is not supported"
        return

    def jdesel(self, ip, i):
        """Deselect atoms for calculating partial PDF
        
        ip  --  phase index starting from 1, if set to 'ALL' jsel applies
                to all phases
        i  --   atom index starting from 1, if set to 'ALL', select all atoms
        
        Raises: 
            NotImplementedError
        """
        raise NotImplementedError, "jdesel() is not supported"
        return

    def bang(self, ia, ja, ka):
        """bang(ia, ja, ka) --> Get the bond angle defined by atoms ia, ja, ka.
        
        Raises:
            NotImplementedError
        """
        raise NotImplementedError, "bang() is not supported"
        return 0.0

    def blen(self, *args):
        """blen(ia, ja) --> Get bond between atoms ia and ja.  Ignored.

        blen(a1, a2, lb, ub) --> Print length of all a1-a2 bonds in range
        [lb,ub], where a1 and a2 are integers representing atom types. 1
        represent the first type of atom in the phase, 2 represents the second
        type of atom in the structure, an so on. Either a1 or a2 can be the
        keyword ALL, in which all atom types are used for that end of the
        calculated bonds.
        """
        return

    def show_scat(self, stype):
        """Print scattering length for all atoms.  Ignored.
        
        stype -- 'X' (xray) or 'N' (neutron).
        """
        return

    def show_scat_string(self, stype):
        """Get string with scattering length for all atoms.
        
        stype -- 'X' (xray) or 'N' (neutron).
        
        Raises:
            NotImplementedError
        """
        raise NotImplementedError, "show_scat_string() is not supported"
        return ""

    def set_scat(self, *args):
        """set_scat('N', itype, len) --> Set neutron scattering length for itype
        atoms.  
        
        set_scat('X', a1, b1, a2, b2, a3, b3, a4, b4, c) --> I don't know what
        this does.  
        
        Raises: 
            NotImplementedError
            ValueError if input variables are bad 
        """
        raise NotImplementedError, "set_scat() is not supported"
        return

    def reset_scat(self, stype, itype):
        """reset_scat(stype, itype) --> I don't know what this does.
        
        Raises: 
            NotImplementedError
            ValueError if input variables are bad 
        """
        raise NotImplementedError, "reset_scat() is not supported"
        return

    def num_atoms(self):
        """Get number of atoms in current phase.

        Raises:
            ControlKeyError if phase does not exists
        """
        curfit = self._fits[-1]
        curphase = curfit.strucs[self._curphase]
        return len(curphase)

    # Begin refineable variables.

    def lat(self, n):
        """lat(n) --> Get reference to lattice variable n.
        
        n can be an integer or a string representing the lattice variable.
        1 <==> 'a'
        2 <==> 'b'
        3 <==> 'c'
        4 <==> 'alpha'
        5 <==> 'beta'
        6 <==> 'gamma'
        """
        LatParams = { 'a':1, 'b':2, 'c':3, 'alpha':4, 'beta':5, 'gamma':6 }
        import types
        if type(n) is types.StringType:
            n = LatParams[n]
        return "lat(%i)" % n


    def x(self, i):
        """x(i) --> Get reference to x-value of atom i."""
        return "x(%i)" % i


    def y(self, i):
        """y(i) --> Get reference to y-value of atom i."""
        return "y(%i)" % i


    def z(self, i):
        """z(i) --> Get reference to z-value of atom i."""
        return "z(%i)" % i


    def u11(self, i):
        """u11(i) --> Get reference to U(1,1) for atom i.
        
        U is the anisotropic thermal factor tensor.
        """
        return "u11(%i)" % i


    def u22(self, i):
        """u22(i) --> Get reference to U(2,2) for atom i.
        
        U is the anisotropic thermal factor tensor.
        """
        return "u22(%i)" % i


    def u33(self, i):
        """u33(i) --> Get reference to U(3,3) for atom i.
        
        U is the anisotropic thermal factor tensor.
        """
        return "u33(%i)" % i


    def u12(self, i):
        """u12(i) --> Get reference to U(1,2) for atom i.
        
        U is the anisotropic thermal factor tensor.
        """
        return "u12(%i)" % i


    def u13(self, i):
        """u13(i) --> Get reference to U(1,3) for atom i.
        
        U is the anisotropic thermal factor tensor.
        """
        return "u13(%i)" % i


    def u23(self, i):
        """u23(i) --> Get reference to U(2,3) for atom i.
        
        U is the anisotropic thermal factor tensor.
        """
        return "u23(%i)" % i


    def occ(self, i):
        """occ(i) --> Get reference to occupancy of atom i."""
        return "occ(%i)" % i


    def pscale(self):
        """pscale() --> Get reference to pscale.
       
        pscale is the fraction of the total structure that the current phase
        represents.
        """
        return "pscale"


    def pfrac(self):
        """pfrac() --> same as pscale.
       
        pscale is the fraction of the total structure that the current phase
        represents.
        """
        return self.pscale()


    def srat(self):
        """srat() --> Get reference to sigma ratio.
        
        The sigma ratio determines the reduction in the Debye-Waller factor for
        distances below rcut.
        """
        return "srat"


    def delta1(self):
        """delta1() --> Get reference to linear sharpening factor
        
        1/R peak sharpening factor.
        """
        return "delta1"


    def delta2(self):
        """delta2() --> Get reference to delta2
        
        The phenomenological correlation constant in the Debye-Waller factor.
        The (1/R^2) peak sharpening factor.
        """
        return "delta2"


    def delta(self):
        """delta() --> deprecated, same as delta2().
        """
        return self.delta2()


    def gamma(self):
        """gamma() --> deprecated, same as delta1().
        """
        return self.delta1()


    def dscale(self):
        """dscale() --> Get reference to dscale.
        
        The data scale factor.
        """
        return "dscale"

    def qsig(self):
        """qsig() --> Get reference to qsig.
       
        instrument q-resolution factor.
        """
        return "qsig"


    def qalp(self):
        """qalp() --> Get reference to qalp.
       
        Quadratic peak sharpening factor.
        """
        return "qalp"


    def rcut(self):
        """rcut() --> Get reference to rcut.
        
        rcut is the value of r below which peak sharpening, defined by the sigma
        ratio (srat), applies.
        """
        return "rcut"

    # End refineable variables.
    
# End of class PdfFitSandbox

if __name__ == "__main__":
    p = PdfFitSandbox()
    print p.sandbox().keys()

# version
__id__ = "$Id$"

# End of file
