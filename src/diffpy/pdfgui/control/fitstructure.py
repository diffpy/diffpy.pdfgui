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

"""class FitStructure for storage of one phase and related fitting parameters
"""

import copy
import re
import numpy

from diffpy.pdfgui.control.pdfstructure import PDFStructure
from diffpy.pdfgui.control.constraint import Constraint
from diffpy.pdfgui.control.parameter import Parameter
from diffpy.pdfgui.control.controlerrors import ControlTypeError, ControlValueError
from diffpy.structure import Atom

class FitStructure(PDFStructure):
    """FitStructure holds initial and refined structure and related fit
    parameters.  Inherited from PDFStructure.

    Class data members:
        symposeps   -- tolerance for recognizing site as symmetry position

    Data members (in adition to those in PDFStructure):
        owner       -- instance of parent Fitting (set in Organizer.add())
        initial     -- initial structure, same as self
        refined     -- refined structure when available or None
        constraints -- dictionary of { refvar_string : Constraint_instance }
        selected_pairs -- string of selected pairs, by default "all-all".
                       Use setSelectedPairs() and getSelectedPairs() methods
                       to access its value.
        custom_spacegroup -- instance of SpaceGroup which has no equivalent
                       in diffpy.structure.spacegroups module.  This can happen
                       after reading from a CIF file.  When equivalent space
                       group exists, custom_spacegroup is None.

    Refinable variables:  pscale, spdiameter, delta1, delta2, sratio, lat(n),
        where n=1..6,  x(i), y(i), z(i), occ(i), u11(i), u22(i), u33(i),
        u12(i), u13(i), u23(i), where i=1..Natoms

    Non-refinable variable:  rcut, stepcut
    """

    # class data members:
    symposeps = 0.001
    # evaluation of sorted_standard_space_groups deferred when necessary
    sorted_standard_space_groups = []

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
        self.selected_pairs = "all-all"
        self.initial.pdffit['sgoffset'] = [0.0, 0.0, 0.0]
        self.custom_spacegroup = None
        return


    def _update_custom_spacegroup(self, parser):
        """Helper method for read() and readStr(), which takes care
        of setting custom_spacegroup after successful reading.

        parser -- instance of StructureParser used in reading.

        No return value.
        """
        self.custom_spacegroup = None
        self.initial.pdffit['sgoffset'] = [0.0, 0.0, 0.0]
        if hasattr(parser, "spacegroup"):
            sg = parser.spacegroup
            # when sg.number is None or 0, we have a custom spacegroup
            if not sg.number:
                # overwrite sg.number with 0, an identifier for custom SG
                sg.number = 0
                self.custom_spacegroup = sg
            # here sg.number is 0 or positive integer
            self.initial.pdffit['spcgr'] = sg.short_name
        return


    def read(self, filename, format='auto'):
        """Load structure from a file, raise ControlFileError for invalid
        or unknown structure format.  Overloads PDFStructure.read()
        to handle custom_spacegroup attribute.

        filename -- file to be loaded
        format   -- structure format such as 'pdffit', 'pdb', 'xyz'.  When
                    'auto' all available formats are tried in a row.

        Return instance of StructureParser used to load the data.
        See Structure.read() for more info.
        """
        p = PDFStructure.read(self, filename, format)
        # update data only after successful reading
        self._update_custom_spacegroup(p)
        # FIXME Temporary workaround to prevent forced isotropy of the Uij
        # values.  To be removed and handled by atom isotropy column.
        self.anisotropy = True
        return p


    def readStr(self, s, format='auto'):
        """Same as PDFStructure.readStr, but handle the
        custom_spacegroup data.

        Return instance of StructureParser used to load the data.
        See Structure.readStr() for more info.
        """
        p = PDFStructure.readStr(self, s, format)
        # update data only after successful reading
        self._update_custom_spacegroup(p)
        # FIXME Temporary workaround to prevent forced isotropy of the Uij
        # values.  To be removed and handled by atom isotropy column.
        self.anisotropy = True
        return p


    def __getattr__(self, name):
        """Map self.initial to self.
        This is called only when normal attribute lookup fails.
        """
        if name == "initial":
            value = self
        else:
            emsg = "A instance has no attribute '%s'" % name
            raise AttributeError(emsg)
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
        for var, con in self.constraints.items():
            con.guess(self.initial.getvar(var))
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
        """Evaluate constraint formulas and adjust initial PDFStructure.

        parameters -- dictionary of parameter indices with Parameter
                      instance values.  Values may also be float type.
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
        for var in list(self.constraints.keys()):
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
        for i, a in enumerate(self.initial):
            if not a in acd: continue
            # there are some constraints for atom a
            siteindex = i + 1
            cnts = acd[a]
            for barevar, con in cnts.items():
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
        # FIXME Temporary workaround to prevent forced isotropy of the Uij
        # values.  To be removed and handled by atom isotropy column.
        for a in atomlist:
            a.anisotropy = True
        # workaround ends here.
        self.initial[index:index] = atomlist
        self._restoreAtomConstraints(acd)
        return

    def deleteAtoms(self, indices):
        """Removed atoms at given indices and adjust self.constraints.

        indices -- list of integer indices of atoms to be deleted
        """
        acd = self._popAtomConstraints()
        # get unique, reverse sorted indices
        ruindices = sorted(set(indices), reverse=True)
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
            raise ControlValueError("mno must contain 3 positive integers")
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
                for barevar, con in acd[a].items():
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
        for ai, an in zip(self.initial, newatoms):
            if an in acd:
                acd[ai] = acd[an]
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
        from diffpy.structure.symmetryutilities import isSpaceGroupLatPar
        return isSpaceGroupLatPar(spacegroup, *self.initial.lattice.abcABG())


    def getSpaceGroupList(self):
        """Return a list of SpaceGroup instances sorted by International
        Tables number.  When custom_spacegroup is defined, the list starts
        with custom_spacegroup.
        """
        if not FitStructure.sorted_standard_space_groups:
            import diffpy.structure.spacegroups as SG
            existing_names = {}
            unique_named_list = []
            for sg in SG.SpaceGroupList:
                if sg.short_name not in existing_names:
                    unique_named_list.append(sg)
                existing_names[sg.short_name] = True
            # sort by International Tables number, stay compatible with 2.3
            n_sg = [(sg.number % 1000, sg) for sg in unique_named_list]
            n_sg.sort()
            FitStructure.sorted_standard_space_groups = [sg for n, sg in n_sg]
        sglist = list(FitStructure.sorted_standard_space_groups)
        if self.custom_spacegroup:
            sglist.insert(0, self.custom_spacegroup)
        return sglist

    def getSpaceGroup(self, sgname):
        """Find space group in getSpaceGroupList() by short_name or number.
        sgname can be non-standard in case of CIF file defined space group.

        Return instance of SpaceGroup.
        Raise ValueError if sgname cannot be found or when it is not present
        in getSpaceGroupList().
        """
        import diffpy.structure.spacegroups as SG
        # this should match the "CIF data" sgname
        sgmatch = [sg for sg in self.getSpaceGroupList()
                if sg.short_name == sgname]
        # use standard lookup function when not matched by short_name
        if not sgmatch:
            sgmatch.append(SG.GetSpaceGroup(sgname))
        if not sgmatch:
            emsg = "Unknown space group %r" % sgname
            raise ValueError(emsg)
        sgfound = sgmatch[0]
        return sgfound

    def expandAsymmetricUnit(self, spacegroup, indices, sgoffset=[0,0,0]):
        """Perform symmetry expansion for atoms at given indices.
        Temperature factors may be corrected to reflect the symmetry.
        All constraints for expanded atoms are erased with the exception
        of the occupancy("occ".  Constraints of unaffected atoms are adjusted
        for new positions self.initial.

        spacegroup  -- instance of SpaceGroup from diffpy.structure
        indices     -- list of integer indices of atoms to be expanded
        sgoffset    -- optional offset of space group origin [0,0,0]
        """
        from diffpy.structure.symmetryutilities import ExpandAsymmetricUnit
        acd = self._popAtomConstraints()
        # get unique, reverse sorted indices
        ruindices = sorted(set(indices), reverse=True)
        coreatoms = [self.initial[i] for i in ruindices]
        corepos = [a.xyz for a in coreatoms]
        coreUijs = [a.U for a in coreatoms]
        eau = ExpandAsymmetricUnit(spacegroup, corepos, coreUijs,
                sgoffset=sgoffset, eps=self.symposeps)
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
        # remember this spacegroup as the last one used
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

        spacegroup  -- instance of SpaceGroup from diffpy.structure
        indices     -- list of integer indices of atoms to be expanded
        posflag     -- required bool flag for constraining positions
        Uijflag     -- required bool flag for Uij constrainment
        sgoffset    -- optional offset of space group origin [0,0,0]
        """
        if not posflag and not Uijflag:     return
        # need to do something
        from diffpy.structure.symmetryutilities import SymmetryConstraints
        # get unique sorted indices
        tobeconstrained = dict.fromkeys(indices)
        uindices = sorted(tobeconstrained.keys())
        # remove old constraints
        pospat = re.compile(r'^([xyz])\((\d+)\)')
        Uijpat = re.compile(r'^(u11|u22|u33|u12|u13|u23)\((\d+)\)')
        for var in list(self.constraints.keys()):
            mpos = posflag and pospat.match(var)
            mUij = Uijflag and Uijpat.match(var)
            if mpos and (int(mpos.group(2)) - 1) in tobeconstrained:
                del self.constraints[var]
            elif mUij and (int(mUij.group(2)) - 1) in tobeconstrained:
                del self.constraints[var]
        # find the largest used parameter index; pidxused must have an element
        pidxused = [i for i in self.owner.updateParameters()] + [0]
        # new parameters will start at the next decade
        parzeroidx = 10*(max(pidxused)/10) + 10
        # dictionary of parameter indices and their values
        newparvalues = {}
        selatoms = [self.initial[i] for i in uindices]
        selpos = [a.xyz for a in selatoms]
        selUijs = [a.U for a in selatoms]
        symcon = SymmetryConstraints(spacegroup, selpos, selUijs,
                sgoffset=sgoffset, eps=self.symposeps)
        # deal with positions
        if posflag:
            # fix positions:
            for a, xyz in zip(selatoms, symcon.positions):  a.xyz = xyz
            possymbols, parvalues = _makeParNames(symcon.pospars, parzeroidx)
            newparvalues.update(parvalues)
            eqns = symcon.positionFormulasPruned(possymbols)
            for aidx, eq in zip(uindices, eqns):
                siteidx = aidx + 1
                for barevar, formula in eq.items():
                    var = barevar + "(%i)" % siteidx
                    self.constraints[var] = Constraint(formula)
        # deal with temperature factors
        if Uijflag:
            # fix thermals
            for a, Uij in zip(selatoms, symcon.Uijs):  a.U = Uij
            Usymbols, parvalues = _makeParNames(symcon.Upars, parzeroidx)
            newparvalues.update(parvalues)
            eqns = symcon.UFormulasPruned(Usymbols)
            for aidx, eq in zip(uindices, eqns):
                siteidx = aidx + 1
                for barevar, formula in eq.items():
                    # keys in formula dictionary are uppercase
                    var = barevar.lower() + "(%i)" % siteidx
                    self.constraints[var] = Constraint(formula)
        # update parameter values in parent Fitting
        self.owner.updateParameters()
        for pidx, pvalue in newparvalues.items():
            parobj = self.owner.parameters[pidx]
            parobj.setInitial(pvalue)
        # and finally remember this space group
        self.initial.pdffit["spcgr"] = spacegroup.short_name
        self.initial.pdffit["sgoffset"] = list(sgoffset)
        return

    def setSelectedPairs(self, s):
        """Set the value of selected_pairs to s, raise ControlValueError when
        s has invalid syntax.  The selected_pairs is a comma separated list of
        words formatted as

            [!]{element|indexOrRange|all}-[!]{element|indexOrRange|all}

        where '!' excludes the given atoms from first or second pair.

        Examples:

            all-all              all possible pairs
            Na-Na                only Na-Na pairs
            all-all, !Na-        all pairs except Na-Na (first index skips Na)
            all-all, -!Na        same as previous (second index skips Na)
            Na-1:4               pairs of Na and first 4 atoms
            all-all, !Cl-!Cl     exclude any pairs containing Cl
            all-all, !Cl-, -!Cl  same as previous
            1-all                only pairs including the first atom

        Use getPairSelectionFlags() method to get a list of included values
        for first and second pair index.
        """
        # check syntax of s
        psf = self.getPairSelectionFlags(s)
        self.selected_pairs = psf['fixed_pair_string']
        return

    def getSelectedPairs(self):
        return self.selected_pairs

    def getPairSelectionFlags(self, s=None):
        """Translate string s to a list of allowed values for first and second
        pair index.  Raise ControlValueError for invalid syntax of s.  See
        setSelectedPairs() docstring for a definition of pair selection syntax.

        s -- string describing selected pairs (default: self.selected_pairs)

        Return a dictionary with following keys:

        firstflags  -- list of selection flags for first indices
        secondflags -- list of selection flags for second indices
        fixed_pair_string -- argument corrected to standard syntax
        """
        if s is None:   s = self.selected_pairs
        Natoms = len(self.initial)
        # sets of first and second indices
        firstflags = Natoms * [False]
        secondflags = Natoms * [False]
        # words of fixed_pair_string
        words_fixed = []
        s1 = s.strip(' \t,')
        words = re.split(r' *, *', s1)
        for w in words:
            wparts = w.split('-')
            if len(wparts) != 2:
                emsg = "Selection word '%s' must contain one dash '-'." % w
                raise ControlValueError(emsg)
            sel0 = self._parseAtomSelectionString(wparts[0])
            sel1 = self._parseAtomSelectionString(wparts[1])
            wfixed = sel0['fixedstring'] + '-' + sel1['fixedstring']
            words_fixed.append(wfixed)
            for idx, flg in sel0['flags'].items():
                firstflags[idx] = flg
            for idx, flg in sel1['flags'].items():
                secondflags[idx] = flg
        # build returned dictionary
        rv = { 'firstflags' : firstflags,
               'secondflags' : secondflags,
               'fixed_pair_string' : ", ".join(words_fixed),
        }
        return rv

    def applyPairSelection(self, server, phaseidx):
        """Apply pair selection for calculations of partial PDF.

        server   -- instance of PdfFit engine
        phaseidx -- phase index in PdfFit engine starting from 1
        """
        psf = self.getPairSelectionFlags()
        idx = 0
        for iflag, jflag in zip(psf['firstflags'], psf['secondflags']):
            idx += 1
            server.selectAtomIndex(phaseidx, 'i', idx, iflag)
            server.selectAtomIndex(phaseidx, 'j', idx, jflag)
        return


    def getSelectedIndices(self, s):
        '''Indices of the atoms that match the specified selection string.

        s    -- selection string consisting of one or more atom selection
                words formatted as [!]{element|indexOrRange|all}
                Example: "1:4, 7, Cl".

        Return a list of integers.
        Raise ControlValueError for invalid selection string format.
        '''
        s1 = ''.join(c for c in s if not c.isspace())
        words = s1.split(',')
        indices = set()
        for w in words:
            asd = self._parseAtomSelectionString(w)
            for idx, flg in asd['flags'].items():
                if flg:
                    indices.add(idx)
                else:
                    indices.discard(idx)
        rv = sorted(indices)
        return rv


    # Regular expression object for matching atom selection strings.
    # Will be assign with the first call to _parseAtomSelectionString.
    _rxatomselection = None

    def _parseAtomSelectionString(self, s):
        '''Process string that describes a set of atoms in the structure.

        s    -- selection string formatted as [!]{element|indexOrRange|all}
                "!" negates the selection, indexOrRange can be 1, 1:4,
                where atom indices starts from 1, and "all" matches all atoms.

        Return a dictionary with following keys:
        'fixedstring'    -- selection string adjusted to standard formatting
        'flags'          -- dictionary of atom indices and boolean flags for
                            normal or negated selection.
        Raise ControlValueError for invalid string format.
        '''
        # delayed initialization of the class variable
        if self._rxatomselection is None:
            FitStructure._rxatomselection = re.compile(r'''
            (?P<negate>!?)                      # exclamation point
            (?:(?P<element>[a-zA-Z]+)$|         # element|all   or
               (?P<start>\d+)(?P<stop>:\d+)?$   # number range
            )''', re.VERBOSE)
        assert self._rxatomselection
        Natoms = len(self.initial)
        flags  = {}
        rv = {'fixedstring' : '',  'flags' : flags}
        # allow empty string and return an empty flags dictionary
        s1 = s.replace(' ', '')
        if not s1:  return rv
        mx = self._rxatomselection.match(s1)
        if not mx:
            emsg = "Invalid selection syntax in '%s'" % s
            raise ControlValueError(emsg)
        if mx.group('negate'):
            rv['fixedstring'] = '!'
        flg = not mx.group('negate')
        # process atom type
        if mx.group('element'):
            elfixed = mx.group('element')
            elfixed = elfixed[0:1].upper() + elfixed[1:].lower()
            if elfixed == 'All':
                flags.update(dict.fromkeys(range(Natoms), flg))
                rv['fixedstring'] += elfixed.lower()
            else:
                for idx in range(Natoms):
                    if self.initial[idx].element == elfixed:
                        flags[idx] = flg
                rv['fixedstring'] += elfixed
        # process range
        else:
            lo = max(int(mx.group('start')) - 1, 0)
            rv['fixedstring'] += mx.group('start')
            hi = lo + 1
            if mx.group('stop'):
                hi = int(mx.group('stop')[1:])
                rv['fixedstring'] += mx.group('stop')
            hi = min(hi, Natoms)
            flags.update(dict.fromkeys(range(lo, hi), flg))
        return rv


    def copy(self, other=None):
        """copy self to other. if other is None, create new instance

        other -- reference to other object

        returns reference to copied object
        """
        # check arguments
        if other is None:
            other = FitStructure(self.name)
        elif not isinstance(other, PDFStructure):
            emsg = "other must be PDFStructure or FitStructure"
            raise ControlTypeError(emsg)
        # copy initial structure (self) to other
        PDFStructure.copy(self, other)
        # copy refined structure to other when it is FitStructure
        if isinstance(other, FitStructure):
            if self.refined is None:
                other.refined = None
            else:
                other.refined = self.refined.copy(other.refined)
        # copy constraints
        other.constraints = copy.deepcopy(self.constraints)
        other.selected_pairs = self.selected_pairs
        return other

    def load(self, z, subpath):
        """Load structure from a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        #subpath = projname/fitname/structure/myname/
        from diffpy.pdfgui.utils import asunicode
        from diffpy.pdfgui.control.pdfguicontrol import CtrlUnpickler
        subs = subpath.split('/')
        rootDict = z.fileTree[subs[0]][subs[1]][subs[2]][subs[3]]
        strudata = asunicode(z.read(subpath + 'initial'))
        self.initial.readStr(strudata, 'pdffit')
        # refined
        if 'refined' in rootDict:
            self.refined = PDFStructure(self.name)
            refdata = asunicode(z.read(subpath + 'refined'))
            self.refined.readStr(refdata, 'pdffit')
        # constraints
        if 'constraints' in rootDict:
            self.constraints = CtrlUnpickler.loads(z.read(subpath+'constraints'))
            translate = { 'gamma' : 'delta1',
                          'delta' : 'delta2',
                          'srat'  : 'sratio' }
            for old, new in translate.items():
                if old in self.constraints:
                    self.constraints[new] = self.constraints.pop(old)
        # selected_pairs
        if "selected_pairs" in rootDict:
            self.selected_pairs = asunicode(z.read(subpath+'selected_pairs'))
        # sgoffset
        if "sgoffset" in rootDict:
            sgoffsetstr = asunicode(z.read(subpath+'sgoffset'))
            sgoffset = [float(w) for w in sgoffsetstr.split()]
            self.initial.pdffit['sgoffset'] = sgoffset
        # custom_spacegroup
        if "custom_spacegroup" in rootDict:
            spkl = z.read(subpath+'custom_spacegroup')
            self.custom_spacegroup = CtrlUnpickler.loads(spkl)
        return

    def save(self, z, subpath):
        """Save structure to a zipped project file.

        z       -- zipped project file
        subpath -- path to its own storage within project file
        """
        from diffpy.pdfgui.utils import safeCPickleDumps
        z.writestr(subpath+'initial', self.initial.writeStr('pdffit'))
        if self.refined:
            z.writestr(subpath+'refined', self.refined.writeStr('pdffit'))
        if self.constraints:
            spkl = safeCPickleDumps(self.constraints)
            z.writestr(subpath+'constraints', spkl)
        z.writestr(subpath+'selected_pairs', self.selected_pairs)
        # sgoffset
        sgoffset = self.initial.pdffit.get('sgoffset', [0.0, 0.0, 0.0])
        sgoffsetstr = "%g %g %g" % tuple(sgoffset)
        z.writestr(subpath+'sgoffset', sgoffsetstr)
        if self.custom_spacegroup:
            spkl = safeCPickleDumps(self.custom_spacegroup)
            z.writestr(subpath+'custom_spacegroup', spkl)
        return

    def getYNames(self):
        """get names of data item which can be plotted as y

        returns a name str list
        """
        return list(self.constraints.keys())

    def getXNames(self):
        """get names of data item which can be plotted as x

        returns a name str list
        """
        # in fact nothing
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
        data = self.owner.getMetaData(name)
        if data is not None:
            return data
        return self.owner._getData(self, name, step)

# End of class FitStructure

# Local helper functions -----------------------------------------------------

def _makeParNames(sympars, parzeroindex):
    '''Return a tuple of (symbols, parvalues), where symbols is a list of
    unique PDFFit parameter strings in "@%i" format and parvalues is a
    dictionary of parameter indices and their values.
    The symbols have indices 10n + (1, 2, 3) when referring to x, y, z, or
    10n + (4, 5, 6, 7, 8, 9) when referring to Uij.

    sympars      -- pospars or Upars attribute of a SymmetryConstraints object
                    Must be a sequence of symbols and values.
    parzeroindex -- the offset of all parameter indices.
                    Must be a multiple of 10.

    Return a tuple of (possymbols, Usymbols, parvalues).
    This function is only used in FitStructure.applySymmetryConstraints method.
    '''
    if parzeroindex % 10:
        raise ValueError('parzeroindex must be a multiple of 10.')
    smbindex = {'x' : 1,  'y' : 2,  'z' : 3,
                'U11' : 4,  'U22' : 5,  'U33' : 6,
                'U12' : 7,  'U13' : 8,  'U23' : 9}
    symbols = []
    parvalues = {}
    for smb, value in sympars:
        if smb[:1] == 'U':
            nsite = 10 * int(smb[3:])
            nvar = smbindex[smb[:3]]
        else:
            nsite = 10 * int(smb[1:])
            nvar = smbindex[smb[:1]]
        pidx = parzeroindex + nsite + nvar
        symbols.append('@%i' % pidx)
        parvalues[pidx] = value
    assert len(symbols) == len(parvalues)
    rv = (symbols, parvalues)
    return rv


# End of file
