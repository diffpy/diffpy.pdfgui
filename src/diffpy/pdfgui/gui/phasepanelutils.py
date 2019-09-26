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

"""Common methods used in the phase panels."""

import wx
from diffpy.utils.wx import gridutils

# List of row entries taken from the clipboard
clipcells = []

# String describing what atoms should be selected.
selected_atoms = ''

def float2str(x):
    """compact string representation of float"""
    s = "%g" % x
    if s.find('.') == -1 and s.find('e') == -1:
        s = s + ".0"
    return s

def refreshTextCtrls(panel):
    """Refreshes the TextCtrls on the panel.

    This is used by phaseconfigurepanel and phaseresultspanel.

    This method updates the following TextCtrls with with contents of the
    structure member variable of the panel.
    textCtrlA
    textCtrlB
    textCtrlC
    textCtrlAlpha
    textCtrlBeta
    textCtrlGamma
    textCtrlScaleFactor
    textCtrlDelta1
    textCtrlDelta2
    textCtrlSratio
    textCtrlRcut
    textCtrlStepcut
    textCtrlSpdiameter
    """
    if panel.structure is None:
        # clear textcontrols
        panel.textCtrlA.SetValue("")
        panel.textCtrlB.SetValue("")
        panel.textCtrlC.SetValue("")
        panel.textCtrlAlpha.SetValue("")
        panel.textCtrlBeta.SetValue("")
        panel.textCtrlGamma.SetValue("")
        panel.textCtrlScaleFactor.SetValue("")
        panel.textCtrlDelta1.SetValue("")
        panel.textCtrlDelta2.SetValue("")
        panel.textCtrlSratio.SetValue("")
        panel.textCtrlRcut.SetValue("")
        panel.textCtrlStepcut.SetValue("")
        panel.textCtrlSpdiameter.SetValue("")

    else:
        # update panel with values from panel.structure
        # update textctrls
        panel.textCtrlA.SetValue(float2str(panel.structure.lattice.a))
        panel.textCtrlB.SetValue(float2str(panel.structure.lattice.b))
        panel.textCtrlC.SetValue(float2str(panel.structure.lattice.c))
        panel.textCtrlAlpha.SetValue(float2str(panel.structure.lattice.alpha))
        panel.textCtrlBeta.SetValue(float2str(panel.structure.lattice.beta))
        panel.textCtrlGamma.SetValue(float2str(panel.structure.lattice.gamma))
        panel.textCtrlScaleFactor.SetValue(
            float2str(panel.structure.pdffit['scale']))
        panel.textCtrlDelta1.SetValue(
            float2str(panel.structure.pdffit['delta1']))
        panel.textCtrlDelta2.SetValue(
            float2str(panel.structure.pdffit['delta2']))
        panel.textCtrlSratio.SetValue(
            float2str(panel.structure.pdffit['sratio']))
        panel.textCtrlRcut.SetValue(
            float2str(panel.structure.pdffit['rcut']))
        panel.textCtrlStepcut.SetValue(
            float2str(panel.structure.pdffit['stepcut']))
        panel.textCtrlSpdiameter.SetValue(
            float2str(panel.structure.pdffit['spdiameter']))
    return

