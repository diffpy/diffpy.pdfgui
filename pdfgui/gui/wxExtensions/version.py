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

"""Definition of __version__ for wxExtensions package.
"""

# to update __version__ add hashmark below just before committing
#####

__id__ = "$Id$"

__version__ = "0.1."

svnrevision = __id__.split()[2:3]
if svnrevision:     __version__ += svnrevision[0]
else:               __version__ += "?"

# End of file
