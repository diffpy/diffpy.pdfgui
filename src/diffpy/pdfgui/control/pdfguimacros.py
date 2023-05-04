#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Methods for macros used in pdfgui."""

from __future__ import print_function

import os
import copy

from diffpy.pdfgui.control.controlerrors import ControlValueError
from diffpy.pdfgui.control.fitdataset import FitDataSet

def makeRSeries(control, fit, maxfirst = None, maxlast = None, maxstep = None,
        minfirst = None, minlast = None, minstep = None):
    """Make an series of fits with an increasing r-range.

    The new fits are appended to the end of any current fits in the control.

    control     --  The control object that will contain the fits
    fit         --  The prototype fit
    maxfirst    --  The first value of the maximum of the fit range
    maxlast     --  The last value of the maximum of the fit range
    maxstep     --  The step size of the maximum of the fit range
    minfirst    --  The first value of the minimum of the fit range
    minlast     --  The last value of the minimum of the fit range
    minstep     --  The step size of the minimum of the fit range

    returns a list of the new fit organization objects
    """
    # Check to see if the input values are correct.

    # MIN-MIN: FIRST < LAST
    if minfirst is not None and minlast is not None\
            and not minfirst < minlast:
        message = "The first value of the minimum (%.2f)\
                 \nmust be less than the last value of the\
                 \nminimum (%.2f)" % (minfirst, minlast)
        raise ControlValueError(message)

    # MAX-MAX: FIRST < LAST
    if maxfirst is not None and maxlast is not None\
            and not maxfirst < maxlast:
        message = "The first value of the maximum (%.2f)\
                 \nmust be less than the last value of the\
                 \nmaximum (%.2f)" % (maxfirst, maxlast)
        raise ControlValueError(message)

    # MAX > MIN: FIRST-FIRST
    if maxfirst is not None and minfirst is not None\
            and not maxfirst > minfirst:
        message = "The first value of the fit maximum (%.2f)\
                 \nmust be greater than first value of the fit\
                 \nminimum (%.2f)." % (maxfirst, minfirst)
        raise ControlValueError(message)

    # MAX > MIN: LAST-LAST
    if maxlast is not None and minlast is not None\
            and not maxlast > minlast:
        message = "The last value of the fit maximum (%.2f)\
                 \nmust be greater than last value of the fit\
                 \nminimum (%.2f)." % (maxlast, minlast)
        raise ControlValueError(message)

    # STEP > 0
    message = "Step size (%.2f) must be greater than 0."
    if maxstep is not None and not maxstep > 0:
        raise ControlValueError(message % maxstep)
    if minstep is not None and not minstep > 0:
        raise ControlValueError(message % minstep)

    # Check to see that either max or min is fully specified
    maxlist = [maxfirst, maxlast]
    minlist = [minfirst, minlast]
    if maxlist.count(None) == 1 or minlist.count(None) == 1:
        raise ControlValueError("First and last values are partially specified")
    if maxstep is None and minstep is None:
        raise ControlValueError("Either minstep or maxstep must be specified.")

    maxlist = []
    minlist = []
    if maxfirst is not None:
        if maxstep is None: maxstep = minstep
        maxrange = int((maxlast-maxfirst)/(1.0*maxstep)+1)
        maxlist = [maxfirst + i*maxstep for i in range(maxrange)]
    if minfirst is not None:
        if minstep is None: minstep = maxstep
        minrange = int((minlast-minfirst)/(1.0*minstep)+1)
        minlist = [minfirst + i*minstep for i in range(minrange)]

    # Resize the lists to the length of the shortest
    serieslen = min(len(maxlist), len(minlist))
    if serieslen != 0:
        maxlist = maxlist[:serieslen]
        minlist = minlist[:serieslen]
    else:
        serieslen =  max(len(maxlist), len(minlist))

    basename = fit.name
    fits = []

    newname = ''
    lastname = ''
    fitcopy = control.copy(fit)
    # Duplicate the original fit and change the appropriate parameters.
    for i in range(serieslen):
        lastname = newname

        # Loop over datasets
        for ds in fitcopy.datasets:

            if minlist:
                fitrmin = minlist[i]
            else:
                fitrmin = ds.fitrmin
            if maxlist:
                fitrmax = maxlist[i]
            else:
                fitrmax = ds.fitrmax

            # Check to see that the values are in bounds and sensical
            if fitrmin < ds.rmin or fitrmin >= ds.rmax:
                message = "Fit minimum (%.2f) is outside the data range\
                           \n[%.2f, %.2f].\
                           \nAdjust the range of the series."\
                           % (fitrmin, ds.rmin, ds.rmax)
                raise ControlValueError(message)
            if fitrmax <= ds.rmin or fitrmax > ds.rmax:
                message = "Fit maximum (%.2f) is outside the data range\
                           \n[%.2f, %.2f].\
                           \nAdjust the range of the series."\
                           % (fitrmax, ds.rmin, ds.rmax)
                raise ControlValueError(message)
            if fitrmin >= fitrmax:
                message = "Fit minimum (%.2f) is greater than the\
                           \nmaximum (%.2f).\
                           \nIncrease maxstep or reduce minstep." % (fitrmin, fitrmax)
                raise ControlValueError(message)


            # Set the values if all is well
            if minlist:
                ds.fitrmin = fitrmin
            if maxlist:
                ds.fitrmax = fitrmax

        # Set the parameters to the previous fit's name, if one exists.
        if lastname:
            parval = "=%s" % lastname
            for par in fitcopy.parameters.values():
                par.setInitial(parval)

        # Now paste the copy into the control.
        newname = "%s-(%.2f,%.2f)" % (basename, fitrmin, fitrmax)
        o = control.paste(fitcopy, new_name = newname)
        fits.append(o)

    return [f.organization() for f in fits]


