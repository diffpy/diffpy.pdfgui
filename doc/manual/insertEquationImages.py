#!/usr/bin/python

"""Replace all equation marks in HTML file with <img> tag to display
corresponding PNG file.  This assumes PNG files are in correct sequence.
"""

# constants

rc = {
        'directory' : 'images',     # directory with equation images
}

eqmark = '<!-- EquationMark -->'

########################################################################
# business

import sys
import os
import re

eqcnt = 0
def eqreplace(mx):
    """helper function to replace equation marks.

    mx -- regular expression match object

    Return replacement string.
    """
    global eqcnt
    eqcnt += 1
    imgfile = "eq-%02i.png" % eqcnt
    imgurl = os.path.join(rc['directory'], imgfile)
    s = '</p><p align="center"><img src="%s" alt="%s">' % (imgurl, imgurl)
    return s

def replaceEquationMarks(filename):
    """Replace equation marks in given file.
    Overwrite the file if it gets modified.
    No return value.
    """
    s = open(filename).read()
    s1 = re.sub(eqmark, eqreplace, s)
    if s1 != s:     open(filename, 'w').write(s1)
    return

def main():
    for f in sys.argv[1:]:
        replaceEquationMarks(f)

if __name__ == "__main__":
    main()
