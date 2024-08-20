.. _quick_start:

Tutorial
########

Please, have your co-workers or students try it out and let us know if you
have any comments.  We want to make it really easy for the new users to get
started with PDFgui.

=======================================
Lesson 1: Creating simple fit of Ni PDF
=======================================

Input files:

* :download:`Ni-xray.gr <../tutorial/Ni-xray.gr>` - experimental X-ray PDF data
* :download:`Ni.stru <../tutorial/Ni.stru>` - Ni f.c.c. structure in PDFfit format

Procedure:

1. Open a terminal and type ``pdfgui`` to start the program.

2. Create a new Fit:
    1. Select "FITTING" in the left-most vertical tab.
    2. Click right mouse button in the left panel and choose "New Fit" in the pop-up menu.

3. Load structure model:
    1. Place the cursor of the mouse onto the title of the Fit, click the right button and choose "Insert Phase" in the pop-up menu.
    2. Click the "Open" button and load the `Ni.stru` file.

   The right panel has 3 tabs for the initial configuration, constraints panel for expressing structure properties as functions of tunable parameters, and Results panel for refined structure.

4. Load experimental PDF data:
    1. Select the title of "Fit 1", click the right button and choose "Insert Data Set" in the pop-up menu.
    2. Load the `Ni-xray.gr` file.

   Again, the right panel shows 3 tabs for properties of this dataset.

5. Define what is refined:
    1. Click on the `Ni-xray.gr` data and select the "Constraints" tab.
    2. Type ``@1`` into "Scale Factor" edit box.
    3. Select the `Ni.stru` phase and its "Constraints" tab.
    4. Fill "a", "b", "c" boxes with ``@5``.

   A refined variable can be expressed as a math expression:
   ``f(@n1, @n2, @n3, ...)`` where
   ``@n1`` stands for fitted parameter and
   ``n1, n2, ...`` are arbitrary positive integers.
   This allows simple linking of related variables - for example, since
   cell lengths a, b, c are all expressed as ``@5``, the refined structure will remain cubic.

6. Start the refinement:
    1. Select "Fit 1" in the left panel.  The parameters panel shows a list of used parameters and their initial values.
    2. Click the "gear" icon on the toolbar and watch the fit progress in the terminal window.

7. Plot the results:
    1. Select "PLOTTING" in the left-most vertical tab.
    2. Select the `Ni-xray.gr` dataset.
    3. Select "r" as the X plotting variable.
    4. Hold down shift and select "Gcalc" and "Gtrunc" as the Y plotting variables.
    5. Click "Plot" button.

   A new window pops up with plots.  You can try out the buttons in the toolbar below.

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
