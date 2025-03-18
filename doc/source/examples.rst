.. _examples:

Examples
########

===================
Sequential fitting
===================

---------
r series
---------

In certain modeling situations the user could benefit from fitting a data set through a series of refinements that differ one from another by the corresponding fitting ranges. An example of this when one wants to study the details of the local- to average-structure crossover in a complex material. PDFgui has a pre-written macro that automates the setup of this type of refinement.


1. Create a fit as in :ref:`lesson1`.

2. Select the fit from the fit tree. From the “Fits” menu, select Macros, and choose “r-Series” option. The Current Action panel will display following setting requirements

3. type "5" for the first upper limit, "20" for the last upper limit, and the step of "5" Angstroms. Leave the second row blank.

4. click “OK” in the current action panel and 4 new fits with desired incremental limits are geberated below the original fit.

    .. figure:: images/fig3-05.png
       :align: center
       :figwidth: 100%

       Figure 2.1: Appearance of the setup panel for specifying an incremental r-series fit conditions.


   The first row deals with the increment setup of the upper r of the refinements. User should specify the first and the last fit maximum r-value, and corresponding step (increment), all in units of Angstroms.

   In the second row information is needed to specify the lower r refinement limit. Again, the user sets the first and the last value, and step. This allows for a box car of either fixed or variable width to be defined. If the second row is left blank, the corresponding refinement series will be with incremental maximum r only, and fixed lower limit.

5. Select all four of them and execute the refinement. Once the sequence is done, you can review the results using the plot control.



.. _temperature-series:
------------------
temperature series
------------------

Frequently, one must handle a large number of data sets originating from a single sample collected at various temperatures. One of the common modeling schemes in such cases is to perform sequential fitting of such data series, which is known to yield well behaved modeling parameters.

Input files:

- :download:`Temperature data series <manual_resources/Temperature data series.zip>` containing:

    1. a temperature series of data collected on LaMnO3 at various temperatures from 300 K to 1150 K.
    2. a template project named ``lmo-template.dpp``.

LaMnO3 exhibits Jahn-Teller (JT) order-disorder phase transition just above 700 K, where the long range orbital order is lost at high temperature, but the local JT distortion survives. The formal space group does not change at this transition.

The data collected at NPDF instrument at LANSCE at Los Alamos National Laboratory. The project consists of a fit called lmo-pbnm , which will serve as a template and which contains *Pbnm* phase of LaMnO3 and a 300 K data set. The fit refinement is set up to cover 1.7-19.5 Angstroms range, and all the parameter values are set to their converged values for this temperature. The fit setup uses isotropic ADPs for all atomic sites.



1. open ``lmo-template.dpp`` use "Open Project" selection from "File" menu.
2. Select Macros from the “Fit” menu on the menu bar, and choose “Temperature Series”. The current action panel will reflect the selection.
3. Click on “Add” button. Using “Shift” and mouse-select operation you should select all the data sets mentioned in the above list, except the 300 K one, as this is already in the template fit, and then press “Open”.


  .. figure:: images/fig3-06.png
     :align: center
     :figwidth: 100%

     Figure 2.2: Setting up a T-series sequential refinement for LaMnO3. Ordering by temperature will ensure that the fits are linked correctly.

4. Order the data by temperature. The data can be ordered by temperature by clicking the “Temperature” header.

   Since the files contain meta-data, the GUI is going to pick up temperature information from the files. User should verify that the information is correct.

5. Ensure that the template fit is selected on the fit tree. Click on the “OK” button. This will generate a sequence of linked fits in the fit tree in the order of the temperature increase. Each fit is linked to the previous, except for the template fit for the 300 K data

6. Highlight all the fits in the fit tree which can be done by selecting a fit and hitting “Ctrl”+“Shift”+“A” .

7. start the sequential refinement by clicking |gear|.

8. On the plot control choose the temperature for x axis, and select the Uiso of O2 (for example atom 20) for the y axis. Clicking “Plot” will display the plot of Uiso(20) vs T.


  .. figure:: images/fig3-07.png
     :align: center
     :figwidth: 100%


     Figure 2.3: Displaying the refinement results as a function of external parameter: T-series refinement of LaMnO3, example of isotropic ADP of oxygen atom on general position in *Pbnm* setting. Notable are the offsets just above 700 K (Jahn-Teller transition), and at around 1000 K when sample converts from orthorhombic to rhombohedral symmetry.


Despite quite high temperatures, an onset of the static offset above the transition temperature is clearly marked by this parameter, as apparent in Figure 3.7. Curious user could repeat the same T-series refinement restricting the refinement range upper limit to say 5-6 Angstroms and observe the outcome. The refinement sequence execution should be very quick in this case


