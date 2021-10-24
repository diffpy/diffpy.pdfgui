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

"""This module contains the FitTree object designed for use in PDFgui.

Classes:
    FitTree         --  A tree specific to orgainizing data for pdffit

Exceptions:
    FitTreeError    --  Exception for errors with FitTree operations.
"""

import wx
import re
import base64

from diffpy.pdfgui.gui.pdfguiglobals import iconpath
from diffpy.pdfgui.control.fitting import Fitting
from diffpy.pdfgui.control.controlerrors import ControlError
from diffpy.pdfgui.utils import safeCPickleDumps, pickle_loads
from diffpy.pdfgui.gui.wxextensions import wx12

class FitTree(wx12.TreeCtrl):
    """TreeCtrl designed to organize pdffit fits.

    The root of the tree is hidden. Below that there are several levels
    which are diagrammed below.

    _ fit (*)
    |
    |____ phase (5)
    |____ datset (*)
    |____ calculation (*)

    Fits are at the top level. Under fits there are phases, datasets, and
    calculations (in that order).

    It is required that the data for each node is a dictionary. In the 'type'
    entry of this dictionary is the node type (fit, phase, dataset,
    calculation). Fit items also have a 'cdata' entry in their tree item
    dictionary. This is the control center data associated with this node's
    branch.

    Data members:
    control     --  The pdfguicontrol object that interfaces between the tree
                    and the pdffit2 engine. The tree is a mirror of the internal
                    structure of the control.

    """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_MULTIPLE,
            validator=wx.DefaultValidator, name="FitTree"):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

        # Define the control
        # This is set by the mainFrame
        # self.control = pdfguicontrol()

        # Define bitmaps
        datasetbmp = wx.Bitmap(iconpath("datasetitem.png"))
        phasebmp = wx.Bitmap(iconpath("phaseitem.png"))
        fitbmp = wx.Bitmap(iconpath("fititem.png"))
        calcbmp = wx.Bitmap(iconpath("calculationitem.png"))
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fitbmid = il.Add(fitbmp)
        self.dtsbmid = il.Add(datasetbmp)
        self.phabmid = il.Add(phasebmp)
        self.clcbmid = il.Add(calcbmp)
        self.SetImageList(il)
        self.treeImageList = il


        return

    def InitializeTree(self):
        """This initializes the tree by adding a root node."""
        self.root = self.AddRoot("The Root Item")
        self.SetNodeType(self.root, "root")
        # Testing code
        #fit1 = self.AddFit()
        #self.AddPhase(fit1, "Phase 1")
        #self.AddPhase(fit1, "Phase 2")
        #self.AddDataSet(fit1, "Data 1")
        #self.AddCalc(fit1, "Calc 1")
        #self.Expand(fit1)
        return

    def GetTreeItemDict(self, node):
        """Get the data dictionary of the node."""
        return self.GetItemData(node)

    def GetFitRoot(self, node):
        """Return the id of the fit in which the passed node resides."""
        if not node: return
        fitId = node
        nextId = self.GetItemParent(node)
        while nextId != self.root:
            fitId = nextId
            nextId = self.GetItemParent(nextId)
        return fitId

    def GetChildren(self, node):
        """Get the ids of the children of a given node."""
        cookie = 0
        ids = []
        (child, cookie) = self.GetFirstChild(node)
        while child.IsOk():
            ids.append(child)
            (child, cookie) = self.GetNextChild(node, cookie)

        return ids

    def GetSiblings(self, node):
        """Get the ids of the siblings of a given node."""
        parent = self.GetItemParent(node)
        ids = self.GetChildren(parent)
        ids.remove(node)
        return ids

    def GetAllType(self, node):
        """Get the id of each item in the tree of the same type as node."""
        nodetype = self.GetNodeType(node)
        fits = self.GetChildren(self.root)
        if nodetype == 'fit':
            return fits
        else:
            sametype = []
            for fit in fits:
                children = self.GetChildren(fit)
                sametype.extend( [child for child in children if
                    self.GetNodeType(child) == nodetype] )
            return sametype

    def GetPhases(self, node):
        """Get a list of phase in branch.

        node is either the fit-root or a node in the fit-branch of interest.
        """
        nodes = self.GetChildren(self.GetFitRoot(node))
        ids = [id for id in nodes if self.GetNodeType(id) == 'phase']
        return ids

    def GetDataSets(self, node):
        """Get a list of datasets in branch.

        node is either the fit-root or a node in the fit-branch of interest.
        """
        nodes = self.GetChildren(self.GetFitRoot(node))
        ids = [id for id in nodes if self.GetNodeType(id) == 'dataset']
        return ids

    def GetCalculations(self, node):
        """Get a list of calculations in branch.

        node is either the fit-root or a node in the fit-branch of interest.
        """
        nodes = self.GetChildren(self.GetFitRoot(node))
        ids = [id for id in nodes if self.GetNodeType(id) == 'calculation']
        return ids

    def GetNodeType(self, node):
        """Get the node type.

        This is the "type" entry in the data dictionary of the node.
        """
        if not node:
            return None
        datadict = self.GetTreeItemDict(node)
        if datadict is None:
            return None
        return datadict['type']

    def SetNodeType(self, node, tp):
        """Set the node type of a node."""
        if not node: return
        datadict = self.GetTreeItemDict(node)
        if datadict is None:
            datadict = {}
            self.SetItemData(node, datadict)
        datadict['type'] = tp
        return

    def GetBranchName(self, node):
        """Get the name of the branch in which node resides."""
        fp = self.GetFitRoot(node)
        return self.GetItemText(fp)

    def GetLastPhase(self, node):
        """Get the last phase child of the parent node.

        This method is helpful in placing datasets and phases into the fit tree.
        This method depends on the fact that phases are placed before datasets
        in the fit tree.
        """
        siblings = self.GetChildren(node)
        lastphase = None
        for sib in siblings:
            if self.GetNodeType(sib) == "dataset": break
            elif self.GetNodeType(sib) == "calculation": break
            else: lastphase = sib
        return lastphase

    def GetLastDataSet(self, node):
        """Get the last dataset child of the fit node.

        If there is no last dataset node, this may return the last phase node.
        The purpose of getting this node is to know where to place another node,
        so the actual node type is not important.
        """
        siblings = self.GetChildren(node)
        lastdata = None
        for sib in siblings:
            if self.GetNodeType(sib) == "calculation": break
            else: lastdata = sib
        return lastdata

    def GetNumPhases(self, node):
        """Get the number of phases in a branch.

        node    --  A node in the branch, or the root of the branch.
        """
        parent = self.GetFitRoot(node)
        family = self.GetChildren(parent)
        phases = [item for item in family if self.GetNodeType(item) == 'phase']
        return len(phases)

    def GetNumDataSets(self, node):
        """Get the number of datasets in a branch.

        node    --  A node in the branch, or the root of the branch.
        """
        parent = self.GetFitRoot(node)
        family = self.GetChildren(parent)
        phases = [item for item in family if self.GetNodeType(item) == 'dataset']
        return len(phases)

    def GetPositionInSubtree(self, node):
        """Get the index if the node in its subtree.

        For fits the position is absolute within the tree. For phases, datasets,
        and calculations, the location is taken to be in reference to the other
        nodes of its type. This is designed to be compatible with the control
        center.
        """
        parent = self.GetItemParent(node)
        brood = self.GetChildren(parent)
        pos = 0
        for sib in brood:
            if sib == node:
                break
            else: pos += 1
        nodetype = self.GetNodeType(node)
        if nodetype == 'dataset':
            pos -= self.GetNumPhases(node)
        if nodetype == 'calculation':
            pos -= self.GetNumPhases(node) + self.GetNumDataSets(node)
        return pos

    def SetControlData(self, node, data):
        """Set the control center data associated with the node.

        This need only be called for 'fit' nodes.
        This is the "cdata" entry in the data dictionary of the
        node. It holds the object with which the right panel interfaces. For
        example, for a 'phase' node, it contains a Structure object.
        """
        nodetype = self.GetNodeType(node)
        if nodetype != 'fit':
            message = 'Node type %s does not hold its own data' % nodetype
            raise FitTreeError(message)

        self.GetTreeItemDict(node)['cdata'] = data
        return

    def GetControlData(self, node):
        """Get the control center data associated with a node.

        NOTE: The fit-root of a node holds this data. This method makes it
        convenient to retrieve it.
        """
        nodetype = self.GetNodeType(node)
        parent = self.GetFitRoot(node)
        pdata = self.GetTreeItemDict(parent)['cdata']
        if nodetype == 'fit':
            return pdata
        elif nodetype == 'phase':
            pos = self.GetPositionInSubtree(node)
            return pdata.getStructure(pos)
        elif nodetype == 'dataset':
            pos = self.GetPositionInSubtree(node)
            return pdata.getDataSet(pos)
        elif nodetype == 'calculation':
            pos = self.GetPositionInSubtree(node)
            return pdata.getCalculation(pos)
        else:
            message = "Node of type %s does not exist" % nodetype
            raise FitTreeError(message)
        return

    def AddFit(self, fitname = "Fit 1", cdata = None, paste = False):
        """Append a new fit tree to the end of the current fits.

        fitname     --  The name of the fit. This is incremented if it already
                        exists.
        cdata       --  Control data for the node. If cdata is None (default),
                        then the control is asked to create new data.
        paste       --  Whether or not the cdata is being pasted from another
                        node (default False).

        Returns the id of the new node.
        """
        # Name the fit, but check to not duplicate names.
        fits = self.GetChildren(self.root)
        names = [self.GetItemText(f) for f in fits]
        fitname = incrementName(fitname, names)

        newfit = self.AppendItem(self.root, fitname)
        self.SetNodeType(newfit, 'fit')
        self.SetItemImage(newfit, self.fitbmid, wx.TreeItemIcon_Normal)
        pos = self.GetPositionInSubtree(newfit)

        try:
            # Set the node data for the new node
            if cdata is None:
                cdata = self.control.newFitting(fitname, pos)
            elif paste:
                cdata = self.control.paste(cdata, None, fitname, pos)
            self.SetControlData(newfit, cdata)
            return newfit
        except:
            self.Delete(newfit)
            raise
        return

    def AddPhase(self, node, label, insertafter=None, filename=None,
            makedata = True, cdata=None):
        """Add a new blank Phase to the tree as a child of node.

        node        --  The parent 'fit' node.
        label       --  The name of the new node.
        insertafter --  The node after which to insert the new phase. If
                        insertafter is None (default) the new phase is
                        appended to the end of the phases in the subtree of
                        the parent node.
        filename    --  The file from which to load the structure. If this is
                        None (default), a new structure is created.
        makedata    --  Tells whether the control needs to make data for the
                        node (default True).
        cdata       --  Control data for the node. If cdata is None (default),
                        then it is assumed that the node already has data in the
                        control. See ExtendProjectTree and __InsertBranch for
                        examples of how this is used.

        Phases are always placed before DataSets.

        Raises:
            FitTreeError if node is not a "fit" node.
            FitTreeError if insertafter is not a "phase" node.

        Returns the id of the new node.
        """
        # Check to make sure the new phase is a child of a fit or calculation
        nodetype = self.GetNodeType(node)
        if nodetype != "fit":
            message = "Can only add a phase as a child of a fit."
            raise FitTreeError(message)

        if insertafter is not None:
            afttype = self.GetNodeType(insertafter)
            if afttype != "phase":
                insertafter = None

        if insertafter:
            newphase = self.InsertItem(node, insertafter, label)
        else:
            lastphase = self.GetLastPhase(node)
            if lastphase:
                # Put the new phase after the last
                newphase = self.InsertItem(node, lastphase, label)
            else:
                newphase = self.PrependItem(node, label)

        self.SetNodeType(newphase, "phase")
        self.SetItemImage(newphase, self.phabmid, wx.TreeItemIcon_Normal)

        # Set the control data to the new phase
        pdata = self.GetControlData(node)
        pos = self.GetPositionInSubtree(newphase)

        # Try to get/make the node data from the control. If it doesn't work,
        # then delete the new node.
        try:
            if makedata:
                if filename is None:
                    self.control.newStructure(pdata, label, pos)
                else:
                    self.control.loadStructure(pdata, filename, label, pos)

            elif cdata is not None:
                self.control.paste(cdata, pdata, label, pos)
            return newphase
        except:
            self.Delete(newphase)
            raise
        return

    def AddDataSet(self, node, label, insertafter=None, filename=None,
            makedata=True, cdata=None):
        """Add a new DataSet to the tree as a child of fit.

        node        --  The parent node of the dataset. Must be 'fit' type.
        label       --  The label of the new node.
        insertafter --  The node after which to insert the new dataset. If
                        insertafter is None (default) the new dataset is
                        appended to the end of the datasets in the subtree of
                        the parent node.
        filename    --  The name of the file from which to load the data.
        makedata    --  Tells whether the control needs to make data for the
                        node (default True). If True, cdata is ignored.
        cdata       --  Control data for the node. If False cdata is None
                        (default), then it is assumed that the node already has
                        data in the control. See ExtendProjectTree and
                        __InsertBranch for examples of how this is used.

        DataSets are always placed after Phases.

        Raises:
            FitTreeError if node is not a "fit" node.
            FitTreeError if insertafter is not a "dataset" node.

        Returns the id of the new node.
        """
        # Check to make sure the new dataset is a child of a fit
        nodetype = self.GetNodeType(node)
        if nodetype != "fit":
            message = "Can only add a data set as a child of a fit."
            raise FitTreeError(message)

        if insertafter is not None:
            afttype = self.GetNodeType(node)
            if afttype != "dataset":
                insertafter = None

        if insertafter:
            newset = self.InsertItem(node, insertafter, label)
        else:
            lastset = self.GetLastDataSet(node)
            if lastset:
                newset = self.InsertItem(node, lastset, label)
            else:
                newset = self.PrependItem(node, label)

        self.SetNodeType(newset, "dataset")
        self.SetItemImage(newset, self.dtsbmid, wx.TreeItemIcon_Normal)
        # Attach the control center data to the new dataset
        pos = self.GetPositionInSubtree(newset)
        pdata = self.GetControlData(node)

        try:
            if makedata:
                if filename is not None:
                    self.control.loadDataset(pdata, filename, label, pos)
                else:
                    raise FitTreeError("Cannot load a dataset without a name!")
            elif cdata is not None:
                self.control.paste(cdata, pdata, label, pos)
            return newset
        except:
            self.Delete(newset)
            raise
        return

    def AddCalc(self, node, label, insertafter=None, makedata=True, cdata=None):
        """Add a new DataSet to the tree as a child of fit.

        node        --  The parent node of the calculation. Must be 'fit' type.
        label       --  The label of the new node.
        insertafter --  The node after which to insert the new calculation. If
                        insertafter is None (default) the new calculation is
                        appended to the end of the calculation in the subtree of
                        the parent node.
        makedata    --  Tells whether the control needs to make data for the
                        node (default True). If True, cdata is ignored.
        cdata       --  Control data for the node. If False cdata is None
                        (default), then it is assumed that the node already has
                        data in the control. See ExtendProjectTree and
                        __InsertBranch for examples of how this is used.

        Calculations are always placed after datasets.

        Raises:
            FitTreeError if node is not a "fit" node.
            FitTreeError if insertafter is not a "calculation" node.

        Returns the id of the new node.
        """
        # Check to make sure the new calculation is a child of a fit
        nodetype = self.GetNodeType(node)
        if nodetype != "fit":
            message = "Can only add a calculation as a child of a fit."
            raise FitTreeError(message)

        if insertafter is not None:
            afttype = self.GetNodeType(node)
            if afttype != "calculation":
                insertafter = None

        sibs = self.GetCalculations(node)
        names = [self.GetItemText(sb) for sb in sibs]
        label = incrementName(label, names)

        if insertafter:
            newcalc = self.InsertItem(node, insertafter, label)
        else:
            newcalc = self.AppendItem(node, label)

        self.SetNodeType(newcalc, "calculation")
        self.SetItemImage(newcalc, self.clcbmid, wx.TreeItemIcon_Normal)
        # Attach the control center data to the new datacalc
        pos = self.GetPositionInSubtree(newcalc)
        pdata = self.GetControlData(node)

        try:
            if makedata:
                self.control.newCalculation(pdata, label, pos)
            elif cdata is not None:
                self.control.paste(cdata, pdata, label, pos)
            return newcalc
        except:
            self.Delete(newcalc)
            raise
        return

    def CopyBranch(self, startnode):
        """Make a copy of a tree branch.

        The branch is held in the system clipboard so it can be used in another
        instance of the fittree.
        """
        nodetype = self.GetNodeType(startnode)
        cdata = self.control.copy(self.GetControlData(startnode))
        if isinstance(cdata, Fitting):
            cdata = cdata.stripped()
        cdata.type = nodetype
        cdatabytes = safeCPickleDumps(cdata)
        cdatabytes = 'pdfgui_cliboard='.encode() + cdatabytes
        #wxpython only accepts str, use base64 to convert bytes to str
        cdatastring = base64.b64encode(cdatabytes)
        textdata = wx.TextDataObject(cdatastring)
        if not wx.TheClipboard.IsOpened():
            opened = wx.TheClipboard.Open()
            if not opened: raise FitTreeError("Cannot open the clipboard.")
        wx.TheClipboard.SetData(textdata)
        wx.TheClipboard.Close()
        return

    def GetClipboard(self):
        """Get the clipboard data.

        Returns the controldata in the clipboard, or None if the clipboard is
        empty or contains the wrong type of data.
        """
        # Check to see if data is present
        if not wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
            return None

        textdata = wx.TextDataObject()
        if not wx.TheClipboard.IsOpened():
            opened = wx.TheClipboard.Open()
            if not opened: return None
        success = wx.TheClipboard.GetData(textdata)
        wx.TheClipboard.Close()
        if not success: return None
        cdatastring = textdata.GetText()

        cdata = None
        # use base64 to convert str back to bytes
        try:
            cdatabytes = base64.b64decode(cdatastring.encode())

            if cdatabytes[:16] == 'pdfgui_cliboard='.encode():
                cdatabytes = cdatabytes[16:]
                cdata = pickle_loads(cdatabytes)
        except:
            pass
        return cdata

    def PasteBranch(self, entrypoint = None):
        """Paste the branch from the clipboard into tree at the given node.

        A certain type of branch can only be copied to specific places.

        fit         -   A fit can be pasted to anywhere. This does not overwrite
                        an existing node, but simply inserts the fit into the
                        last available slot.
        phase       -   A phase can be pasted from anywhere. If pasted from a
                        fit, it is placed at the end of the phase section of
                        that node. If inserted from a dataset or a calculation,
                        it is placed at the end of the phase section.
        dataset     -   A dataset can be pasted from anywhere. If pasted from a
                        fit, the dataset is appended at the end of the other
                        datasets. If pasted from a dataset, the pasted set is
                        inserted right after that one. If pasted from a phase,
                        it is placed at the beginning of the dataset section. If
                        pasted from a calculation, it is placed at the end of
                        the dataset section.
        calculation -   A calculation can be pasted to anywhere, but it appears
                        at the end of the calculation section of the tree. If
                        pasted from a calculation node, it is inserted after
                        that node.

        Raises:
            FitTreeError if the entrypoint and branch type are incompatible.
        """
        cdata = self.GetClipboard()
        if cdata is None:
            message = "There is no branch to paste!"
            raise FitTreeError(message)

        # Now we have the cdata, we must put it into the tree
        branchtype = cdata.type
        insertafter = None
        prepend = False
        entrytype = None
        if entrypoint:
            entrytype = self.GetNodeType(entrypoint)
        # Check to see what we are trying to paste, and where.

        if branchtype == "fit":
            # Paste after the selected fit containing the selection, or
            # after the last fit if a calculation is selected. If nothing is
            # selected, just paste it!

            entrytype = None
            if entrypoint:
                entrypoint = self.GetFitRoot(entrypoint)
                entrytype = self.GetNodeType(entrypoint)

            if entrytype is None:
                entrypoint = self.root
                insertafter = None
            elif entrytype == "fit":
                insertafter = entrypoint
                entrypoint = self.root
            else: # Just in case
                raise FitTreeError("Cannot paste a fit branch here.")

        if branchtype == "phase":
            # Paste after selected phase, or append to the end of the phase
            # section of a fit.

            if entrytype == "phase":
                # The entry is to be a sibling.
                insertafter = entrypoint
                entrypoint = self.GetItemParent(entrypoint)
            elif entrytype in ("dataset", "calculation"):
                # Paste to the end of the phases, if they exist.
                entrypoint = self.GetItemParent(entrypoint)
                insertafter = self.GetLastPhase(entrypoint)
                if not insertafter:
                    # Put the branch at the beginning of the phases
                    prepend = True
            elif entrytype == "fit":
                # Get the last phase in the phase section, which may not
                # exist.
                insertafter = self.GetLastPhase(entrypoint)
                if not insertafter:
                    # Put the branch at the beginning of the phases
                    prepend = True
            else: # Just in case
                raise FitTreeError("Cannot paste a phase branch here.")

        if branchtype == "dataset":
            # Paste after a selected dataset, or into a selected fit.

            if entrytype == "dataset":
                # The entry is to be a sibling.
                insertafter = entrypoint
                entrypoint = self.GetItemParent(entrypoint)
            elif entrytype == "phase":
                # The entry goes to the end of the phases, which must exist.
                entrypoint = self.GetItemParent(entrypoint)
                insertafter = self.GetLastPhase(entrypoint)
            elif entrytype == "calculation":
                # The entry goes to the end of the datasets.
                entrypoint = self.GetItemParent(entrypoint)
                insertafter = self.GetLastDataSet(entrypoint)
            elif entrytype == "fit":
                insertafter = self.GetLastDataSet(entrypoint)
                # The entrypoint is ok. The branch is appended to the end of
                # the calculations.
                pass
            else:
                raise FitTreeError("Cannot paste a data set branch here.")

        if branchtype == "calculation":
            # Paste after the selected calculation or after the calculations.

            if entrytype == "calculation":
                # The entry is to be a sibling.
                insertafter = entrypoint
                entrypoint = self.GetItemParent(entrypoint)
            elif entrytype in ("phase", "dataset"):
                entrypoint = self.GetItemParent(entrypoint)
                insertafter = self.GetLastDataSet(entrypoint)
            elif entrytype == "fit":
                insertafter = self.GetLastDataSet(entrypoint)
            else: # Just in case
                raise FitTreeError("Cannot paste a calculation branch here.")


        # Now set the name of the item to be inserted.
        label = self.__copyLabel(cdata.name, entrypoint)

        # Now we have a label. We must insert the item into the tree.
        newnode = self.__InsertBranch(cdata, entrypoint, label, insertafter,
                prepend)

        return newnode

    def __copyLabel(self, oldlabel, entrypoint):
        """Make a new label that is appropriate for a new node."""
        # Append "_copy" to the end of the label, unless it already has that.
        # In that case, just add a number to indicate which copy it is.
        siblings = self.GetChildren(entrypoint)
        labels = [self.GetItemText(sb) for sb in siblings]
        match = r"_copy\d*$"
        label = re.sub(match, '', oldlabel)
        label += "_copy"
        label = incrementName(label, labels)
        return label

    def __InsertBranch(self, cdata, entrypoint, label, insertafter = None,
            prepend = False):
        """Instert control data into the tree.

        cdata       --  The control data that goes with the branch
        entrypoint  --  The subbranch (fit root) to paste into
        label       --  The label of the new node
        insertafter --  A node after which to insert. If insertafter is None
                        (default), then the new node will be pasted after the
                        last node of the same type.
        prepend     --  Prepend to the beginning of the node group (default
                        False). insertafter takes prescedent over prepend.

        Returns the newly inserted node.
        """
        if cdata is None:
            message = "There is no branch to paste!"
            raise FitTreeError(message)

        branchtype = cdata.type
        #cdata.name = label
        if branchtype == 'fit':
            cdata.name = label
            newnode = self.ExtendProjectTree([cdata.organization()],
                    clear=False, paste=True)
        elif branchtype == 'phase':
            newnode = self.AddPhase(entrypoint, label, insertafter=insertafter,
                    makedata=False, cdata=cdata)
        elif branchtype == 'dataset':
            newnode = self.AddDataSet(entrypoint, label, insertafter=insertafter,
                    makedata=False, cdata=cdata)
        elif branchtype == 'calculation':
            newnode = self.AddCalc(entrypoint, label, insertafter=insertafter,
                    makedata=False, cdata=cdata)
        else:
            raise FitTreeError("Unrecognized node type: %s" % branchtype)

        return newnode

    def DeleteBranches(self, selections):
        """Remove the subtree starting from the selected node(s)."""
        # Get a list of branch heads
        branchset = [node for node in selections if self.GetNodeType(node) ==\
        "fit"]

        # Get their children
        childset = []
        for node in branchset:
            childset.extend(self.GetChildren(node))

        # Collect all nodes, removing any children of branch nodes.
        nodeset = [node for node in selections if node not in childset]

        for node in nodeset:
            cdata = self.GetControlData(node)
            self.control.remove(cdata)
            self.Delete(node)
        return nodeset

    def SelectAll(self):
        """Select all nodes."""
        self.UnselectAll()
        fits = self.GetChildren(self.root)
        for fit in fits:
            children = self.GetChildren(fit)
            self.SelectItem(fit)
            for child in children:
                self.SelectItem(child)
        return

    def SelectAllType(self, node = None):
        """Select all nodes of same type as passed node.

        node    --  Node whose type to select. If node is None (default), then
                    all fit nodes will be selected.
        """
        self.UnselectAll()
        if node is None:
            # Get the first fit node
            fits = self.GetChildren(self.root)
            if not fits: return
            node = fits[0]
        typelist = self.GetAllType(node)
        for item in typelist:
            self.SelectItem(item)
        return

    def ExtendProjectTree(self, treelist, clear=True, paste=False):
        """Extend the project tree from the treelist.

        treelist    --  A list of control data returned by
                        Oraganizer.organization()
        clear       --  Clear the tree before adding new nodes (default True)
        paste       --  Whether or not the cdata is being pasted from another
                        node (default False).

        The treelist here is of the type returned from pdfguicontrol.load.
        It is a list of fit lists with the following format.
        node[0]     --  fit object
        node[1]     --  list of (name, dataset) tuples
        node[2]     --  list of (name, phase) tuples
        node[3]     --  list of (name, calculation) tuples

        Note that node[1] should be empty if the node is a calculation.

        Returns the last insterted fit or calculation node
        """
        # Clean slate
        if clear:
            self.DeleteAllItems()
            self.InitializeTree()
        roots = []

        # Return if the treelist is empty
        if not treelist: return

        # Build the tree
        for item in treelist:
            broot = item[0]
            name = broot.name
            node = self.AddFit(name, cdata = broot, paste = paste)

            if node is None:
                message = "Cannot insert data. Malformed tree list."
                raise FitTreeError(message)

            roots.append(node)
            # Build the rest of the tree. Note that we don't want to create new
            # data, but we don't pass the cdata since it is already included in
            # the fit root.
            phases = item[2]
            for (name, phase) in phases:
                self.AddPhase(node, name, makedata = False)
            dsets = item[1]
            for (name, set) in dsets:
                self.AddDataSet(node, name, makedata = False)
            calcs = item[3]
            for (name, calc) in calcs:
                self.AddCalc(node, name, makedata = False)

        for item in roots:
            self.Expand(item)
        return node

# End class FitTree


# Exceptions
class FitTreeError(ControlError):
    def __init__(self, *args):
        ControlError.__init__(self, *args)
        return
# End class FitTreeError


# Utility functions
def incrementName(name, namelist, start = 1):
    """Increment the name by assigning the lowest number to the end such
    that the name does not appear in the namelist.
    """
    newname = name
    match = r"\d+$"
    counter = start
    while newname in namelist:
        newname = re.sub(match, '', name)
        counter += 1
        newname = "%s%i" % (newname, counter)
    return newname