# Temperature Series
def makeTemperatureSeries(control, fit, paths, temperatures):
    """Make a temperature series.

    control         --  pdguicontrol instance
    fit             --  The template fit
    paths           --  list of path names of new datasets
    temperatures    --  list of temperatures corresponding to the datasets

    returns a list of the new fit organization objects
    """

    if len(fit.datasets) != 1:
        message = "Can't apply macro to fits with multiple datasets."
        raise ControlValueError(message)

    fits = []
    # holds all of the other information about the dataset
    fitbasename = fit.name
    fitnewname = fit.name
    fitlastname = fit.name
    dataset = fit.datasets[0]
    for i in range(len(paths)):
        filename = paths[i]
        fitlastname = fitnewname

        fitcopy = control.copy(fit)

        # Get rid of the old dataset
        temp = fitcopy.datasets[0]
        fitcopy.remove(temp)

        # Configure the new dataset
        dsname = os.path.basename(filename)
        newdataset = FitDataSet(dsname)
        newdataset.readObs(filename)

        newdataset.qdamp = dataset.qdamp
        newdataset.qbroad = dataset.qbroad
        newdataset.dscale = dataset.dscale
        newdataset.fitrmin = dataset.fitrmin
        newdataset.fitrmax = dataset.fitrmax
        rstep = dataset.fitrstep
        st = dataset.getFitSamplingType()
        newdataset.setFitSamplingType(st, rstep)
        doping = dataset.metadata.get("doping")
        if doping is None: doping = 0.0
        newdataset.metadata["doping"] = doping
        newdataset.constraints = copy.deepcopy(dataset.constraints)

        # Set the chosen temperature
        newdataset.metadata["temperature"] = temperatures[i]

        # Add the dataset to the fitcopy
        fitcopy.add(newdataset, None)

        # Set the parameters to the previous fit's name, if one exists.
        if fitlastname:
            parval = "=%s" % fitlastname
            for par in fitcopy.parameters.values():
                par.setInitial(parval)

        # Now paste the copy into the control.
        fitnewname = "%s-T%i=%g" % (fitbasename, i + 1, temperatures[i])
        o = control.paste(fitcopy, new_name = fitnewname)
        fits.append(o)

    return [f.organization() for f in fits]

