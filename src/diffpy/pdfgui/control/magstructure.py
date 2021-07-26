#!/usr/bin/env python
##############################################################################
#
# diffpy.mpdf         by Billinge Group
#                     Simon J. L. Billinge sb2896@columbia.edu
#                     (c) 2016 trustees of Columbia University in the City of
#                           New York.
#                      All rights reserved
#
# File coded by:    Benjamin Frandsen
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


"""functions and classes to create magnetic structures for mPDF calculations."""


import copy
import numpy as np
from diffpy.srreal.bondcalculator import BondCalculator
from diffpy.pdfgui.control.mpdfcalculator import jCalc

def generateAtomsXYZ(struc, rmax=30.0, magIdxs=[0], square=False):
    """Generate array of atomic Cartesian coordinates from a given structure.

    Args:
        struc (diffpy.Structure object): provides lattice parameters and unit
            cell of the desired structure
        rmax (float): largest distance from central atom that should be
            included
        magIdxs (python list): list of integers giving indices of magnetic
            atoms in the unit cell
        square (boolean): if not True, atoms within a given radius from the
            origin will be returned; if True, then the full grid will be
            returned rather than just a spherical selection.

    Returns:
        numpy array of triples giving the Cartesian coordinates of all the
            magnetic atoms. Atom closest to the origin placed first in array.

    Note: If square = True, this may have problems for structures that have
        a several distorted unit cell (i.e. highly non-orthorhombic).
    """
    if not square:
        magAtoms = struc[magIdxs]
        bc = BondCalculator(rmax=rmax+np.linalg.norm(struc.lattice.stdbase.sum(axis=1)))
        bc.setPairMask(0, 'all', True, others=False)
        bc(magAtoms)
        r0 = struc.xyz_cartn[magIdxs[0]]
        atoms = np.vstack([r0, r0+bc.directions[bc.sites0 == 0]])

    else:
        ### generate the coordinates of each unit cell
        lat = struc.lattice
        unitcell = lat.stdbase
        cellwithatoms = struc.xyz_cartn[np.array(magIdxs)]
        dim1 = int(np.round(rmax/np.linalg.norm(unitcell[0])))
        dim2 = int(np.round(rmax/np.linalg.norm(unitcell[1])))
        dim3 = int(np.round(rmax/np.linalg.norm(unitcell[2])))
        ocoords = np.mgrid[-dim1:dim1+1, -dim2:dim2+1, -dim3:dim3+1].transpose().ravel().reshape((2*dim1+1)*(2*dim2+1)*(2*dim3+1), 3)
        latos = np.dot(ocoords, unitcell)

        ### rearrange latos array so that [0, 0, 0] is the first one (for convenience)
        latos[np.where(np.all(latos == [0, 0, 0], axis=1))] = latos[0]
        latos[0] = np.array([0, 0, 0])

        ### create list of all atomic positions
        atoms = np.empty([len(latos)*len(cellwithatoms), 3])
        index = 0
        for lato in latos:
            for atompos in cellwithatoms:
                atoms[index] = lato + atompos
                index += 1

    return atoms

def generateSpinsXYZ(struc, atoms=np.array([[]]), kvecs=np.array([[0, 0, 0]]),
                     basisvecs=np.array([[0, 0, 1]]), origin=np.array([0,0,0])):
    """Generate array of 3-vectors representing the spins in a structure.

    Args:
        struc (diffpy.Structure object): provides lattice parameters and unit
            cell of the desired structure
        atoms (numpy array): list of atomic coordinates of all the magnetic
            atoms of a given magnetic species in the structure
        kvecs (numpy array): list of three-vectors giving the propagation
            vector(s) of the magnetic structure
        basisvecs (numpy array): list of three-vectors describing the spin
            located at the spin origin.
        origin (numpy array): Cartesian coordinates specifying the origin
            to be used when calculating the phases of the spins.

    Returns:
        numpy array of triples giving the spin vectors of all the magnetic
            atoms, in the same order as the atoms array provided as input.

    """

    lat = struc.lattice
    rlat = lat.reciprocal()
    (astar, bstar, cstar) = (rlat.cartesian((1, 0, 0)), rlat.cartesian((0, 1, 0)),
                             rlat.cartesian((0, 0, 1)))
    i = 1j

    spins = 0*atoms
    cspins = 0*atoms + 0j*atoms
    if len(np.array(kvecs).shape) == 1:
        kvecs = [kvecs]        
    if len(np.array(basisvecs).shape) == 1:
        basisvecs = [basisvecs]        
    for idx, kvec in enumerate(kvecs):
        kcart = kvec[0]*astar + kvec[1]*bstar + kvec[2]*cstar
        phasefac = np.exp(-2.0*np.pi*i*np.dot(atoms-origin, kcart))
        cspins += basisvecs[idx]*phasefac[:, np.newaxis]
    spins = np.real(cspins)

    if np.abs(np.imag(cspins)).max() > 0.0001:
        print((np.abs(np.imag(cspins)).max()))
        print('Warning: basis vectors resulted in complex spins.')
        print('Imaginary parts have been discarded.')

    return spins

def generateFromUnitCell(unitcell, atombasis, spinbasis, rmax=30.0):
    """Generate array of atomic Cartesian coordinates from a given structure.

    Args:
        unitcell (numpy array): np.array([avec, bvec, cvec])
        atombasis (numpy array): gives positions of magnetic atoms in
            fractional coordinates; np.array([pos1, pos2, pos3, ...])
        spinbasis (numpy array): gives orientations of the magnetic moments
            in the unit cell, in the same order as atombasis
        rmax (float): largest distance from central atom that should be
            included

    Returns:
        atoms = numpy array of triples giving the Cartesian coordinates of all
              the magnetic atoms. Atom closest to the origin placed first in
              array.
        spins = numpy array of triples giving the Cartesian coordinates of all
              the spins in the structure, in the same order as atoms.

    Note: This will only work well for structures that can be expressed with a
        unit cell that is close to orthorhombic or higher symmetry.
    """
    if len(np.array(atombasis).shape) == 1:
        atombasis = [atombasis]        
    if len(np.array(spinbasis).shape) == 1:
        spinbasis = [spinbasis]        
    cellwithatoms = np.dot(atombasis, unitcell) ### check this
    radius = rmax+15.0
    dim1 = int(np.round(radius/np.linalg.norm(unitcell[0])))
    dim2 = int(np.round(radius/np.linalg.norm(unitcell[1])))
    dim3 = int(np.round(radius/np.linalg.norm(unitcell[2])))

    ### generate the coordinates of each unit cell
    ocoords = np.mgrid[-dim1:dim1+1, -dim2:dim2+1, -dim3:dim3+1].transpose().ravel().reshape((2*dim1+1)*(2*dim2+1)*(2*dim3+1), 3)
    latos = np.dot(ocoords, unitcell)

    ### select points within a desired radius from origin
    latos = latos[np.where(np.apply_along_axis(np.linalg.norm, 1, latos) <=
                           (rmax+np.linalg.norm(unitcell.sum(axis=1))))]

    ## rearrange latos array so that [0, 0, 0] is the first one (for convenience)
    latos[np.where(np.all(latos == [0, 0, 0], axis=1))] = latos[0]
    latos[0] = np.array([0, 0, 0])

    ### create list of all atomic positions
    atoms = np.empty([len(latos)*len(cellwithatoms), 3])
    spins = np.empty_like(atoms)
    index = 0
    for lato in latos:
        for j, atompos in enumerate(cellwithatoms):
            atoms[index] = lato + atompos
            spins[index] = spinbasis[j]
            index += 1
    return atoms, spins

