#!/usr/bin/env python

# Installation script for diffpy.pdfgui

"""PDFgui - graphical user interface for real space structure refinement.

Packages:   diffpy.pdfgui
Scripts:    pdfgui
"""

from setuptools import setup, find_packages
import fix_setuptools_chmod

# define distribution
setup(
        name = 'diffpy.pdfgui',
        namespace_packages = ['diffpy'],
        version = '1.0c1',
        packages = [
            'diffpy',
            'diffpy.pdfgui',
            'diffpy.pdfgui.control',
            'diffpy.pdfgui.gui',
            'diffpy.pdfgui.gui.wxExtensions',
        ],
        scripts = 'applications/pdfgui',
        package_data = {
            'icons' : ['*.png', '*.ico'],
            'doc' : ['*.pdf'],
            'doc/manual' : ['*.html', '*.pdf'],
            'doc/manual/images' : ['*.png'],
            'doc/tutorial' : ['*'],
        },
        install_requires = [
            'diffpy.Structure',
            'diffpy.pdffit2',
            'wx',
            'numpy',
            'matplotlib',
        ],
        dependency_links = [
            'http://diffpy.org/packages/',
        ],

        author = 'Simon J.L. Billinge',
        author_email = 'sb2896@columbia.edu',
        description = "GUI for PDF simulation and structure refinement.",
        license = 'BSD',
        url = 'http://www.diffpy.org/',
        keywords = 'PDF structure refinement GUI',
)

# End of file