-----------------------------------
doping series
-----------------------------------

Fitting a series of PDF data that correspond to a set of samples with related chemistry, such as various doping series, represents another important sequential modeling aspect that is supported in PDFgui.


Input files:

- :download:`Doping data series <manual_resources/Doping data series.zip>` containing:

    1. series of Ca-doped LaMnO3 samples with various Ca content data from 0 to 0.28.
    2. a template project named ``lcmo-template.dpp``.


The data are collected on LaMnO3 at GEM instrument at ISIS, UK. The project consists of a fit called lcmo-pbnm, which will serve as a template and which contains *Pbnm* phase of LaMnO3 and a 10 K data set, x000t010q35.gr.

The difference here with respect to the template used in the previous example is that Ca sites are introduced in the structure, but are assigned zero occupancy. However, existence of the
Ca dopant species in the structure of the template is essential for the macro to operate. Also,
upper limit used in Fourier transform for obtaining this set of data is 35 inverse Angstroms,
in contrast to 32 inverse Angstroms in previous example.

1. open ``lcmo-template.dpp`` use "Open Project" selection from "File" menu.
2. Select Macros from the “Fit” menu on the menu bar, and choose “Doing series”. The current action panel will reflect the selection.


  .. figure:: images/fig3-08.png
     :align: center
     :figwidth: 100%

     Figure 2.4: After loading of the Ca-doping data series of LaMnO3 system, proper doping assignment needs to be carried out, as the doping levels introspected from the file names in this example incorrectly reflect the scientific situation. Note that dopant atom has to be present in the template seed used to generate the linked sequence of fits.


3. Click on “Add” button. Using “Shift” and mouse-select operation you should select all the data sets mentioned in the above list, and then press “Open” button.


3. Specify the base element and dopant. Verify the doping information and fix them by clicking on the corresponding values and simply typing in the correct values.

   It should be noted at this point that the data files do not contain any relevant meta-data in the file headers. the GUI fill the fields by picking up doping information from the file names. These values should be checked manually.

4. Order the data by clicking the header.

5. Ensure that the template fit is selected on the fit tree. Click on the “OK” button. This will generate a sequence of linked fits in the fit tree in the order of the Ca content increase.

6. Highlight all the fits in the fit tree which can be done by selecting a fit and hitting “Ctrl”+“Shift”+“A” .

After the convergence is achieved for all the fits in the fit tree, the results can be displayed
graphically such that various converged fit parameters are plotted versus Ca content.



  .. figure:: images/fig3-09.png
     :align: center
     :figwidth: 100%

     Figure 2.5: Sequence of refined parameters, such as lattice constants, can be plotted vs doping using PDFgui plotting facilities. Figure features lattice parameter *b* in *Pbnm* space group setting for series of Ca-doped LaMnO3 samples for doping concentrations between 0 and 0.28 at 10 K temperature.




=================================================
Advanced post-processing of sequential refinement
=================================================

While PDFgui allows to collate data from a series of sequential refinements, there are many data query options that are not possible or very tedious with a GUI. A particularly tedious
task would be to extract bond lengths for every temperature refined in a large series. In fact, the GUI just does not seem to be suitable interface and things are much easier
and more flexible to accomplish with Python scripts.

As a first example, let us assume that a converged sequential refinement from :ref:`temperature-series` , has been saved under the same name as *lmotemplate.ddp*. The following Python script extracts temperatures and refined values of the lattice parameter c::

    # python script
    from diffpy.pdfgui import tui
    # import the tui library
    prj = tui.LoadProject('lmo-template.ddp') # read PDFgui project file
    temperatures = prj.getTemperatures()
    # list of temperature values
    phases = prj.getPhases()
    # list of phase objects
    tcount = len(temperatures)
    # number of temperature points
    for i in range(tcount):
    Ti = temperatures[i]
    # get the refined lattice parameter c
    ci = phases[i].r


Save the example above to a file, say “lmo refined c.py” and run it as::

    python lmo_refined_c.py

Note that the script cannot load the unmodified *lmo-template.ddp* file, because it does not have any refinement results.

The tutorial directory contains an advanced script :download:`tui mno_bond_lengths.py <manual_resources/tui_mno_bond_lengths.py>`, which
extracts the shortest Mn-O bond lengths from the same PDFgui project. Please, see the
comments in the script for detailed explanation.

