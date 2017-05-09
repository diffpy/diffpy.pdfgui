# -*- Makefile -*-
########################################################################
#
# wxExtensions      by DANSE Diffraction group
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

PROJECT = wxExtensions
PACKAGE = wxExtensions

#--------------------------------------------------------------------------
#

all: export


#--------------------------------------------------------------------------
#
# export

EXPORT_PYTHON_MODULES =     \
    __init__.py             \
    autowidthlabelsgrid.py  \
    listctrls.py            \
    paneldialog.py          \
    validators.py           \



export:: export-python-modules

# End of file
