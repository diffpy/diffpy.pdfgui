#!/usr/bin/env python
##############################################################################
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
##############################################################################
"""Small shared routines:
    numericStringSort   -- sort list of strings according to numeric value
    safeCPickleDumps    -- same as pickle.dumps, but safe for NaN and Inf
"""


def numericStringSort(lst):
    """Sort list of strings inplace according to general numeric value. Each
    string gets split to string and integer segments to create keys for
    comparison.  Signs, decimal points and exponents are ignored.

    lst  -- sorted list of strings

    No return value to highlight inplace sorting.
    """
    import re

    rx = re.compile(r"(\d+)")
    keys = [rx.split(s) for s in lst]
    for k in keys:
        k[1::2] = [int(i) for i in k[1::2]]
    newlst = sorted(zip(keys, lst))
    lst[:] = [kv[1] for kv in newlst]
    return


def safeCPickleDumps(obj):
    """Get pickle representation of an object possibly containing NaN or Inf.
    By default it uses pickle.HIGHEST_PROTOCOL, but falls back to ASCII
    protocol 0 if there is SystemError frexp() exception.

    obj -- object to be pickled

    Return pickle string.
    """

    import pickle

    ascii_protocol = 0
    try:
        s = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
    except SystemError:
        s = pickle.dumps(obj, ascii_protocol)
    return s


def asunicode(s):
    """Convert string or bytes object to a text type."""
    rv = s
    if not isinstance(s, str):
        rv = s.decode("utf-8")
    return rv


# End of file
