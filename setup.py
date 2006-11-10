#!/usr/bin/env python

# This script is usually called from top level diffpy installation.

"""PDFgui - graphical user interface for real space structure refinement.

Packages:   diffpy.pdfgui
Scripts:    pdfgui, pdfserver
"""

# version
__id__ = "$Id: setup.py 730 2006-10-28 20:30:18Z juhas $"

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
        install_cmd = self.get_finalized_command('install')
        if self.install_dir == install_cmd.prefix:
            self.install_dir = install_cmd.install_lib
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
import sys
import os.path
mydir = os.path.dirname(__file__)
if mydir not in sys.path:   sys.path.insert(0, mydir)
""".lstrip()

def check_diffpy__init__(distribution):
    """check if diffpy has __init__.py and create one if not
    """
    from distutils import log
    install_lib = None
    if 'install' in distribution.commands:
        opts = distribution.get_option_dict('install')
        install_lib = opts.get('install_lib', 2*[None])[1]
    if 'install_lib' in distribution.commands and not install_lib:
        opts = distribution.get_option_dict('install_lib')
        install_lib = opts.get('install_dir', 2*[None])[1]
    if not install_lib:             return
    initfile = os.path.join(install_lib, 'diffpy', '__init__.py')
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
