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

"""class PDFDataSet for experimental PDF data.
"""

import os.path
import re
import copy
import time
from getpass import getuser

from diffpy.pdfgui.control.pdfcomponent import PDFComponent
from diffpy.pdfgui.control.controlerrors import \
        ControlKeyError, ControlFileError

class PDFDataSet(PDFComponent):
    """PDFDataSet is a class for experimental PDF data.

    Data members:
        robs       -- list of observed r points
        Gobs       -- list of observed G values
        drobs      -- list of standard deviations of robs
        dGobs      -- list of standard deviations of Gobs
        stype      -- scattering type, 'X' or 'N'
        qmax       -- maximum value of Q in inverse Angstroms.  Termination
                      ripples are neglected for qmax=0.
        qdamp      -- specifies width of Gaussian damping factor in pdf_obs due
                      to imperfect Q resolution
        qbroad     -- quadratic peak broadening factor related to dataset
        spdiameter -- particle diameter for shape damping function
                      Note: This attribute was moved to PDFStructure.
                      It is kept for backward compatibility when reading
                      PDFgui project files.
        dscale     -- scale factor of this dataset
        rmin       -- same as robs[0]
        rmax       -- same as robs[-1]
        filename   -- set to absolute path after reading from file
        metadata   -- dictionary for other experimental conditions, such as
                      temperature or doping

    Global member:
        persistentItems -- list of attributes saved in project file
        refinableVars   -- set (dict) of refinable variable names.
    """

    persistentItems = [ 'robs', 'Gobs', 'drobs', 'dGobs', 'stype', 'qmax',
                     'qdamp', 'qbroad', 'dscale', 'rmin', 'rmax', 'metadata' ]
    refinableVars = dict.fromkeys(('qdamp', 'qbroad', 'dscale'))

    def __init__(self, name):
        """Initialize.

        name -- name of the data set. It must be a unique identifier.
        """
        PDFComponent.__init__(self, name)
        self.clear()
        return

    def clear(self):
        """reset all data members to initial empty values"""
        self.robs = []
        self.Gobs = []
        self.drobs = []
        self.dGobs = []
        self.stype = 'X'
        # user must specify qmax to get termination ripples
        self.qmax = 0.0
        self.qdamp = 0.001
        self.qbroad = 0.0
        self.spdiameter = None
        self.dscale = 1.0
        self.rmin = None
        self.rmax = None
        self.filename = None
        self.metadata = {}
        return

    def setvar(self, var, value):
        """Assign data member using PdfFit-style variable.
        Used by applyParameters().

        var   -- string representation of dataset PdfFit variable.
                 Possible values: qdamp, qbroad, dscale
        value -- new value of the variable
        """
        barevar = var.strip()
        fvalue = float(value)
        if barevar in PDFDataSet.refinableVars:
            setattr(self, barevar, fvalue)
        else:
            emsg = "Invalid PdfFit dataset variable %r" % barevar
            raise ControlKeyError(emsg)
        return

    def getvar(self, var):
        """Obtain value corresponding to PdfFit dataset variable.
        Used by findParameters().

        var   -- string representation of dataset PdfFit variable.
                 Possible values: qdamp, qbroad, dscale

        returns value of var
        """
        barevar = var.strip()
        if barevar in PDFDataSet.refinableVars:
            value = getattr(self, barevar)
        else:
            emsg = "Invalid PdfFit dataset variable %r" % barevar
            raise ControlKeyError(emsg)
        return value

    def read(self, filename):
        """load data from PDFGetX2 or PDFGetN gr file

        filename -- file to read from

        returns self
        """
        try:
            with open(filename) as fp:
                self.readStr(fp.read())
        except PDFDataFormatError as err:
            basename = os.path.basename(filename)
            emsg = ("Could not open '%s' due to unsupported file format " +
                "or corrupted data. [%s]") % (basename, err)
            raise ControlFileError(emsg)
        self.filename = os.path.abspath(filename)
        return self


    def readStr(self, datastring):
        """read experimental PDF data from a string

        datastring -- string of raw data

        returns self
        """
        self.clear()
        # useful regex patterns:
        rx = { 'f' : r'[-+]?(\d+(\.\d*)?|\d*\.\d+)([eE][-+]?\d+)?' }
        # find where does the data start
        res = re.search(r'^#+ start data\s*(?:#.*\s+)*', datastring, re.M)
        # start_data is position where the first data line starts
        if res:
            start_data = res.end()
        else:
            # find line that starts with a floating point number
            regexp = r'^\s*%(f)s' % rx
            res = re.search(regexp, datastring, re.M)
            if res:
                start_data = res.start()
            else:
                start_data = 0
        header = datastring[:start_data]
        databody = datastring[start_data:].strip()

        # find where the metadata starts
        metadata = ''
        res = re.search(r'^#+\ +metadata\b\n', header, re.M)
        if res:
            metadata = header[res.end():]
            header = header[:res.start()]

        # parse header
        # stype
        if re.search('(x-?ray|PDFgetX)', header, re.I):
            self.stype = 'X'
        elif re.search('(neutron|PDFgetN)', header, re.I):
            self.stype = 'N'
        # qmax
        regexp = r"\bqmax *= *(%(f)s)\b" % rx
        res = re.search(regexp, header, re.I)
        if res:
            self.qmax = float(res.groups()[0])
        # qdamp
        regexp = r"\b(?:qdamp|qsig) *= *(%(f)s)\b" % rx
        res = re.search(regexp, header, re.I)
        if res:
            self.qdamp = float(res.groups()[0])
        # qbroad
        regexp = r"\b(?:qbroad|qalp) *= *(%(f)s)\b" % rx
        res = re.search(regexp, header, re.I)
        if res:
            self.qbroad = float(res.groups()[0])
        # spdiameter
        regexp = r"\bspdiameter *= *(%(f)s)\b" % rx
        res = re.search(regexp, header, re.I)
        if res:
            self.spdiameter = float(res.groups()[0])
        # dscale
        regexp = r"\bdscale *= *(%(f)s)\b" % rx
        res = re.search(regexp, header, re.I)
        if res:
            self.dscale = float(res.groups()[0])
        # temperature
        regexp = r"\b(?:temp|temperature|T)\ *=\ *(%(f)s)\b" % rx
        res = re.search(regexp, header)
        if res:
            self.metadata['temperature'] = float(res.groups()[0])
        # doping
        regexp = r"\b(?:x|doping)\ *=\ *(%(f)s)\b" % rx
        res = re.search(regexp, header)
        if res:
            self.metadata['doping'] = float(res.groups()[0])

        # parsing gerneral metadata
        if metadata:
            regexp = r"\b(\w+)\ *=\ *(%(f)s)\b" % rx
            while True:
                res = re.search(regexp, metadata, re.M)
                if res:
                    self.metadata[res.groups()[0]] = float(res.groups()[1])
                    metadata = metadata[res.end():]
                else:
                    break

        # read actual data - robs, Gobs, drobs, dGobs
        inf_or_nan = re.compile('(?i)^[+-]?(NaN|Inf)\\b')
        has_drobs = True
        has_dGobs = True
        # raise PDFDataFormatError if something goes wrong
        try:
            for line in databody.split("\n"):
                v = line.split()
                # there should be at least 2 value in the line
                self.robs.append(float(v[0]))
                self.Gobs.append(float(v[1]))
                # drobs is valid if all values are defined and positive
                has_drobs = (has_drobs and
                        len(v) > 2 and not inf_or_nan.match(v[2]))
                if has_drobs:
                    v2 = float(v[2])
                    has_drobs = v2 > 0.0
                    self.drobs.append(v2)
                # dGobs is valid if all values are defined and positive
                has_dGobs = (has_dGobs and
                        len(v) > 3 and not inf_or_nan.match(v[3]))
                if has_dGobs:
                    v3 = float(v[3])
                    has_dGobs = v3 > 0.0
                    self.dGobs.append(v3)
            if not has_drobs:
                self.drobs = len(self.robs) * [0.0]
            if not has_dGobs:
                self.dGobs = len(self.robs) * [0.0]
        except (ValueError, IndexError) as err:
            raise PDFDataFormatError(err)
        self.rmin = self.robs[0]
        self.rmax = self.robs[-1]
        if not has_drobs:   self.drobs = len(self.robs) * [0.0]
        if not has_dGobs:   self.dGobs = len(self.robs) * [0.0]
        return self


    def write(self, filename):
        """Write experimental PDF data to a file.

        filename -- name of file to write to

        No return value.
        """
        txt = self.writeStr()
        f = open(filename, 'w')
        f.write(txt)
        f.close()
        return

    def writeStr(self):
        """String representation of experimental PDF data.

        Return data string.
        """
        lines = []
        # write metadata
        lines.extend([
            'History written: ' + time.ctime(),
            'produced by ' + getuser(),
            '##### PDFgui' ])
        # stype
        if self.stype == 'X':
            lines.append('stype=X  x-ray scattering')
        elif self.stype == 'N':
            lines.append('stype=N  neutron scattering')
        # qmax
        if self.qmax == 0:
            qmax_line = 'qmax=0   correction not applied'
        else:
            qmax_line = 'qmax=%.2f' % self.qmax
        lines.append(qmax_line)
        # qdamp
        lines.append('qdamp=%g' % self.qdamp)
        # qbroad
        lines.append('qbroad=%g' % self.qbroad)
        # dscale
        lines.append('dscale=%g' % self.dscale)
        # metadata
        if len(self.metadata) > 0:
            lines.append('# metadata')
            for k, v in self.metadata.items():
                lines.append( "%s=%s" % (k,v) )
        # write data:
        lines.append('##### start data')
        lines.append('#L r(A) G(r) d_r d_Gr')
        for i in range(len(self.robs)):
            lines.append('%g %g %g %g' % \
                (self.robs[i], self.Gobs[i], self.drobs[i], self.dGobs[i]) )
        # that should be it
        datastring = "\n".join(lines) + "\n"
        return datastring

    def copy(self, other=None):
        """copy self to other. if other is None, create new instance

        other -- ref to other object
        returns reference to copied object
        """
        if other is None:
            other = PDFDataSet(self.name)
        elif isinstance(other, PDFDataSet):
            other.clear()
        # some attributes can be assigned, e.g., robs, Gobs, drobs, dGobs are
        # constant so they can be shared between copies.
        assign_attributes = ( 'robs', 'Gobs', 'drobs', 'dGobs', 'stype',
                'qmax', 'qdamp', 'qbroad', 'dscale',
                'rmin', 'rmax', 'filename' )
        # for others we will assign a copy
        copy_attributes = ( 'metadata', )
        for a in assign_attributes:
            setattr(other, a, getattr(self, a))
        for a in copy_attributes:
            setattr(other, a, copy.deepcopy(getattr(self, a)))
        return other

# End of class PDFDataSet


class PDFDataFormatError(Exception):
    """Exception class marking failure to proccess PDF data string.
    """
    pass

# End of file
