#!/usr/bin/env python
########################################################################
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
########################################################################

"""Common methods used in the phase panels."""
from pdfgui.control.controlerrors import *

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
    textCtrlSrat
    textCtrlRcut
    """
    if panel.structure == None:
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
        panel.textCtrlSrat.SetValue("")
        panel.textCtrlRcut.SetValue("")

    else:
        # update panel with values from panel.structure
        # update textctrls
        panel.textCtrlA.SetValue(float2str(panel.structure.lattice.a))
        panel.textCtrlB.SetValue(float2str(panel.structure.lattice.b))
        panel.textCtrlC.SetValue(float2str(panel.structure.lattice.c))
        panel.textCtrlAlpha.SetValue(float2str(panel.structure.lattice.alpha))
        panel.textCtrlBeta.SetValue(float2str(panel.structure.lattice.beta))
        panel.textCtrlGamma.SetValue(float2str(panel.structure.lattice.gamma))
        panel.textCtrlScaleFactor.SetValue(float2str(panel.structure.pdffit['scale']) )
        panel.textCtrlDelta1.SetValue(float2str(panel.structure.pdffit['delta1']))
        panel.textCtrlDelta2.SetValue(float2str(panel.structure.pdffit['delta2']))
        panel.textCtrlSrat.SetValue(float2str(panel.structure.pdffit['srat']))
        panel.textCtrlRcut.SetValue(float2str(panel.structure.pdffit['rcut']))
    return

def refreshGrid(panel):
    """Refreshes grid on the panel.

    This is used by phaseconfigurepanel and phaseresultspanel.
    
    This method fills the grid with the contents of the structure member
    variable of the panel. It is expected that the grid is named 'gridAtoms'.
    """
    if panel.structure == None:
        # remove all rows from grid
        panel.gridAtoms.BeginBatch()
        if panel.gridAtoms.GetNumberRows() != 0:
            panel.gridAtoms.DeleteRows( numRows = panel.gridAtoms.GetNumberRows() )
        panel.gridAtoms.EndBatch()

    else:
        # update the grid with atoms
        i = 0
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
        for atom in panel.structure:
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
            i+=1
    
    panel.gridAtoms.AutosizeLabels()
    panel.gridAtoms.AutoSizeColumns()
    panel.gridAtoms.EndBatch()

    panel.gridAtoms.AdjustScrollbars()
    panel.gridAtoms.ForceRefresh()
    return
        
__id__ = "$Id$"
