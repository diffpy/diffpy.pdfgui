#!/usr/bin/python

"""Read one or more texinfo files and extract any equations marked
in the code with '@EquationMark' macro as PNG files to the images
directory.
"""

# constants

rc = {
        'directory' : 'images',     # output directory
        'resolution' : 72,          # equation images resolution
        'eqns' : [],                # list of raw equation codes
        'tmpdir' : None,            # temporary directory
}

eqlatex = r"""
\documentclass{article}
\usepackage{exscale}
\pagestyle{empty}
\setlength{\oddsidemargin}{0in}
\setlength{\textwidth}{7in}
\begin{document}
\huge
%s
\end{document}
""".lstrip()

eqmark = "@EquationMark"

##############################################################################
# business

import sys
import os
import shutil

def loadEquations():
    """Search for equation codes preceded by @EquationMark macro.
    Store equation codes in rc['eqns'].
    """
    lines = []
    for f in sys.argv[1:]:
        fhandle = open(f)
        lines.extend(fhandle.readlines())
    # process all lines in sequence
    atmark = False
    attex = False
    eqlines = []
    for line in lines:
        bareline = line.strip().rstrip('{}')
        if bareline == eqmark:
            atmark = True
            continue
        elif atmark and bareline == "@tex":
            attex = True
            continue
        elif attex and bareline == "@end tex":
            atmark = False
            attex = False
            eq = ''.join(eqlines) + '\n'
            rc['eqns'].append(eq)
            eqlines = []
        elif attex:
            eqlines.append(line)
    return

def writePNGFiles():
    from tempfile import mkdtemp
    rc['tmpdir'] = mkdtemp()
    rc['directory'] = os.path.abspath(rc['directory'])
    neqn = len(rc['eqns'])
    for i in range(neqn):
        fname = "eq-%02i.tex" % (i + 1)
        fpath = os.path.join(rc['tmpdir'], fname)
        fhandle = open(fpath, 'w')
        s = eqlatex % rc['eqns'][i]
        fhandle.write(s)
        fhandle.close()
        convertToPNG(fpath)
        pngsrc = fpath[:-4] + ".png"
        pngdst = os.path.join(rc['directory'], fname[:-4] + ".png")
        shutil.copyfile(pngsrc, pngdst)
    return

def convertToPNG(texfile):
    """Compile texfile and convert it to PNG.
    """
    os.chdir(os.path.dirname(texfile))
    texbasename = os.path.splitext(os.path.basename(texfile))[0]
    cmd = "latex --interaction nonstopmode %r" % texbasename
    os.system(cmd) != 0 and sys.exit(1)
    cmd = "dvips %r" % texbasename
    os.system(cmd) != 0 and sys.exit(1)
    psfilename = texbasename + ".ps"
    bb = getBoundingBox(psfilename)
    pgbb = getPageBoundingBox(psfilename)
    pt2px = rc['resolution'] / 72.0
    xpx = pt2px * bb[0]
    ypx = pt2px * (pgbb[3] - bb[3])
    wpx = pt2px * (bb[2] - bb[0])
    hpx = pt2px * (bb[3] - bb[1])
    geometry = "%ix%i+%i+%i" % (wpx, hpx, xpx, ypx)
    pngfilename = texbasename + ".png"
    cmd = "convert -strip -density %i %r -crop %s +repage %r" % \
        (rc['resolution'], psfilename, geometry, pngfilename)
    os.system(cmd) != 0 and sys.exit(1)
    return

def getBoundingBox(psfilename):
    """Run ghostscript to obtain effective bounding box of psfilename.
    Return a list of bounding box coordinates.
    """
    cmd = "gs -dNOPAUSE -dBATCH -q -sDEVICE=bbox %r" % psfilename
    # gs sends bbox output to stderr
    i, o, e = os.popen3(cmd)
    i.close()
    out = o.read()
    o.close()
    out += e.read()
    e.close()
    bb = [ int(w) for w in out.split()[1:5] ]
    return bb

def getPageBoundingBox(psfilename):
    """Obtain bounding box value defined in psfilename.
    Return a list of bounding box coordinates.
    """
    import re
    with open(psfilename) as fp:
        s = fp.read()
    bbline = re.search('^%%BoundingBox: *(.*)$', s, re.M)
    pgbb = [ int(w) for w in bbline.group(1).split()[:4] ]
    return pgbb

def main():
    loadEquations()
    writePNGFiles()
    shutil.rmtree(rc['tmpdir'])

if __name__ == "__main__":
    main()
