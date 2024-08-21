#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Definition of __version__ and __date__."""

import os
import time
from importlib.metadata import distribution, version

__date__ = time.ctime(os.path.getctime(distribution("diffpy.pdfgui")._path))
__version__ = version("diffpy.pdfgui")

# End of file
