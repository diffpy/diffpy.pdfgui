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


import six
from six.moves.configparser import RawConfigParser
import six.moves.cPickle as pickle

# protocol=2 keep project files compatible with Python 2
# PDFGUI_PICKLE_PROTOCOL = 2


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
    newlst = sorted(zip(keys, lst))
    lst[:] = [kv[1] for kv in newlst]
    return

def pickle_loads(sdata, encoding="latin1"):
    """Mimic interface of Python 3 pickle.loads.

    Using encoding='latin1' is required for unpickling NumPy arrays and
    instances of datetime, date and time pickled by Python 2.

    Return the reconstructed object hierarchy.
    """
    rv = (pickle.loads(sdata, encoding=encoding) if six.PY3
          else pickle.loads(sdata))
    return rv


def safeCPickleDumps(obj):
    """Get pickle representation of an object possibly containing NaN or Inf.
    By default it uses pickle.HIGHEST_PROTOCOL, but falls back to ASCII
    protocol 0 if there is SystemError frexp() exception.

    obj -- object to be pickled

    Return pickle string.
    """
    ascii_protocol = 0
    try:
        s = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
    except SystemError:
        s = pickle.dumps(obj, ascii_protocol)
    return s


# This should be unnecessary in Python 3
# TODO - replace getquoted/setquoted with get/set after dropping Python 2

class QuotedConfigParser(RawConfigParser):

    def getquoted(self, section, option):
        """Retrieve option value previously set with setquoted.

        This allows to work with unicode strings.
        """
        vq = self.get(section, option)
        rv = vq.decode('utf-8') if six.PY2 else vq
        return rv


    def setquoted(self, section, option, value):
        """Set option to a value encoded with urllib.quote.

        This allows to store and write out unicode strings.
        Use getquoted to recover the decoded value.
        """
        vq = value.encode('utf-8') if six.PY2 else value
        return self.set(section, option, vq)

# class QuotedConfigParser

def quote_plain(s):
    """Return a possibly Unicode string quoted as plain ASCII.

    The returned value is suitable as a path component in the
    project file format.
    """
    from six.moves.urllib.parse import quote_plus
    rv = quote_plus(asunicode(s).encode('utf-8'))
    return rv


def unquote_plain(s):
    """Unquote string previously encoded with quote_plain.
    """
    from six.moves.urllib.parse import unquote_plus
    u = unquote_plus(s)
    rv = asunicode(u)
    return rv


def asunicode(s):
    '''Convert string or bytes object to a text type.

    This is `unicode` in Python 2 and `str` in Python 3.
    '''
    rv = s
    if not isinstance(s, six.text_type):
        rv = s.decode('utf-8')
    return rv

# End of file
