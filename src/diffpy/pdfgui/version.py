#!/usr/bin/env python
##############################################################################
#
# (c) 2024 The Trustees of Columbia University in the City of New York.
# All rights reserved.
#
# File coded by: Billinge Group members and community contributors.
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/diffpy/diffpy.pdfgui/graphs/contributors
#
# See LICENSE.rst for license information.
#
##############################################################################
"""Definition of __version__."""

#  We do not use the other three variables, but can be added back if needed.
#  __all__ = ["__date__", "__git_commit__", "__timestamp__", "__version__"]

import os
import time
from importlib.metadata import distribution, version

# obtain version information
__date__ = time.ctime(os.path.getctime(distribution("diffpy.pdfgui")._path))
__version__ = version("diffpy.pdfgui")
