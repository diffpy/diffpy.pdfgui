.. _extras:

Extras
######

============
PDF plotting
============


Plotting capabilities of PDFgui are provided through the plot control panel and the quick-plot icon on the tool bar. A quick-plot is created by selecting a node in the fit tree and
then clicking the quick-plot icon in the tool bar. The same quick-plot can be created by
middle-clicking on a node in the fit tree.


The plot control allows for selection of x and y coordinates for plotting.
The
**actual quantities** that could be assigned to the coordinates is determined by selection of either ``Fit``,
or ``Phase``, or ``Data`` on the fit tree. The choices for x and y coordinates varies depending
on what is selected on the fit tree.
**Special options** like *index*, *temperature* and *doping*
are available as choices for x in cases of plotting multiple fit results from sequential fitting
protocols. The **plot window** provides essential functionality such as *zoom*, *pan*, *cursor*
*coordinate tracking*, and *shifts*. Features such as *saving*, *exporting* and *printing* are also
available.

The principal intent of the plotting functionality is to allow quick access to the
fitting results to enhance the scientific process. If ``Data`` is selected on the fit tree, the user
can plot various aspects of the PDF function, such as data, model and difference PDF
profiles as a function of inter-atomic distance r. If the ``Fit`` or the ``Phase`` are selected, then
various parameters, both structural and internal can be plotted instead.


Since several formal
plotting examples were given through the tutorial exercise, and having simplicity of usage in
mind, no other plotting examples are provided, hoping that the usage is sufficiently simple
for users to master individually with ease. An example plot of Rw vs refinement step is
shown in Figure 4.1 for Ni example.



  .. figure:: images/fig4-01.png
     :align: center
     :figwidth: 100%

     Figure 4.1: Plotting window featuring Rw vs refinement step for Ni example. The basic functionality for manipulating the plot is provided through icons on the tool bar of the plotting window.



========================
Displaying the structure
========================

PDFgui can visualize 3D structures by displaying them with an external visualization program. The visualization program needs to be specified together with a suitable structure
format in the “Edit → Preferences” menu in PDFgui. The structure plotting feature has
been tested with the following programs:

============================================ ===============================
AtomEyeAtomEye structure viewer, XCFG format http://li.mit.edu/A/Graphics/A/
============================================ ===============================
PyMOLPyMOL structure viewer, PDB format      https://www.pymol.org
============================================ ===============================

**A note for AtomEye users:**

AtomEye requires its standard output is connected to a terminal. On Unix this happens
when pdfgui is started from a terminal. However if you prefer to start PDFgui using a
desktop shortcut or via “Run Application” dialog of the window manager, you need to put
the following information to the “Edit → Preferences” menu of PDFgui.::

    Structure viewer executable: xterm
    Argument string: -iconic -e ATOMEYE %s
    Structure format: xcfg

In the above, ``ATOMEYE`` is the path to the ATOMEYE executable.

For Cygwin users, the workaround is to launch the executable from a batch file. Batch
files can only run in a command window on Windows and so AtomEye’s requirements would
be for sure satisfied. In addition the batch file can be used to adjust environment variables::

    atomeye.bat
    ------------------------------------------------------------------------
    set DISPLAY=localhost:0
    set PATH=C:\cygwin\bin;C:\cygwin\usr\X11R6\bin;C:\ATOMEYE_DIR;%PATH%
    start A.exe %*
    ------------------------------------------------------------------------

  Here ``ATOMEYE_DIR`` needs to be replaced with a proper path. Make sure that the X-server
application included with Cygwin is started.


With a structural visualizer available, PDFgui
allows for initial or refined structures to be visualized by passing required structural information that program. This is achieved by highlighting a desired phase on the ``Fit Tree``, and
then selecting ``Plot Initial Structure`` or ``Plot Refined Structure`` from the “Phases” drop-down menu. The quick-plot button (or middle-click) will also invoke the structure viewer
with the refined structure, or initial structure if the refined structure does not yet exist. The control of the visualization is dependent on the viewer used.

An example Ni structure visualization with AtomEye is shown in Figure 4.2.



  .. figure:: images/fig4-02.png
     :align: center
     :figwidth: 100%

     Figure 4.2: Using AtomEye functionality (if installed on your system) for 3D visualization of the initial and refined PDF structures: example of Ni structure.

================================
Advanced usage and special needs
================================

The PDFgui is designed to accommodate most common modeling situations. However,
it does not encapsulate all the capabilities available within the modeling engine, such as
calculation of differential PDFs, handling atoms with special scattering properties, etc.

Advanced usage of PDFfit2 engine to resolve any such special modeling need that user
may have is available through usage of Python scripts in the expert command line mode,
similar to that featured in the PDFFIT program. Handling these situations requires de-tailed knowledge of the PDFfit2 syntax based on Python, which is beyond the scope of
this user guide and will be described elsewhere. Refer to the `PDFfit2 API <https://www.diffpy.org/doc/pdffit2>`_ and the `diffpy-users group <https://groups.google.com/d/forum/diffpy-users>`_ for help with PDFfit2 scripting.
