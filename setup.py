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
        version = '1.0',
        namespace_packages = ['diffpy'],
        packages = find_packages(),
        include_package_data = True,
        test_suite = 'diffpy.pdfgui.tests',
        entry_points = {
            'gui_scripts': [
                'pdfgui=diffpy.pdfgui.applications.pdfgui:main',
            ],
        },
        data_files = [
            ('icons', dirglob('icons', '*.png', '*.ico')),
            ('doc', dirglob('doc', '*.pdf')),
            ('doc/manual', dirglob('doc/manual', '*.html', '*.pdf')),
            ('doc/manual/images', dirglob('doc/manual/images', '*.png')),
            ('doc/tutorial', dirglob('doc/tutorial', '*')),
        ],
        # manual and tutorial files should not be zipped
        zip_safe = False,
        install_requires = [
            'diffpy.Structure>=1.1-r6772',
            'diffpy.pdffit2>=1.0-r6766',
            'diffpy.utils>=1.0-r6769',
        ],
        dependency_links = [
            'http://www.diffpy.org/packages/',
        ],

        author = 'Simon J.L. Billinge',
        author_email = 'sb2896@columbia.edu',
        maintainer = 'Pavol Juhas',
        maintainer_email = 'pj2192@columbia.edu',
        url = 'http://www.diffpy.org/',
        download_url = 'http://www.diffpy.org/packages/',
        description = "GUI for PDF simulation and structure refinement.",
        license = 'BSD',
        keywords = 'PDF structure refinement GUI',
        classifiers = [
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 5 - Production/Stable',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications',
            'Intended Audience :: Science/Research',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2.5',
            'Topic :: Scientific/Engineering :: Physics',
        ],
)

# End of file
