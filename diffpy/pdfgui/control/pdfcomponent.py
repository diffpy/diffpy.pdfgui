#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Jiwu Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

class PDFComponent(object):
    """Common base class."""
    def __init__(self, name):
        """initialize

        name -- object name
        """
        self.name = name

    def close ( self, force = False ):
        """close myself

        force -- if forcibly (no wait)
        """
        pass

# End of file
