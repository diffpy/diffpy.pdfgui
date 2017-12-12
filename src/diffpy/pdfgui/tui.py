#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Text user interface - utilities for extracting data from project files.
"""


class LoadProject:
    """Load and access data in pdfgui project file.

    Protected instance data:

    _project    -- instance of PDFGuiControl with loaded project file.
    """

    # public methods

    def __init__(self, filename=None):
        """Initialize LoadProject object, by reading existing project file.

        filename -- path to PDFgui project file.
        """
        from diffpy.pdfgui.control.pdfguicontrol import PDFGuiControl
        self._project = PDFGuiControl()
        # business
        if filename is not None:
            self.load(filename)
        return


    def load(self, filename):
        """Load a project.

        filename -- path to PDFgui project file.

        No return value.
        """
        self._project.load(filename)
        return


    def save(self, filename):
        """Save the project.

        filename -- path where to write the PDFgui project.

        No return value.
        """
        self._project.save(filename)
        return


    def getFits(self):
        """Get all fits defined in the project file.

        Return list of Fitting objects.
        """
        rv = self._project.fits[:]
        return rv


    def getDataSets(self, fits=None):
        """Return a list of all datasets contained in specified fits.

        fits -- optional list of Fitting objects that own datasets.
                When not specified, get datasets from all fits defined
                in the project.

        Return list of FitDataSet objects.
        """
        if fits is None:
            fitlist = self.getFits()
        else:
            fitlist = fits
        rv = sum([fit.datasets for fit in fitlist], [])
        return rv


    def getCalculations(self, fits=None):
        """Return list of all calculations contained in specified fits.

        fits -- optional list of Fitting objects that own datasets.
                When not specified, get datasets from all fits defined
                in the project.

        Return list of Calculation objects.
        """
        if fits is None:
            fitlist = self.getFits()
        else:
            fitlist = fits
        rv = sum([fit.calcs for fit in fitlist], [])
        return rv


    def getPhases(self, fits=None):
        """Collect all phases contained in specified fits.

        fits -- optional list of Fitting objects that own datasets.
                When not specified, get phases from all fits defined
                in the project.

        Return list of FitStructure objects.
        """
        if fits is None:
            fitlist = self.getFits()
        else:
            fitlist = fits
        rv = sum([fit.strucs for fit in fitlist], [])
        return rv


    def getTemperatures(self, datasets=None):
        """Extract temperatures from a list of datasets.

        datasets -- optional list of FitDataSet objects.  When not
                    specified, temperatures are extracted from all
                    datasets in the project.

        Return list of floating point values.  The list may contain
        None-s for datasets with undefined temperature.
        """
        if datasets is None:
            dslist = self.getDataSets()
        else:
            dslist = datasets
        temperatures = [ds.metadata.get('temperature') for ds in dslist]
        return temperatures


    def getDopings(self, datasets=None):
        """Extract doping values from a list of datasets.

        datasets -- optional list of FitDataSet objects.  When not
                    specified, doping values are extracted from all
                    datasets in the project.

        Return list of floating point values.  The list may contain
        None-s for datasets with undefined doping.
        """
        if datasets is None:
            dslist = self.getDataSets()
        else:
            dslist = datasets
        dopings = [ds.metadata.get('doping') for ds in dslist]
        return dopings


# End of class LoadProject
