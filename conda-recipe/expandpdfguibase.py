#!/usr/bin/env python

import sys
from pkg_resources import Requirement, resource_filename

pkg = Requirement.parse('diffpy.pdfgui')
PDFGUIPATH = resource_filename(pkg, '')
assert PDFGUIPATH.lower().startswith(sys.prefix.lower())
PDFGUIBASE = PDFGUIPATH[len(sys.prefix):].replace('\\', '/').strip('/')

if __name__ == "__main__":
    with open(sys.argv[1]) as fp:
        content = fp.read()
    output = content.replace('@PDFGUIBASE@', PDFGUIBASE)
    sys.stdout.write(output)
