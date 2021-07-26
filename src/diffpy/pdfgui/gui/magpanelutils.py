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

    This is used by magconfigurepanel and magconstraintspanel.

    This method updates the following TextCtrls with with contents of the
    structure member variable of the panel.
    textCtrlCorrLength
    textCtrlOrdScale
    textCtrlParaScale
    """
    if panel.structure.magStructure is None:
        # clear textcontrols
        panel.textCtrlCorrLength.SetValue("")
        panel.textCtrlOrdScale.SetValue("")
        panel.textCtrlParaScale.SetValue("")

    else:
        # update panel with values from panel.structure
        # update textctrls
        print(panel.structure.magStructure)
        panel.textCtrlCorrLength.SetValue(float2str(panel.structure.magStructure.corr))
        panel.textCtrlOrdScale.SetValue(float2str(panel.structure.magStructure.ord))
        panel.textCtrlParaScale.SetValue(float2str(panel.structure.magStructure.para))

def refreshGrid(panel):
    """Refreshed grid on the panel.

    This is used by magconfigurepanel and magconstraintspanel

    This method fills the grid with the magnetic contents of the structure member
    variable of the panel. It is expected that the grid is named 'gridAtoms'.
    """

    nmagatoms = 0
    for m in panel.structure.magnetic_atoms:
        if m[0] == 1:
            nmagatoms += 1
    nrows = panel.gridAtoms.GetNumberRows()
    panel.gridAtoms.BeginBatch()
    # make sure grid has correct number of rows
    if nmagatoms > nrows:
        panel.gridAtoms.InsertRows(numRows = nmagatoms - nrows)
    elif nmagatoms < nrows:
        panel.gridAtoms.DeleteRows(numRows = nrows - nmagatoms)

    # start with clean grid
    panel.gridAtoms.ClearGrid()

    # fill the first 'elem' column with element symbols and x, y, z values if magnetic
    count = 0
    for row, atom in zip(range(len(panel.structure)), panel.structure):
        if panel.structure.magnetic_atoms[row][0] == 1:
            panel.gridAtoms.SetRowLabelValue(count, str(row+1))
            atom_info = atom.element + " (" + float2str(atom.xyz[0]) + "," + float2str(atom.xyz[1]) + "," + float2str(atom.xyz[2]) + ")"
            panel.gridAtoms.SetCellValue(count, 0, atom_info)
            magSpecies = panel.structure.magStructure.species[panel.structure.magnetic_atoms[row][1]]
            basisvecs = '(0.0, 0.0, 0.0)' if magSpecies.basisvecs is None else panel.arrayToStr(magSpecies.basisvecs)
            panel.gridAtoms.SetCellValue(count, 1, basisvecs)
            kvecs = '(0.0, 0.0, 0.0)' if magSpecies.kvecs is None else panel.arrayToStr(magSpecies.kvecs)
            panel.gridAtoms.SetCellValue(count, 2, kvecs)
            ffkey = 'None' if magSpecies.ffparamkey is None else magSpecies.ffparamkey
            panel.gridAtoms.SetCellValue(count, 3, ffkey)
            count += 1


    panel.gridAtoms.AutosizeLabels()
    panel.gridAtoms.AutoSizeColumns()
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
