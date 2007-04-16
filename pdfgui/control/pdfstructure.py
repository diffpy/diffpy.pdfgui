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

import copy
import re
from pdfcomponent import PDFComponent
from diffpy.Structure import PDFFitStructure
from controlerrors import ControlKeyError, ControlFileError

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

        Return self.
        """
        from diffpy.Structure import InvalidStructureFormat
        try:
            PDFFitStructure.read(self, filename, format)
        except InvalidStructureFormat:
            import os.path
            emsg = ("Could not open '%s' due to unsupported file format " +
                    "or corrupted data.") % os.path.basename(filename)
            raise ControlFileError, emsg
        return self

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

    def setvar(self, var, value):
        """assign to data member using PdfFit-style variable
        This can be used when applying constraint equations with particular
        parameter values.

        var   -- string representation of PdfFit variable.  Possible values:
                 pscale, delta1, delta2, srat, rcut, lat(n), where n = 1..6,
                 x(i), y(i), z(i), occ(i), u11(i), u22(i), u33(i),
                 u12(i), u13(i), u23(i), where i = 1..Natoms
        value -- new value of the variable
        """
        translate = {'gamma' : 'delta1',  'delta' : 'delta2'}
        barevar = var.strip()
        barevar = translate.get(barevar, barevar)
        fvalue = float(value)
        parenthesis = re.match(r'^(\w+)\((\d+)\)$', barevar)
        if barevar in ('pscale', 'pfrac'):
            self.pdffit['scale'] = fvalue
        elif barevar in ('delta1', 'delta2', 'srat', 'rcut'):
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
                raise ControlKeyError, \
                        "Invalid PdfFit phase variable %r" % barevar
        else:
            raise ControlKeyError, \
                    "Invalid PdfFit phase variable %r" % barevar
        return

    def getvar(self, var):
        """obtain value corresponding to PdfFit phase variable var
        This can be used when guessing Parameter values from constraints
        dictionary.

        var   -- string representation of PdfFit variable.  Possible values:
                 pscale, delta1, delta2, srat, rcut, lat(n), where n = 1..6,
                 x(i), y(i), z(i), occ(i), u11(i), u22(i), u33(i),
                 u12(i), u13(i), u23(i), where i = 1..Natoms

        returns value of var
        """
        translate = {'gamma' : 'delta1',  'delta' : 'delta2'}
        barevar = var.strip()
        barevar = translate.get(barevar, barevar)
        parenthesis = re.match(r'^(\w+)\((\d+)\)$', barevar)
        if barevar in ('pscale', 'pfrac'):
            value = self.pdffit['scale']
        elif barevar in ('delta1', 'delta2', 'srat', 'rcut'):
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
            raise ControlKeyError, "Invalid PdfFit phase variable %r" % barevar
        # all should be fine here, but value may be NumPy.float64scalar type
        value = float(value)
        return value

# End of class PDFStructure

if __name__ == "__main__":
    stru = PDFStructure('name')
    stru.lattice.setLatPar(3.0, 4.0, 5.0)
    from diffpy.Structure import Atom
    stru.append( Atom('Ni', [0, 0, 0.2]) )
    for i in range(1,7):
        print "lat(%i) =" % i, stru.getvar('lat(%i)' % i)
    stru.setvar('z(1)', 0.1)
    print "x(1) =", stru.getvar('x(1)')
    print "y(1) =", stru.getvar('y(1)')
    print "z(1) =", stru.getvar('z(1)')
    print "u23(1) =", stru.getvar('u23(1)')

# version
__id__ = "$Id$"

# End of file