def getFFparams(name, j2=False):
    """Get list of parameters for approximation of magnetic form factor

    Args:
        name (str): Name of magnetic ion in form 'Mn2' for Mn2+, etc.
        j2 (boolean): True of the j2 approximation should be calculated;
            otherwise, the j0 approximation is calculated.

    Returns:
        Python list of the 7 coefficients in the analytical approximation
            given at e.g. https://www.ill.eu/sites/ccsl/ffacts/ffachtml.html
    """
    if not j2:
        j0dict = {'Am2': [0.4743, 21.7761, 1.58, 5.6902, -1.0779, 4.1451, 0.0218],
                  'Am3': [0.4239, 19.5739, 1.4573, 5.8722, -0.9052, 3.9682, 0.0238],
                  'Am4': [0.3737, 17.8625, 1.3521, 6.0426, -0.7514, 3.7199, 0.0258],
                  'Am5': [0.2956, 17.3725, 1.4525, 6.0734, -0.7755, 3.6619, 0.0277],
                  'Am6': [0.2302, 16.9533, 1.4864, 6.1159, -0.7457, 3.5426, 0.0294],
                  'Am7': [0.3601, 12.7299, 1.964, 5.1203, -1.356, 3.7142, 0.0316],
                  'Ce2': [0.2953, 17.6846, 0.2923, 6.7329, 0.4313, 5.3827, -0.0194],
                  'Co0': [0.4139, 16.1616, 0.6013, 4.7805, -0.1518, 0.021, 0.1345],
                  'Co1': [0.099, 33.1252, 0.3645, 15.1768, 0.547, 5.0081, -0.0109],
                  'Co2': [0.4332, 14.3553, 0.5857, 4.6077, -0.0382, 0.1338, 0.0179],
                  'Co3': [0.3902, 12.5078, 0.6324, 4.4574, -0.15, 0.0343, 0.1272],
                  'Co4': [0.3515, 10.7785, 0.6778, 4.2343, -0.0389, 0.2409, 0.0098],
                  'Cr0': [0.1135, 45.199, 0.3481, 19.4931, 0.5477, 7.3542, -0.0092],
                  'Cr1': [-0.0977, 0.047, 0.4544, 26.0054, 0.5579, 7.4892, 0.0831],
                  'Cr2': [1.2024, -0.0055, 0.4158, 20.5475, 0.6032, 6.956, -1.2218],
                  'Cr3': [-0.3094, 0.0274, 0.368, 17.0355, 0.6559, 6.5236, 0.2856],
                  'Cr4': [-0.232, 0.0433, 0.3101, 14.9518, 0.7182, 6.1726, 0.2042],
                  'Cu0': [0.0909, 34.9838, 0.4088, 11.4432, 0.5128, 3.8248, -0.0124],
                  'Cu1': [0.0749, 34.9656, 0.4147, 11.7642, 0.5238, 3.8497, -0.0127],
                  'Cu2': [0.0232, 34.9686, 0.4023, 11.564, 0.5882, 3.8428, -0.0137],
                  'Cu3': [0.0031, 34.9074, 0.3582, 10.9138, 0.6531, 3.8279, -0.0147],
                  'Cu4': [-0.0132, 30.6817, 0.2801, 11.1626, 0.749, 3.8172, -0.0165],
                  'Dy2': [0.1308, 18.3155, 0.3118, 7.6645, 0.5795, 3.1469, -0.0226],
                  'Dy3': [0.1157, 15.0732, 0.327, 6.7991, 0.5821, 3.0202, -0.0249],
                  'Er2': [0.1122, 18.1223, 0.3462, 6.9106, 0.5649, 2.7614, -0.0235],
                  'Er3': [0.0586, 17.9802, 0.354, 7.0964, 0.6126, 2.7482, -0.0251],
                  'Eu2': [0.0755, 25.296, 0.3001, 11.5993, 0.6438, 4.0252, -0.0196],
                  'Eu3': [0.0204, 25.3078, 0.301, 11.4744, 0.7005, 3.942, -0.022],
                  'Fe0': [0.0706, 35.0085, 0.3589, 15.3583, 0.5819, 5.5606, -0.0114],
                  'Fe1': [0.1251, 34.9633, 0.3629, 15.5144, 0.5223, 5.5914, -0.0105],
                  'Fe2': [0.0263, 34.9597, 0.3668, 15.9435, 0.6188, 5.5935, -0.0119],
                  'Fe3': [0.3972, 13.2442, 0.6295, 4.9034, -0.0314, 0.3496, 0.0044],
                  'Fe4': [0.3782, 11.38, 0.6556, 4.592, -0.0346, 0.4833, 0.0005],
                  'Gd2': [0.0636, 25.3823, 0.3033, 11.2125, 0.6528, 3.7877, -0.0199],
                  'Gd3': [0.0186, 25.3867, 0.2895, 11.1421, 0.7135, 3.752, -0.0217],
                  'Ho2': [0.0995, 18.1761, 0.3305, 7.8556, 0.5921, 2.9799, -0.023],
                  'Ho3': [0.0566, 18.3176, 0.3365, 7.688, 0.6317, 2.9427, -0.0248],
                  'Mn0': [0.2438, 24.9629, 0.1472, 15.6728, 0.6189, 6.5403, -0.0105],
                  'Mn1': [-0.0138, 0.4213, 0.4231, 24.668, 0.5905, 6.6545, -0.001],
                  'Mn2': [0.422, 17.684, 0.5948, 6.005, 0.0043, -0.609, -0.0219],
                  'Mn3': [0.4198, 14.2829, 0.6054, 5.4689, 0.9241, -0.0088, -0.9498],
                  'Mn4': [0.376, 12.5661, 0.6602, 5.1329, -0.0372, 0.563, 0.0011],
                  'Mo0': [0.1806, 49.0568, 1.2306, 14.7859, -0.4268, 6.9866, 0.0171],
                  'Mo1': [0.35, 48.0354, 1.0305, 15.0604, -0.3929, 7.479, 0.0139],
                  'Nb0': [0.3946, 49.2297, 1.3197, 14.8216, -0.7269, 9.6156, 0.0129],
                  'Nb1': [0.4572, 49.9182, 1.0274, 15.7256, -0.4962, 9.1573, 0.0118],
                  'Nd2': [0.1645, 25.0453, 0.2522, 11.9782, 0.6012, 4.9461, -0.018],
                  'Nd3': [0.054, 25.0293, 0.3101, 12.102, 0.6575, 4.7223, -0.0216],
                  'Ni0': [-0.0172, 35.7392, 0.3174, 14.2689, 0.7136, 4.5661, -0.0143],
                  'Ni1': [0.0705, 35.8561, 0.3984, 13.8042, 0.5427, 4.3965, -0.0118],
                  'Ni2': [0.0163, 35.8826, 0.3916, 13.2233, 0.6052, 4.3388, -0.0133],
                  'Ni3': [-0.0134, 35.8677, 0.2678, 12.3326, 0.7614, 4.2369, -0.0162],
                  'Ni4': [-0.009, 35.8614, 0.2776, 11.7904, 0.7474, 4.2011, -0.0163],
                  'Np3': [0.5157, 20.8654, 2.2784, 5.893, -1.8163, 4.8457, 0.0211],
                  'Np4': [0.4206, 19.8046, 2.8004, 5.9783, -2.2436, 4.9848, 0.0228],
                  'Np5': [0.3692, 18.19, 3.151, 5.85, -2.5446, 4.9164, 0.0248],
                  'Np6': [0.2929, 17.5611, 3.4866, 5.7847, -2.8066, 4.8707, 0.0267],
                  'Pd0': [0.2003, 29.3633, 1.1446, 9.5993, -0.3689, 4.0423, 0.0251],
                  'Pd1': [0.5033, 24.5037, 1.9982, 6.9082, -1.524, 5.5133, 0.0213],
                  'Pr3': [0.0504, 24.9989, 0.2572, 12.0377, 0.7142, 5.0039, -0.0219],
                  'Pu3': [0.384, 16.6793, 3.1049, 5.421, -2.5148, 4.5512, 0.0263],
                  'Pu4': [0.4934, 16.8355, 1.6394, 5.6384, -1.1581, 4.1399, 0.0248],
                  'Pu5': [0.3888, 16.5592, 2.0362, 5.6567, -1.4515, 4.2552, 0.0267],
                  'Pu6': [0.3172, 16.0507, 3.4654, 5.3507, -2.8102, 4.5133, 0.0281],
                  'Rh0': [0.0976, 49.8825, 1.1601, 11.8307, -0.2789, 4.1266, 0.0234],
                  'Rh1': [0.3342, 29.7564, 1.2209, 9.4384, -0.5755, 5.332, 0.021],
                  'Ru0': [0.1069, 49.4238, 1.1912, 12.7417, -0.3176, 4.9125, 0.0213],
                  'Ru1': [0.441, 33.3086, 1.4775, 9.5531, -0.9361, 6.722, 0.0176],
                  'Sc0': [0.2512, 90.0296, 0.329, 39.4021, 0.4235, 14.3222, -0.0043],
                  'Sc1': [0.4889, 51.1603, 0.5203, 14.0764, -0.0286, 0.1792, 0.0185],
                  'Sc2': [0.5048, 31.4035, 0.5186, 10.9897, -0.0241, 1.1831, 0.0],
                  'Sm2': [0.0909, 25.2032, 0.3037, 11.8562, 0.625, 4.2366, -0.02],
                  'Sm3': [0.0288, 25.2068, 0.2973, 11.8311, 0.6954, 4.2117, -0.0213],
                  'Tb2': [0.0547, 25.5086, 0.3171, 10.5911, 0.649, 3.5171, -0.0212],
                  'Tb3': [0.0177, 25.5095, 0.2921, 10.5769, 0.7133, 3.5122, -0.0231],
                  'Tc0': [0.1298, 49.6611, 1.1656, 14.1307, -0.3134, 5.5129, 0.0195],
                  'Tc1': [0.2674, 48.9566, 0.9569, 15.1413, -0.2387, 5.4578, 0.016],
                  'Ti0': [0.4657, 33.5898, 0.549, 9.8791, -0.0291, 0.3232, 0.0123],
                  'Ti1': [0.5093, 36.7033, 0.5032, 10.3713, -0.0263, 0.3106, 0.0116],
                  'Ti2': [0.5091, 24.9763, 0.5162, 8.7569, -0.0281, 0.916, 0.0015],
                  'Ti3': [0.3571, 22.8413, 0.6688, 8.9306, -0.0354, 0.4833, 0.0099],
                  'Tm2': [0.0983, 18.3236, 0.338, 6.9178, 0.5875, 2.6622, -0.0241],
                  'Tm3': [0.0581, 15.0922, 0.2787, 7.8015, 0.6854, 2.7931, -0.0224],
                  'U3': [0.5058, 23.2882, 1.3464, 7.0028, -0.8724, 4.8683, 0.0192],
                  'U4': [0.3291, 23.5475, 1.0836, 8.454, -0.434, 4.1196, 0.0214],
                  'U5': [0.365, 19.8038, 3.2199, 6.2818, -2.6077, 5.301, 0.0233],
                  'V0': [0.4086, 28.8109, 0.6077, 8.5437, -0.0295, 0.2768, 0.0123],
                  'V1': [0.4444, 32.6479, 0.5683, 9.0971, -0.2285, 0.0218, 0.215],
                  'V2': [0.4085, 23.8526, 0.6091, 8.2456, -0.1676, 0.0415, 0.1496],
                  'V3': [0.3598, 19.3364, 0.6632, 7.6172, -0.3064, 0.0296, 0.2835],
                  'V4': [0.3106, 16.816, 0.7198, 7.0487, -0.0521, 0.302, 0.0221],
                  'Y0': [0.5915, 67.6081, 1.5123, 17.9004, -1.113, 14.1359, 0.008],
                  'Yb2': [0.0855, 18.5123, 0.2943, 7.3734, 0.6412, 2.6777, -0.0213],
                  'Yb3': [0.0416, 16.0949, 0.2849, 7.8341, 0.6961, 2.6725, -0.0229],
                  'Zr0': [0.4106, 59.9961, 1.0543, 18.6476, -0.4751, 10.54, 0.0106],
                  'Zr1': [0.4532, 59.5948, 0.7834, 21.4357, -0.2451, 9.036, 0.0098]}
        try:
            return j0dict[name]
        except KeyError:
            print('No magnetic form factor found for that element/ion.')
            return ['none']
    else:
        j2dict = {'Am2' : [3.5237, 15.9545, 2.2855, 5.1946, -0.0142, 0.5853, 0.0033],
                  'Am3' : [2.8622, 14.7328, 2.4099, 5.1439, -0.1326, 0.0309, 0.1233],
                  'Am4' : [2.4141, 12.9478, 2.3687, 4.9447, -0.2490, 0.0215, 0.2371],
                  'Am5' : [2.0109, 12.0534, 2.4155, 4.8358, -0.2264, 0.0275, 0.2128],
                  'Am6' : [1.6778, 11.3372, 2.4531, 4.7247, -0.2043, 0.0337, 0.1892],
                  'Am7' : [1.8845, 9.1606, 2.0746, 4.0422, -0.1318, 1.7227, 0.0020],
                  'Ce2' : [0.9809, 18.0630, 1.8413, 7.7688, 0.9905, 2.8452, 0.0120],
                  'Co0' : [1.9678, 14.1699, 1.4911, 4.9475, 0.3844, 1.7973, 0.0027],
                  'Co1' : [2.4097, 16.1608, 1.5780, 5.4604, 0.4095, 1.9141, 0.0031],
                  'Co2' : [1.9049, 11.6444, 1.3159, 4.3574, 0.3146, 1.6453, 0.0017],
                  'Co3' : [1.7058, 8.8595, 1.1409, 3.3086, 0.1474, 1.0899, -0.0025],
                  'Co4' : [1.3110, 8.0252, 1.1551, 3.1792, 0.1608, 1.1301, -0.0011],
                  'Cr0' : [3.4085, 20.1267, 2.1006, 6.8020, 0.4266, 2.3941, 0.0019],
                  'Cr1' : [3.7768, 20.3456, 2.1028, 6.8926, 0.4010, 2.4114, 0.0017],
                  'Cr2' : [2.6422, 16.0598, 1.9198, 6.2531, 0.4446, 2.3715, 0.0020],
                  'Cr3' : [1.6262, 15.0656, 2.0618, 6.2842, 0.5281, 2.3680, 0.0023],
                  'Cr4' : [1.0293, 13.9498, 1.9933, 6.0593, 0.5974, 2.3457, 0.0027],
                  'Cu0' : [1.9182, 14.4904, 1.3329, 4.7301, 0.3842, 1.6394, 0.0035],
                  'Cu1' : [1.8814, 13.4333, 1.2809, 4.5446, 0.3646, 1.6022, 0.0033],
                  'Cu2' : [1.5189, 10.4779, 1.1512, 3.8132, 0.2918, 1.3979, 0.0017],
                  'Cu3' : [1.2797, 8.4502, 1.0315, 3.2796, 0.2401, 1.2498, 0.0015],
                  'Cu4' : [0.9568, 7.4481, 0.9099, 3.3964, 0.3729, 1.4936, 0.0049],
                  'Dy2' : [0.5917, 18.5114, 1.1828, 6.7465, 0.8801, 2.2141, 0.0229],
                  'Dy3' : [0.2523, 18.5172, 1.0914, 6.7362, 0.9345, 2.2082, 0.0250],
                  'Er2' : [0.4693, 18.5278, 1.0545, 6.6493, 0.8679, 2.1201, 0.0261],
                  'Er3' : [0.1710, 18.5337, 0.9879, 6.6246, 0.9044, 2.1004, 0.0278],
                  'Eu2' : [0.8970, 18.4429, 1.3769, 7.0054, 0.9060, 2.4213, 0.0190],
                  'Eu3' : [0.3985, 18.4514, 1.3307, 6.9556, 0.9603, 2.3780, 0.0197],
                  'Fe0' : [1.9405, 18.4733, 1.9566, 6.3234, 0.5166, 2.1607, 0.0036],
                  'Fe1' : [2.6290, 18.6598, 1.8704, 6.3313, 0.4690, 2.1628, 0.0031],
                  'Fe2' : [1.6490, 16.5593, 1.9064, 6.1325, 0.5206, 2.1370, 0.0035],
                  'Fe3' : [1.3602, 11.9976, 1.5188, 5.0025, 0.4705, 1.9914, 0.0038],
                  'Fe4' : [1.5582, 8.2750, 1.1863, 3.2794, 0.1366, 1.1068, -0.0022],
                  'Gd2' : [0.7756, 18.4695, 1.3124, 6.8990, 0.8956, 2.3383, 0.0199],
                  'Gd3' : [0.3347, 18.4758, 1.2465, 6.8767, 0.9537, 2.3184, 0.0217],
                  'Ho2' : [0.5094, 18.5155, 1.1234, 6.7060, 0.8727, 2.1589, 0.0242],
                  'Ho3' : [0.2188, 18.5157, 1.0240, 6.7070, 0.9251, 2.1614, 0.0268],
                  'Mn0' : [2.6681, 16.0601, 1.7561, 5.6396, 0.3675, 2.0488, 0.0017],
                  'Mn1' : [3.2953, 18.6950, 1.8792, 6.2403, 0.3927, 2.2006, 0.0022],
                  'Mn2' : [2.0515, 15.5561, 1.8841, 6.0625, 0.4787, 2.2323, 0.0027],
                  'Mn3' : [1.2427, 14.9966, 1.9567, 6.1181, 0.5732, 2.2577, 0.0031],
                  'Mn4' : [0.7879, 13.8857, 1.8717, 5.7433, 0.5981, 2.1818, 0.0034],
                  'Mo0' : [5.1180, 23.4217, 4.1809, 9.2080, -0.0505, 1.7434, 0.0053],
                  'Mo1' : [7.2367, 28.1282, 4.0705, 9.9228, -0.0317, 1.4552, 0.0049],
                  'Nb0' : [7.4796, 33.1789, 5.0884, 11.5708, -0.0281, 1.5635, 0.0047],
                  'Nb1' : [8.7735, 33.2848, 4.6556, 11.6046, -0.0268, 1.5389, 0.0044],
                  'Nd2' : [1.4530, 18.3398, 1.6196, 7.2854, 0.8752, 2.6224, 0.0126],
                  'Nd3' : [0.6751, 18.3421, 1.6272, 7.2600, 0.9644, 2.6016, 0.0150],
                  'Ni0' : [1.0302, 12.2521, 1.4669, 4.7453, 0.4521, 1.7437, 0.0036],
                  'Ni1' : [2.1040, 14.8655, 1.4302, 5.0714, 0.4031, 1.7784, 0.0034],
                  'Ni2' : [1.7080, 11.0160, 1.2147, 4.1031, 0.3150, 1.5334, 0.0018],
                  'Ni3' : [1.1612, 7.7000, 1.0027, 3.2628, 0.2719, 1.3780, 0.0025],
                  'Ni4' : [1.1612, 7.7000, 1.0027, 3.2628, 0.2719, 1.3780, 0.0025],
                  'Np3' : [3.7170, 15.1333, 2.3216, 5.5025, -0.0275, 0.7996, 0.0052],
                  'Np4' : [2.9203, 14.6463, 2.5979, 5.5592, -0.0301, 0.3669, 0.0141],
                  'Np5' : [2.3308, 13.6540, 2.7219, 5.4935, -0.1357, 0.0493, 0.1224],
                  'Np6' : [1.8245, 13.1803, 2.8508, 5.4068, -0.1579, 0.0444, 0.1438],
                  'Pd0' : [3.3105, 14.7265, 2.6332, 5.8618, -0.0437, 1.1303, 0.0053],
                  'Pd1' : [4.2749, 17.9002, 2.7021, 6.3541, -0.0258, 0.6999, 0.0071],
                  'Pr3' : [0.8734, 18.9876, 1.5594, 6.0872, 0.8142, 2.4150, 0.0111],
                  'Pu3' : [2.0885, 12.8712, 2.5961, 5.1896, -0.1465, 0.0393, 0.1343],
                  'Pu4' : [2.7244, 12.9262, 2.3387, 5.1633, -0.1300, 0.0457, 0.1177],
                  'Pu5' : [2.1409, 12.8319, 2.5664, 5.1522, -0.1338, 0.0457, 0.1210],
                  'Pu6' : [1.7262, 12.3240, 2.6652, 5.0662, -0.1695, 0.0406, 0.1550],
                  'Rh0' : [3.3651, 17.3444, 3.2121, 6.8041, -0.0350, 0.5031, 0.0146],
                  'Rh1' : [4.0260, 18.9497, 3.1663, 6.9998, -0.0296, 0.4862, 0.0127],
                  'Ru0' : [3.7445, 18.6128, 3.4749, 7.4201, -0.0363, 1.0068, 0.0073],
                  'Ru1' : [5.2826, 23.6832, 3.5813, 8.1521, -0.0257, 0.4255, 0.0131],
                  'Sc0' : [10.8172, 54.3270, 4.7353, 14.8471, 0.6071, 4.2180, 0.0011],
                  'Sc1' : [8.5021, 34.2851, 3.2116, 10.9940, 0.4244, 3.6055, 0.0009],
                  'Sc2' : [4.3683, 28.6544, 3.7231, 10.8233, 0.6074, 3.6678, 0.0014],
                  'Sm2' : [1.0360, 18.4249, 1.4769, 7.0321, 0.8810, 2.4367, 0.0152],
                  'Sm3' : [0.4707, 18.4301, 1.4261, 7.0336, 0.9574, 2.4387, 0.0182],
                  'Tb2' : [0.6688, 18.4909, 1.2487, 6.8219, 0.8888, 2.2751, 0.0215],
                  'Tb3' : [0.2892, 18.4973, 1.1678, 6.7972, 0.9437, 2.2573, 0.0232],
                  'Tc0' : [4.2441, 21.3974, 3.9439, 8.3753, -0.0371, 1.1870, 0.0066],
                  'Tc1' : [6.4056, 24.8243, 3.5400, 8.6112, -0.0366, 1.4846, 0.0044],
                  'Ti0' : [4.3583, 36.0556, 3.8230, 11.1328, 0.6855, 3.4692, 0.0020],
                  'Ti1' : [6.1567, 27.2754, 2.6833, 8.9827, 0.4070, 3.0524, 0.0011],
                  'Ti2' : [4.3107, 18.3484, 2.0960, 6.7970, 0.2984, 2.5476, 0.0007],
                  'Ti3' : [3.3717, 14.4441, 1.8258, 5.7126, 0.2470, 2.2654, 0.0005],
                  'Tm2' : [0.4198, 18.5417, 0.9959, 6.6002, 0.8593, 2.0818, 0.0284],
                  'Tm3' : [0.1760, 18.5417, 0.9105, 6.5787, 0.8970, 2.0622, 0.0294],
                  'U3' : [4.1582, 16.5336, 2.4675, 5.9516, -0.0252, 0.7646, 0.0057],
                  'U4' : [3.7449, 13.8944, 2.6453, 4.8634, -0.5218, 3.1919, 0.0009],
                  'U5' : [3.0724, 12.5460, 2.3076, 5.2314, -0.0644, 1.4738, 0.0035],
                  'V0' : [3.8099, 21.3471, 2.3295, 7.4089, 0.4333, 2.6324, 0.0015],
                  'V1' : [4.7474, 23.3226, 2.3609, 7.8082, 0.4105, 2.7063, 0.0014],
                  'V2' : [3.4386, 16.5303, 1.9638, 6.1415, 0.2997, 2.2669, 0.0009],
                  'V3' : [2.3005, 14.6821, 2.0364, 6.1304, 0.4099, 2.3815, 0.0014],
                  'V4' : [1.8377, 12.2668, 1.8247, 5.4578, 0.3979, 2.2483, 0.0012],
                  'Y0' : [14.4084, 44.6577, 5.1045, 14.9043, -0.0535, 3.3189, 0.0028],
                  'Yb2' : [0.3852, 18.5497, 0.9415, 6.5507, 0.8492, 2.0425, 0.0301],
                  'Yb3' : [0.1570, 18.5553, 0.8484, 6.5403, 0.8880, 2.0367, 0.0318],
                  'Zr0' : [10.1378, 35.3372, 4.7734, 12.5453, -0.0489, 2.6721, 0.0036],
                  'Zr1' : [11.8722, 34.9200, 4.0502, 12.1266, -0.0632, 2.8278, 0.0034]}
        try:
            return j2dict[name]
        except KeyError:
            print('No magnetic form factor found for that element/ion.')
            return ['none']

