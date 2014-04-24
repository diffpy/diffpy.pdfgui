#!/usr/bin/env python

# Installation script for diffpy.pdfgui

"""PDFgui - graphical user interface for real space structure refinement.

Packages:   diffpy.pdfgui
Scripts:    pdfgui
"""

import os
from setuptools import setup, find_packages

# versioncfgfile holds version data for git commit hash and date.
# It must reside in the same directory as version.py.
MYDIR = os.path.dirname(os.path.abspath(__file__))
versioncfgfile = os.path.join(MYDIR, 'diffpy/pdfgui/version.cfg')

def gitinfo():
    from subprocess import Popen, PIPE
    kw = dict(stdout=PIPE, cwd=MYDIR)
    proc = Popen(['git', 'describe', '--match=v[[:digit:]]*'], **kw)
    desc = proc.stdout.read()
    proc = Popen(['git', 'log', '-1', '--format=%H %at %ai'], **kw)
    glog = proc.stdout.read()
    rv = {}
    rv['version'] = '-'.join(desc.strip().split('-')[:2]).lstrip('v')
    rv['commit'], rv['timestamp'], rv['date'] = glog.strip().split(None, 2)
    return rv


def getversioncfg():
    from ConfigParser import SafeConfigParser
    cp = SafeConfigParser()
    cp.read(versioncfgfile)
    gitdir = os.path.join(MYDIR, '.git')
    if not os.path.isdir(gitdir):  return cp
    try:
        g = gitinfo()
    except OSError:
        return cp
    d = cp.defaults()
    if g['version'] != d.get('version') or g['commit'] != d.get('commit'):
        cp.set('DEFAULT', 'version', g['version'])
        cp.set('DEFAULT', 'commit', g['commit'])
        cp.set('DEFAULT', 'date', g['date'])
        cp.set('DEFAULT', 'timestamp', g['timestamp'])
        cp.write(open(versioncfgfile, 'w'))
    return cp

versiondata = getversioncfg()

def dirglob(d, *patterns):
    from glob import glob
    rv = []
    for p in patterns:
        rv += glob(os.path.join(d, p))
    return rv

# define distribution
setup(
        name = 'diffpy.pdfgui',
        version = versiondata.get('DEFAULT', 'version'),
        namespace_packages = ['diffpy'],
        packages = find_packages(),
        include_package_data = True,
        test_suite = 'diffpy.pdfgui.tests',
        entry_points = {
            'gui_scripts': [
                'pdfgui=diffpy.pdfgui.applications.pdfgui:main',
            ],
        },
        data_files = [
            ('icons', dirglob('icons', '*.png', '*.ico')),
            ('doc', dirglob('doc', '*.pdf')),
            ('doc/manual', dirglob('doc/manual', '*.html', '*.pdf')),
            ('doc/manual/images', dirglob('doc/manual/images', '*.png')),
            ('doc/tutorial', dirglob('doc/tutorial', '*')),
        ],
        # manual and tutorial files should not be zipped
        zip_safe = False,
        install_requires = [
            'diffpy.Structure>=1.1-r6772',
            'diffpy.pdffit2>=1.0-r6766',
            'diffpy.utils>=1.0-r6769',
        ],
        dependency_links = [
            'http://www.diffpy.org/packages/',
        ],

        author = 'Simon J.L. Billinge',
        author_email = 'sb2896@columbia.edu',
        maintainer = 'Pavol Juhas',
        maintainer_email = 'pj2192@columbia.edu',
        url = 'http://www.diffpy.org/',
        download_url = 'http://www.diffpy.org/packages/',
        description = "GUI for PDF simulation and structure refinement.",
        license = 'BSD',
        keywords = 'PDF structure refinement GUI',
        classifiers = [
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 5 - Production/Stable',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications',
            'Intended Audience :: Science/Research',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2.5',
            'Topic :: Scientific/Engineering :: Physics',
        ],
)

# End of file
