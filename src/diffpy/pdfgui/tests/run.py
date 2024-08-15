#!/usr/bin/env python
##############################################################################
#
# (c) 2012-2024 The Trustees of Columbia University in the City of New York.
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

"""Convenience module for executing all unit tests with

python -m diffpy.pdfgui.tests.run
"""


if __name__ == "__main__":
    import sys

    # show warnings by default
    if not sys.warnoptions:
        import os
        import warnings

        warnings.simplefilter("default")
        # also affect subprocesses
        os.environ["PYTHONWARNINGS"] = "default"
    from diffpy.pdfgui.tests import test

    # produce zero exit code for a successful test
    sys.exit(not test().wasSuccessful())

# End of file
