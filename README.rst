.. image:: https://travis-ci.org/diffpy/diffpy.pdfgui.svg?branch=master
   :target: https://travis-ci.org/diffpy/diffpy.pdfgui

.. image:: https://codecov.io/gh/diffpy/diffpy.pdfgui/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/diffpy/diffpy.pdfgui


PDFgui
========================================================================

Graphical user interface program for structure refinements to atomic
pair distribution function.

PDFgui is a friendly interface to PDFfit2 refinement engine, with many
powerful extensions.  To get started, please open the manual from the
help menu and follow the tutorial instructions.  A detailed description
is available in the doc/Farrow-jpcm-2007.pdf paper.


REQUIREMENTS
------------------------------------------------------------------------

PDFgui requires Python 3.7, 3.6, 3.5 or 2.7 and several third-party
libraries that are used by PDFgui and its components.

* setuptools   - tools for installing Python packages
* wxpython     - graphical user interface toolkit for Python
* NumPy        - library for scientific computing with Python
* matplotlib   - Python 2D plotting library
* diffpy.pdffit2 - computational engine for PDFgui,
  https://github.com/diffpy/diffpy.pdffit2
* diffpy.structure - simple storage and manipulation of atomic
  structures, https://github.com/diffpy/diffpy.structure
* diffpy.utils - shared helper utilities for wx GUI,
  https://github.com/diffpy/diffpy.utils

We recommend to use `Anaconda Python <https://www.anaconda.com/download>`_
which allows to conveniently install PDFgui and all its software
dependencies with a single command.  For other Python distributions
it is necessary to install the required software separately.  As an
example, on Ubuntu Linux some of the required software can be
installed using ::

   sudo apt-get install \
      python-setuptools python-wxtools python-numpy \
      python-matplotlib

To install the remaining packages see the installation instructions
at their respective web pages.

Notice that due to the update from Python2 to Python3, the `.ddp` project
file that was saved by Python2 PDFgui cannot be read by Python3 PDFgui at
this moment.

INSTALLATION
------------------------------------------------------------------------

The preferred method is to use Anaconda Python and install from the
"diffpy" channel of Anaconda packages ::

   conda config --add channels diffpy
   conda install diffpy.pdfgui

PDFgui can be then started from a terminal ("Anaconda Prompt" on
Windows) by executing the "pdfgui" program.  An alternative
method on Windows is to start PDFgui through the DiffPy start menu.

If you don't use Anaconda or prefer to install from sources, make
sure the required software is all in place and run ::

   python setup.py install

By default the files are installed to standard system directories,
which may require the use of ``sudo`` for write privileges.  If
administrator (root) access is not available, see the output from
``python setup.py install --help`` for options to install as a regular
user to user-writable locations.  Note that installation to non-standard
directories may require adjustments to the PATH and PYTHONPATH
environment variables.  The installation integrity can be verified by
changing to the HOME directory and running ::

   python -m diffpy.pdfgui.tests.rundeps

With Anaconda PDFgui can be later upgraded to the latest released
version using ::

   conda update diffpy.pdfgui

With other Python distributions the program can be upgraded to
the latest version as follows ::

   easy_install --upgrade diffpy.pdfgui


Other software
````````````````````````````````````````````````````````````````````````

PDFgui can use an external structure viewer for displaying analyzed
structures.  We have tested with several structure viewers such as

* AtomEye, http://li.mit.edu/A/Graphics/A/
* PyMol, https://www.pymol.org

Other viewers should work as well, as long as they understand one of
the output structure formats supported by PDFgui.


DEVELOPMENT
------------------------------------------------------------------------

PDFgui is an open-source software available in a git repository at
https://github.com/diffpy/diffpy.pdfgui.

Feel free to fork the project and contribute.  To install PDFgui
in a development mode where the source files are used directly
rather than copied to a system directory, use ::

   python setup.py develop --user


CONTACTS
------------------------------------------------------------------------

For more information on PDFgui please visit the project web-page:

https://www.diffpy.org/products/pdfgui.html

or email Prof. Simon Billinge at sb2896@columbia.edu
