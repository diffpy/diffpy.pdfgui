#!/usr/bin/env python

# This script is usually called from top level diffpy installation.

"""PDFgui - graphical user interface for real space structure refinement.

Packages:   diffpy.pdfgui
Scripts:    pdfgui, pdfserver
"""

# version
__id__ = "$Id$"

from distutils.core import setup
import sys
import os.path
import glob

thisfile = os.path.abspath(locals().get('__file__', 'setup.py'))
setup_dir = os.path.dirname(thisfile)

sys.path.insert(0, setup_dir)
import pdfgui.version
sys.path.pop(0)
package_version = pdfgui.version.__version__

# icons directory should be inside pdfgui/gui.  To do that, we need
# data_files fix from http://wiki.python.org/moin/DistutilsInstallDataScattered
from distutils.command.install_data import install_data
class smart_install_data(install_data):
    def run(self):
        # need to change default self.install_dir to the library dir
        # do this only when install_lib command is defined
        if 'install_lib' in self.distribution.command_obj:
            install_lib = self.get_finalized_command('install_lib')
            self.install_dir = install_lib.install_dir
        return install_data.run(self)
# End of smart_install_data

# build list of icon files
iconfiles = glob.glob( os.path.join(setup_dir, 'pdfgui/gui/icons/*.png') )

# define distribution
setup_args = {
    "name" : "PDFgui",
    "description" : "GUI for PDF simulation and structure refinement.",
    "version" : package_version,
    "packages" : [
        "diffpy.pdfgui",
        "diffpy.pdfgui.control",
        "diffpy.pdfgui.gui",
        "diffpy.pdfgui.gui.wxExtensions",
        ],
    "package_dir" : {"diffpy.pdfgui" : os.path.join(setup_dir, "pdfgui")},
    "data_files" : [('diffpy/pdfgui/gui/icons', iconfiles)],
    "scripts" : [
        os.path.join(setup_dir, "applications/pdfgui"),
        os.path.join(setup_dir, "applications/pdfserver"),
        ],
    "cmdclass" : { 'install_data' : smart_install_data },
}

diffpy__init__code = """
""".lstrip()

def check_diffpy__init__(distribution):
    """check if diffpy/__init__.py exists and create one if not
    """
    from distutils import log
    if distribution.dry_run:    return
    if 'install_lib' not in distribution.command_obj:   return
    lib_install_dir = distribution.get_command_obj('install_lib').install_dir
    initfile = os.path.join(lib_install_dir, 'diffpy', '__init__.py')
    if os.path.isfile(initfile):    return
    # we need to create and compile the file
    log.info("creating " + initfile)
    out = open(initfile, 'w')
    out.write(diffpy__init__code)
    out.close()
    import compiler
    log.info("byte-compiling %s to %s" % \
            (initfile, os.path.basename(initfile)) )
    compiler.compileFile(initfile)
    return

if __name__ == "__main__":
    distribution = setup(**setup_args)
    check_diffpy__init__(distribution)

# End of file 
