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

"""Common functions for manipulating wx.grid.Grid.
"""

# module version
__id__ = "$Id$"


def getSelectionRows(grid):
    """Indices of the rows that have any cell selected.
    """
    rows = grid.GetNumberRows()
    rset = set()
    if grid.GetSelectedCols():
        rset.update(range(rows))
    rset.update(grid.GetSelectedRows())
    for r, c in grid.GetSelectedCells():
        rset.add(r)
    blocks = zip(grid.GetSelectionBlockTopLeft(),
            grid.GetSelectionBlockBottomRight())
    for tl, br in blocks:
        rset.update(range(tl[0], br[0] + 1))
    rv = sorted(rset)
    return rv


def getSelectionColumns(grid):
    """Indices of columns that have any cell selected.
    """
    cols = grid.GetNumberCols()
    cset = set()
    if grid.GetSelectedRows():
        cset.update(range(cols))
    cset.update(grid.GetSelectedCols())
    for r, c in grid.GetSelectedCells():
        cset.add(c)
    blocks = zip(grid.GetSelectionBlockTopLeft(),
            grid.GetSelectionBlockBottomRight())
    for tl, br in blocks:
        cset.update(range(tl[1], br[1] + 1))
    rv = sorted(cset)
    return rv


def getSelectedCells(grid):
    """Get list of (row,col) pairs of selected cells.
    
    This returns selected cells whether they are in blocks or are
    independent.
    
    This could be sped up if necessary.
    """
    rows = grid.GetNumberRows()
    cols = grid.GetNumberCols()
    selection = []
    
    for i in xrange(rows):
        for j in xrange(cols):
            if grid.IsInSelection(i,j):
                selection.append((i,j))

    return selection


def limitSelectionToRows(grid, indices):
    '''Limit selection to the specified row indices.
    No action for empty indices.

    grid     -- instance of wx.grid.Grid
    indices  -- list of row indices to be selected, must be sorted and unique.

    No return value.
    '''
    import bisect
    if not indices:  return
    cols = grid.GetNumberCols()
    rowblocks = _indicesToBlocks(indices)
    cindices = getSelectionColumns(grid) or [grid.GetGridCursorCol()]
    colblocks = _indicesToBlocks(cindices)
    grid.ClearSelection()
    for rlo, rhi in rowblocks:
        for clo, chi in colblocks:
            grid.SelectBlock(rlo, clo, rhi, chi, True)
    # move cursor to the selected area
    krow = bisect.bisect_left(indices, grid.GetGridCursorRow())
    krow = min(krow, len(indices) - 1)
    kcol = bisect.bisect_left(cindices, grid.GetGridCursorCol())
    kcol = min(kcol, len(cindices) - 1)
    grid.SetGridCursor(indices[krow], cindices[kcol])
    return


def quickResizeColumns(grid, indices):
    """Resize the columns that were recently affected by cell changes.
    
    This is faster than the normal grid AutoSizeColumns, since the latter loops
    over the entire grid. In addition, this will not cause a
    EVT_GRID_CMD_CELL_CHANGE event to be thrown, which can cause recursion.
    This method will only increase column size.
    """
    # Get the columns and maximum text width in each one
    dc = wx.ScreenDC() 
    maxSize = {}
    for (i, j) in indices:
        if j not in maxSize:
            renderer = grid.GetCellRenderer(i,j)
            attr = grid.GetOrCreateCellAttr(i,j)
            size = renderer.GetBestSize(grid, attr, dc, i, j).width
            size += 10 # Need a small buffer
            maxSize[j] = size

    grid.BeginBatch()
    for (j,size) in maxSize.items():
        if size > grid.GetColSize(j):
            grid.SetColSize(j, size)
    grid.EndBatch()
    return

# Local Helpers --------------------------------------------------------------

def _indicesToBlocks(indices):
    '''Convert a list of integer indices to a list of (start, stop) tuples.
    The (start, stop) tuple defines a continuous block, where the stop index
    is included in the block.

    indices  -- list of integer indices, must be unique and sorted.

    Return a list of (start, stop) tuples.
    '''
    rngs = []
    i0 = -100
    for i in indices:
        if i > i0 + 1:
            rngs.append([i, i])
        else:
            rngs[-1][-1] = i
        i0 = i
    rv = map(tuple, rngs)
    return rv
