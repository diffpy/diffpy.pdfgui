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
    safeCPickleDumps    -- same as cPickleDumps, but safe for NaN and Inf
"""


from ConfigParser import RawConfigParser


def numericStringSort(lst):
    """Sort list of strings inplace according to general numeric value.
    Each string gets split to string and integer segments to create keys
    for comparison.  Signs, decimal points and exponents are ignored.

    lst  -- sorted list of strings

    No return value to highlight inplace sorting.
    """
    import re
    rx = re.compile(r'(\d+)')
    keys = [ rx.split(s) for s in lst ]
    for k in keys:  k[1::2] = [ int(i) for i in k[1::2] ]
    newlst = zip(keys, lst)
    newlst.sort()
    lst[:] = [kv[1] for kv in newlst]
    return

def safeCPickleDumps(obj):
    """Get cPickle representation of an object possibly containing NaN or Inf.
    By default it uses cPickle.HIGHEST_PROTOCOL, but falls back to ASCII
    protocol 0 if there is SystemError frexp() exception.

    obj -- object to be pickled

    Return cPickle string.
    """
    import cPickle
    ascii_protocol = 0
    try:
        s = cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL)
    except SystemError:
        s = cPickle.dumps(obj, ascii_protocol)
    return s


# This should be unnecessary in Python 3
class QuotedConfigParser(RawConfigParser):

    def getquoted(self, section, option):
        """Retrieve option value previously set with setquoted.

        This allows to work with unicode strings.
        """
        vq = self.get(section, option)
        rv = vq.decode('utf8')
        return rv


    def setquoted(self, section, option, value):
        """Set option to a value encoded with urllib.quote.

        This allows to store and write out unicode strings.
        Use getquoted to recover the decoded value.
        """
        vq = value.encode('utf8')
        return self.set(section, option, vq)

# class QuotedConfigParser

def quote_plain(s):
    """Return a possibly Unicode string quoted as plain ASCII.

    The returned value is suitable as a path component in the
    project file format.
    """
    from urllib import quote_plus
    rv = quote_plus(s.encode('utf8'))
    return rv


def unquote_plain(s):
    """Unquote string previously encoded with quote_plain.
    """
    from urllib import unquote_plus
    u = unquote_plus(str(s))
    rv = u.decode('utf8')
    return rv

# End of file
