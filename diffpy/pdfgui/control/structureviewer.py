##############################################################################
#
# diffpy.pdfgui     by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2009 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas  
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Template module file.  Defines example class Foo and routine func.
These have unit tests in Testfoo file in the trunk/tests directory.
"""

# module version
__id__ = "$Id$"


import sys
import os.path
import tempfile
import shutil

from diffpy.pdfgui.control.controlerrors import ControlConfigError


def getStructureViewer():
    """Factory returning singleton instance of the StructureViewer class.
    """
    global _struviewer
    if _struviewer is None:
        _struviewer = StructureViewer()
    return _struviewer

_struviewer = None



class StructureViewer(object):
    """Class for plotting structure in general structure viewer.
    It takes care of creating temporary structure file in a desired
    format and launching structure viewer as a background process.
    The temporary files are removed when StructureViewer instance
    goes out of scope.

    Data attributes:

    executable -- full path to the structure viewer program or a program
                  that can be found in system PATH.
    argstr     -- argument string for the viewer program, it can use shell
                  quoting.  Instances of '%s' in the string are replaced with
                  temporary structure file.  By default '%s'
    fileformat -- structure format that can be loaded by the viewer.
                  Must be one of output formats supported by diffpy.Structure
                  package.  By default 'pdb'.
    _tmpdir    -- Temporary directory for structure files opened by the viewer.
                  tmpdir is None before the first call to plot.  The directory
                  and everything inside is removed when StructureViewer goes
                  out of the scope.
    _plotcount -- Number of plots created by this viewer.
    """


    def __init__(self, executable=None, argstr=None, fileformat=None):
        """Create Foo instance.

        value   -- initial value, must be a string or number convertible
                   to integer.  When not supplied, assign 42.
        """
        # declare instance data
        self.executable = 'atomeye'
        self.argstr = '%s'
        self.fileformat = 'pdb'
        self._tmpdir = None
        self._plotcount = 0
        # process arguments:
        if executable is not None:
            self.executable = executable
        if argstr is not None:
            self.argstr = argstr
        if fileformat is not None:
            self.fileformat = fileformat
        # finish every method with return
        return


    def getConfig(self):
        """Return current configuration of StructureViewer instance.

        Returns dictionary with the following keys:
        ('executable', 'argstr', 'fileformat')
        """
        cfgkeys = ('executable', 'argstr', 'fileformat')
        kv = [(k, getattr(self, k)) for k in cfgkeys]
        rv = dict(kv)
        return rv


    def setConfig(self, cfg):
        """Configure StructureViewer instance, by passing configuration
        dictionary or named arguments.

        cfg     -- New configuration dictionary, with the same keys as
                   returned by getConfig().  Any other keys are ignored.

        No return value.
        """
        # iterate over keys from getConfig dictionary
        for k in self.getConfig():
            if k in cfg:  setattr(self, k, cfg[k])
        return


    def getFileFormats():
        """Return list of valid values for the fileformat attribute.
        """
        from diffpy.Structure.Parsers import outputFormats
        return outputFormats()
    getFileFormats = staticmethod(getFileFormats)


    def plot(self, stru):
        """Launch new structure viewer and open a temporary copy of stru.

        stru    -- instance of Structure class from diffpy.Structure

        No return value.
        Raise ControlConfigError if structure viewer could not be launched.
        """
        import subprocess
        import shlex
        import re
        # make sure shlex.split is not called with None, because
        # it would read standard input
        s = self.argstr and self.argstr or ''
        args = shlex.split(s)
        strupath = self._writeTemporaryStructure(stru)
        # substitute strupath in args using % operator
        pat = re.compile(r'(?<!%)(%%)*%s')
        for i, a in enumerate(args):
            cnt = len(pat.findall(a))
            tpl = cnt * (strupath,)
            args[i] = a % tpl
        args.insert(0, self.executable)
        try:
            subprocess.Popen(args)
        except OSError, err:
            emsg = ('Error executing StructureViewer %s: %s' %
                    (self.executable, err))
            raise ControlConfigError(emsg)
        return


    def __del__(self):
        """Remove temporary files created by this instance StructureViewer.
        """
        # short circuit if nothing has been created
        if self._tmpdir is None:    return
        # Function for showing unremovable files
        def onerror(fnc, path, error):
            print >>sys.stderr, ('Cannot remove %s - %s' % (path, error))
            return
        # For safety remove _tmpdir subdirectories by their names
        for i in range(self._plotcount):
            di = os.path.join(self._tmpdir, '%04i' % i)
            shutil.rmtree(di, True, onerror)
        # finally remove _tmpdir, which should now be empty
        try:
            os.rmdir(self._tmpdir)
        except OSError, err:
            onerror(None, self._tmpdir, err)
            pass
        return


    def _writeTemporaryStructure(self, stru):
        """Create new temporary structure file in specified fileformat.

        stru -- instance of Structure class

        Return full path to the temporary file.
        """
        # get extension preferred by fileformat
        from diffpy.Structure.Parsers import parser_index
        ffext = parser_index[self.fileformat]['file_extension']
        d = self._createTemporaryDirectory()
        strutail = (getattr(stru, 'name', '') or getattr(stru, 'title', '') or
                ('structure' + os.path.basename(d)))
        struext = os.path.splitext(strutail)[-1]
        if struext.lower() != ffext.lower():
            strutail += ffext
        strupath = os.path.join(d, strutail)
        stru.write(strupath, format=self.fileformat)
        return strupath


    def _createTemporaryDirectory(self):
        """Create new numbered temporary directory below self._tmpdir.

        Create _tmpdir if it does not exist yet.

        Return full path to the new temporary directory.
        """
        if self._tmpdir is None:
            self._tmpdir = tempfile.mkdtemp()
        dname = "%04i" % self._plotcount
        dpath = os.path.join(self._tmpdir, dname)
        os.mkdir(dpath)
        self._plotcount += 1
        return dpath


# End of class StructureViewer

# End of file.
