#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Chris Farrow, Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

# generated by wxGlade 0.9.3 on Fri Jul 19 16:05:04 2019

import re

import wx
import wx.grid

from diffpy.pdfgui.control.constraint import Constraint
from diffpy.pdfgui.control.controlerrors import ControlValueError
from diffpy.pdfgui.gui import phasepanelutils, tooltips
from diffpy.pdfgui.gui.pdfpanel import PDFPanel
from diffpy.pdfgui.gui.sgconstraindialog import SGConstrainDialog
from diffpy.pdfgui.gui.wxextensions.autowidthlabelsgrid import AutoWidthLabelsGrid
from diffpy.pdfgui.gui.wxextensions.textctrlutils import textCtrlAsGridCell
from diffpy.utils.wx import gridutils


class PhaseConstraintsPanel(wx.Panel, PDFPanel):
    def __init__(self, *args, **kwds):
        PDFPanel.__init__(self)
        # begin wxGlade: PhaseConstraintsPanel.__init__
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)

        sizerMain = wx.BoxSizer(wx.VERTICAL)

        sizerPanelName = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizerMain.Add(sizerPanelName, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.labelPanelName = wx.StaticText(self, wx.ID_ANY, "Phase Constraints")
        self.labelPanelName.SetFont(
            wx.Font(
                18,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                0,
                "",
            )
        )
        sizerPanelName.Add(self.labelPanelName, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)

        sizerLatticeParameters = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizerMain.Add(sizerLatticeParameters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        grid_sizer_3 = wx.FlexGridSizer(2, 6, 0, 0)
        sizerLatticeParameters.Add(grid_sizer_3, 1, wx.EXPAND, 0)

        self.labelA = wx.StaticText(self, wx.ID_ANY, "a")
        grid_sizer_3.Add(self.labelA, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlA = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_3.Add(self.textCtrlA, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelB = wx.StaticText(self, wx.ID_ANY, "b")
        grid_sizer_3.Add(self.labelB, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlB = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_3.Add(self.textCtrlB, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelC = wx.StaticText(self, wx.ID_ANY, "c")
        grid_sizer_3.Add(self.labelC, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlC = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_3.Add(self.textCtrlC, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelAlpha = wx.StaticText(self, wx.ID_ANY, "alpha")
        grid_sizer_3.Add(self.labelAlpha, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlAlpha = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_3.Add(self.textCtrlAlpha, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelBeta = wx.StaticText(self, wx.ID_ANY, "beta")
        grid_sizer_3.Add(self.labelBeta, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlBeta = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_3.Add(self.textCtrlBeta, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelGamma = wx.StaticText(self, wx.ID_ANY, "gamma")
        grid_sizer_3.Add(self.labelGamma, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlGamma = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_3.Add(self.textCtrlGamma, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        sizerAdditionalParameters = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizerMain.Add(sizerAdditionalParameters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        grid_sizer_4 = wx.FlexGridSizer(3, 6, 0, 0)
        sizerAdditionalParameters.Add(grid_sizer_4, 1, wx.EXPAND, 0)

        self.labelScaleFactor = wx.StaticText(self, wx.ID_ANY, "Scale Factor")
        grid_sizer_4.Add(
            self.labelScaleFactor,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL,
            5,
        )

        self.textCtrlScaleFactor = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_4.Add(self.textCtrlScaleFactor, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        grid_sizer_4.Add((20, 10), 0, 0, 0)

        self.labelDelta1 = wx.StaticText(self, wx.ID_ANY, "delta1")
        grid_sizer_4.Add(self.labelDelta1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlDelta1 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_4.Add(self.textCtrlDelta1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelDelta2 = wx.StaticText(self, wx.ID_ANY, "delta2")
        grid_sizer_4.Add(self.labelDelta2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlDelta2 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_4.Add(self.textCtrlDelta2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelSpdiameter = wx.StaticText(self, wx.ID_ANY, "spdiameter")
        grid_sizer_4.Add(
            self.labelSpdiameter,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL,
            5,
        )

        self.textCtrlSpdiameter = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_4.Add(self.textCtrlSpdiameter, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelSratio = wx.StaticText(self, wx.ID_ANY, "sratio")
        grid_sizer_4.Add(self.labelSratio, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlSratio = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        grid_sizer_4.Add(self.textCtrlSratio, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelRcut = wx.StaticText(self, wx.ID_ANY, "rcut")
        grid_sizer_4.Add(self.labelRcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlRcut = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_READONLY)
        grid_sizer_4.Add(self.textCtrlRcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.labelStepcut = wx.StaticText(self, wx.ID_ANY, "stepcut")
        grid_sizer_4.Add(self.labelStepcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.textCtrlStepcut = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_READONLY)
        grid_sizer_4.Add(self.textCtrlStepcut, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        sizerAtoms = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL)
        sizerMain.Add(sizerAtoms, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizerAtoms.Add(sizer_1, 0, wx.EXPAND, 0)

        self.labelIncludedPairs = wx.StaticText(self, wx.ID_ANY, "Included Pairs")
        sizer_1.Add(self.labelIncludedPairs, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.textCtrlIncludedPairs = wx.TextCtrl(self, wx.ID_ANY, "all-all", style=wx.TE_READONLY)
        self.textCtrlIncludedPairs.SetMinSize((240, 25))
        sizer_1.Add(self.textCtrlIncludedPairs, 0, wx.ALL, 5)

        self.gridAtoms = AutoWidthLabelsGrid(self, wx.ID_ANY, size=(1, 1))
        self.gridAtoms.CreateGrid(0, 11)
        self.gridAtoms.EnableDragRowSize(0)
        self.gridAtoms.SetColLabelValue(0, "elem")
        self.gridAtoms.SetColLabelValue(1, "x")
        self.gridAtoms.SetColLabelValue(2, "y")
        self.gridAtoms.SetColLabelValue(3, "z")
        self.gridAtoms.SetColLabelValue(4, "u11")
        self.gridAtoms.SetColLabelValue(5, "u22")
        self.gridAtoms.SetColLabelValue(6, "u33")
        self.gridAtoms.SetColLabelValue(7, "u12")
        self.gridAtoms.SetColLabelValue(8, "u13")
        self.gridAtoms.SetColLabelValue(9, "u23")
        self.gridAtoms.SetColLabelValue(10, "occ")
        sizerAtoms.Add(self.gridAtoms, 1, wx.EXPAND, 0)

        self.SetSizer(sizerMain)
        sizerMain.Fit(self)

        self.Layout()

        self.Bind(wx.grid.EVT_GRID_CMD_CELL_CHANGED, self.onCellChange, self.gridAtoms)
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_RIGHT_CLICK, self.onCellRightClick, self.gridAtoms)
        self.Bind(wx.grid.EVT_GRID_CMD_EDITOR_SHOWN, self.onEditorShown, self.gridAtoms)
        self.Bind(
            wx.grid.EVT_GRID_CMD_LABEL_RIGHT_CLICK,
            self.onLabelRightClick,
            self.gridAtoms,
        )
        # end wxGlade
        self.__customProperties()

    # ########################################################################
    # Misc Methods

    def __customProperties(self):
        """Custom properties for the panel."""
        self.structure = None
        self.constraints = {}
        self.results = None
        self._textctrls = [
            "textCtrlA",
            "textCtrlB",
            "textCtrlC",
            "textCtrlAlpha",
            "textCtrlBeta",
            "textCtrlGamma",
            "textCtrlScaleFactor",
            "textCtrlDelta1",
            "textCtrlDelta2",
            "textCtrlSratio",
            "textCtrlSpdiameter",
        ]
        self._row = 0
        self._col = 0
        self._focusedText = None
        self._selectedCells = []
        # bind onSetFocus onKillFocus events to text controls
        for widget in self._textctrls:
            self.__dict__[widget].Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
            self.__dict__[widget].Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
            self.__dict__[widget].Bind(wx.EVT_KEY_DOWN, self.onTextCtrlKey)

        # set up grid
        self.lAtomConstraints = [
            "x",
            "y",
            "z",
            "u11",
            "u22",
            "u33",
            "u12",
            "u13",
            "u23",
            "occ",
        ]
        # pdffit internal naming
        self.lConstraints = [
            "lat(1)",
            "lat(2)",
            "lat(3)",
            "lat(4)",
            "lat(5)",
            "lat(6)",
            "pscale",
            "delta1",
            "delta2",
            "sratio",
            "spdiameter",
        ]
        textCtrlIds = [getattr(self, n).GetId() for n in self._textctrls]
        self._id2varname = dict(zip(textCtrlIds, self.lConstraints))

        # Define tooltips.
        self.setToolTips(tooltips.phasepanel)

        # NOTE: GridCellAttr is reference counted.
        # Each call of SetX(attr) decreases its reference count.
        # We need to call attr.IncRef before each SetX(attr)
        # https://github.com/wxWidgets/Phoenix/issues/627#issuecomment-354219493

        # set 'elem' abd 'name' columns to read-only
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly(True)
        attr.IncRef()
        self.gridAtoms.SetColAttr(0, attr)
        attr.IncRef()
        self.gridAtoms.SetColAttr(11, attr)
        # drop local reference to `attr` as it was constructed here.
        attr.DecRef()

        # catch key events and apply them to the grid
        self.Bind(wx.EVT_KEY_DOWN, self.onKey)

        # Hide some stuff
        self.labelRcut.Hide()
        self.textCtrlRcut.Hide()
        self.labelStepcut.Hide()
        self.textCtrlStepcut.Hide()
        return

    # Create the onTextCtrlKey event handler from textCtrlAsGridCell from
    # wxextensions.textctrlutils
    onTextCtrlKey = textCtrlAsGridCell

    def _cache(self):
        """Cache the current structure and constraints for future
        comparison."""
        pass

    def refresh(self):
        """Refresh wigets on the panel."""
        if self.structure is None:
            raise ValueError("structure is not defined.")

        self.refreshTextCtrls()

        # # update the grid ###
        natoms = len(self.structure)
        nrows = self.gridAtoms.GetNumberRows()
        self.gridAtoms.BeginBatch()
        # make sure grid has correct number of rows
        if natoms > nrows:
            self.gridAtoms.InsertRows(numRows=natoms - nrows)
        elif natoms < nrows:
            self.gridAtoms.DeleteRows(numRows=nrows - natoms)

        # start with clean grid
        self.gridAtoms.ClearGrid()

        # fill the first 'elem' column with element symbols
        for row, atom in zip(range(natoms), self.structure):
            self.gridAtoms.SetCellValue(row, 0, atom.element)

        # update constraints
        bareAtomVarColumn = dict(zip(self.lAtomConstraints, range(1, 1 + len(self.lAtomConstraints))))
        avpat = re.compile(r"(\w+)\((\d+)\)$")
        for var, con in self.constraints.items():
            m = avpat.match(var)
            if not m:
                continue
            barevar = m.group(1)
            if barevar not in bareAtomVarColumn:
                continue
            column = bareAtomVarColumn[barevar]
            row = int(m.group(2)) - 1
            if not 0 <= row < natoms:
                emsg = "Invalid variable index for %r" % var
                raise ControlValueError(emsg)
            self.gridAtoms.SetCellValue(row, column, con.formula)
            barevar = re.sub(r"\(\d+\)$", "", var)
            if barevar not in bareAtomVarColumn:
                continue

        self.gridAtoms.AutosizeLabels()
        self.gridAtoms.AutoSizeColumns()
        self.gridAtoms.EndBatch()

        self.gridAtoms.AdjustScrollbars()
        self.gridAtoms.ForceRefresh()
        return

    def refreshTextCtrls(self):
        """Refreshes the TextCtrls."""

        for widget, var in zip(self._textctrls, self.lConstraints):
            wobj = getattr(self, widget)
            if var in self.constraints:
                s = self.constraints[var].formula
            else:
                s = ""
            wobj.SetValue(s)

        pairs = self.structure.getSelectedPairs()
        self.textCtrlIncludedPairs.SetValue(pairs)
        return

    def applyTextCtrlChange(self, id, value):
        """Update a structure according to a change in a TextCtrl.

        id      --  textctrl id
        value   --  new value
        """
        self.mainFrame.needsSave()
        var = self._id2varname[id]
        formula = value.strip()
        if formula != "":
            self.constraints[var] = Constraint(formula)
            return self.constraints[var].formula
        else:
            self.constraints.pop(var, None)
            return ""

    def applyCellChange(self, i, j, value):
        """Update an atom according to a change in a cell.

        i       --  cell position
        j       --  cell position
        value   --  new value

        returns the new value stored in the data object, or None if value is
        somehow invalid.
        """
        self.mainFrame.needsSave()
        key = self.lAtomConstraints[j - 1] + "({})".format(i + 1)
        formula = value.strip()
        if formula != "":
            self.constraints[key] = Constraint(formula)
            return self.constraints[key].formula
        else:
            self.constraints.pop(key, None)
            return ""
        return

    # ########################################################################
    # Event Handlers

    # TextCtrl Events
    def onSetFocus(self, event):
        """Saves a TextCtrl value, to be compared in onKillFocuse later."""
        self._focusedText = event.GetEventObject().GetValue()
        event.Skip()
        return

    def onKillFocus(self, event):
        """Check value of TextCtrl and update structure if necessary."""
        event.Skip()
        if not self.mainFrame:
            return
        textctrl = event.GetEventObject()
        value = textctrl.GetValue()
        if value != self._focusedText:
            self.applyTextCtrlChange(textctrl.GetId(), value)
            self.refreshTextCtrls()
            self.mainFrame.needsSave()
        self._focusedText = None
        return

    # Grid Events
    def onLabelRightClick(self, event):  # wxGlade: PhaseConstraintsPanel.<event_handler>
        """Bring up right-click menu."""
        if self.structure is not None:
            dx = dy = 0
            if event.GetRow() == -1:
                dy = self.gridAtoms.GetGridCornerLabelWindow().GetSize().y
            if event.GetCol() == -1:
                dx = self.gridAtoms.GetGridCornerLabelWindow().GetSize().x

            # do not popup menu if the whole grid is set to read only
            if len(self.structure) == 0:
                self.popupMenu(
                    self.gridAtoms,
                    event.GetPosition().x - dx,
                    event.GetPosition().y - dy,
                )
        event.Skip()
        return

    def onCellRightClick(self, event):  # wxGlade: PhaseConstraintsPanel.<event_handler>
        """Bring up right-click menu."""
        self._row = event.GetRow()
        self._col = event.GetCol()

        # If the right-clicked node is not part of a group, then make sure that
        # it is the only selected cell.
        append = False
        r = self._row
        c = self._col
        if self.gridAtoms.IsInSelection(r, c):
            append = True
        self.gridAtoms.SelectBlock(r, c, r, c, append)

        self.popupMenu(self.gridAtoms, event.GetPosition().x, event.GetPosition().y)
        event.Skip()
        return

    def onEditorShown(self, event):  # wxGlade: PhaseConstraintsPanel.<event_handler>
        """Capture the focused text when the grid editor is shown."""
        i = event.GetRow()
        j = event.GetCol()
        self._focusedText = self.gridAtoms.GetCellValue(i, j)
        self._selectedCells = gridutils.getSelectedCells(self.gridAtoms)
        return

    def onCellChange(self, event):  # wxGlade: PhaseConstraintsPanel.<event_handler>
        """Update focused and selected text when a cell changes."""
        # NOTE: be careful with refresh(). It calls Grid.AutoSizeColumns, which
        # creates a EVT_GRID_CMD_CELL_CHANGED event, which causes a recursion
        # loop.
        i = event.GetRow()
        j = event.GetCol()

        value = self.gridAtoms.GetCellValue(i, j)
        while (i, j) in self._selectedCells:
            self._selectedCells.remove((i, j))
        # We need the edited cell to be at the front of the list
        self._selectedCells.insert(0, (i, j))
        self.fillCells(value)
        self._focusedText = None
        return

    def fillCells(self, value):
        """Fill cells with a given value.

        value       --  string value to place into cells

        This uses the member variable _selectedCells, a list of (i,j) tuples for
        the selected cells.
        """
        for i, j in self._selectedCells:
            if not self.gridAtoms.IsReadOnly(i, j):
                # Get the last valid text from the cell. For the cell that triggered
                # this method, that is the _focusedText, for other cells it is the
                # value returned by GetCellValue
                oldvalue = self._focusedText
                if oldvalue is None:
                    oldvalue = self.gridAtoms.GetCellValue(i, j)
                self._focusedText = None
                newvalue = self.applyCellChange(i, j, value)
                # print i, j, value, oldvalue, newvalue
                if newvalue is None:
                    # Get out of here. If the value is invalid, it won't be valid
                    # for any cells.
                    newvalue = oldvalue
                    self.gridAtoms.SetCellValue(i, j, str(newvalue))
                    break
                else:
                    self.gridAtoms.SetCellValue(i, j, str(newvalue))

        gridutils.quickResizeColumns(self.gridAtoms, self._selectedCells)
        return

    def onKey(self, event):
        """Catch key events in the panel."""
        key = event.GetKeyCode()

        # Select All - Ctrl+A
        if event.ControlDown() and key == 65:
            rows = self.gridAtoms.GetNumberRows()
            cols = self.gridAtoms.GetNumberCols()
            self.gridAtoms.SelectBlock(0, 0, rows, cols)

        # context menu key
        elif key == wx.WXK_MENU:
            self.popupMenu(self.gridAtoms, event.GetPosition().x, event.GetPosition().y)

        # Vim-like search for atom selection
        elif key == 47:
            self.onPopupSelect(event)

        # Delete
        elif key == 127:
            self._selectedCells = gridutils.getSelectedCells(self.gridAtoms)
            self.fillCells("")
            self.mainFrame.needsSave()

        # Can't get these to work. Maybe later.
        #  Copy - Ctrl+C / Ctrl+Insert
        # if event.ControlDown() and (key == 67 or key == wx.WXK_INSERT):
        #    if phasepanelutils.canCopySelectedCells(self):
        #        phasepanelutils.copySelectedCells(self)

        #  Paste - Ctrl+V / Shift+Insert
        # if (event.ControlDown() and key == 86) or\
        #   (event.ShiftDown() and key == wx.WXK_INSERT):
        #       if phasepanelutils.canPasteIntoCells(self):
        #           phasepanelutils.pasteIntoCells(self)

        else:
            event.Skip()
        return

    # ########################################################################
    # Grid popup menu and handlers

    def popupMenu(self, window, x, y):
        """Creates the popup menu.

        window  --  window, where to popup a menu
        x       --  x coordinate
        y       --  y coordinate
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "spaceGroupID"):
            self.spaceGroupID = wx.NewIdRef()
            self.selectID = wx.NewIdRef()
            self.copyID = wx.NewIdRef()
            self.pasteID = wx.NewIdRef()

            self.Bind(wx.EVT_MENU, self.onPopupSpaceGroup, id=self.spaceGroupID)
            self.Bind(wx.EVT_MENU, self.onPopupSelect, id=self.selectID)
            self.Bind(wx.EVT_MENU, self.onPopupCopy, id=self.copyID)
            self.Bind(wx.EVT_MENU, self.onPopupPaste, id=self.pasteID)

        # make a menu
        menu = wx.Menu()

        # add some other items
        menu.Append(self.spaceGroupID, "&Symmetry constraints...")
        menu.AppendSeparator()
        menu.Append(self.selectID, "Select &atoms...")
        menu.Append(self.copyID, "&Copy")
        menu.Append(self.pasteID, "&Paste")

        # Disable some items if there are no atoms selected
        indices = gridutils.getSelectionRows(self.gridAtoms)
        if not indices:
            menu.Enable(self.spaceGroupID, False)

        # Check for copy/paste
        if not phasepanelutils.canCopySelectedCells(self):
            menu.Enable(self.copyID, False)
        if not phasepanelutils.canPasteIntoCells(self):
            menu.Enable(self.pasteID, False)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        window.PopupMenu(menu, wx.Point(x, y))
        menu.Destroy()
        return

    def onPopupSpaceGroup(self, event):
        """Create a supercell with the supercell dialog."""
        if self.structure is not None:

            indices = gridutils.getSelectionRows(self.gridAtoms)
            dlg = SGConstrainDialog(self)
            dlg.mainFrame = self.mainFrame
            dlg.indices = indices
            dlg.setStructure(self.structure)
            dlg.updateWidgets()
            if dlg.ShowModal() == wx.ID_OK:
                spcgrp = dlg.getSpaceGroup()
                offset = dlg.getOffset()
                posflag = dlg.getPosFlag()
                tempflag = dlg.getTempFlag()
                self.structure.applySymmetryConstraints(spcgrp, indices, posflag, tempflag, offset)
                self.refresh()
            dlg.Destroy()
            self.mainFrame.needsSave()
        return

    def onPopupSelect(self, event):
        """Limit cell selection to specified atom selection string."""
        phasepanelutils.showSelectAtomsDialog(self)
        return

    def onPopupCopy(self, event):
        """Copy selected cells."""
        phasepanelutils.copySelectedCells(self)
        return

    def onPopupPaste(self, event):
        """Paste previously copied cells."""
        phasepanelutils.pasteIntoCells(self)
        return


# end of class PhaseConstraintsPanel