# Doping Series
def makeDopingSeries(control, fit, base, dopant, paths, doping):
    """Make a temperature series.

    control         --  pdguicontrol instance
    fit             --  The template fit
    base            --  Name of the base element
    dopant          --  Name of the dopant element
    paths           --  list of path names of new datasets
    doping          --  list of doping values corresponding to the datasets

    returns a list of the new fit organization objects
    """
    from diffpy.pdffit2 import is_element

    # Make sure that base and dopant are elements
    base = base.title()
    dopant = dopant.title()
    if not is_element(base):
        raise ControlValueError("'%s' is not an element!"%base)
    if not is_element(dopant):
        raise ControlValueError("'%s' is not an element!"%dopant)

    # Make sure that base and dopant are in the structure file(s)
    hasBase = False
    hasDopant = False
    for S in fit.strucs:
        for atom in S:
            if atom.element == base:
                hasBase = True
            if atom.element == dopant:
                hasDopant = True
        if hasBase and hasDopant: break

    if not hasBase:
        message = "The template structure does not contain the base atom."
        raise ControlValueError(message)

    if not hasDopant:
        message = "The template structure does not contain the dopant atom."
        raise ControlValueError(message)

    # Make sure we're only replacing a single dataset
    if len(fit.datasets) != 1:
        message = "Can't apply macro to fits with multiple datasets."
        raise ControlValueError(message)


    fits = []
    # holds all of the other information about the dataset
    fitbasename = fit.name
    fitnewname = fit.name
    fitlastname = fit.name
    dataset = fit.datasets[0]
    for i in range(len(paths)):
        filename = paths[i]
        fitlastname = fitnewname

        fitcopy = control.copy(fit)

        # Get rid of the old dataset
        temp = fitcopy.datasets[0]
        fitcopy.remove(temp)

        # Configure the new dataset
        dsname = os.path.basename(filename)
        newdataset = FitDataSet(dsname)
        newdataset.readObs(filename)

        newdataset.qdamp = dataset.qdamp
        newdataset.qbroad = dataset.qbroad
        newdataset.dscale = dataset.dscale
        newdataset.fitrmin = dataset.fitrmin
        newdataset.fitrmax = dataset.fitrmax
        rstep = dataset.fitrstep
        st = dataset.getFitSamplingType()
        newdataset.setFitSamplingType(st, rstep)
        temperature = dataset.metadata.get("temperature")
        if temperature is None: temperature = 300.0
        newdataset.metadata["temperature"] = temperature
        newdataset.constraints = copy.deepcopy(dataset.constraints)

        # Set the chosen temperature
        newdataset.metadata["doping"] = doping[i]

        # Add the dataset to the fitcopy
        fitcopy.add(newdataset, None)

        # Update the doping information in the structures
        for S in fitcopy.strucs:
            for A in S:
                if A.element == dopant:
                    A.occupancy = doping[i]
                if A.element == base:
                    A.occupancy = 1-doping[i]


        # Set the parameters to the previous fit's name, if one exists.
        if fitlastname:
            parval = "=%s" % fitlastname
            for par in fitcopy.parameters.values():
                par.setInitial(parval)

        # Now paste the copy into the control.
        fitnewname = "%s-%1.4f" % (fitbasename, doping[i])
        o = control.paste(fitcopy, new_name = fitnewname)
        fits.append(o)

    return [f.organization() for f in fits]

if __name__ == "__main__":
    from diffpy.pdfgui.control.pdfguicontrol import PDFGuiControl
    control = PDFGuiControl()
    control.load("../../tests/testdata/ni.ddp")
    fit = control.fits[0]
    olist = makeRSeries(control, fit, 5, 20, 5)
    print('\n'.join(f[0].name for f in olist))

# End of file
