########################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2007 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################

"""Small shared routines:
    numericStringSort -- sort list of strings according to numeric value
"""

__id__ = "$Id$"

def numericStringSort(lst):
    """Sort list of strings inplace according to general numeric value.
    Each string gets split to string and integer segments to create keys
    for comparison.  Signs, decimal points and exponents are ignored.
    
    lst  -- sorted list of strings
    
    Return lst.
    """
    import re
    rx = re.compile(r'(\d+)')
    keys = [ rx.split(s) for s in lst ]
    for k in keys:  k[1::2] = [ int(i) for i in k[1::2] ]
    newlst = zip(keys, lst)
    newlst.sort()
    lst[:] = [kv[1] for kv in newlst]
    return lst

# End of file
