# This module is imported from top level diffpy setup.py.
# It has to define the following variables:
#     name, description, diffpy_deps, other_deps, setup_args
# Optional variables:
#     makefiles -- a list of Makefiles to be build before installation

"""PDFgui - graphical user interface for real space structure refinement.

Packages:   diffpy.pdfgui
Scripts:    pdfgui
"""

# version
__id__ = "$Id$"

import os.path
import glob

thisfile = os.path.abspath(locals().get('__file__', 'setup_args.py'))
thisdir = os.path.dirname(thisfile)

def prependThisDir(files):
    return [os.path.join(thisdir, f) for f in files]

# name of this subpackage
name = "diffpy.pdfgui"
description = "GUI for PDF simulation and structure refinement.",

# dependencies from diffpy
diffpy_deps = [
        "diffpy.Structure",
        "diffpy.pdffit2"
    ]

# things to make
makefiles = prependThisDir(['doc/manual/Makefile'])

# third-party dependencies
other_deps = [
    "wxPython",
    "numpy",
    "matplotlib",
    ]

# define distribution arguments for this subpackage
setup_args = {
    "name" : name,
    "description" : description,
    "packages" : [
        "diffpy.pdfgui",
        "diffpy.pdfgui.control",
        "diffpy.pdfgui.gui",
        "diffpy.pdfgui.gui.wxExtensions",
        ],
    "package_dir" : {
        "diffpy.pdfgui" : os.path.join(thisdir, "pdfgui")
        },
    "scripts" : prependThisDir([
        "applications/pdfgui",
        ]),
    "data_files" : [
        ('pdfgui/icons', prependThisDir([
            'icons/*.png',
            'icons/*.ico',
            ]) ),
        ('pdfgui/doc', prependThisDir([
            'AUTHORS.txt',
            'LICENSE.txt',
            'README.txt',
            'doc/TUTORIAL.txt',
            'doc/Farrow-jpcm-2007.pdf',
            'doc/manual/*.pdf',
            'doc/manual/*.html',
            ]) ),
        ('pdfgui/doc/images', prependThisDir([
            'doc/manual/images/*.png',
            'doc/manual/images/*.jpg'
            ]) ),
        ('pdfgui/doc/tutorial', prependThisDir([
            'doc/tutorial/*'
            ]) ),
        ],
    }

# End of file 
