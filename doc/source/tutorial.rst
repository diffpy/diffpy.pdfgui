.. _tutorial:

Tutorial
########

Please, have your co-workers or students try it out and let us know if you
have any comments.  We want to make it really easy for the new users to get
started with PDFgui.

=======================================
Lesson 1: Creating simple fit of Ni PDF
=======================================

Input files:

- :download:`Ni data <manual_resources/Ni data.zip>` containing:
    1. Ni-xray.gr - experimental X-ray PDF data
    2. Ni.stru - Ni f.c.c. structure in PDFfit format

This manual will help you to get started with ``PDFgui``.  We strongly recommend that that you refer to
the book `Atomic pair distribution function analysis: a primer` by Simon J. L. Billinge, Kirsten Jensen
Soham Banerjee, Emil S. Bozin, Benjamin A. Frandsen, Maxwell W. Terban and Robert J. Koch, Oxford:
Oxford University Press, 2024. URL: https://global.oup.com/academic/product/atomicpair-distribution-function-analysis-9780198885801?cc=us&lang=en&
for much more extensive and detailed descriptions of carrying out fits with PDFgui (and the related program diffpy-cmi).

Procedure:

1. Open ``pdfgui``. Instructions for doing this depend on your system, but an example would be
   to open a terminal, activate your pdfgui conda environment, and type ``pdfgui`` at the prompt,
   or to double-click a project file on windows.

2. Create a new Fit:
    1. In the GUI locate the ``Fit Tree`` panel.  In the default layout it is at the top left of the page.
    2. With your mouse on that panel, right-click the mouse and select "New Fit" from the pop-up menu.
    3. By default, your fit will be called ``Fit 1``. To give it a more meaningful name, left
       click the ``Fit 1`` name. It should open an editable box and you can type in a name for your
       fit such as "Fit of Ni structure to Ni data"
    4. Note, an alternative workflow to create a new fit is to find ``New fit`` under the ``Fits`` dropdown menu.

3. Load structure model:
    1. Carefully place your cursor on to the title of the Fit and right-click. Select "Insert Phase" from the pop-up menu.
    2. Click the "Open" button and navigate to and load the ``Ni.stru`` file that you downloaded.  You could select
       valid structure model file, a ``.stru`` or a ``.cif`` file.
    3. Note, an alternative workflow for adding structural models is to select ``New Phase`` from the ``Phases`` dropdown menu.

   If you select the Phase in the ``Fit Tree`` by left clicking on it, you will see in the
   right panel 3 tabs, ``Configure`` ``Constraints``, ``Results``.  Feel free to click one
   these tabs and look inside.  The Configure panel has the initial inputs from the loaded str or cif file,
   The ``Constraints`` panel will hold the constraints we will set up for our fits, it should be empty now,
   and the results tab will contain the results of any fit.

   Note that what you see on the right is "Context Dependent", it depends on what you have selected on the left.
   By selecting a phase on the left, the tabs on the right contain information about that phase, and so on.

4. Load experimental PDF data:
    1. As before, hover over your cursor over the title of your fit and right-click.  This time select
       ``Insert Data Set`` from the pop-up menu.
    2. Navigate to and load the `Ni-xray.gr` file that you downloaded.

   Again, the right panel shows 3 tabs, now for properties of this dataset.

5. Define what is refined:
    1. Click on the `Ni-xray.gr` data and select the "Constraints" tab.
    2. Type ``@1`` into the "Scale Factor" edit box.
    3. Select the `Ni.stru` phase and its "Constraints" tab.
    4. Fill "a", "b", "c" boxes with ``@5``.

   Here we are defining "variables" that will be refined and giving them names
   variable "@1", "@5", etc. and linking them to model parameters by typing them
   in the text-box associated with the parameter.  So by typing ``@1`` in the
   data "Scale-Factor" text box we are saying that we are logically assigning the constraint
   equation ``data.scale_factor = variable("@1")``.

   When we assign the three parameters ``a``, ``b`` and ``c`` to the same variable,
   ``@5``, we are implicitly ensuring that the refinement will respect
   the cubic symmetry of the nickel structure and that ``a = b = c``, because the
   three parameters are assigned to the same variable, so however much ``a``
   is changed in the refinement, ``b`` and ``c`` will be changed by the same amount.
   Note that the variable ensures that changes to ``a``, ``b`` and ``c`` are always
   the same, so we have to also ensure that the initial values of ``a``, ``b`` and ``c``
   are the same as each other to ensure that the structure is cubic and remains so.

   PDFgui allows us to express more complex constraint equations than
   simply assigning a parameter to a variable.
   In general, we can type into be Constraints tab text box any math expression:
   ``f(@n1, @n2, @n3, ...)`` where
   ``@n1`` stands for the fitted parameter, where it is understood that
   ``n1, n2, ...`` are arbitrary positive integers.
   This allows simple linking of related variables.  For example, if we want to allow a
   crystallographic site to contain either Ni or Pt, we don't know how much Ni or Pt is
   on the site, but we want it to be always fully occupied, we could create two lattice
   site entries with the same fractional coordinates, with one assigned Ni as the element and the other
   assigned Pt as the element. Then we could assign the Ni occupancy as ``@100``.  Then
   typing ``1-@100`` into the constraint text box of the Pt occupancy ensures that however
   much the occupancy of the Ni site goes down in a refinement, the occupancy of the Pt on that
   same site goes up by the same amount.  This ensures full occupancy of that site, as long
   as the initial occupancies of the Ni and Pt added up to 1.

