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

import sys

import pytest

if __name__ == "__main__":
    # show output results from every test function
    args = ["-v"]
    # show the message output for skipped and expected failure tests
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    print("pytest arguments: {}".format(args))
    # call pytest and exit with the return code from pytest
    exit_res = pytest.main(args)
    sys.exit(exit_res)

# End of file
