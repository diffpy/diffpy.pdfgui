#!/usr/bin/env python
reset()

#####################################################################
# Ni- (FCC) Refinement - average structure
######################################################################

read_struct("Ni.stru")
read_data("Ni_2-8.chi.gr", X, 40.0, 0.0)

###############################################################
# Experimental and lattice parameters
###############################################################

constrain(lat(1),1)
constrain(lat(2),1)
constrain(lat(3),1)

constrain(pscale,2)

setpar(1, lat(1))
setpar(2, 1.4)

pdfrange(1, 1.5, 20.0)

fixpar(ALL)
freepar(1)
freepar(2)

refine()