def spinsFromAtoms(magstruc,positions,fractional=True,returnIdxs=False):
    """Return the spin vectors corresponding to specified atomic
       positions.

    Args:
        magstruc: MagSpecies or MagStructure object containing atoms and spins
        positions (list or array): atomic positions for which the
            corresponding spins should be returned.
        fractional (boolean): set as True if the atomic positions are in
            fractional coordinates of the crystallographic lattice
            vectors.
        returnIdxs (boolean): if True, the indices of the spins will also be
            returned.
    Returns:
        Array consisting of the spins corresponding to the atomic positions.
    """
    if len(np.array(positions).shape) == 1:
        positions = [positions]        
    spins = []
    idxs = []
    badlist = []
    for pos in positions:
        if fractional:
            pos=magstruc.struc.lattice.cartesian(pos)
        mask = np.all(np.round(magstruc.atoms,decimals=4)==
                      np.round(pos,decimals=4),axis=1)
        goodspins = magstruc.spins[mask]
        goodidxs = np.where(mask)[0]
        if len(goodspins) == 1:
            spins.append(goodspins[0])
            idxs.append(goodidxs[0])
        elif len(goodspins) > 1:        
            print('Warning: duplicate atoms in structure')
            spins.append(goodspins)
            idxs.append(goodidxs)
        elif len(goodspins) == 0:
            spins.append([])
            idxs.append([])
            badlist.append(pos)
    if len(badlist) > 0:
        print('The following atomic positions do not correspond to a spin:')
        for bad in badlist:
            if fractional:
                bad=magstruc.struc.lattice.fractional(pos)
            print(bad)
    if not returnIdxs:    
        return spins
    else:
        return spins,idxs

