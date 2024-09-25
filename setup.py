#!/usr/bin/env python

# Extensions script for diffpy.pdfgui

import os
import re
import sys
import glob
from setuptools import setup
from setuptools import Extension

# Define extension arguments here
ext_kws = {
        'libraries' : [],
        'extra_compile_args' : [],
        'extra_link_args' : [],
        'include_dirs' : [],
}

def create_extensions():
    "Initialize Extension objects for the setup function."
    ext = Extension('diffpy.pdfgui.pdfgui',
                    glob.glob('src/extensions/*.cpp'),
                    **ext_kws)
    return [ext]


# Extensions not included in pyproject.toml
setup_args = dict(
    ext_modules = [],
)


if __name__ == '__main__':
    setup_args['ext_modules'] = create_extensions()
    setup(**setup_args)

