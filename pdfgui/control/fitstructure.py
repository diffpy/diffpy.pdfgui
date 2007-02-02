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

"""class FitStructure for storage of one phase and related fitting parameters
"""

# version
__id__ = "$Id$"

import copy
import re
import numpy
from pdfstructure import PDFStructure
from constraint import Constraint
from parameter import Parameter
from controlerrors import ControlTypeError, ControlValueError
from Structure import Atom

class FitStructure(PDFStructure):
    """FitStructure holds initial and refined structure and related fit
    parameters.  Inherited from PDFStructure.

    Data members (in adition to those in PDFStructure):
        owner       -- instance of parent Fitting (set in Organizer.add())
        initial     -- initial structure, same as self
        refined     -- refined structure when available or None
        constraints -- dictionary of { refvar_string : Constraint_instance }

    Refinable variables: pscale, delta1, delta2, srat, lat(n), where n = 1..6,
                         x(i), y(i), z(i), occ(i), u11(i), u22(i), u33(i),
                         u12(i), u13(i), u23(i), where i = 1..Natoms

    Non-refinable variable:  rcut
    """

    def __init__(self, name, *args, **kwargs):
        """Initialize FitDataSet.

        name         -- name of the data set.  The same name is used for
                        self.initial and self.final.
        args, kwargs -- optional arguments passed to parent PDFStructure
        """
        PDFStructure.__init__(self, name)
        self.owner = None
        # self.initial deliberately not assigned,
        # it gets mapped to self by __getattr__
        self.refined = None
        self.constraints = {}
        return
        
    def __getattr__(self, name):
        """Map self.initial to self.
        This is called only when normal attribute lookup fails.
        """
        if name == "initial":
            value = self
        else:
            raise AttributeError, "A instance has no attribute '%s'" % name
        return value

    def _getStrId(self):
        """make a string identifier
        
        return value: string id
        """
        return "p_" + self.name

    def clearRefined(self):
        """Clear all refinement results.
        """
        self.refined = None
        return

    def obtainRefined(self, server, iphase):
        """Upload refined phase from PdfFit server instance.

        server -- instance of PdfFit server
        iphase -- index of this phase in server
        """
        server.setphase(iphase)
        if self.refined is None:
            self.refined = PDFStructure(self.name)
        self.refined.readStr(server.save_struct_string(iphase), 'pdffit')
        return

    def findParameters(self):
        """Obtain dictionary of parameters used by self.constraints.
        The keys of returned dictionary are integer parameter indices, and
        the values are Parameter instances, with guessed initial values.

        returns dictionary of indices and Parameter instances
        """
        foundpars = {}
        for var, con in self.constraints.iteritems():
            con.guess(self.initial.getvar(var))
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
        """Evaluate constraint formulas and adjust initial PDFStructure.

        parameters -- dictionary of parameter indices with Parameter
                      instance values.  Values may also be float type.
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
            self.initial.setvar(var, con.evalFormula(parvalues))
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

    def _popAtomConstraints(self):
        """Take out atom-related items from the constraints dictionary.

        This is useful when atom indices are going to change due to
        insertion or removal of atoms.  See also _restoreAtomConstraints().

        Return a dictionary of atom instances vs dictionary of related
        refinable variables (stripped of "(siteindex)") and Constraint
        instances - for example {atom : {'u13' : constraint}}.
        """
        rv = {}
        # atom variable pattern
        avpat = re.compile(r'^([xyz]|occ|u11|u22|u33|u12|u13|u23)\((\d+)\)')
        for var in self.constraints.keys():
            m = avpat.match(var)
            if not m:   continue
            barevar = m.group(1)
            atomidx = int(m.group(2)) - 1
            cnts = rv.setdefault(self.initial[atomidx], {})
            cnts[barevar] = self.constraints.pop(var)
        return rv

    def _restoreAtomConstraints(self, acd):
        """Restore self.constraints from atom constraints dictionary.  This
        is useful for getting correct atom indices into refvar strings.
        See also _popAtomConstraints()

        acd -- dictionary obtained from _popAtomConstraints()
        """
        for i in range(len(self.initial)):
            a = self.initial[i]
            if not a in acd:    continue
            # there are some constraints for atom a
            siteindex = i + 1
            cnts = acd[a]
            for barevar, con in cnts.iteritems():
                var = barevar + "(%i)" % siteindex
                self.constraints[var] = con
        return

    def insertAtoms(self, index, atomlist):
        """Insert list of atoms before index and adjust self.constraints.

        index    -- position in the initial structure, atoms are appended
                    when larger than len(self.initial).
        atomlist -- list of atom instances.
        """
        acd = self._popAtomConstraints()
        self.initial[index:] = atomlist + self.initial[index:]
        self._restoreAtomConstraints(acd)
        return

    def deleteAtoms(self, indices):
        """Removed atoms at given indices and adjust self.constraints.

        indices -- list of integer indices of atoms to be deleted
        """
        acd = self._popAtomConstraints()
        # get unique, reverse sorted indices
        ruindices = dict.fromkeys(indices).keys()
        ruindices.sort()
        ruindices.reverse()
        for i in ruindices:
            self.initial.pop(i)
        self._restoreAtomConstraints(acd)
        return

    def expandSuperCell(self, mno):
        """Perform supercell expansion for this structure and adjust
        constraints for positions and lattice parameters.  New lattice
        parameters are multiplied and fractional coordinates divided by
        corresponding multiplier.  New atoms are grouped with their source
        in the original cell.
        
        mno -- tuple or list of three positive integer cell multipliers along
        the a, b, c axis
        """
        # check argument
        if tuple(mno) == (1, 1, 1):     return
        if min(mno) < 1:
            raise ControlValueError, "mno must contain 3 positive integers"
        # back to business
        acd = self._popAtomConstraints()
        mnofloats = numpy.array(mno[:3], dtype=float)
        ijklist = [(i,j,k) for i in range(mno[0])
                    for j in range(mno[1]) for k in range(mno[2])]
        # build a list of new atoms
        newatoms = []
        for a in self.initial:
            for ijk in ijklist:
                adup = Atom(a)
                adup.xyz = (a.xyz + ijk)/mnofloats
                newatoms.append(adup)
                # does atom a have any constraint?
                if a not in acd:    continue
                # add empty constraint dictionary for duplicate atom
                acd[adup] = {}
                for barevar, con in acd[a].iteritems():
                    formula = con.formula
                    if barevar in ("x", "y", "z"):
                        symidx = "xyz".index(barevar)
                        if ijk[symidx] != 0:
                            formula += " + %i" % ijk[symidx]
                        if mno[symidx] > 1:
                            formula = "(%s)/%.1f" % (formula, mno[symidx])
                            formula = re.sub(r'\((@\d+)\)', r'\1', formula)
                    # keep other formulas intact and add constraint
                    # for barevar of the duplicate atom
                    acd[adup][barevar] = Constraint(formula)
        # replace original atoms with newatoms
        self.initial[:] = newatoms
        # and rebuild their constraints
        self._restoreAtomConstraints(acd)
        # take care of lattice parameters
        self.initial.lattice.setLatPar(
                a=mno[0]*self.initial.lattice.a,
                b=mno[1]*self.initial.lattice.b,
                c=mno[2]*self.initial.lattice.c )
        # adjust lattice constraints if present
        latvars = ( "lat(1)", "lat(2)", "lat(3)" )
        for var, multiplier in zip(latvars, mno):
            if var in self.constraints and multiplier > 1:
                con = self.constraints[var]
                formula = "%.0f*(%s)" % (multiplier, con.formula)
                formula = re.sub(r'\((@\d+)\)', r'\1', formula)
                con.formula = formula
        return

    def isSpaceGroupPossible(self, spacegroup):
        """Check if space group is consistent with lattice parameters.

        spacegroup -- instance of SpaceGroup

        Return bool.
        """
        from Structure.SymmetryUtilities import isSpaceGroupLatPar
        return isSpaceGroupLatPar(spacegroup, *self.initial.lattice.abcABG())

    def expandAsymmetricUnit(self, spacegroup, indices, sgoffset=[0,0,0]):
        """Perform symmetry expansion for atoms at given indices.
        Temperature factors may be corrected to reflect the symmetry. 
        All constraints for expanded atoms are erased with the exception
        of the occupancy("occ".  Constraints of unaffected atoms are adjusted
        for new positions self.initial.

        spacegroup  -- instance of Structure.SpaceGroup
        indices     -- list of integer indices of atoms to be expanded
        sgoffset    -- optional offset of space group origin [0,0,0]
        """
        from Structure.SymmetryUtilities import ExpandAsymmetricUnit
        acd = self._popAtomConstraints()
        # get unique, reverse sorted indices
        ruindices = dict.fromkeys(indices).keys()
        ruindices.sort()
        ruindices.reverse()
        coreatoms = [self.initial[i] for i in ruindices]
        corepos = [a.xyz for a in coreatoms]
        coreUijs = [a.U for a in coreatoms]
        eau = ExpandAsymmetricUnit(spacegroup, corepos, coreUijs,
                sgoffset=sgoffset)
        # build a nested list of new atoms:
        newatoms = []
        for i in range(len(coreatoms)):
            ca = coreatoms[i]
            caocc_con = None
            if ca in acd and "occ" in acd[ca]:
                caocc_con = acd[ca]["occ"]
            eca = []    # expanded core atom
            for j in range(eau.multiplicity[i]):
                a = Atom(ca)
                a.xyz = eau.expandedpos[i][j]
                a.U = eau.expandedUijs[i][j]
                eca.append(a)
                if caocc_con is None:   continue
                # make a copy of occupancy constraint
                acd[a] = {"occ" : copy.copy(caocc_con)}
            newatoms.append(eca)
        # insert new atoms where they belong
        for i, atomlist in zip(ruindices, newatoms):
            self.initial[i:i+1] = atomlist
        self.initial.pdffit["spcgr"] = spacegroup.short_name
        self.initial.pdffit["sgoffset"] = list(sgoffset)
        # tidy constraints
        self._restoreAtomConstraints(acd)
        return

    def applySymmetryConstraints(self, spacegroup, indices, posflag, Uijflag,
            sgoffset=[0,0,0]):
        """Generate symmetry constraints for positions and thermal factors.
        Both positions and thermal factors may get corrected to reflect
        space group symmetry.  Old positional and thermal constraints get
        erased.  New parameter indices start at fist decade after the last
        used parameter.

        spacegroup  -- instance of Structure.SpaceGroup
        indices     -- list of integer indices of atoms to be expanded
        posflag     -- required bool flag for constraining positions
        Uijflag     -- required bool flag for Uij constrainment
        sgoffset    -- optional offset of space group origin [0,0,0]
        """
        if not posflag and not Uijflag:     return
        # need to do something
        from Structure.SymmetryUtilities import SymmetryConstraints
        # get unique sorted indices
        tobeconstrained = dict.fromkeys(indices)
        uindices = tobeconstrained.keys()
        uindices.sort()
        # remove old constraints
        pospat = re.compile(r'^([xyz])\((\d+)\)')
        Uijpat = re.compile(r'^(u11|u22|u33|u12|u13|u23)\((\d+)\)')
        for var in self.constraints.keys():
            mpos = posflag and pospat.match(var)
            mUij = Uijflag and Uijpat.match(var)
            if mpos and (int(mpos.group(2)) - 1) in tobeconstrained:
                del self.constraints[var]
            elif mUij and (int(mUij.group(2)) - 1) in tobeconstrained:
                del self.constraints[var]
        # find the largest used parameter index; pidxused must have an element
        pidxused = [i for i in self.owner.updateParameters()] + [0]
        # new parameters will start at the next decade
        firstpospar = firstUijpar = 10*(max(pidxused)/10) + 11
        # dictionary of parameter indices and their values
        newparvalues = {}
        selatoms = [self.initial[i] for i in uindices]
        selpos = [a.xyz for a in selatoms]
        selUijs = [a.U for a in selatoms]
        symcon = SymmetryConstraints(spacegroup, selpos, selUijs,
                sgoffset=sgoffset)
        # deal with positions
        if posflag:
            # fix positions:
            for a, xyz in zip(selatoms, symcon.positions):  a.xyz = xyz
            numpospars = len(symcon.pospars)
            posparindices = [i + firstpospar for i in range(numpospars)]
            posparvalues = symcon.posparValues()
            newparvalues.update( dict(zip(posparindices, posparvalues)) )
            possymbols = [ "@%i" % i for i in posparindices ]
            eqns = symcon.positionFormulasPruned(possymbols)
            for aidx, eq in zip(uindices, eqns):
                siteidx = aidx + 1
                sortedsmbls = eq.keys()
                sortedsmbls.sort()
                for barevar, formula in eq.items():
                    var = barevar + "(%i)" % siteidx
                    self.constraints[var] = Constraint(formula)
            # adjust firstUijpar
            if numpospars:
                firstUijpar += numpospars
                firstUijpar = 10*(firstUijpar/10) + 11
        # deal with temperature factors
        if Uijflag:
            # fix thermals
            for a, Uij in zip(selatoms, symcon.Uijs):  a.U = Uij
            numUpars = len(symcon.Upars)
            Uparindices = [i + firstUijpar for i in range(numUpars)]
            Uparvalues = symcon.UparValues()
            newparvalues.update( dict(zip(Uparindices, Uparvalues)) )
            Usymbols = [ "@%i" % i for i in Uparindices ]
            eqns = symcon.UFormulasPruned(Usymbols)
            for aidx, eq in zip(uindices, eqns):
                siteidx = aidx + 1
                sortedsmbls = eq.keys()
                sortedsmbls.sort()
                for barevar, formula in eq.items():
                    # keys in formula dictionary are uppercase
                    var = barevar.lower() + "(%i)" % siteidx
                    self.constraints[var] = Constraint(formula)
        # update parameter values in parent Fitting
        self.owner.updateParameters()
        for pidx, pvalue in newparvalues.iteritems():
            parobj = self.owner.parameters[pidx]
            parobj.setInitial(pvalue)
        # and finally remember this space group
        self.initial.pdffit["spcgr"] = spacegroup.short_name
        self.initial.pdffit["sgoffset"] = list(sgoffset)
        return

    def copy(self, other=None):
        """copy self to other. if other is None, create new instance

        other -- reference to other object

        returns reference to copied object
        """
        # check arguments
        if other is None:
            other = FitStructure(self.name)
        elif not isinstance(other, PDFStructure):
            raise ControlTypeError, \
                "other must be PDFStructure or FitStructure"
        # copy initial structure (self) to other
        PDFStructure.copy(self, other)
        # copy refined structure to other when it is FitStructure
        if isinstance(other, FitStructure):
            if self.refined is None:
                other.refined = None
            else:
                self.refined.copy(other.refined)
        # copy constraints
        other.constraints = copy.deepcopy(self.constraints)
        return other

    def load(self, z, subpath):
        """Load structure from a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        #subpath = projname/fitname/structure/myname/
        subs = subpath.split('/')
        rootDict = z.fileTree[subs[0]][subs[1]][subs[2]][subs[3]]
        self.initial.readStr(z.read(subpath+'initial'), 'pdffit')
        if rootDict.has_key('refined'):
            self.refined = PDFStructure(self.name)
            self.refined.readStr(z.read(subpath+'refined'), 'pdffit')
            
        import cPickle
        if rootDict.has_key('constraints'):
            self.constraints = cPickle.loads(z.read(subpath+'constraints'))
            translate = {'gamma' : 'delta1',  'delta' : 'delta2'}
            for old, new in translate.items():
                if old in self.constraints:
                    self.constraints[new] = self.constraints.pop(old)
            #for k,v in constraints.items():
            #    self.constraints[k] = Constraint(v)
        return
        
    def save(self, z, subpath):
        """Save structure to a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        import cPickle
        z.writestr(subpath+'initial', self.initial.writeStr('pdffit'))
        if self.refined:
            z.writestr(subpath+'refined', self.refined.writeStr('pdffit'))
        if self.constraints:
            # make a picklable dictionary of constraints
            #constraints = {}
            #for k,v in self.constraints.items():
            #    constraints[k] = v.formula
            bytes = cPickle.dumps(self.constraints, cPickle.HIGHEST_PROTOCOL)
            z.writestr(subpath+'constraints', bytes)
        return
        
    def getYNames(self):
        """get names of data item which can be plotted as y 

        returns a name str list
        """
        return self.constraints.keys()
    
    def getXNames(self):
        """get names of data item which can be plotted as x
        
        returns a name str list
        """
        # While FitDataSet has its own metadata, structure can only use
        # it's owner, namely fitting's metadata
        return self.owner.getMetaDataNames()
    
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
        data = self.owner.getMetaData(name)
        if data is not None:
            return data
        return self.owner._getData(self, name, step)        
        
# End of class FitStructure

# simple test code
if __name__ == "__main__":
    fitNi = FitStructure('name')
    from Structure import Atom
    fitNi.initial.lattice.setLatPar(3.52, 3.52, 3.52)
    fitNi.initial.append(Atom('Ni', [0.0, 0.0, 0.0]))
    fitNi.initial.append(Atom('Ni', [0.0, 0.5, 0.5]))
    fitNi.initial.append(Atom('Ni', [0.5, 0.0, 0.5]))
    fitNi.initial.append(Atom('Ni', [0.5, 0.5, 0.0]))
    for a in fitNi.initial:
        a.setUiso(0.00126651)
    fitNi.constraints['lat(1)'] = Constraint('@1')
    fitNi.constraints['y(2)'] = Constraint('@3 + 0.4')
    for i in range(2, 5):
        fitNi.constraints['u11(%i)' % i] = Constraint('@7 * 3.0')
    print fitNi.initial
    fitNi.expandSuperCell([2,2,2])
    print "expanded:"
    print fitNi.initial
    print "== constraint formulas =="
    for var, con in fitNi.constraints.iteritems():
        print "%s = %s" % (var, con.formula)
    print "== findParameters() =="
    for i, p in fitNi.findParameters().iteritems():
        print "%i: initialValue() = %r" % (i, p.initialValue())
    print "== initial after applyParameters({ 1 : 3.6, 7 : 0.008 }) =="
    pd = fitNi.findParameters()
    pd.update({1 : 3.6, 7 : 0.008})
    fitNi.applyParameters(pd)
    print "initial.lattice =", fitNi.initial.lattice
    print "all U[0,0] =", [a.U[0,0] for a in fitNi.initial]

# End of file