def atomsFromSpins(magstruc,spinvecs,fractional=True,returnIdxs=False):
    """Return the atomic positions corresponding to specified spins.

    Args:
        magstruc: MagSpecies or MagStructure object containing atoms and spins
        spinvecs (list or array): spin vectors for which the
            corresponding atoms should be returned.
        fractional (boolean): set as True if the atomic positions are to be
            returned as fractional coordinates of the crystallographic lattice
            vectors.
        returnIdxs (boolean): if True, the indices of the atoms will also be
            returned.

    Returns:
        List of arrays of atoms corresponding to the spins.
    """
    if len(np.array(spinvecs).shape) == 1:
        spinvecs = [spinvecs]        
    atoms = []
    idxs = []
    badlist = []
    for spin in spinvecs:
        mask = np.all(np.round(magstruc.spins,decimals=5)==
                      np.round(spin,decimals=5),axis=1)
        goodatoms = magstruc.atoms[mask]
        goodidxs = np.where(mask)[0]
        if fractional:
            goodatoms=magstruc.struc.lattice.fractional(goodatoms)
        atoms.append(goodatoms)
        idxs.append(goodidxs)
        if len(goodidxs) == 0:
            badlist.append(spin)
    if len(badlist)>0:
        print('The following spins were not found in the structure:')
        for bad in badlist:
            print(bad)
    if not returnIdxs:    
        return atoms
    else:
        return atoms,idxs

