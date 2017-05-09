#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfgui     by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2016 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Helper routines for running other unit tests.
"""

# helper functions

def datafile(filename):
    from pkg_resources import resource_filename
    rv = resource_filename(__name__, "testdata/" + filename)
    return rv

# End of file