To learn more about the tui module and about the objects and functions that it returns, please see the API documentation for  `diffpy.pdfgui <http://docs.danse.us/diffraction/diffpy.pdfgui/>`_ .


Feel free to ask at the  `diffpy-users <https://groups.google.com/d/forum/diffpy-users>`_   group if you need help with data extracting scripts.



======================
Nanoparticle structure
======================

Determining the structure of a nanoparticle is notoriously difficult. Diffraction experiments
on nanoparticle samples yield broad diffraction patterns that are hard to analyze using
conventional crystallographic approaches. The PDF analysis of nanoparticles is becoming
increasingly common.


The PDF signal gets damped at higher distances due to the diminished number
of pairs in the nanoparticle structure that contribute to those distances. For certain simpler
cases when nanoparticles can be assumed to have spherical shape, characteristic parameters
such as nanoparticle diameter can be obtained.

PDFgui is capable of modeling the effect of the finite nanoparticle size using a spherical
shape factor. Relevant PDF parameter is ``spdiameter`` which is the diameter of the nanoparticle. This parameter is highly correlated with various other parameters one would like to
refine, such as ``anisotropic ADPs``, ``scale factors``, ``correlated motion parameters`` and so on.
The refinement procedure is therefore rather delicate and the solutions are not as robust as
we are used to in cases of crystalline materials.

To illustrate the program capabilities we present a case of CdSe nanoparticle approx-
imately 3nm in size.

Input files:

- :download:`Doping data series <manual_resources/Nanoparticle structure.zip>` containing:

  1. two PDF data collected from the bulk and naoparticle material.
  2. a project named ``CdSe-nano.ddp``
  3. a structure model named ``CdSe-wurtzite.stru``


This project contains two fits: the first one is a bulk CdSe reference, and the other pertains to the CdSe nanoparticle. For consistency the PDFs of both bulk and nano samples were obtained using Qmax of 14 inverse Angstroms, although the bulk material PDF could have been processed using a higher value.
Synchrotron x-ray radiation was used to obtain the
data at 300 K, based on an experiment carried out at 6-ID-D at the Advanced Photon
Source at Argonne National Laboratory.


The structure used for both data sets is wurtzite,
space group P63mc. From calibrations on Ni standard Qdamp value of 0.0486 was obtained
and is used here.


1. Refine the parameter on the bulk references.

   The fit is carried out over a ``Fit Range`` from 1.7 to 19.8 Angstroms, using 7 parameters: lattice parameters ``a`` and ``c`` (``@1`` and ``@2`` respectively), selenium ``z`` fractional coordinate (``@11``), isotropic ADPs for Cd and Se (``@21`` and ``@23`` respectively), the data ``Scale Factor`` (``@100``), and finally correlated motion related quadratic term coefficient ``delta2`` (``@200``).

   We note that while the fit is reasonable, the values of the isotropic ADPs are enlarged. The fit can be further improved if anisotropic ADPs are introduced, although the z-direction related components will remain enlarged due to the stacking disorder present in the structure. The referent value of 5.69 for ``delta2`` will be used as a starting value for the nanoparticle fit.


2. Refine the parameter on the nanoparticle.

   we will use the same starting values for all the parameters, except for ``delta2`` and the nanoparticle diameter, ``spdiameter``. The former is set to 5.69, and the later to 25 Angstroms.


   In other cases an approximate value of the spherical nanoparticle size is usually known, and it is the best to start from a reasonably good guess. Refining the nanoparticle data reveals nanoparticle diameter of approximately 30 Angstroms, as further illustrated in Figure 3.10. Enlarged values of isotropic ADPs are again observed, and the fit is reasonably good.


  .. figure:: images/fig3-10.png
     :align: center
     :figwidth: 100%

     Figure 2.6: Fitting the structure of a nanoparticle: 3nm CdSe nanoparticle example.


Further improvements can be obtained by introducing anisotropic ADPs, where again values related to the z-direction will remain abnormally large most probably due to the stacking related disorder.A detailed description of this system and successful PDF modeling can be found in this publication: `Quantitative size-dependent structure and strain determination of CdSe nanoparticles using atomic pair distribution function analysis <https://link.aps.org/doi/10.1103/PhysRevB.76.115413>`_.


In general, a successful fitting scenario depends on particular details of a structural prob- lem one is determined to solve. The problem of determining the structure of a nanoparticle remains difficult. PDFgui is not intended to necessarily provide the solution, it is rather a helpful tool in the process of determining new details and exploring the space of possible solution candidates, yielding success in some instances.

.. |gear| image:: /images/gear-icon.png
.. |stop| image:: /images/stop-icon.png
