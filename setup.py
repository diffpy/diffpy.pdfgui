#!/usr/bin/env python

# Installation script for diffpy.pdfgui

"""PDFgui - graphical user interface for real space structure refinement.

Packages:   diffpy.pdfgui
Scripts:    pdfgui
"""

import os
import re
import sys
from setuptools import setup, find_packages

# Use this version when git data are not available, like in git zip archive.
# Update when tagging a new release.
FALLBACK_VERSION = '2.0.0'

# determine if we run with Python 3.
PY3 = (sys.version_info[0] == 3)

# versioncfgfile holds version data for git commit hash and date.
# It must reside in the same directory as version.py.
MYDIR = os.path.dirname(os.path.abspath(__file__))
versioncfgfile = os.path.join(MYDIR, 'src/diffpy/pdfgui/version.cfg')
gitarchivecfgfile = os.path.join(MYDIR, '.gitarchive.cfg')

def gitinfo():
    from subprocess import Popen, PIPE
    kw = dict(stdout=PIPE, cwd=MYDIR, universal_newlines=True)
    proc = Popen(['git', 'describe', '--tags', '--match=v[[:digit:]]*'], **kw)
    desc = proc.stdout.read()
    proc = Popen(['git', 'log', '-1', '--format=%H %ct %ci'], **kw)
    glog = proc.stdout.read()
    rv = {}
    rv['version'] = '.post'.join(desc.strip().split('-')[:2]).lstrip('v')
    rv['commit'], rv['timestamp'], rv['date'] = glog.strip().split(None, 2)
    return rv


def getversioncfg():
    if PY3:
        from configparser import RawConfigParser
    else:
        from ConfigParser import RawConfigParser
    vd0 = dict(version=FALLBACK_VERSION, commit='', date='', timestamp=0)
    # first fetch data from gitarchivecfgfile, ignore if it is unexpanded
    g = vd0.copy()
    cp0 = RawConfigParser(vd0)
    cp0.read(gitarchivecfgfile)
    if len(cp0.get('DEFAULT', 'commit')) > 20:
        g = cp0.defaults()
        mx = re.search(r'\btag: v(\d[^,]*)', g.pop('refnames'))
        if mx:
            g['version'] = mx.group(1)
    # then try to obtain version data from git.
    gitdir = os.path.join(MYDIR, '.git')
    if os.path.exists(gitdir) or 'GIT_DIR' in os.environ:
        try:
            g = gitinfo()
        except OSError:
            pass
    # finally, check and update the active version file
    cp = RawConfigParser()
    cp.read(versioncfgfile)
    d = cp.defaults()
    rewrite = not d or (g['commit'] and (
        g['version'] != d.get('version') or g['commit'] != d.get('commit')))
    if rewrite:
        cp.set('DEFAULT', 'version', g['version'])
        cp.set('DEFAULT', 'commit', g['commit'])
        cp.set('DEFAULT', 'date', g['date'])
        cp.set('DEFAULT', 'timestamp', g['timestamp'])
        with open(versioncfgfile, 'w') as fp:
            cp.write(fp)
    return cp

versiondata = getversioncfg()


def dirglob(d, *patterns):
    from glob import glob
    rv = []
    for p in patterns:
        rv += glob(os.path.join(d, p))
    return rv


with open(os.path.join(MYDIR, 'README.rst')) as fp:
    long_description = fp.read()

# define distribution
setup_args = dict(
    name = 'diffpy.pdfgui',
    version = versiondata.get('DEFAULT', 'version'),
    packages = find_packages(os.path.join(MYDIR, 'src')),
    package_dir = {'' : 'src'},
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
        'six',
        'diffpy.structure>=3',
        'diffpy.pdffit2',
        'diffpy.utils',
    ],

    author = 'Simon J.L. Billinge',
    author_email = 'sb2896@columbia.edu',
    maintainer = 'Pavol Juhas',
    maintainer_email = 'pavol.juhas@gmail.com',
    url = 'https://github.com/diffpy/diffpy.pdfgui',
    description = "GUI for PDF simulation and structure refinement.",
    long_description = long_description,
    long_description_content_type = 'text/x-rst',
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
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
    ],
)

if __name__ == '__main__':
    setup(**setup_args)

# End of file
