#!/usr/bin/env python

'''Extract the shortest Mn-O bond lengths from all fits in PDFgui project.

This script loops through all refined phases in PDFgui project and calculates
their shortest Mn-O bond lengths using diffpy.pdffit2 library.  The results
are plotted versus temperature and saved to "mno-bond-lengths.dat" file.
'''

from __future__ import print_function

# PDFgui project file
project_file = 'lmo-template.ddp'
output_file = 'mno-bond-lengths.dat'

# Import tui (Text User Interface) functions from diffpy.pdfgui
from diffpy.pdfgui import tui

# load project file
prj = tui.LoadProject(project_file)

# Define a function for calculating shortest MnO bond length
# using diffpy.pdffit2

# Create a PDF calculator object that will be used in that function.
from diffpy.pdffit2 import PdfFit
pf = PdfFit()

def shortestBond_MnO(stru):
    """extract the shortest MnO bond length in a structure.

    stru -- initial or refined phase from a PDFgui project

    Return the shortest bond length.
    """
    pf.reset()
    pf.add_structure(stru)
    bnds = pf.bond_length_types('Mn', 'O', 0.01, 3)
    return bnds['dij'][0]

# Extract temperatures from PDFgui project to Python list.
# Temperature needs to be defined per each dataset in the project.
temperatures = prj.getTemperatures()

# Build a list of shortest Mn-O bonds from all refined phases.
MnO_bond_lengths = []
for phase in prj.getPhases():
    if phase.refined is None:
        print("Cannot find phase refinement results in", project_file)
        print("Open the file in PDFgui, run refinement, save and try again.")
        # terminate the script by raising error condition
        raise RuntimeError('Missing refinement results.')
    MnO_bond_lengths.append(shortestBond_MnO(phase.refined))

# Save bond lengths to a file
outfile = open(output_file, 'w')
print("# Shortest Mn-O bond length extracted from", project_file, file=outfile)
print("# temperature(K) bond_length(A)", file=outfile)
for t, b in zip(temperatures, MnO_bond_lengths):
    print(t, b, file=outfile)
outfile.close()

dashline = 78 * '-'
print(dashline)
print("Mn-O bond lengths saved to", output_file)
print(dashline)

# Plot results using matplotlib; pylab is a part of matplotlib that
# provides MATLAB-like plotting functions.

import pylab
pylab.plot(temperatures, MnO_bond_lengths, 'o--')
pylab.title('Data from refined phases in PDFgui project %s' % project_file)
pylab.xlabel('temperature (K)')
pylab.ylabel('shortest Mn-O bond (A)')

# Show the plot window.  This must be the last command in the script.
pylab.show()
