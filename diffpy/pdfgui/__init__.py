#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfgui     by DANSE Diffraction group
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

'''Constants:
    __version__ -- full version of this PDFgui release
'''


from diffpy.pdfgui.version import __version__

# unit tests

def test():
    '''Execute all unit tests for the diffpy.pdfgui package.
    Return a unittest TestResult object.
    '''
    from diffpy.pdfgui.tests import test
    return test()


# End of file
