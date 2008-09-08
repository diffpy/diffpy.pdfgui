#!/usr/bin/env python

# Installation script for diffpy.pdfgui

"""PDFgui - graphical user interface for real space structure refinement.

Packages:   diffpy.pdfgui
Scripts:    pdfgui
"""

import os
from setuptools import setup, find_packages
import fix_setuptools_chmod

def dirglob(d, *patterns):
    from glob import glob
    rv = []
    for p in patterns:
        rv += glob(os.path.join(d, p))
    return rv

# define distribution
setup(
        name = 'diffpy.pdfgui',
        version = '1.0c1',
        namespace_packages = ['diffpy'],
        packages = find_packages(),
        scripts = ['applications/pdfgui'],
        data_files = [
            ('icons', dirglob('icons', '*.png', '*.ico')),
            ('doc', dirglob('doc', '*.pdf')),
            ('doc/manual', dirglob('doc/manual', '*.html', '*.pdf')),
            ('doc/manual/images', dirglob('doc/manual/images', '*.png')),
            ('doc/tutorial', dirglob('doc/tutorial', '*')),
        ],
        install_requires = [
            'diffpy.Structure',
            'diffpy.pdffit2',
        ],
        dependency_links = [
            'http://www.diffpy.org/packages/',
        ],

        author = 'Simon J.L. Billinge',
        author_email = 'sb2896@columbia.edu',
        description = "GUI for PDF simulation and structure refinement.",
        license = 'BSD',
        url = 'http://www.diffpy.org/',
        keywords = 'PDF structure refinement GUI',
)

# End of file
