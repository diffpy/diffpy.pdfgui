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

import copy
import re

from diffpy.structure import PDFFitStructure
from diffpy.pdfgui.control.pdfcomponent import PDFComponent
from diffpy.pdfgui.control.controlerrors import \
        ControlKeyError, ControlFileError


class PDFStructure(PDFComponent, PDFFitStructure):
    """PDFStructure contains structure information, which can be used for 3D
    rendering as well as structure refinement."""

    def __init__(self, name, *args, **kwargs):
        """Initialize PDFStructure.

        name         -- name of this PDFStructure.
        args, kwargs -- optional arguments passed to parent Structure class
        """
        PDFComponent.__init__(self, name)
        PDFFitStructure.__init__(self, *args, **kwargs)
        return


    def read(self, filename, format='auto'):
        """Load structure from a file, raise ControlFileError for invalid
        or unknown structure format.

        filename -- file to be loaded
        format   -- structure format such as 'pdffit', 'pdb', 'xyz'.  When
                    'auto' all available formats are tried in a row.

        Return instance of StructureParser used to load the data.
        See Structure.read() for more info.
        """
        from diffpy.structure import StructureFormatError
        try:
            p = PDFFitStructure.read(self, filename, format)
        except StructureFormatError as err:
            import os.path
            emsg = "Unable to read file '%s'\n%s." % (
                    os.path.basename(filename), err)
            raise ControlFileError(emsg)
        return p


    def copy(self, other=None):
        """copy self to other. if other is None, create an instance

        other -- ref to other object

        returns reference to copied object
        """
        if other is None:
            other = PDFStructure(self.name)
        for a in PDFFitStructure().__dict__:
            setattr(other, a, copy.deepcopy(getattr(self, a)))
        other[:] = copy.deepcopy(self[:])
        return other


    # dictionary of allowed keys from self.pdffit dictionary,
    # that can be used in setvar and getvar methods.
    _allowed_pdffit_vars = dict.fromkeys(('spdiameter', 'stepcut',
            'delta1', 'delta2', 'sratio', 'rcut'))


    def setvar(self, var, value):
        """assign to data member using PdfFit-style variable
        This can be used when applying constraint equations with particular
        parameter values.

        var   -- string representation of PdfFit variable.  Possible values:
                 pscale, spdiameter, stepcut, delta1, delta2, sratio, rcut,
                 lat(n), where n=1..6,  x(i), y(i), z(i), occ(i), u11(i),
                 u22(i), u33(i), u12(i), u13(i), u23(i), where i=1..Natoms
        value -- new value of the variable
        """
        barevar = var.strip()
        fvalue = float(value)
        parenthesis = re.match(r'^(\w+)\((\d+)\)$', barevar)
        # common error message
        emsg = "Invalid PdfFit phase variable %r" % barevar
        if barevar in ('pscale'):
            self.pdffit['scale'] = fvalue
        elif barevar in PDFStructure._allowed_pdffit_vars:
            self.pdffit[barevar] = fvalue
        elif barevar == 'lat(1)':
            self.lattice.setLatPar(a=fvalue)
        elif barevar == 'lat(2)':
            self.lattice.setLatPar(b=fvalue)
        elif barevar == 'lat(3)':
            self.lattice.setLatPar(c=fvalue)
        elif barevar == 'lat(4)':
            self.lattice.setLatPar(alpha=fvalue)
        elif barevar == 'lat(5)':
            self.lattice.setLatPar(beta=fvalue)
        elif barevar == 'lat(6)':
            self.lattice.setLatPar(gamma=fvalue)
        elif parenthesis:
            pvar = parenthesis.group(1)
            idx = int(parenthesis.group(2))
            atom = self[idx-1]
            if pvar == "x":
                atom.xyz[0] = fvalue
            elif pvar == "y":
                atom.xyz[1] = fvalue
            elif pvar == "z":
                atom.xyz[2] = fvalue
            elif pvar == "occ":
                atom.occupancy = fvalue
            elif pvar in ("u11", "u22", "u33", "u12", "u13", "u23"):
                i, j = int(pvar[1]) - 1,  int(pvar[2]) - 1
                atom.U[i,j], atom.U[j,i] = fvalue, fvalue
            else:
                raise ControlKeyError(emsg)
        else:
            raise ControlKeyError(emsg)
        return


    def getvar(self, var):
        """obtain value corresponding to PdfFit phase variable var
        This can be used when guessing Parameter values from constraints
        dictionary.

        var   -- string representation of PdfFit variable.  Possible values:
                 pscale, spdiameter, stepcut, delta1, delta2, sratio, rcut,
                 lat(n), where n = 1..6,  x(i), y(i), z(i), occ(i), u11(i),
                 u22(i), u33(i), u12(i), u13(i), u23(i), where i=1..Natoms

        returns value of var
        """
        barevar = var.strip()
        parenthesis = re.match(r'^(\w+)\((\d+)\)$', barevar)
        # common error message
        emsg = "Invalid PdfFit phase variable %r" % barevar
        if barevar in ('pscale'):
            value = self.pdffit['scale']
        elif barevar in PDFStructure._allowed_pdffit_vars:
            value = self.pdffit[barevar]
        elif barevar == 'lat(1)':
            value = self.lattice.a
        elif barevar == 'lat(2)':
            value = self.lattice.b
        elif barevar == 'lat(3)':
            value = self.lattice.c
        elif barevar == 'lat(4)':
            value = self.lattice.alpha
        elif barevar == 'lat(5)':
            value = self.lattice.beta
        elif barevar == 'lat(6)':
            value = self.lattice.gamma
        elif parenthesis:
            pvar = parenthesis.group(1)
            idx = int(parenthesis.group(2))
            atom = self[idx-1]
            if pvar == "x":
                value = atom.xyz[0]
            elif pvar == "y":
                value = atom.xyz[1]
            elif pvar == "z":
                value = atom.xyz[2]
            elif pvar == "occ":
                value = atom.occupancy
            elif pvar in ("u11", "u22", "u33", "u12", "u13", "u23"):
                i, j = int(pvar[1]) - 1,  int(pvar[2]) - 1
                value = atom.U[i,j]
            else:
                raise ControlKeyError(emsg)
        else:
            raise ControlKeyError(emsg)
        # all should be fine here, but value may be NumPy.float64scalar type
        value = float(value)
        return value

# End of class PDFStructure

# End of file
