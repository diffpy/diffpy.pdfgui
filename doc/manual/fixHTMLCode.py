#!/usr/bin/python

"""Replace all equation marks in HTML file with <img> tag to display
corresponding PNG file.  This assumes PNG files are in correct sequence.
Also fix any accented characters texinfo does not get right.
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

def replaceEquationMarks(s):
    """Replace equation marks in given string.
    Return modified string.
    """
    s1 = re.sub(eqmark, eqreplace, s)
    return s1

def fixAccents(s):
    """Fix accented characters in texinfo HTML output.
    Return string with fixed characters.
    """
    s1 = s.replace('Boz&lt;in', 'Bo&#382;in')
    return s1

def main():
    for f in sys.argv[1:]:
        s = open(f).read()
        s1 = replaceEquationMarks(s)
        s1 = fixAccents(s1)
        if s1 != s:     open(f, 'w').write(s1)


if __name__ == "__main__":
    main()
