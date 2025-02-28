#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
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

# generated by wxGlade 0.9.3 on Fri Jul 19 15:59:31 2019

import wx

from diffpy.pdfgui.gui.fittree import incrementName
from diffpy.pdfgui.gui.pdfpanel import PDFPanel


class AddPhasePanel(wx.Panel, PDFPanel):
    """Panel for adding a phase.

    Several items must know to this panel so it knows where to try to insert the
    phase.
    entrypoint  --  The FitTree item id from which we entered this panel.
                    dataset or a calculation item.
    entryfit    --  The parent of the new dataset.
    entryphase  --  The phase below which to place the new phase. This can be
                    None, which means the new phase is appended to the end of
                    the phase section of the entryfit.
    """

    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        # begin wxGlade: AddPhasePanel.__init__
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_4, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)

        self.labelOpenPhase = wx.StaticText(self, wx.ID_ANY, "Load a structure from file.")
        self.labelOpenPhase.SetFont(
            wx.Font(
                12,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                "Sans",
            )
        )
        sizer_4.Add(self.labelOpenPhase, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.buttonOpen = wx.Button(self, wx.ID_OPEN, "Open")
        sizer_4.Add(self.buttonOpen, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.static_line_5 = wx.StaticLine(self, wx.ID_ANY)
        sizer_1.Add(self.static_line_5, 0, wx.EXPAND, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_5, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)

        self.labelCreatePhase = wx.StaticText(self, wx.ID_ANY, "Create a structure from scratch.")
        self.labelCreatePhase.SetFont(
            wx.Font(
                12,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                "Sans",
            )
        )
        sizer_5.Add(self.labelCreatePhase, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.buttonNew = wx.Button(self, wx.ID_NEW, "New")
        sizer_5.Add(self.buttonNew, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.static_line_6 = wx.StaticLine(self, wx.ID_ANY)
        sizer_1.Add(self.static_line_6, 0, wx.BOTTOM | wx.EXPAND, 10)

        self.buttonCancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        sizer_1.Add(self.buttonCancel, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        sizer_1.Add((450, 10), 0, 0, 0)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.onOpen, self.buttonOpen)
        self.Bind(wx.EVT_BUTTON, self.onNew, self.buttonNew)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.buttonCancel)
        # end wxGlade
        self.__customProperties()

    # UTILITY FUNCTIONS ####

    def __customProperties(self):
        """Custom Properties go here."""
        self.entrypoint = None  # The entrypoint on the tree
        self.entryfit = None  # The fit in which to insert an item
        self.entryphase = None  # The phase under which to insert an item
        self.fullpath = ""  # The last loaded structure
        return

    def readConfiguration(self):
        """Read the 'PHASE' configuration.

        In the 'PHASE' section of the project ConfigurationParser the
        following is set by this panel.

        'last'      --  The last structure file added to the project. This is
                        stored in the class variable fullpath.
        """
        remember = False
        if self.cP.has_option("PHASE", "remember"):
            remember = self.cP.getboolean("PHASE", "remember")

        if remember:
            if self.cP.has_option("PHASE", "last"):
                self.fullpath = self.cP.get("PHASE", "last")
                import os.path

                if not os.path.exists(self.fullpath):
                    self.fullpath = ""
            else:
                self.fullpath = ""
        return

    def updateConfiguration(self):
        """Update the configuration for the 'DATASET'."""
        if not self.cP.has_section("PHASE"):
            self.cP.add_section("PHASE")
        self.cP.set("PHASE", "last", self.fullpath)
        return

    # EVENT CODE ####

    def onOpen(self, event):  # wxGlade: AddPhasePanel.<event_handler>
        """Add a the new phase to the tree.

        The phase is added as a child of entryfit, right after the
        entryphase, if it exists. If entryphase is None, the new phase
        is appended to the end of the children of entryfit.
        """
        import os.path

        newnode = None
        dir, filename = os.path.split(self.fullpath)
        if not dir:
            dir = self.mainFrame.workpath
        matchstring = "|".join(
            (
                "Structure file",
                "*.cif;*CIF;*.stru;*.STRU;*.pdb;*.PDB;*.xyz;*.XYZ",
                "Crystallographic Information File (*.cif)",
                "*.cif;*.CIF",
                "PDFfit structure files (*.stru)",
                "*.stru;*.STRU",
                "Protein Data Bank files (*.pdb)",
                "*.pdb;*.PDB",
                "Coordinate files (*.xyz)",
                "*.xyz;*.XYZ",
                "All Files",
                "*",
            )
        )
        d = wx.FileDialog(None, "Choose a file", dir, "", matchstring)
        if d.ShowModal() == wx.ID_OK:
            self.fullpath = d.GetPath()
            self.mainFrame.workpath = os.path.dirname(self.fullpath)

            # Update the configuration
            self.updateConfiguration()

            # Add the item to the tree.
            name = os.path.basename(self.fullpath)

            # Check the name and alter it if necessary
            siblings = self.treeCtrlMain.GetChildren(self.entryfit)
            names = [self.treeCtrlMain.GetItemText(i) for i in siblings]
            name = incrementName(name, names)

            newnode = self.treeCtrlMain.AddPhase(
                self.entryfit, name, insertafter=self.entryphase, filename=self.fullpath
            )

            self.mainFrame.setMode("fitting")
            self.treeCtrlMain.SetItemBold(self.entrypoint, False)
            self.treeCtrlMain.UnselectAll()
            self.mainFrame.makeTreeSelection(newnode)
            self.validateStructure(newnode)
        d.Destroy()
        return

    def onNew(self, event):  # wxGlade: AddPhasePanel.<event_handler>
        """Add a new item to be created from scratch."""
        # Set the name of the new phase
        siblings = self.treeCtrlMain.GetChildren(self.entryfit)
        names = [self.treeCtrlMain.GetItemText(i) for i in siblings]
        label = "New Phase"
        label = incrementName(label, names)

        # Create the phase
        newnode = self.treeCtrlMain.AddPhase(self.entryfit, label, insertafter=self.entryphase)

        # Go to the new node
        self.mainFrame.setMode("fitting")
        self.treeCtrlMain.SetItemBold(self.entrypoint, False)
        self.treeCtrlMain.UnselectAll()
        self.mainFrame.makeTreeSelection(newnode)
        self.treeCtrlMain.EditLabel(newnode)
        return

    def onCancel(self, event):  # wxGlade: AddPhasePanel.<event_handler>
        """Cancel this addition.

        Go back to the last panel.
        """
        self.mainFrame.setMode("fitting")
        self.treeCtrlMain.SetItemBold(self.entrypoint, False)
        self.treeCtrlMain.UnselectAll()
        self.mainFrame.makeTreeSelection(self.entrypoint)
        return

    def validateStructure(self, node):
        """Make sure that the structure is valid."""
        from diffpy.pdfgui.control.controlerrors import ControlError

        dataobject = self.treeCtrlMain.GetControlData(node)
        stru = dataobject.initial
        for a in stru:
            nonzero = 0
            for row in a.U:
                nonzero += row.any()
            if not nonzero:
                raise ControlError("Structure has atoms with all zero ADP values.")
        return

    # Methods overloaded from PDFPanel
    def refresh(self):
        """Bold text the entrypoint on the tree.

        This also reads the configuration.
        """
        self.readConfiguration()

        selections = self.treeCtrlMain.GetSelections()
        entrypoint = selections[0]
        entryphase = entrypoint
        entryfit = self.treeCtrlMain.GetFitRoot(entrypoint)

        entrytype = self.treeCtrlMain.GetNodeType(entryphase)
        if entrytype != "phase":
            entryphase = None

        # Prepare the window
        self.entrypoint = entrypoint
        self.entryphase = entryphase
        self.entryfit = entryfit

        # Make the entry point bold.
        self.treeCtrlMain.SetItemBold(self.entrypoint)
        self.treeCtrlMain.UnselectAll()
        return


# end of class AddPhasePanel
