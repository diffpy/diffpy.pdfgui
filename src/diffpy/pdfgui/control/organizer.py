#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Jiwu Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

from diffpy.pdfgui.control.pdfcomponent import PDFComponent
from diffpy.pdfgui.control.fitdataset import FitDataSet
from diffpy.pdfgui.control.fitstructure import FitStructure
from diffpy.pdfgui.control.calculation import Calculation
from diffpy.pdfgui.control.controlerrors import ControlTypeError

class Organizer(PDFComponent):
    """Base class for Fitting. It holds separate lists of datasets,
    strucs and calculations

    datasets:     dataset list
    strucs:       structure list
    calcs:        calculation list
    """

    def __init__(self, name):
        """initialize

        name -- component name
        """
        from diffpy.pdfgui.control.pdflist import PDFList
        PDFComponent.__init__(self, name)

        self.datasets = PDFList()
        self.strucs = PDFList()
        self.calcs = PDFList()

        # self.metadata is created but not pickled only for the purpose
        # of plotting. It holds common metadata from all its datasets
        self.metadata = {}

        # controlCenter is the reference to global PDFGuiControl object
        from diffpy.pdfgui.control.pdfguicontrol import pdfguicontrol
        self.controlCenter = pdfguicontrol()

    def __findList(self, id):
        if isinstance(id, FitDataSet):
            return self.datasets
        elif isinstance(id, FitStructure):
            return self.strucs
        elif isinstance(id, Calculation):
            return self.calcs
        else:
            emsg = "Unknown type object '%s'" % id.name
            raise ControlTypeError(emsg)

    def add(self, id, position=None):
        """add structure/dataset/calculation

        id       -- reference to structure/dataset/calculation
        position -- position to insert, by default the last one
        """
        objList = self.__findList(id)
        if position is None:
            position = len(objList)
        objList.insert(position, id)

        # successfully added, set the object owner
        id.owner = self

    def remove(self, id):
        """remove structure/dataset/calculation

        id -- reference to structure/dataset/calculation
        """
        objList = self.__findList(id)
        objList.remove(id)
        return id

    def rename(self, id, newname):
        """rename structure/dataset/calculation

        id -- reference to structure/dataset/calculation
        newname -- new name to be given
        """
        objList = self.__findList(id)
        objList.rename(id.name, newname)

    def index(self, id):
        """find the position of item in the list

        id -- id of object
        return : object position
        """
        objList = self.__findList(id)
        return objList.index(id.name)

    def hasStructures(self):
        """Check to see if there are structures."""
        return len(self.strucs) > 0

    def getStructure(self, pos):
        """get structure by position

        pos -- the position of structure in the list
        """
        # The function can only be called by gui code. So don't catch IndexError
        # Any IndexError is a program bug thus should be propagated as is.
        return self.strucs[pos]

    def hasDataSets(self):
        """Check to see if there are datasets."""
        return len(self.datasets) > 0

    def getDataSet(self, pos):
        """get dataset by position

        pos -- the position of dataset in the list
        """
        # The function can only be called by gui code. So don't catch IndexError
        # Any IndexError is a program bug thus should be propagated as is.
        return self.datasets[pos]

    def hasCalculations(self):
        """Check to see if there are calculations."""
        return len(self.calcs) > 0

    def getCalculation(self, pos):
        """get calculation by position

        pos -- the position of calculation in the list
        """
        # The function can only be called by gui code. So don't catch IndexError
        # Any IndexError is a program bug thus should be propagated as is.
        return self.calcs[pos]

    def load(self, z, subpath):
        """load data from a zipped project file

        z -- zipped project file
        subpath -- path to its own storage within project file

        returns a tree of internal hierachy
        """
        # subpath = projName/myName/
        from diffpy.pdfgui.utils import unquote_plain
        subs = subpath.split('/')
        rootDict = z.fileTree[subs[0]][subs[1]]
        if 'structure' in rootDict:
            for strucName in rootDict['structure'].keys():
                struc = FitStructure(unquote_plain(strucName))
                struc.load(z, subpath + 'structure/' + strucName + '/')
                self.add(struc)

        if 'dataset' in rootDict:
            for datasetName in rootDict['dataset'].keys():
                dataset = FitDataSet(unquote_plain(datasetName))
                dataset.load(z, subpath + 'dataset/' + datasetName + '/')
                self.add(dataset)

        if 'calculation' in rootDict:
            for calcName in rootDict['calculation'].keys():
                calc = Calculation(unquote_plain(calcName))
                calc.load(z, subpath + 'calculation/' + calcName + '/')
                self.add(calc)

        self.__forward_spdiameter()

        return self.organization()

    def save(self, z, subpath):
        """save data from a zipped project file

        z -- zipped project file
        subpath -- path to its own storage within project file
        """
        # strucs and datasets
        from diffpy.pdfgui.utils import quote_plain
        for struc in self.strucs:
            struc.save(z, subpath + 'structure/' + quote_plain(struc.name) + '/')
        for dataset in self.datasets:
            dataset.save(z, subpath + 'dataset/' + quote_plain(dataset.name) + '/')
        for calc in self.calcs:
            calc.save(z, subpath + 'calculation/' + quote_plain(calc.name) + '/')
        return

    def copy(self, other = None):
        """copy self to other. if other is None, create an instance

        other -- ref to other object
        returns reference to copied object
        """
        if other is None:
            other = Organizer(self.name)

        for dataset in self.datasets:
            other.add(dataset.copy())
        for struc in self.strucs:
            other.add(struc.copy())
        for calc in self.calcs:
            other.add(calc.copy())
        return other

    def organization(self):
        """get internal organization

        returns a tree of internal hierachy
        """
        org = [None]*4
        org [0] = self
        org [1] = []
        for dataset in self.datasets:
            org[1].append((dataset.name, dataset))
        org [2] = []
        for struc in self.strucs:
            org[2].append((struc.name, struc))
        org [3] = []
        for calc in self.calcs:
            org[3].append((calc.name, calc))

        return org


    def __forward_spdiameter(self):
        """Copy spdiameter value loaded from fit or calculation to phase.

        This method takes care of loading old PDFgui projects where
        spdiameter belonged to FitDataSet or Calculation classes.
        It should be called only from the Organizer.load method.
        """
        # Jump out if any of structures has spdiameter set
        for stru in self.strucs:
            if stru.getvar('spdiameter'):   return
        # Search datasets for spdiameter and its constraints
        spd_assigned = lambda ds : bool(ds.spdiameter)
        spd_constrained = lambda ds : 'spdiameter' in ds.constraints
        # Figure out the value and constraint for spdiameter.
        # The highest priority is for a dataset with constrained spdiameter,
        # then for dataset with assigned spdiameter and finally from
        # a calculation.
        spd_val = spd_cns = None
        constrained_datas = list(filter(spd_constrained, self.datasets))
        assigned_datas = list(filter(spd_assigned, self.datasets))
        assigned_calcs = list(filter(spd_assigned, self.calcs))
        if constrained_datas:
            spd_val = constrained_datas[0].spdiameter
            spd_cns = constrained_datas[0].constraints['spdiameter']
        elif assigned_datas:
            spd_val = assigned_datas[0].spdiameter
        elif assigned_calcs:
            spd_val = assigned_calcs[0].spdiameter
        # assign spd_val to all structures that don't have it set
        for stru in self.strucs:
            if spd_val and not stru.getvar('spdiameter'):
                stru.setvar('spdiameter', spd_val)
            if spd_cns:
                stru.constraints.setdefault('spdiameter', spd_cns)
        # finally remove any spdiameter constraints from all datasets
        for ds in self.datasets:
            ds.constraints.pop('spdiameter', None)
        return


# End of class Organizer

# simple test code
if __name__ == "__main__":
    Organizer('name')

# End of file
