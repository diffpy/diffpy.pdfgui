########################################################################
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
########################################################################

"""PDFGui application
Functions:
    main()      PDFGui driver
"""

from version import __version__

def main():
    """PDFGui kick starter.
    Command line options and arguments can be passed via cmdopts
    and cmdargs variables in pdfgui.gui.pdfguiglobals module.
    """
    import pdfgui.gui.Main
    pdfgui.gui.Main.main()
    return

# version
__id__ = "$Id$"

# End of file 
