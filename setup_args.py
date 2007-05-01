# This module is imported from top level diffpy setup.py.
# It has to define the following variables:
#     name, description, diffpy_deps, other_deps, setup_args

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

# name of this subpackage
name = "diffpy.pdfgui"
description = "GUI for PDF simulation and structure refinement.",

# dependencies from diffpy
diffpy_deps = [
        "diffpy.Structure",
        "diffpy.pdffit2"
    ]

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
    "scripts" : [
        os.path.join(thisdir, "applications/pdfgui"),
        ],
    "data_files" : [
        ('pdfgui/icons', [
            'icons/*.png',
            'icons/*.ico',
            ]),
        ('pdfgui/doc', [
            'AUTHORS.txt',
            'LICENSE.txt',
            'README.txt',
            'doc/TUTORIAL.txt',
            'doc/Farrow-jpcm-subm.pdf',
            'doc/manual/*.pdf',
            'doc/manual/*.html',
            ]),
        ('pdfgui/doc/images', [
            'doc/manual/images/*.png',
            'doc/manual/images/*.jpg'
            ]),
        ('pdfgui/doc/tutorial', [
            'doc/tutorial/*'
            ]),
        ],
    }

# expand data_files
edf = []
for d, lst in setup_args["data_files"]:
    lst = [f for pat in lst for f in glob.glob(os.path.join(thisdir, pat))]
    edf.append((d, lst))
setup_args["data_files"] = edf

# End of file 
