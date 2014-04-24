#!/usr/bin/env python
reset()


#####################################################################
# Refinement - average structure
######################################################################

read_struct("CdSe_bulk_wur.stru")

###############################################################
# Experimental and lattice parameters
###############################################################
constrain(lat(1),"@1")
constrain(lat(2),"@1")
constrain(lat(3),"@2")

setpar(1,lat(1))
setpar(2,lat(3))

constrain(pfrac,20)
#constrain(qsig,21)
constrain(delta,22)

setpar(20,0.5)
#setpar(21,0.053)
setpar(22,3.5)

fixpar(22)
#fixpar(21)



###############################################################
# Temperature factors
###############################################################
#CD
for i in range (1, 3):
        constrain(u11(i),4)
        constrain(u22(i),4)
        constrain(u33(i),6)

setpar(4,0.005)
#setpar(5,u22(1))
setpar(6,0.008)

for i in range(3, 5):
        constrain(u11(i),7)
        constrain(u22(i),7)
        constrain(u33(i),9)

setpar(7,0.005)
#setpar(8,u22(1))
setpar(9,0.008)

fixpar(9)

###############################################################
# Postions ref.
###############################################################
constrain(z(3),100)
constrain(z(4),"0.5+@100")
setpar(100,z(3))







#######################
# read second phase P2
#######################

read_struct("CdSe_cub.stru")

###############################################################
# Experimental and lattice parameters
###############################################################

constrain(lat(1),"@3")
constrain(lat(2),"@3")
constrain(lat(3),"@3")

setpar(3,lat(1))
#setpar(2,lat(3))

constrain(pfrac,"1.0 - @20")

setpar(20,.5)


###############################################################
# Temperature factors P2
###############################################################

for i in range(1, 5):
        constrain(u11(i),400)
        constrain(u22(i),400)
        constrain(u33(i),600)

setpar(400,0.01)
#setpar(5,u22(1))
setpar(600,0.015)

for i in range(5, 9):
        constrain(u11(i),700)
        constrain(u22(i),700)
        constrain(u33(i),900)

setpar(700,0.01)
#setpar(8,u22(1))
setpar(900,0.015)
fixpar(900)


##########################
#  Dataset
#########################
read_data("CdSe15_old_4-30_nor.gr",X,14.0,0.0)
constrain(qsig,21)
setpar(21,0.135)


#constrain(dscale,26)
#setpar(26, 1.0)

pdfrange(1,1.5,19.99)



###############################################################
# Run fit
###############################################################

fixpar(400)
fixpar(600)
fixpar(700)
fixpar(100)
fixpar(21)

refine()


freepar(400)
freepar(600)
freepar(700)
freepar(100)
freepar(21)

refine()

####
constrain(dscale,26)
setpar(26, 1.0)

refine()

freepar(21)

refine()

freepar(900)
freepar(9)
refine()

###############################################################
# Save data
###############################################################


save_pdf(1,"Si_mixtwophases.pdf")
save_struct(1,"Si_mixtwophases-a.stru")
save_struct(2,"Si_mixtwophases-b.stru")
save_res("Si_mixtwophases2.res")
save_dif(1,"Si_mixtwophases2.dif")
