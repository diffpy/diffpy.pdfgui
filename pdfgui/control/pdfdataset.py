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

"""class PDFDataSet for experimental PDF data.
"""

import os.path
import re
import copy
from pdfcomponent import PDFComponent
from controlerrors import ControlKeyError

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
        qsig       -- specifies width of Gaussian damping factor in pdf_obs due
                      to imperfect Q resolution
        qalp       -- quadratic peak broadening factor related to dataset
        spdiameter -- particle diameter for shape damping function
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
                     'qsig', 'qalp', 'spdiameter', 'dscale', 'rmin', 'rmax',
                     'metadata' ]
    refinableVars = dict.fromkeys(('qsig', 'qalp', 'dscale', 'spdiameter'))

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
        self.qsig = 0.001
        self.qalp = 0.0
        self.spdiameter = 0.0
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
                 Possible values: qsig, qalp, dscale, spdiameter
        value -- new value of the variable
        """
        barevar = var.strip()
        fvalue = float(value)
        if barevar in PDFDataSet.refinableVars:
            setattr(self, barevar, fvalue)
        else:
            raise ControlKeyError, \
                    "Invalid PdfFit dataset variable %r" % barevar
        return

    def getvar(self, var):
        """Obtain value corresponding to PdfFit dataset variable.
        Used by findParameters().

        var   -- string representation of dataset PdfFit variable.
                 Possible values: qsig, qalp, dscale, spdiameter

        returns value of var
        """
        barevar = var.strip()
        if barevar in PDFDataSet.refinableVars:
            value = getattr(self, barevar)
        else:
            raise ControlKeyError, \
                    "Invalid PdfFit dataset variable %r" % barevar
        return value

    def read(self, filename):
        """load data from PDFGetX2 or PDFGetN gr file

        filename -- file to read from

        returns self
        """
        self.readStr(open(filename,'rb').read())
        self.filename = os.path.abspath(filename)
        return self

    def readStr(self, datastring):
        """read experimental PDF data from a string

        datastring -- string of raw data

        returns self
        """
        self.clear()
        # find where does the data start
        res = re.search(r'^#+ start data\s*(?:#.*\s+)*', datastring, re.M)
        # start_data is position where the first data line starts
        if res:
            start_data = res.end()
        else:
            res = re.search(r'^[^#]', datastring, re.M)
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
        rx = { 'f' : r'[-+]?(\d+(\.\d*)?|\d*\.\d+)([eE][-+]?\d+)?' }
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
        # qsig
        regexp = r"\bqsig *= *(%(f)s)\b" % rx
        res = re.search(regexp, header, re.I)
        if res:
            self.qsig = float(res.groups()[0])
        # qalp
        regexp = r"\bqalp *= *(%(f)s)\b" % rx
        res = re.search(regexp, header, re.I)
        if res:
            self.qalp = float(res.groups()[0])
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
        for line in databody.split("\n"):
            v = line.split()
            # we want to raise exception if there is short data line
            # if len(v) < 2:
            #   continue
            self.robs.append(float(v[0]))
            self.Gobs.append(float(v[1]))
            self.drobs.append(len(v) > 2 and float(v[2]) or 0.0)
            self.dGobs.append(len(v) > 3 and float(v[3]) or 0.0)
        self.rmin = self.robs[0]
        self.rmax = self.robs[-1]
        return self

    def write(self, filename):
        """write experimental PDF data to a file

        filename -- name of file to write to
        """
        bytes = self.writeStr()
        f = open(filename, 'w')
        f.write(bytes)
        f.close()
        return

    def writeStr(self):
        """string representation of experimental PDF data

        returns data string
        """
        import time
        from getpass import getuser
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
        if self.qmax:
            lines.append('qmax=%.2f' % self.qmax)
        # qsig
        lines.append('qsig=%g' % self.qsig)
        # qalp
        lines.append('qalp=%g' % self.qalp)
        # spdiameter
        lines.append('spdiameter=%g' % self.spdiameter)
        # dscale
        lines.append('dscale=%g' % self.dscale)
        # metadata
        if len(self.metadata) > 0:
            lines.append('# metadata')
            for k, v in self.metadata.iteritems():
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
                'qmax', 'qsig', 'qalp', 'spdiameter', 'dscale',
                'rmin', 'rmax', 'filename' )
        # for others we will assign a copy
        copy_attributes = ( 'metadata', )
        for a in assign_attributes:
            setattr(other, a, getattr(self, a))
        import copy
        for a in copy_attributes:
            setattr(other, a, copy.deepcopy(getattr(self, a)))
        return other

# End of class PDFDataSet

# simple test code
if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    dataset = PDFDataSet("test")
    dataset.read(filename)
    print "== metadata =="
    for k, v in dataset.metadata.iteritems():
        print k, "=", v
    print "== data members =="
    for k, v in dataset.__dict__.iteritems():
        if k in ('metadata', 'robs', 'Gobs', 'drobs', 'dGobs') or k[0] == "_":
            continue
        print k, "=", v
    print "== robs Gobs drobs dGobs =="
    for i in range(len(dataset.robs)):
        print dataset.robs[i], dataset.Gobs[i], dataset.drobs[i], dataset.dGobs[i]
    print "== writeStr() =="
    print dataset.writeStr()
    print "== datasetcopy.writeStr() =="
    datasetcopy = dataset.copy()
    print datasetcopy.writeStr()

# version
__id__ = "$Id$"

# End of file