def refreshGrid(panel):
    """Refreshes grid on the panel.

    This is used by phaseconfigurepanel and phaseresultspanel.

    This method fills the grid with the contents of the structure member
    variable of the panel. It is expected that the grid is named 'gridAtoms'.
    """
    if panel.structure is None:
        # remove all rows from grid
        panel.gridAtoms.BeginBatch()
        if panel.gridAtoms.GetNumberRows() != 0:
            panel.gridAtoms.DeleteRows( numRows = panel.gridAtoms.GetNumberRows() )
        panel.gridAtoms.EndBatch()

    else:
        # update the grid with atoms
        panel.gridAtoms.BeginBatch()

        # set column labels
        panel.gridAtoms.SetColLabelValue(0, "elem")
        panel.gridAtoms.SetColLabelValue(1, "x")
        panel.gridAtoms.SetColLabelValue(2, "y")
        panel.gridAtoms.SetColLabelValue(3, "z")
        panel.gridAtoms.SetColLabelValue(4, "u11")
        panel.gridAtoms.SetColLabelValue(5, "u22")
        panel.gridAtoms.SetColLabelValue(6, "u33")
        panel.gridAtoms.SetColLabelValue(7, "u12")
        panel.gridAtoms.SetColLabelValue(8, "u13")
        panel.gridAtoms.SetColLabelValue(9, "u23")
        panel.gridAtoms.SetColLabelValue(10, "occ")

        # make sure grid has correct number of rows and blank it
        natoms = len(panel.structure)
        nrows = panel.gridAtoms.GetNumberRows()
        if natoms > nrows:
            panel.gridAtoms.InsertRows(numRows = natoms - nrows)
        elif natoms < nrows:
            panel.gridAtoms.DeleteRows(numRows = nrows - natoms)
        panel.gridAtoms.ClearGrid()
        for i, atom in enumerate(panel.structure):
            panel.gridAtoms.SetCellValue(i,0, str(atom.element)) # element
            panel.gridAtoms.SetCellValue(i,1, float2str(atom.xyz[0])) # x
            panel.gridAtoms.SetCellValue(i,2, float2str(atom.xyz[1])) # y
            panel.gridAtoms.SetCellValue(i,3, float2str(atom.xyz[2])) # z
            panel.gridAtoms.SetCellValue(i,4, float2str(atom.U[0,0])) # U(1,1)
            panel.gridAtoms.SetCellValue(i,5, float2str(atom.U[1,1])) # U(2,2)
            panel.gridAtoms.SetCellValue(i,6, float2str(atom.U[2,2])) # U(3,3)
            panel.gridAtoms.SetCellValue(i,7, float2str(atom.U[0,1])) # U(1,2)
            panel.gridAtoms.SetCellValue(i,8, float2str(atom.U[0,2])) # U(1,3)
            panel.gridAtoms.SetCellValue(i,9, float2str(atom.U[1,2])) # U(2,3)
            panel.gridAtoms.SetCellValue(i,10,float2str(atom.occupancy)) # occupancy

    panel.gridAtoms.AutosizeLabels()
    panel.gridAtoms.AutoSizeColumns()
    panel.gridAtoms.EndBatch()

    panel.gridAtoms.AdjustScrollbars()
    return

# Utility functions

def showSelectAtomsDialog(panel):
    """Extend or limit selection to a string atom selection.

    panel    -- instance of PhaseConfigurePanel or PhaseConstraintsPanel

    No return value.
    """
    # do nothing for non-existant or empty structure
    if not panel.structure:  return
    msg = '\n'.join([
        'Specify index, symbol or "all", use "!" to subtract selection.',
        'Examples: "Na", "1:4, 6, 9:10", "all, !Na".',
    ])
    global selected_atoms
    dlg = wx.TextEntryDialog(panel, msg, "Select Atoms", selected_atoms)
    if dlg.ShowModal() == wx.ID_OK:
        s1 = dlg.GetValue().strip()
        rows = panel.structure.getSelectedIndices(s1)
        selected_atoms = s1
        if s1:
            gridutils.limitSelectionToRows(panel.gridAtoms, rows)
    dlg.Destroy()
    return

def canCopySelectedCells(panel):
    """Check to see if we can copy selected cells.

    To be copyable, the cells must exist in a single block or there must be a
    single cell selected. Note that a block that is selected by individual cells
    is considered a collection of individual atoms, not a block. This is default
    wxPython behavior.
    """
    grid = panel.gridAtoms

    topleft = grid.GetSelectionBlockTopLeft()
    individuals = grid.GetSelectedCells()
    numsel = len(topleft) + len(individuals)
    return numsel == 1