6. Start the refinement:
    1. Select the fit to run by left clicking the title of the fit in the ``Fit Tree`` panel.
       The ``Parameters`` panel on the right shows a list of variables that you have defined
       and their initial values.  Each one also has a check-box that allows you to fix them
       (prevent them from varying in the subsequent refinement).  Unchecked boxes mean the variable
       will be refined.
    2. When you are satisfied with the configuration, click the "gear" icon on the toolbar
       and watch the fit progress in the terminal window.

7. Plot the results:
    1. Select the data in the fit (in this case the `Ni-xray.gr` dataset) by left clicking it.
    2. Click the ``plot`` icon in the toolbar.  This is the icon that looks a bit like a PDF
       to the right of the Gear and the red/grey X.

    A new window pops up with the plots. It will show the data in blue, the best-fit model
    curve in red, and offset below, the difference curve in green.  The offset of the difference
    curve appears at a default value of ``-5.0``.  You can make your plot more pretty and meaningful
    by typing a different offset into the ``offset`` text box and hitting ``Plot`` again.

    It is possible to configure the plot in the ``Plot Control`` panel in the GUI.
    In the default layout it will be at the lower-left of the GUI panel.

    1. To plot the fit (as was done above) elect "r" as the X plotting variable.
    2. Hold down shift and select "Gcalc" and "Gtrunc" as the Y plotting variables.
    3. Click the "Plot" button.

    This panel allows more plotting options for advanced cases such as plotting the values
    of parameters refined across multiple fits to extract temperature dependent information.


8. Save your project for later use.

======================================================
Lesson 2: Build structure model using crystal symmetry
======================================================

In the previous example the initial structure was defined by an existing file. However, PDFgui makes it very easy to build a structure model from scratch and constrain it with arbitrary crystal symmetry.

1. Create a blank structure:
    1. Click the FITTING tab.
    2. Repeat steps 1-3a from Lesson 1, but choose the "New" button. Rename "New Phase" to "Ni fcc".

2. Define asymmetric unit:
    1. Right click the header of the empty atoms grid in the "Configure" page.
    2. Insert 1 atom using the popup menu.
    3. Change the elem cell to "Ni".
    4. Select the u11-u33 cells and type "0.004" and press Enter.

3. Expand to all equivalent positions:
    1. Right click the first Ni atom and select "Expand space group". A "Space Group Expansion" dialog should open.
    2. In the dialog, select Fm-3m or just type 225 in the "Space Group" box and hit "OK".

   You should now have four atoms in the atoms grid.

4. Generate symmetry constraints:
    1. Select the "Constraints" tab.
    2. Select all atoms. This can be done by dragging the mouse over the atom names or by clicking on the "elem" header.
    3. Right click in a selected cell and select "Symmetry constraints." A "Space Group Constraints" dialog should open.
    4. "Fm-3m" should already appear in the "Space Group" box. If it does not, select it as you did in step 3 and hit "OK".

   The u11-u33 cells should all read the same value. The "x", "y" and "z" cells should be all empty because Ni atoms are at special positions in Fm-3m. You may try to select lower-symmetry space and check what happens with the constraints. The space group constraints may be mixed by selecting different groups of atoms, for example, when only certain species show lowered symmetry.

5. Continue the fit as in Lesson 1.

=============================
Lesson 3: Multi-stage fitting
=============================

Learn how to string together fits.

1. Create a fit as in Lesson 1.

2. Copy the fit:
    1. Right click on the fit name "Fit 1" in the right panel (the fit tree).
    2. Select "Copy" from the pop-up menu.

3. Paste the fit:
    1. Right click in the empty space between the first fit in the fit tree.
    2. Select "Paste Fit." This will create "Fit 1_copy", a copy of "Fit 1" in the fit tree.

4. Link the fits:
    1. Click on "Fit 1_copy" in the fit tree.
    2. In the "Parameters" panel, select the entire "Initial" column.
    3. Type ``=Fit 1`` and then press Enter. The "Initial" values of the parameters should now read ``=Fit1:n``, where "n" is the index of the parameter.

   This is the linking syntax: ``=name:index``.
   "name" is the name of another fit.
   "index" is the index of a parameter in that fit.
   If you omit "index", it will default to the index of the parameter you are linking from. A linked parameter uses the refined value of the link as its initial value. This is useful when you are running several related fits.

5. Add more fit parameters:
    1. Select the "Constraints" tab of the `Ni.stru` phase below "Fit 1_copy".
    2. Write ``@9`` in the "delta2" box.

6. Run the fit and plot the results:
    1. Run the fit as in Lesson 1.
    2. Plot the fit as in Lesson 1, but this time hold down Control and select the data sets from "Fit 1" and "Fit 1_copy". You can change the "offset" in the plotting window to 0 to place the plots on top of each other.

==========
References
==========

1. :download:`(pdf) <../manual/Proffen-jac-1999.pdf>`,
   Th. Proffen and S. J. L. Billinge, PDFFIT a program for full profile structural refinement of the atomic pair distribution function, J. Appl. Crystallogr. 32, 572-575 (1999)

2. :download:`(pdf) <../manual/Farrow-jpcm-2007.pdf>`,
   C. L. Farrow, P. Juhas, J. W. Liu, D. Bryndin, J. Bloch, Th. Proffen and S. J. L. Billinge, PDFfit2 and PDFgui: Computer programs for studying nanostructure in crystals, J. Phys.: Condens. Matter 19, 335219 (2007)