def visualizeSpins(atoms,spins):
    """Set up a 3d plot showing an arrangement of spins.

    Args:
        atoms (numpy array): array of atomic positions of spins to be
            visualized.
        spins (numpy array): array of spin vectors in same order as atoms.

    Returns:
        matplotlib figure object with a quiver plot on 3d axes.        
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    xx,yy,zz=np.transpose(atoms)
    uu,vv,ww=np.transpose(spins)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(len(xx)):
        x, y, z = 1.0*xx[i], 1.0*yy[i], 1.0*zz[i]
        u, v, w = 1.0*uu[i], 1.0*vv[i], 1.0*ww[i]
        lngth = np.sqrt(u**2+v**2+w**2)
        ax.quiver(x, y, z, u, v, w, length=lngth, pivot='middle')

    xmin,xmax=ax.get_xlim3d()
    ax.set_xlim3d(np.min((-1,xmin)),np.max((1,xmax)))
    ymin,ymax=ax.get_ylim3d()
    ax.set_ylim3d(np.min((-1,ymin)),np.max((1,ymax)))
    zmin,zmax=ax.get_zlim3d()
    ax.set_zlim3d(np.min((-1,zmin)),np.max((1,zmax)))

    return fig

def findAtomIndices(magstruc,atomList):
    """Return list of indices corresponding to input list of atomic coordinates.

    Args:
        atomList (numpy array of atomic coordinates)

    Returns:
        List of indices corresponding to the atomList.
    """
    if len(np.array(atomList).shape) == 1:
        atomList = [atomList]
    indices = []
    x,y,z=magstruc.atoms.transpose()
    allIdxs = np.arange(len(x))
    for idx, atom in enumerate(atomList):
        xa,ya,za = atom[0],atom[1],atom[2]
        maskx = (np.abs(x - xa) < 0.01)
        masky = (np.abs(y - ya) < 0.01)
        maskz = (np.abs(z - za) < 0.01)
        match = allIdxs[np.logical_and(maskx,np.logical_and(masky,maskz))]
        if len(match) == 0:
            print(('Warning: atom with index '+str(idx)+' in atomList could not'))
            print('be found in the MagStructure, so the index -1 has been')
            print('returned instead.')
            indices.append(-1)
        if len(match) == 1:
            indices.append(match[0])
        if len(match) > 1:
            print(('Warning: '+str(len(match))+' atoms matching index '+str(idx)))
            print('have been found in the MagStructure, so just the first index has')
            print('been returned.')
            indices.append(match[0])

    return indices

def getStrucFromPDFgui(fileName, fitIdx=0, phaseIdx=0):
    """Extract the refined atomic structure from a PDFgui project file.

    Args:
        fileName (str): path to the .ddp file containing the fit
        fitIdx (int): index of fit in .ddp file from which the refined
             structure is to be extracted. Default is 0.
        phaseIdx (int): index of phase within the specified fit for
             which the refined structure is to be extracted. Default
             is 0.

    Returns:
        struc (diffpy.Structure object): Refined atomic structure.
    """
    if fileName[-4:] == '.ddp':
        from diffpy.pdfgui import tui
        prj = tui.LoadProject(fileName)
        try:        
            fit = prj.getFits()[fitIdx]
        except IndexError:
            print('Fit index does not correspond to any fit in your')
            print('PDFgui project.')
            struc = []
            return struc
        try:
            struc = prj.getPhases([fit])[phaseIdx]
            struc = struc.refined
        except IndexError:
            print('Phase index does not correspond to any phase in your')
            print('specified fit in the PDFgui project.')
            struc = []
        return struc
    else:
        print('Please provide a PDFgui project file (.ddp extension)')
        return []

class MagSpecies:
    """Store information for a single species of magnetic atom.


    This class takes a diffpy.Structure object and uses it to generate spins
    based on a set of propagation vectors and basis vectors. For more info
    about magnetic propagation vectors, visit e.g.
    http://andrewsteele.co.uk/physics/mmcalc/docs/magneticpropagationvector

    Args:
        struc (diffpy.Structure object): provides lattice parameters and unit
            cell of desired structure.
        label (string): label for this particular magnetic species. Should be
            different from the labels for any other magnetic species you make.
        magIdxs (python list): list of integers giving indices of magnetic
            atoms in the unit cell
        atoms (numpy array): list of atomic coordinates of all the magnetic
            atoms in the structure; e.g. generated by generateAtomsXYZ()
        spins (numpy array): triplets giving the spin vectors of all the
            atoms, in the same order as the atoms array provided as input.
            In units of hbar.
        rmaxAtoms (float): maximum distance from the origin of atomic
            positions generated by the makeAtoms method.
        basisvecs (numpy array): nested three-vector(s) giving the basis
            vectors to generate the spins. e.g. np.array([[0, 0, 1]]). Any
            phase factor should be included directly with the basisvecs.
        kvecs (numpy array): nested three-vector(s) giving the propagation
            vectors for the magnetic structure in r.l.u.,
            e.g. np.array([[0.5, 0.5, 0.5]])
        S (float): Spin angular momentum quantum number in units of hbar.
        L (float): Orbital angular momentum quantum number in units of hbar.
        J (float): Total angular momentum quantum number in units of hbar.
        gS (float): spin component of the Lande g-factor (g = gS+gL)
        gL (float): orbital component of the Lande g-factor
        ffparamkey (string): gives the appropriate key for getFFparams()
        ffqgrid (numpy array): grid of momentum transfer values used for
            calculating the magnetic form factor.
        ff (numpy array): magnetic form factor.
        useDiffpyStruc (boolean): True if atoms/spins to be generated from
            a diffpy structure object; False if a user-provided unit cell is
            to be used. Note that there may be some problems with user-
            provided unit cells with lattice angles strongly deviated from
            90 degrees.
        latVecs (numpy array): Provides the unit cell lattice vectors as
            np.array([avec, bvec, cvec]). Only useful if useDiffpyStruc = False.
        atomBasis (numpy array): Provides positions of the magnetic atoms
            in fractional coordinates within the unit cell. Only useful if
            useDiffpyStruc = False. Example: np.array([[0, 0, 0], [0.5, 0.5, 0.5]])
        spinBasis (numpy array): Provides the orientations of the spins in
            the unit cell, in the same order as atomBasis. Only useful if
            useDiffpyStruc = False. Example: np.array([[0, 0, 1], [0, 0, -1]]
        spinOrigin (numpy array): Cartesian coordinates of the position that will
            be considered the origin when generating spin directions from basis
            vectors and propagation vectors. Default is np.array([0,0,0]).
        verbose (boolean): If True, will print messages relating to the structure.
            Useful for troubleshooting. Default is False.
    """
    def __init__(self, struc=None, label='', magIdxs=[0], atoms=None, spins=None,
                 rmaxAtoms=30.0, basisvecs=None, kvecs=None, S=0.5, L=0.0,
                 J=None, gS=None, gL=None, ffparamkey=None,
                 ffqgrid=None, ff=None, useDiffpyStruc=True, latVecs=None,
                 atomBasis=None, spinBasis=None, spinOrigin=None, verbose=False):
        self.label = label
        self.rmaxAtoms = rmaxAtoms
        self.S = S
        self.L = L
        if J is None:
            J = S + L
            self.J = J
        else:
            self.J = J
        if gS is None:
            self.gS = 1.0 + 1.0*(S*(S+1)-L*(L+1))/(J*(J+1))
        else:
            self.gS = gS
        if gL is None:
            self.gL = 0.5 + 1.0*(L*(L+1)-S*(S+1))/(2*J*(J+1))
        else:
            self.gL = gL
        self.ffparamkey = ffparamkey
        self.useDiffpyStruc = useDiffpyStruc
        if magIdxs is None:
            self.magIdxs = [0]
        else:
            self.magIdxs = magIdxs
        if struc is None:
            self.struc = []
        else:
            self.struc = struc
        if atoms is None:
            self.atoms = np.array([])
        else:
            self.atoms = atoms
        if spins is None:
            self.spins = np.array([])
        else:
            self.spins = spins
        if basisvecs is None:
            self.basisvecs = np.array([[0, 0, 1]])
        else:
            self.basisvecs = basisvecs
        if kvecs is None:
            self.kvecs = np.array([[0, 0, 0]])
        else:
            self.kvecs = kvecs
        if ff is None:
            self.ff = np.array([])
        else:
            self.ff = ff
        if ffqgrid is None:
            self.ffqgrid = np.arange(0, 10.0, 0.01)
        else:
            self.ffqgrid = ffqgrid
        if latVecs is None:
            self.latVecs = np.array([[4., 0, 0], [0, 4., 0], [0, 0, 4.]])
        else:
            self.ff = latVecs
        if atomBasis is None:
            self.atomBasis = np.array([[0, 0, 0]])
        else:
            self.atomBasis = atomBasis
        if spinBasis is None:
            self.spinBasis = np.array([[0, 0, 1]])
        else:
            self.spinBasis = spinBasis
        if spinOrigin is None:
            self.spinOrigin = np.array([[0, 0, 0]])
        else:
            self.spinOrigin = spinOrigin
        self.verbose = verbose

    def __repr__(self):
        if self.label == '':
            return 'MagSpecies() object'
        else:
            return self.label+': MagSpecies() object'

    def makeAtoms(self):
        """Generate the Cartesian coordinates of the atoms for this species.
        """
        if self.useDiffpyStruc:
            self.atoms = generateAtomsXYZ(self.struc, self.rmaxAtoms, self.magIdxs)
        else:
            try:
                self.atoms, self.spins = generateFromUnitCell(self.latVecs,
                                                              self.atomBasis,
                                                              self.spinBasis,
                                                              self.rmaxAtoms)
            except:
                print('Please check latVecs, atomBasis, and spinBasis.')

    def makeSpins(self):
        """Generate the Cartesian coordinates of the spin vectors in the
               structure. Must provide propagation vector(s) and basis
               vector(s).
        """
        if self.useDiffpyStruc:
            self.spins = generateSpinsXYZ(self.struc, self.atoms, self.kvecs, self.basisvecs, 
                                          self.spinOrigin)
        else:
            print('Since you are not using a diffpy Structure object,')
            print('the spins are generated from the makeAtoms() method.')
            print('Please call that method if you have not already.')

    def makeFF(self):
        """Generate the magnetic form factor.
        """
        g = self.gS+self.gL
        if getFFparams(self.ffparamkey) != ['none']:
            self.ff = (self.gS/g * jCalc(self.ffqgrid, getFFparams(self.ffparamkey))+
                       self.gL/g * jCalc(self.ffqgrid, getFFparams(self.ffparamkey), j2=True))
        else:
            print('Using generic magnetic form factor.')
            self.ff = jCalc(self.ffqgrid)

    def spinsFromAtoms(self,positions,fractional=True,returnIdxs=False):
        """Return the spin vectors corresponding to specified atomic
           positions.

        This method calls the diffpy.mpdf.spinsFromAtoms() method. 

        Args:
            magstruc: MagSpecies or MagStructure object containing atoms and spins
            positions (list or array): atomic positions for which the
                corresponding spins should be returned.
            fractional (boolean): set as True if the atomic positions are in
                fractional coordinates of the crystallographic lattice
                vectors.
            returnIdxs (boolean): if True, the indices of the spins will also be
                returned.
        Returns:
            Array consisting of the spins corresponding to the atomic positions.
        """
        return spinsFromAtoms(self,positions,fractional,returnIdxs)

    def atomsFromSpins(self,spinvecs,fractional=True,returnIdxs=False):
        """Return the atomic positions corresponding to specified spins.

        This method calls the diffpy.mpdf.atomsFromSpins() method. 

        Args:
            magstruc: MagSpecies or MagStructure object containing atoms and spins
            spinvecs (list or array): spin vectors for which the
                corresponding atoms should be returned.
            fractional (boolean): set as True if the atomic positions are to be
                returned as fractional coordinates of the crystallographic lattice
                vectors.
            returnIdxs (boolean): if True, the indices of the atoms will also be
                returned.

        Returns:
            List of arrays of atoms corresponding to the spins.
        """
        return atomsFromSpins(self,spinvecs,fractional,returnIdxs)

    def findAtomIndices(self,atomList):
        """Return list of indices corresponding to input list of atomic coordinates.

        This method calls the diffpy.mpdf.findAtomIndices() method. 

        Args:
            atomList (numpy array of atomic coordinates)

        Returns:
            List of indices corresponding to the atomList.
        """
        return findAtomIndices(self,atomList)

    def runChecks(self):
        """Run some simple checks and raise a warning if a problem is found.
        """
        if self.verbose:        
            print(('Running checks for '+self.label+' MagSpecies object...\n'))

        flagCount = 0
        flag = False

        if self.useDiffpyStruc:
            # check that basisvecs and kvecs have same shape
            if self.kvecs.shape != self.basisvecs.shape:
                flag = True
            if flag:
                flagCount += 1
                if self.verbose:
                    print('kvecs and basisvecs must have the same dimensions.')

        else:
            # check for improperlatVecs array
            if self.latVecs.shape != (3, 3):
                flag = True
            if flag:
                flagCount += 1
                if self.verbose:
                    print('latVecs array does not have the correct dimensions.')
                    print('It must be a 3 x 3 nested array.')
                    print('Example: np.array([[4, 0, 0], [0, 4, 0], [0, 0, 4]])')
            flag = False

            # check for mismatched number of atoms and spins in basis
            if self.atomBasis.shape != self.spinBasis.shape:
                flag = True
            if flag:
                flagCount += 1
                if self.verbose:
                    print('atomBasis and spinBasis must have the same dimensions.')

        # summarize results
        if flagCount == 0:
            if self.verbose:
                print('All MagSpecies() checks passed. No obvious problems found.\n')

    def copy(self):
        """Return a deep copy of the MagSpecies object.
        """
        return copy.deepcopy(self)

class MagStructure:
    """Build on the diffpy.Structure class to include magnetic attributes.

    This class takes a diffpy.Structure object and packages additional info
    relating to magnetic structure, which can then be fed to an MPDFcalculator
    object.

    Args:
        struc (diffpy.Structure object): provides lattice parameters and unit
            cell of desired structure.
        species (python dictionary): dictionary of magnetic species in the
            structure. The values are MagSpecies objects.
        atoms (numpy array): list of atomic coordinates of all the magnetic
            atoms in the structure; e.g. generated by generateAtomsXYZ()
        spins (numpy array): triplets giving the spin vectors of all the
            atoms, in the same order as the atoms array provided as input.
        gfactors (numpy array): Lande g-factors of the magnetic moments
        rmaxAtoms (float): maximum distance from the origin of atomic
            positions generated by the makeAtoms method.
        ffqgrid (numpy array): grid of momentum transfer values used for
            calculating the magnetic form factor.
        ff (numpy array): magnetic form factor. Should be same shape as
            ffqgrid.
        label (string): Optional descriptive string for the MagStructure.
        K1 (float): a constant used for calculating Dr; should be averaged
            over all magnetic species. Important if physical information is
            to be extracted from mPDF scale factors, e.g. moment size.
        K2 (float): another constant used for calculating Dr.
        fractions (python dictionary): Dictionary providing the fraction of
            spins in the magnetic structure corresponding to each species.
        verbose (boolean): If True, will print messages relating to the structure.
            Useful for troubleshooting. Default is False.
   """

    def __init__(self, struc=None, species=None, atoms=None, spins=None,
                 gfactors=None, rmaxAtoms=30.0, ffqgrid=None, ff=None,
                 label='', K1=None, K2=None, fractions=None, verbose=False):

        self.rmaxAtoms = rmaxAtoms
        self.label = label

        if struc is None:
            self.struc = []
        else:
            self.struc = struc
        if atoms is None:
            self.atoms = np.array([])
        else:
            self.atoms = atoms
        if spins is None:
            self.spins = np.array([])
        else:
            self.spins = spins
        if gfactors is None:
            self.gfactors = np.array([2.0])
        else:
            self.gfactors = gfactors
        if species is None:
            self.species = {}
        else:
            self.species = species
        if ffqgrid is None:
            self.ffqgrid = np.arange(0, 10.0, 0.01)
        else:
            self.ffqgrid = ffqgrid
        if ff is None:
            self.ff = jCalc(self.ffqgrid)
        else:
            self.ff = ff
        if K1 is None:
            self.K1 = 0.66667*(1.913*2.81794/2.0)**2*2.0**2*0.5*(0.5+1)
        else:
            self.K1 = K1
        if K2 is None:
            self.K2 = self.K1
        else:
            self.K2 = K2
        if fractions is None:
            self.fractions = {}
        else:
            self.fractions = fractions
        self.verbose = verbose

    def __repr__(self):
        if self.label == '':
            return 'MagStructure() object'
        else:
            return self.label+': MagStructure() object'

    def makeSpecies(self, label, magIdxs=None, atoms=None, spins=None,
                    basisvecs=None, kvecs=None, S=0.5, L=0.0, J=None, gS=None,
                    gL=None, ffparamkey=None,ffqgrid=None, ff=None):
        """Create a MagSpecies object and add it to the species dictionary.

        Args:
            label (string): label for this particular magnetic species. Should be
                different from the labels for any other magnetic species you make.
            magIdxs (python list): list of integers giving indices of magnetic
                atoms in the unit cell
            atoms (numpy array): list of atomic coordinates of all the magnetic
                atoms in the structure; e.g. generated by generateAtomsXYZ()
            spins (numpy array): triplets giving the spin vectors of all the
                atoms, in the same order as the atoms array provided as input.
            basisvecs (numpy array): nested three-vector(s) giving the basis
                vectors to generate the spins. e.g. np.array([[0, 0, 1]]). Any
                phase factor should be included directly with the basisvecs.
            kvecs (numpy array): nested three-vector(s) giving the propagation
                vectors for the magnetic structure in r.l.u.,
                e.g. np.array([[0.5, 0.5, 0.5]])
            gS (float): spin component of the Lande g-factor (g = gS+gL)
            gL (float): orbital component of the Lande g-factor
            ffparamkey (string): gives the appropriate key for getFFparams()
            ffqgrid (numpy array): grid of momentum transfer values used for
                calculating the magnetic form factor.
            ff (numpy array): magnetic form factor.

        """
        # check that the label is not a duplicate with any other mag species.
        duplicate = False
        for name in list(self.species.keys()):
            if name == label:
                duplicate = True
        if not duplicate:
            if ffqgrid is None:
                ffqgrid = np.arange(0, 10.0, 0.01)
            self.species[label] = MagSpecies(self.struc, label, magIdxs, atoms, spins,
                                             self.rmaxAtoms, basisvecs, kvecs, S, L,
                                             J, gS, gL, ffparamkey, ffqgrid, ff,
                                             self.verbose)
            # update the list of fractions
            totatoms = 0.0
            for key in self.species:
                totatoms += self.species[key].atoms.shape[0]
            for key in self.species:                
                if totatoms == 0.0:
                    totatoms = 1.0 # prevent divide by zero problems
                frac = float(self.species[key].atoms.shape[0])/totatoms
                self.fractions[key] = frac
            self.runChecks()
        else:
            print('This label has already been assigned to another species in')
            print('the structure. Please choose a new label.')

    def getCoordsFromSpecies(self):
        """Read in atomic positions and spins from magnetic species.

        This differs from makeSpins() and makeAtoms() because it simply loads
        the atoms and spins from the species without re-generating them from 
        the structure.
        """
        tempA = np.array([[0, 0, 0]])
        tempS = np.array([[0, 0, 0]])
        for key in self.species:
            na = self.species[key].atoms.shape[0]
            ns = self.species[key].atoms.shape[0]
            if (na > 0) and (na == ns):            
                tempA = np.concatenate((tempA, self.species[key].atoms))
                tempS = np.concatenate((tempS, self.species[key].spins))
            else:
                if self.verbose:
                    print(('Coordinates of atoms and spins for ' + key))
                    print('have not been loaded because they have not yet been')
                    print('generated and/or do not match in shape.')
        if tempA.shape != (1, 3):        
            self.atoms = tempA[1:]
            self.spins = tempS[1:]
        elif len(self.species) == 0:
            self.atoms = np.array([])
            self.spins = np.array([])

    def loadSpecies(self, magSpec):
        """Load in an already-existing MagSpecies object

        Args:
            magSpec (MagSpecies object): The magnetic species to be imported
                into the structure.
        """
        # check that the label is not a duplicate with any other mag species.
        duplicate = False
        for name in list(self.species.keys()):
            if name == magSpec.label:
                duplicate = True
        if not duplicate:
            self.species[magSpec.label] = magSpec
            self.struc = magSpec.struc
            self.getCoordsFromSpecies()
            # update the list of fractions
            totatoms = 0.0
            for key in self.species:
                totatoms += self.species[key].atoms.shape[0]
            for key in list(self.species.keys()):
                if totatoms == 0.0:
                    totatoms = 1.0 # prevent divide by zero problems
                frac = float(self.species[key].atoms.shape[0])/totatoms
                self.fractions[key] = frac
            self.runChecks()
        else:
            print('The label for this species has already been assigned to')
            print('another species in the structure. Please choose a new label')
            print('for this species.')

    def removeSpecies(self, label, update=True):
        """Remove a magnetic species from the species dictionary.

        Args:
            label (string): key for the dictionary entry to be removed.
            update (boolean): if True, the MagStructure will update its atoms
                and spins with the removed species now excluded.
        """
        try:
            del self.species[label]
            if update:
                self.getCoordsFromSpecies()
                # update the list of fractions
                totatoms = 0.0
                for key in self.species:
                    totatoms += self.species[key].atoms.shape[0]
                for key in self.species:                
                    if totatoms == 0.0:
                        totatoms = 1.0 # prevent divide by zero problems
                    frac = float(self.species[key].atoms.shape[0])/totatoms
                    self.fractions[key] = frac
        except:
            print('Species cannot be deleted. Check that you are using the')
            print('correct species label.')

    def makeAtoms(self):
        """Generate the Cartesian coordinates of the atoms for this species.

        Args:
            fromUnitCell (boolean): True if atoms/spins to be generated from
                a unit cell provided by the user; False if the diffpy structure
                object is to be used.
            unitcell (numpy array): Provides the unit cell lattice vectors as
                np.array((avec, bvec, cvec)).
            atombasis (numpy array): Provides positions of the magnetic atoms
                in fractional coordinates within the unit cell.
            spin cell (numpy array): Provides the orientations of the spins in
                the unit cell, in the same order as atombasis
        """
        temp = np.array([[0, 0, 0]])
        for key in self.species:
            self.species[key].makeAtoms()
            temp = np.concatenate((temp, self.species[key].atoms))
        self.atoms = temp[1:]

    def makeSpins(self):
        """Generate the Cartesian coordinates of the spin vectors in the
               structure. Calls the makeSpins() method for each MagSpecies in
               the species dictionary and concatenates them together.
        """
        temp = np.array([[0, 0, 0]])
        for key in self.species:
            self.species[key].makeSpins()
            temp = np.concatenate((temp, self.species[key].spins))
        self.spins = temp[1:]

    def makeGfactors(self):
        """Generate an array of Lande g-factors in the same order as the spins
                in the MagStructure.
        """
        temp = np.array([2.0])
        for key in self.species:
            temp = np.concatenate((temp,
                                   (self.species[key].gS+self.species[key].gL)*np.ones(self.species[key].spins.shape[0])))
        self.gfactors = temp[1:]

    def makeFractions(self):
        """Generate the fractions dictionary.
        """
        try:
            totatoms = 0.0
            for key in self.species:
                totatoms += self.species[key].atoms.shape[0]
            for key in self.species:                
                if totatoms == 0.0:
                    totatoms = 1.0 # prevent divide by zero problems
                frac = float(self.species[key].atoms.shape[0])/totatoms
                self.fractions[key] = frac
        except:
            if len(self.species) == 0:
                self.fractions = {}
            else:
                print('Check MagStructure.fractions dictionary for problems.')

    def makeKfactors(self):
        """Set the factors K1 and K2 used for unnormalized mPDF. The fractions
           dictionary must be accurate before running this method.
        """
        K1, K2 = 0, 0        
        for key in self.species:
            gSa, gLa = self.species[key].gS, self.species[key].gL
            ga = gSa + gLa
            Ja = self.species[key].J
            K1 += self.fractions[key]*ga*np.sqrt(Ja*(Ja+1))
            K2 += self.fractions[key]*ga**2*Ja*(Ja+1)
        K1 = K1**2
        K1 *= (1.913*2.81794/2.0)**2*2.0/3.0
        K2 *= (1.913*2.81794/2.0)**2*2.0/3.0
        self.K1 = K1
        self.K2 = K2

    def makeFF(self):
        """Generate the properly weighted average magnetic form factor of all
                the magnetic species in the structure.
        """
        try:
            self.ffqgrid = list(self.species.values())[0].ffqgrid
            self.ff = np.zeros_like(self.ffqgrid)
            totatoms = 0.0
            for key in self.species:
                totatoms += self.species[key].atoms.shape[0]
            for key in self.species:
                frac = float(self.species[key].atoms.shape[0])/totatoms
                self.species[key].makeFF()
                self.ff += frac*self.species[key].ff
        except:
            if len(self.species) == 0:
                self.ff = jCalc(self.ffqgrid)
            else:
                print('Check that all mag species have same q-grid.')

    def makeAll(self):
        """Shortcut method to generate atoms, spins, g-factors, and form
                factor for the magnetic structure all in one go.
        """
        self.makeAtoms()
        self.makeSpins()
        self.makeGfactors()
        self.makeFractions()
        self.makeKfactors()
        self.makeFF()
        self.runChecks()

    def spinsFromAtoms(self,positions,fractional=True,returnIdxs=False):
        """Return the spin vectors corresponding to specified atomic
           positions.

        This method calls the diffpy.mpdf.spinsFromAtoms() method. 

        Args:
            magstruc: MagSpecies or MagStructure object containing atoms and spins
            positions (list or array): atomic positions for which the
                corresponding spins should be returned.
            fractional (boolean): set as True if the atomic positions are in
                fractional coordinates of the crystallographic lattice
                vectors.
            returnIdxs (boolean): if True, the indices of the spins will also be
                returned.
        Returns:
            Array consisting of the spins corresponding to the atomic positions.
        """
        return spinsFromAtoms(self,positions,fractional,returnIdxs)

    def atomsFromSpins(self,spinvecs,fractional=True,returnIdxs=False):
        """Return the atomic positions corresponding to specified spins.

        This method calls the diffpy.mpdf.atomsFromSpins() method. 

        Args:
            magstruc: MagSpecies or MagStructure object containing atoms and spins
            spinvecs (list or array): spin vectors for which the
                corresponding atoms should be returned.
            fractional (boolean): set as True if the atomic positions are to be
                returned as fractional coordinates of the crystallographic lattice
                vectors.
            returnIdxs (boolean): if True, the indices of the atoms will also be
                returned.

        Returns:
            List of arrays of atoms corresponding to the spins.
        """
        return atomsFromSpins(self,spinvecs,fractional,returnIdxs)

    def visualize(self,atoms,spins,showcrystalaxes=False,
                  axesorigin=np.array([0,0,0])):
        """Generate a crude 3-d plot to visualize the selected spins.

        Args:
            atoms (numpy array): array of atomic positions of spins to be
                visualized.
            spins (numpy array): array of spin vectors in same order as atoms.
            showcrystalaxes (boolean): if True, will display the crystal axes
                determined from the first magnetic species in the MagStructure
            axesorigin (array): position at which the crystal axes should be
                displayed
        """
        import matplotlib.pyplot as plt        
        from mpl_toolkits.mplot3d import axes3d

        fig = visualizeSpins(atoms,spins)
        if showcrystalaxes:
            ax3d = fig.axes[0]
            try:
                mspec=list(self.species.items())[0][1]
                if mspec.useDiffpyStruc:
                    lat=mspec.struc.lattice
                    a, b, c = lat.stdbase
                else:
                    a, b, c = mspec.latVecs
                xo, yo, zo = axesorigin
                ax3d.quiver(xo, yo, zo, a[0], a[1], a[2], pivot='tail', color='r')
                ax3d.quiver(xo, yo, zo, b[0], b[1], b[2], pivot='tail', color='g')
                ax3d.quiver(xo, yo, zo, c[0], c[1], c[2], pivot='tail', color='b')
            except:
                print('Please make sure your magnetic structure contains a')
                print('magnetic species with MagSpecies.struc set to a diffpy')
                print('structure or MagSpecies.latVecs provided and')
                print('MagSpecies.useDiffpyStruc set to False.')
        plt.show()

    def findAtomIndices(self,atomList):
        """Return list of indices corresponding to input list of atomic coordinates.

        This method calls the diffpy.mpdf.findAtomIndices() method. 

        Args:
            atomList (numpy array of atomic coordinates)

        Returns:
            List of indices corresponding to the atomList.
        """
        return findAtomIndices(self,atomList)

    def runChecks(self):
        """Run some simple checks and raise a warning if a problem is found.
        """
        # do the MagSpecies checks
        for key in self.species:
            self.species[key].runChecks()

        if self.verbose:        
            print(('Running checks for '+self.label+' MagStructure object...\n'))

        flag = False
        flagCount = 0

        # check for duplication among magnetic species
        if len(self.species) > 0:        
            if list(self.species.values())[0].useDiffpyStruc:
                idxs = []
                for key in self.species:
                    idxs.append(self.species[key].magIdxs)
                idxs = [item for sublist in idxs for item in sublist] # flatten the list
                for idx in idxs:
                    if idxs.count(idx) > 1:
                        flag = True
                if flag:
                    flagCount += 1
                    if self.verbose:
                        print('Warning: Magnetic species may have overlapping atoms.')
                        print('Check the magIdxs lists for your magnetic species.')
                    flag = False

        # check that the fractions are consistent
        totatoms = 0.0
        for key in self.species:
            totatoms += self.species[key].atoms.shape[0]
        for key in self.species:
            if totatoms == 0.0:
                totatoms = 1.0 # prevent divide by zero problems
            frac = float(self.species[key].atoms.shape[0])/totatoms
            if (frac > 0) and (np.abs(frac - self.fractions[key])/frac > 0.1):
                flag = True
        if flag:
            flagCount += 1
            if self.verbose:
                print('Species fractions do not correspond to actual number of')
                print('spins of each species in the structure.')
        flag = False

        # summarize results
        if flagCount == 0:
            if self.verbose:
                print('All MagStructure checks passed. No obvious problems found.')

    def getSpeciesIdxs(self):
        """Return a dictionary with the starting index in the atoms and spins
           arrays corresponding to each magnetic species.
        """
        idxDict = {}
        startIdx = 0
        for key in self.species:
            idxDict[key] = startIdx
            startIdx += self.species[key].atoms.shape[0]
        print(idxDict)
        return idxDict

    def copy(self):
        """Return a deep copy of the MagStructure object."""
        return copy.deepcopy(self)


