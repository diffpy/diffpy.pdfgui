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

"""
PDFgui Graphical User Interface for Pair Distribution Function fitting
Usage: pdfgui [project.dpp]

PDFgui is graphical user interface to PDFfit2 - a Python library for PDF
simulation and structure refinement.  PDFgui has many nice features such
as control of multiple fits, integrated plotting, easy setup of sequential
refinements, and saving of entire project in a single file.

Options:
  -h, --help      display this message
  -V, --version   show program version

Debugging options:
  --db-noed       disable exceptions catching to ErrorReportDialog
  --db-nocf       exit without asking to save modified project
  --db-pdb        use Python debugger to handle error exceptions
"""

from __future__ import print_function

import sys
import os
import getopt


def usage():
    """Show usage info.
    """
    myname = os.path.basename(sys.argv[0])
    msg = __doc__.replace("pdfgui", myname)
    print(msg)
    return


def version():
    from diffpy.pdfgui import __version__
    print("PDFgui", __version__)
    return


def processArguments(argv1):
    '''Process command line arguments and store results in pdfguiglobals.
    This method updates cmdopts, cmdargs and dbopts attributes in the
    pdfguiglobals module.

    argv1   -- list of command line arguments excluding the executable

    Returns boolean flag to indicate if the execution should continue.
    The flag is False, when options contain --help or --version.
    Raises GetoptError for invalid options.
    Raises ValueError for more than one project file arguments or
    when project is not a valid file.
    '''
    from diffpy.pdfgui.gui import pdfguiglobals
    dbopts = pdfguiglobals.dbopts
    dboptions = [('db-' + o[0]) for o in dbopts.alldebugoptions]
    # default parameters
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hV",
                ["help", "version"] + dboptions)
    # process options
    proceed = True
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            proceed = False
        elif o in ("-V", "--version"):
            version()
            proceed = False
        elif o.startswith('--') and o[2:] in dboptions:
            # strip "--db-"
            dbo = o[5:]
            setattr(dbopts, dbo, True)
    pdfguiglobals.cmdopts = opts
    # bail-out here if options contain --help or --version
    if not proceed:     return False
    # otherwise continue checking arguments
    if len(args) == 1 and not os.path.isfile(args[0]):
        emsg = "Project file %s does not exist." % args[0]
        raise ValueError(emsg)
    elif len(args) > 1:
        emsg = "Too many project files."
        raise ValueError(emsg)
    # ready to go
    pdfguiglobals.cmdargs = args
    return proceed


def main():
    '''Main entry point to  PDFgui.
    '''
    # process arguments
    proceed = False
    try:
        proceed = processArguments(sys.argv[1:])
    except (getopt.GetoptError, ValueError) as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    # bail out when no gui is needed
    if not proceed:     sys.exit()
    # initialize gui
    import diffpy.pdfgui.gui.main as guimain
    # Catch control errors, that may happen during project
    # loading, before the GUI gets running
    from diffpy.pdfgui.control.controlerrors import ControlError
    try:
        guimain.main()
    except ControlError as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    return


if __name__ == "__main__":
    main()

# End of file
