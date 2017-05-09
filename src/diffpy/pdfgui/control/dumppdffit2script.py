#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Create list of fits from pdffit2 script and pickle it to standard output.
Usage: dumppdffit2script.py scriptfile.py [arg1] [arg2] ...

Returns exit code 0 if script was successfully read, 1 if an error occured
and 2 if scriptfile.py does not exist
"""


import sys
import os

from diffpy.pdfgui.control.pdffitsandbox import PdfFitSandbox
from diffpy.pdfgui.utils import safeCPickleDumps

def main():
    if len(sys.argv) < 2:
        print >> sys.stderr, "scriptfile not specified."
        sys.exit(2)
    elif not os.path.isfile(sys.argv[1]):
        print >> sys.stderr, "Cannot read %r" % sys.argv[1]
        sys.exit(2)
    scriptfile = sys.argv[1]
    scriptbase = os.path.basename(scriptfile)
    del sys.argv[1]
    box = PdfFitSandbox()
    try:
        box.loadscript(scriptfile)
    except:
        exc_type, exc_value, exc_tb = sys.exc_info()
        import traceback
        for filename, lineno, fnc, line in traceback.extract_tb(exc_tb):
            if os.path.basename(filename) != scriptbase:
                continue
            print >> sys.stderr, "%s:%i:%s" % (scriptfile, lineno, line)
        print >> sys.stderr, exc_value
        sys.exit(1)
    # make sure reading from stderr will not hang, see
    # http://www.python.org/doc/current/lib/popen2-flow-control.html
    os.close(sys.stderr.fileno())
    # all is ready, dump it
    sys.stdout.write( safeCPickleDumps(box.allfits()) )
    return

if __name__ == "__main__":
    main()

# End of file
