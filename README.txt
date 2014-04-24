PDFgui - graphical user interface for real space structure refinement.

PDFgui is a friendly interface to PDFfit2 refinement engine, with many
powerful extensions.  To get started, please open the manual from the
help menu and follow the tutorial instructions.  A detailed description
is available in the doc/Farrow-jpcm-2007.pdf paper.


REQUIREMENTS

PDFgui requires Python 2.5 and several third-party libraries that are
used by PDFgui or other necessary components from the DiffPy library.

    setuptools  -- software distribution tools for Python
    wxPython    -- graphical user interface toolkit for Python
    numpy       -- numerical mathematics and fast array operations for Python
    matplotlib  -- plotting library and interactive interface
    python-dev  -- header files for interfacing Python with C
    GSL         -- GNU Scientific Library for C
    g++         -- GNU C++ compiler

On Ubuntu Linux the required software can be easily installed using
the system package manager:

    sudo aptitude install \
        python-setuptools python-wxtools python-numpy \
        python-matplotlib python-dev libgsl0-dev g++

For other Linux distributions use the respective package manager to install
these packages.  Note there may be somewhat different names.  PDFgui should
work on other Unix-like operating systems and on Mac as well.  Please, search
the web for instructions how to install external dependencies on your
particular platform.


INSTALLATION

Once all the requirements are in place, the installation of PDFgui
should be a breeze:

    python setup.py install

This command installs the "pdfgui" program and all other DiffPy components
that are needed for its operation.  By default the files are installed in
standard system directories, which are usually writeable only by the root.
See the usage info "./setup.py install --help" for options to install
as a normal user under different location.  Note that installation to
non-standard directories you may require adjustments to the PATH and
PYTHONPATH environment variables.

The Python setuptools library provides an easy_install script, which can
be used to update an existing installation of PDFgui or even to do a
new install without an explicit need to download and unzip the code:

    easy_install -U diffpy.pdfgui

This checks the package repository at http://www.diffpy.org/packages/
for any newer releases of PDFgui and if they are present, it updates the
installation.  The easy_install can be also used to get in sync with the
latest development sources in the subversion repository:

    easy_install -U \
	svn://svn@danse.us/diffraction/diffraction/diffpy.pdfgui/trunk


OTHER SOFTWARE

PDFgui can use an external structure viewer for displaying analyzed
structures.  We have tested with several structure viewers such as

    AtomEye   http://mt.seas.upenn.edu/Archive/Graphics/A/
    PyMol     http://pymol.sourceforge.net/

Other viewers should work as well, as long as they understand one of
the output structure formats supported by PDFgui.


CONTACTS

For more information on PDFgui please visit the project web-page:

    http://www.diffpy.org/

or email Prof. Simon Billinge at sb2896@columbia.edu
