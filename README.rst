|Icon| |title|_
===============

.. |title| replace:: diffpy.pdfgui
.. _title: https://diffpy.github.io/diffpy.pdfgui

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.pdfgui
        :height: 100px

|PyPi| |Forge| |PythonVersion| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.pdfgui/actions/workflows/main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.pdfgui/actions/workflows/main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.pdfgui/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.pdfgui

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.pdfgui
        :target: https://anaconda.org/conda-forge/diffpy.pdfgui

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff

.. |PyPi| image:: https://img.shields.io/pypi/v/diffpy.pdfgui
        :target: https://pypi.org/project/diffpy.pdfgui/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.pdfgui
        :target: https://pypi.org/project/diffpy.pdfgui/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.pdfgui/issues

diffpy.pdfgui
========================================================================

Graphical user interface program for structure refinements to atomic
pair distribution function.

PDFgui is a friendly interface to the PDFfit2 refinement engine, with many
powerful extensions.  To get started, please open the manual from the
help menu and follow the tutorial instructions.  A detailed description
is available in the doc/Farrow-jpcm-2007.pdf paper.


Requirements
------------------------------------------------------------------------

PDFgui requires Python 3.8+ or 2.7 and several third-party
libraries that are used by PDFgui and its components.

* setuptools   - tools for installing Python packages
* wxpython     - graphical user interface toolkit for Python
* numpy        - library for scientific computing with Python
* matplotlib   - Python 2D plotting library
* diffpy.pdffit2 - computational engine for PDFgui,
  https://github.com/diffpy/diffpy.pdffit2
* diffpy.structure - simple storage and manipulation of atomic
  structures, https://github.com/diffpy/diffpy.structure
* diffpy.utils - shared helper utilities for wx GUI,
  https://github.com/diffpy/diffpy.utils

We recommend to use `Anaconda Python <https://www.anaconda.com/download>`_
which allows to conveniently install PDFgui and all its software
dependencies with a single command.

Please note that the Python3 PDFgui will read .ddp3 files. It is also
possible for it to read .ddp files that were saved by the Python2 PDFgui
but it will sometimes fail to read these. We are working on a solution
that will be available in a future version.

        diffpy.pdfgui Package, https://github.com/diffpy/diffpy.pdfgui

Installation
------------

The preferred method is to use `Miniconda Python
<https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html>`_
and install from the "conda-forge" channel of Conda packages.

To add "conda-forge" to the conda channels, run the following in a terminal. ::

        conda config --add channels conda-forge

We want to install our packages in a suitable conda environment.
The following creates and activates a new environment named ``diffpy.pdfgui_env`` ::

        conda create -n diffpy.pdfgui_env python=3
        conda activate diffpy.pdfgui_env

Then, to fully install ``diffpy.pdfgui`` in our active environment, run ::

        conda install diffpy.pdfgui

Another option is to use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.pdfgui_env`` environment, we will also have to install dependencies ::

        pip install -r https://raw.githubusercontent.com/diffpy/diffpy.pdfgui/main/requirements/run.txt

and then install the package ::

        pip install diffpy.pdfgui

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.pdfgui/>`_. Once installed, ``cd`` into your ``diffpy.pdfgui`` directory
and run the following ::

        pip install .

Support and Contribute
----------------------

`Diffpy user group <https://groups.google.com/g/diffpy-users>`_ is the discussion forum for general questions and discussions about the use of diffpy.pdfgui. Please join the diffpy.pdfgui users community by joining the Google group. The diffpy.pdfgui project welcomes your expertise and enthusiasm!

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.pdfgui/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.pdfgui/pulls>`_. You can also post it to the `Diffpy user group <https://groups.google.com/g/diffpy-users>`_. 

Feel free to fork the project and contribute. To install diffpy.pdfgui
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Before contribuing, please read our `Code of Conduct <https://github.com/diffpy/diffpy.pdfgui/blob/main/CODE_OF_CONDUCT.rst>`_.

Contact
-------

For more information on diffpy.pdfgui please visit the project `web-page <https://diffpy.github.io/>`_ or email Prof. Simon Billinge at sb2896@columbia.edu.