def canPasteIntoCells(panel):
    """Check if clipboard contents are formatted for grid insertion.

    This also checks to see if the cell selection is appropriate for pasting.
    """
    grid = panel.gridAtoms

    individuals = grid.GetSelectedCells()
    topleft = grid.GetSelectionBlockTopLeft()
    if len(individuals) + len(topleft) != 1: return False

    # Get the text
    if not wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
        return False

    textdata = wx.TextDataObject()
    if not wx.TheClipboard.IsOpened():
        opened = wx.TheClipboard.Open()
        if not opened: return False
    success = wx.TheClipboard.GetData(textdata)
    wx.TheClipboard.Close()
    if not success: return False
    copytext = textdata.GetText()

    # Remove any trailing newline
    copytext = copytext.rstrip('\n')

    # Make sure it is of the appropriate format
    try:
        rowlist = copytext.split('\n')
        # Strip any trailing tabs
        rowlist = [r.rstrip('\t') for r in rowlist]
        celllist = [r.split('\t') for r in rowlist]
    except:
        return False

    if len(celllist) == 0:
        return False
    ncol = len(celllist[0])
    for row in celllist:
        if len(row) != ncol: return False
    if ncol == 0: return False

    global clipcells
    clipcells = celllist
    return True

def copySelectedCells(panel):
    """Copy block of selected cells or individual cell into clipboard.

    This stores the cells as a plain text grid so that it can be copied to and
    from other applications.
    Columns are delimited by tabs '\t'.
    Rows are delimited by newlines '\n'.
    """
    grid = panel.gridAtoms
    copytext = ""

    # Get the cells
    individuals = grid.GetSelectedCells()
    topleft = grid.GetSelectionBlockTopLeft()
    bottomright = grid.GetSelectionBlockBottomRight()

    if len(individuals) == 1:
        copytext = str(grid.GetCellValue(individuals[0]))

    elif len(topleft) == 1:
        # Format the block of cells
        rtl = topleft[0][0]
        ctl = topleft[0][1]
        rbr = bottomright[0][0]
        cbr = bottomright[0][1]

        for row in range(rtl, rbr+1):
            for col in range(ctl, cbr+1):
                copytext += str(grid.GetCellValue(row,col))
                copytext += '\t'
            copytext += '\n'

    # Place the copytext into the clipboard
    if not wx.TheClipboard.IsOpened():
        opened = wx.TheClipboard.Open()
        if not opened: raise IOError("Cannot open the clipboard.")
        textdata = wx.TextDataObject(copytext)
    wx.TheClipboard.SetData(textdata)
    wx.TheClipboard.Close()
    return

def pasteIntoCells(panel):
    """Paste clipboard contents into cells.

    canPasteIntoCells must be called before this method in order to format
    clipboard text for pasting.
    """
    # Double check the clipcells
    if len(clipcells) == 0: return
    if len(clipcells[0]) == 0: return

    grid = panel.gridAtoms
    individuals = grid.GetSelectedCells()
    topleft = grid.GetSelectionBlockTopLeft()
    if len(individuals) > 0:
        tl = individuals[0]
    elif len(topleft) > 0:
        tl = topleft[0]
    else:
        return
    rtl = tl[0]
    ctl = tl[1]

    nrows = grid.GetNumberRows()
    ncols = grid.GetNumberCols()

    rbr = min(nrows, rtl + len(clipcells)) - 1
    cbr = min(ncols, ctl + len(clipcells[0])) - 1

    selections = []
    for row in range(rtl, rbr+1):
        for col in range(ctl, cbr+1):
            if not grid.IsReadOnly(row, col):
                oldvalue = panel.gridAtoms.GetCellValue(row, col)
                newvalue = panel.applyCellChange(row, col, clipcells[row-rtl][col-ctl])
                if newvalue is None: newvalue = oldvalue
                panel.gridAtoms.SetCellValue(row,col,str(newvalue))
                selections.append((row,col))

    gridutils.quickResizeColumns(panel.gridAtoms, selections)

    # Clear the grid and select the inserted entries
    grid.ClearSelection()
    #panel.refresh()
    for row in range(rtl, rbr+1):
        for col in range(ctl, cbr+1):
            if not grid.IsReadOnly(row, col):
                grid.SelectBlock(row,col,row,col,True)
    return

# End of file
