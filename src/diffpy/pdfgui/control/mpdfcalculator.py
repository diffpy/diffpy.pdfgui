#!/usr/bin/env python
##############################################################################
#
# diffpy.mpdf       by Billinge Group
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

"""functions and classes to perform mPDF calculations"""

import copy
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve, fftconvolve

def jCalc(q, params=[0.2394, 26.038, 0.4727, 12.1375, 0.3065, 3.0939, -0.01906],
          j2=False):
    """Calculate the magnetic form factor j0.

    This method for calculating the magnetic form factor is based on the
    approximate empirical forms based on the tables by Brown, consisting of
    the sum of 3 Gaussians and a constant.

    Args:
        q (numpy array): 1-d grid of momentum transfer on which the form
            factor is to be computed
        params (python list): provides the 7 numerical coefficients. The
            default is an average form factor of 3d j0 approximations.
        j2 (boolean): if True, calculate the j2 approximation for orbital
            angular momentum contributions

    Returns:
        numpy array with same shape as q giving the magnetic form factor j0 or j2.
    """
    [A, a, B, b, C, c, D] = params
    if j2:
        return (A*np.exp(-a*(q/4/np.pi)**2)+B*np.exp(-b*(q/4/np.pi)**2)+C*np.exp(-c*(q/4/np.pi)**2)+D)*(q/4.0/np.pi)**2
    else:
        return A*np.exp(-a*(q/4/np.pi)**2)+B*np.exp(-b*(q/4/np.pi)**2)+C*np.exp(-c*(q/4/np.pi)**2)+D

def cv(x1, y1, x2, y2):
    """Perform the convolution of two functions and give the correct output.


    Args:
        x1 (numpy array): independent variable of first function; must be in
            ascending order
        y1 (numpy array): dependent variable of first function
        x2 (numpy array): independent variable of second function; must have
            same grid spacing as x1
        y2 (numpy array): dependent variable of second function

    Returns:
        xcv (numpy array): independent variable of convoluted function, has
            dimension len(x1) + len(x2) - 1

        ycv (numpy array): convolution of y1 and y2, same shape as xcv

    """
    dx = x1[1]-x1[0]
    ycv = dx*convolve(y1, y2, 'full')
    xcv = np.linspace(x1[0]+x2[0], x1[-1]+x2[-1], len(ycv))
    return xcv, ycv

def fourierTransform(q, fq, rmin=0.0, rmax=50.0, rstep=0.1): # requires even q-grid
    """Compute the Fourier transform of a function.

    This method uses the FFT algorithm and returns correctly spaced x and
    y arrays on an even and specifiable grid. The input grid must be evenly
    spaced.

    Args:
        q (numpy array): independent variable for function to be transformed
        fq (numpy array): dependent variable for function to be transformed
        rmin (float, default = 0.0): min value of conjugate independent variable
            grid
        rmax (float, default = 50.0): maximum value of conjugate independent
            variable grid
        rstep (float, default = 0.1): grid spacing for conjugate independent
            variable

    Returns:
        r (numpy array): independent variable grid for transformed quantity

        fr (numpy array): Fourier transform of fq (complex)
    """
    lostep = int(np.ceil((rmin - 1e-8) / rstep))
    histep = int(np.floor((rmax + 1e-8) / rstep)) + 1
    r = np.arange(lostep,histep)*rstep
    qstep = q[1] - q[0]
    if (q[0]-0.01*qstep) > 0: 
        nn = int(np.round(q[0]/qstep))
        addme = np.linspace(0.0,q[0]-qstep,nn)
        q = np.concatenate((addme,q))
        fq = np.concatenate((0.0*addme,fq))
    qmaxrstep = np.pi/rstep
    nin = len(q)
    nbase = max([nin,histep,qmaxrstep/qstep])
    nlog2 = int(np.ceil(np.log2(nbase)))
    nout = 2**nlog2
    qmaxdb = 2*nout*qstep
    yindb=np.concatenate((fq,np.zeros(2*nout - nin)))
    cyoutdb = np.fft.ifft(yindb)*np.sqrt(2/np.pi)*qmaxdb
    frdb = cyoutdb
    rstepfine = 2*np.pi/qmaxdb
    rfine = np.arange(nout) * rstepfine
    frfine = frdb[:nout]
    frr = np.interp(r, rfine, np.real(frfine))
    fri = np.interp(r, rfine, np.imag(frfine))
    if r[0]+0.0001*rstep < 0:
        nn = int(np.round(-r[0]/rstep))
        frr[:nn] = 1.0*frr[2*nn:nn:-1]
        fri[:nn] = -1.0*fri[2*nn:nn:-1]
    fr = frr + 1j*fri
    return r, fr

def cosTransform(q, fq, rmin=0.0, rmax=50.0, rstep=0.1): # requires even q-grid
    """Compute the cosine Fourier transform of a function.

    This method uses the FFT algorithm and returns correctly spaced x and
    y arrays on an even and specifiable grid. The input grid must be evenly
    spaced.

    Args:
        q (numpy array): independent variable for function to be transformed
        fq (numpy array): dependent variable for function to be transformed
        rmin (float, default = 0.0): min value of conjugate independent variable
            grid
        rmax (float, default = 50.0): maximum value of conjugate independent
            variable grid
        rstep (float, default = 0.1): grid spacing for conjugate independent
            variable

    Returns:
        r (numpy array): independent variable grid for transformed quantity

        fr (numpy array): cosine Fourier transform of fq
    """
    r, fr = fourierTransform(q,fq,rmin,rmax,rstep)
    fr = np.real(fr)
    return r, fr

def sinTransform(q, fq, rmin=0.0, rmax=50.0, rstep=0.1): # requires even q-grid
    """Compute the sine Fourier transform of a function.

    This method uses direct integration rather than an FFT and doesn't require
    an even grid. The grid for the Fourier transform is even and specifiable.

    Args:
        q (numpy array): independent variable for function to be transformed
        fq (numpy array): dependent variable for function to be transformed
        rmin (float, default = 0.0): min value of conjugate independent variable
            grid
        rmax (float, default = 50.0): maximum value of conjugate independent
            variable grid
        rstep (float, default = 0.1): grid spacing for conjugate independent
            variable

    Returns:
        r (numpy array): independent variable grid for transformed quantity

        fr (numpy array): sine Fourier transform of fq
    """
    r, fr = fourierTransform(q,fq,rmin,rmax,rstep)
    fr = np.imag(fr)
    return r, fr

def cosTransformDirectIntegration(q, fq, rmin=0.0, rmax=50.0, rstep=0.1): # does not require even q-grid
    """Compute the cosine Fourier transform of a function.

    This method uses direct integration rather than an FFT and doesn't require
    an even grid. The grid for the Fourier transform is even and specifiable.

    Args:
        q (numpy array): independent variable for function to be transformed
        fq (numpy array): dependent variable for function to be transformed
        rmin (float, default = 0.0): min value of conjugate independent variable
            grid
        rmax (float, default = 50.0): maximum value of conjugate independent
            variable grid
        rstep (float, default = 0.1): grid spacing for conjugate independent
            variable

    Returns:
        r (numpy array): independent variable grid for transformed quantity

        fr (numpy array): cosine Fourier transform of fq
    """
    lostep = int(np.ceil((rmin - 1e-8) / rstep))
    histep = int(np.floor((rmax + 1e-8) / rstep)) + 1
    r = np.arange(lostep, histep)*rstep
    qrmat = np.outer(r, q)
    integrand = fq*np.cos(qrmat)
    fr = np.sqrt(2.0/np.pi)*np.trapz(integrand, q)
    return r, fr

def sinTransformDirectIntegration(q, fq, rmin=0.0, rmax=50.0, rstep=0.1): # does not require even q-grid
    """Compute the sine Fourier transform of a function.

    This method uses direct integration rather than an FFT and doesn't require
    an even grid. The grid for the Fourier transform is even and specifiable.

    Args:
        q (numpy array): independent variable for function to be transformed
        fq (numpy array): dependent variable for function to be transformed
        rmin (float, default = 0.0): min value of conjugate independent variable
            grid
        rmax (float, default = 50.0): maximum value of conjugate independent
            variable grid
        rstep (float, default = 0.1): grid spacing for conjugate independent
            variable

    Returns:
        r (numpy array): independent variable grid for transformed quantity

        fr (numpy array): cosine Fourier transform of fq
    """
    lostep = int(np.ceil((rmin - 1e-8) / rstep))
    histep = int(np.floor((rmax + 1e-8) / rstep)) + 1
    r = np.arange(lostep, histep)*rstep
    qrmat = np.outer(r, q)
    integrand = fq*np.sin(qrmat)
    fr = np.sqrt(2.0/np.pi)*np.trapz(integrand, q)
    return r, fr


def getStdUnc(fitResult,data,dataErr=None,numConstraints=0):
    """Return the standard uncertainty of refined parameters.
    This method is based on the scipy.optimize.least_squares routine.
    
    Args:
        fitResult: Output from scipy.optimize.least_squares routine
        data (numpy array): The data against which the fit is performed
        dataErr (numpy array): Experimental uncertainties on the data points
            (set to unity if not provided)
        numConstraints (int): Number of constraints used in the model
    Returns:
        pUnc (numpy array): standard uncertainties of the refined parameters.
        chisq (float): Value of chi^2 for the fit.
    """
    if dataErr is None:
        dataErr = np.ones_like(data)
    weights = 1.0/dataErr**2
    Rw = np.sqrt((fitResult.fun**2).sum()/(data**2*weights).sum())
    numParams = len(fitResult.x)
    Rexp = np.sqrt((data.shape[0]-numParams+numConstraints)/(data**2*weights).sum())
    j = fitResult.jac
    jac = np.dot(j.transpose(),j)
    cov = np.linalg.inv(jac)*Rw**2/Rexp**2
    pUnc = np.sqrt(cov.diagonal())
    chisq = Rw**2/Rexp**2
    return pUnc,chisq

def optimizedSubtraction(rhigh, dhigh, rlow, dlow):
    '''
    This routine stretches and broadens a low-temperature atomic PDF fit residual
    to match a high-temperature fit residual as closely as possible. The idea is
    to minimize thermal effects when doing the temperature subtraction so that
    the mDPF can be obtained as cleanly as possible.
    
    rhigh = r array for high-temperature atomic PDF fit residual
    dhigh = high-temperature atomic PDF fit residual
    rlow = r array for low-temperature atomic PDF fit residual
    dlow = low-temperature atomic PDF fit residual
    Note: the high- and low-temperature fits should be over the same r range
    '''

    def gaussianSmooth(x,y,sig=0.1):
        dr = np.mean((x - np.roll(x,1))[1:])
        rs = np.arange(-10,10,dr)
        s = np.exp(-rs**2/2.0/sig**2)
        xsmooth, ysmooth = cv(x,y,rs,s)
        ysmooth /= np.trapz(s,rs)
        msk = np.logical_and(xsmooth>(x.min()-0.5*dr),xsmooth<(x.max()+0.5*dr))
        return ysmooth[msk]

    def residual(p,x,y,ycomp):
        stretch, width = p
        newx = stretch*x
        newy = np.interp(newx,x,y)
        newy = gaussianSmooth(newx,newy,width)
        msk = (x <= x.max()/stretch)
        return ycomp[msk]-newy[msk]

    p0=[0.999,0.1] # typical starting guesses
    opt = least_squares(residual,p0,args=(rlow,dlow,dhigh))
    print(opt.x)
    stretch = opt.x[0]
    msk = (rlow <= rlow.max()/stretch)
    newdllow = dhigh[msk]-residual(opt.x,rlow,dlow,dhigh)
    diff = newdllow - dhigh[msk]
    return rhigh[msk], diff


def smoothData(xdata,ydata,qCutoff,func='sinc',gaussHeight=0.01):
    """Smooth out high-frequency contributions from the data.

    This method performs a convolution in real space to simulate a truncation
    in reciprocal space. This is motivated by the fact that high-frequency
    noise can sometimes obscure the lower-frequency mPDF signal when the mPDF
    is collected together with the nuclear PDF. This high-frequency noise comes
    from scattering intensity at high q that cannot possibly come from magnetic
    scattering, due to the strong suppression from the magnetic form factor.
    To better isolate the mPDF from this high-frequency noise, one could
    truncate the Fourier transfrom at some cutoff q value beyond which the
    magnetic scattering is negligible (e.g. where the square of the magnetic
    form factor is reduced to 1% of its original value). This can be done by
    multiplying the scattering in q-space by a "window function" that is equal
    to unity for q between 0 and the cutoff value and 0 outside this window.
    By the convolution theorem, this is equivalent to convoluting the full
    Fourier transform in real space with a sinc function. Alternatively, one
    could multiply the scattering in q-space by a Guassian function which is
    reduced to some small amplitude at the desired cutoff q value.  This is
    equivalent to a convolution in real space with another Gaussian function.
    The former method is recommended because it will generally be more
    physically justifiable.

    Args:
        xdata: numpy array containing the independent variable of the data
            to be smoothed.
        ydata: numpy array containing the dependent variable; this array will
            be smoothed.
        qCutoff: q value beyond which all contributions will be ignored.
        func: string specifying the type of real-space convolution function,
            either 'sinc' or 'gaussian' (see previous discussion).
        gaussHeight: float specifying what the height of the q-space Gaussian
            function should be at the specified value of qCutoff.

    Returns:
        Numpy array containing the smoothed version of ydata.
    """
    dr = np.mean((xdata - np.roll(xdata,1))[1:])
    rs = np.arange(-10,10,dr)
    if func=='sinc':
        s = np.sinc(rs*qCutoff/np.pi)
    elif func=='gaussian':
        rg = 1.0/(qCutoff*np.sqrt(np.log(1.0/gaussHeight)/2.0))
        s = np.exp(-rs**2/2.0/rg**2)
    else:
        print('The only function options are sinc and gaussian. Please check')
        print('your input. Using sinc by default.')
        s = np.sinc(rs*qCutoff/np.pi)
    xsmooth, ysmooth = cv(xdata,ydata,rs,s)
    ysmooth /= np.trapz(s,rs)
    msk = np.logical_and(xsmooth>(xdata.min()-0.5*dr),xsmooth<(xdata.max()+0.5*dr))
    return ysmooth[msk]
        
def getDiffData(fileName, fitIdx=0, writedata=False, skips = 14):
    """Extract the fit residual from a structural PDF fit. Works for .fgr and
       .ddp files.

    Args:
        fileName (str): path to the .fgr or .ddp file containing the fit
        fitIdx (int): index of fit in .ddp file from which the residual
             is to be extracted.
        writedata (boolean): whether or not the output should be saved to file
        skips (int): Number of rows to be skipped in .fgr file to get to data;
            default is 14.

    Returns:
        r (numpy array): same r-grid as contained in the fit file

        diff (numpy array): the structural PDF fit residual (i.e. the mPDF)
    """
    if fileName[-4:] == '.fgr':
        allcols = np.loadtxt(fileName, unpack=True, comments='#', skiprows=skips)
        r, diff = allcols[0], allcols[4]
        if writedata:
            np.savetxt(fileName[:-4]+'.diff', np.transpose((r, diff)))
        return r, diff
    elif fileName[-4:] == '.ddp':
        from diffpy.pdfgui import tui
        prj = tui.LoadProject(fileName)
        fit = prj.getFits()[fitIdx]
        dataSet = fit.getDataSet(0)
        r = np.array(dataSet.rcalc)
        diff = np.array(dataSet.Gdiff)
        if writedata:
            np.savetxt(fileName[:-4]+'_'+str(fitIdx)+'.diff',
                       np.transpose((r, diff)))
        return r, diff            
    else:
        print('This file format is not currently supported.')
        return np.array([0]), np.array([0])

def calculatemPDF(xyz, sxyz, gfactors=np.array([2.0]), calcList=np.array([0]),
                  rstep=0.01, rmin=0.0, rmax=20.0, psigma=0.1, qmin=0,
                  qmax=-1, dampRate=0.0, dampPower=2.0, maxextension=10.0,
                  orderedScale=1.0,
                  K1=0.66667*(1.913*2.81794/2.0)**2*2.0**2*0.5*(0.5+1)):
    """Calculate the normalized mPDF.

    At minimum, this module requires input lists of atomic positions and spins.

    Args:
        xyz (numpy array): list of atomic coordinates of all the magnetic
            atoms in the structure.
        sxyz (numpy array): triplets giving the spin vectors of all the
            atoms, in the same order as the xyz array provided as input.
        gfactors (numpy array): Lande g-factors of spins in same order as
            spin array.
        calcList (python list): list giving the indices of the atoms array
            specifying the atoms to be used as the origin when calculating
            the mPDF.
        rstep (float): step size for r-grid of calculated mPDF.
        rmin (float): minimum value of r for which mPDF should be calculated.
        rmax (float): maximum value of r for which mPDF should be calculated.
        psigma(float): std deviation (in Angstroms) of Gaussian peak
            to be convoluted with the calculated mPDF to simulate thermal
            motion.
        qmin (float): minimum experimentally accessible q-value (to be used
            for simulating termination ripples). If <0, no termination effects
            are included.
        qmax (float): maximum experimentally accessible q-value (to be used
            for simulating termination ripples). If <0, no termination effects
            are included.
        dampRate (float): generalized ("stretched") exponential damping rate
                of the mPDF.
        dampPower (float): power of the generalized exponential function.
        maxextension (float): extension of the r-grid on which the mPDF is
            calculated to properly account for contribution of pairs just
            outside the boundary.
        ordScale (float): overall scale factor for the mPDF function f(r).
        K1 (float): A constant related to the total angular momentum quantum
            number and the average Lande splitting factor.

    Returns: numpy arrays for r and the mPDF fr.
        """
    # check if g-factors have been provided
    if sxyz.shape[0] != gfactors.shape[0]:
        gfactors = 2.0*np.ones(sxyz.shape[0])
    # calculate s1, s2
    r = np.arange(rmin, rmax+maxextension+rstep, rstep)
    rbin = np.concatenate([r-rstep/2, [r[-1]+rstep/2]])

    s1 = np.zeros(len(r))
    s2 = np.zeros(len(r))

    if type(calcList) is str:
        if calcList == 'all':
            calcList = np.arange(len(xyz))

    for uu in calcList:
        ri = xyz[uu]
        rj = xyz
        si = sxyz[uu]
        sj = sxyz
        gi = gfactors[uu]
        gj = gfactors

        dxyz = rj-ri
        d2xyz = np.sum((dxyz)**2, axis=1).reshape(dxyz.shape[0], 1)
        d1xyz = np.sqrt(d2xyz)
        d1xyz[uu] = 1e-6 ### avoid divide by zero problem
        d1xyzr = d1xyz.ravel()

        xh = dxyz / d1xyz
        yh = si - xh * np.sum(si*xh, axis=1).reshape(dxyz.shape[0], 1)
        yh_dis = np.sum(yh**2, axis=1)
        yh_ind = np.nonzero(np.abs(yh_dis) < 1e-10)
        yh[yh_ind] = [0, 0, 0]
        yh_dis[yh_ind] = 1e-6 ### avoid divide by zero problem

        aij = np.sum(si * yh, axis=1) * np.sum(sj * yh, axis=1) / yh_dis
        aij[uu] = 0
        bij = 2 * np.sum(si * xh, axis=1) * np.sum(sj * xh, axis=1) - aij

        w2 = bij / d1xyzr**3

        d1xyzr[uu] = 0.0
        s1 += np.histogram(d1xyzr, bins=rbin, weights=gi*gj*aij)[0]
        s2 += np.histogram(d1xyzr, bins=rbin, weights=gi*gj*w2)[0]

    # apply Gaussian shape function
    if psigma != None:
        x = np.arange(-3, 3, rstep)
        y = np.exp(-x**2 / psigma**2 / 2) * (1 / np.sqrt(2*np.pi) / psigma)

        s1[0] = 0
        s1 = fftconvolve(s1, y)
        s1 = s1[int(len(x)/2): int(-len(x)/2+1)]

        s2 = fftconvolve(s2, y) * rstep
        s2 = s2[int(len(x)/2): int(-len(x)/2+1)]

    ss2 = np.cumsum(s2)

    if rmin == 0:
        r[0] = 1e-4*rstep # avoid infinities at r = 0
    fr = s1 / r + r * (ss2[-1] - ss2)
    r[0] = rmin
    fr /= len(calcList)*K1/(1.913*2.81794/2.0)**2

    fr *= orderedScale*np.exp((-1.0*(dampRate*r)**dampPower)/dampPower)
    # Do the convolution with the termination function if qmin/qmax have been given
    if qmin >= 0 and qmax > qmin:
        rth = np.arange(0.0, rmax+maxextension+rstep, rstep)
        rth[0] = 1e-4*rstep # avoid infinities at r = 0
        th = (np.sin(qmax*rth)-np.sin(qmin*rth))/np.pi/rth
        rth[0] = 0.0
        rcv, frcv = cv(r, fr, rth, th)
        mask = np.logical_and(rcv >= r[0]-0.5*rstep, rcv <= r[-1]+0.5*rstep)
        rcv = rcv[mask]
        frcv = frcv[mask]
        # Scale the convolved function back to the scale of the original
        a1 = np.trapz(np.abs(fr),r)        
        a2 = np.trapz(np.abs(frcv),rcv)
        frcv = frcv * a1 / a2
    else:
        rcv, frcv = r, fr

    return rcv, frcv


def calculateDr(r, fr, q, ff, paraScale=1.0, rmintr=-5.0, rmaxtr=5.0,
                drtr=0.01, qmin=0, qmax=-1, K1=None, K2=None):
    """Calculate the unnormalized mPDF quantity D(r).

    This module requires a normalized mPDF as an input, as well as a magnetic
    form factor and associated q grid.

    Args:
        r (numpy array): r grid for the properly normalized mPDF.
        fr (numpy array): the properly normalized mPDF.
        q (numpy array): grid of momentum transfer values used for calculating
            the magnetic form factor.
        ff (numpy array): magnetic form factor. Same shape as ffqgrid.
        paraScale (float): scale factor for the paramagnetic part of the
            unnormalized mPDF function D(r).
        rmintr (float): minimum value of r for the Fourier transform of the
            magnetic form factor required for unnormalized mPDF.
        rmaxtr (float): maximum value of r for the Fourier transform of the
            magnetic form factor required for unnormalized mPDF.
        drtr (float): step size for r-grid used for calculating Fourier
            transform of magnetic form mactor.
        qmin (float): minimum experimentally accessible q-value (to be used
            for simulating termination ripples). If <0, no termination effects
            are included.
        qmax (float): maximum experimentally accessible q-value (to be used
            for simulating termination ripples). If <0, no termination effects
            are included.
        K1 (float): a constant used for calculating Dr; should be averaged
            over all magnetic species. Important if physical information is
            to be extracted from mPDF scale factors, e.g. moment size.
        K2 (float): another constant used for calculating Dr.

    Returns: numpy array for the unnormalized mPDF Dr.
    """
    if K1 is None:
        K1 = 0.66667*(1.913*2.81794/2.0)**2*2.0**2*0.5*(0.5+1)
    if K2 is None:
        K2 = K1
    rsr, sr = cosTransform(q, ff, rmintr, rmaxtr, drtr)
    #### Double-check whether or not I should normalize sr!
    #norm = np.trapz(sr,rsr)
    #sr /= norm
    #sr = np.sqrt(np.pi/2.0)*sr ### I don't think we should multiply by sqrt(pi/2)
    rSr, Sr = cv(rsr, sr, rsr, sr)
    rDr, Dr = cv(r, K1/(2.0*np.pi)*fr, rSr, Sr)
    para = -K2/np.pi*np.gradient(Sr, rSr[1]-rSr[0]) ### paramagnetic term in d(r)
    if qmin >= 0 and qmax > qmin:
        rstep = r[1]-r[0]
        rth = np.arange(0.0, r.max()+rstep, rstep)
        rth[0] = 1e-4*rstep # avoid infinities at r = 0
        th = (np.sin(qmax*rth)-np.sin(qmin*rth))/np.pi/rth
        rth[0] = 0.0
        rpara, para = cv(rSr, para, rth, th)
    else:
        rpara, para = rSr, para
    # make sure para and Dr match up in shape
    dr = r[1]-r[0]
    goodslice = np.logical_and(rDr >= r.min() - 0.5*dr, rDr <= r.max()+0.5*dr)
    Dr = Dr[goodslice]
    para = para[rpara >= r.min()]
    if para.shape[0] < Dr.shape[0]:
        para = np.concatenate((para, np.zeros(Dr.shape[0]-para.shape[0])))
    else:
        para = para[:Dr.shape[0]]
    Dr += paraScale*para
    return Dr

def calculateMagScatt(r, fr, qmin=0.0, qmax=20.0, qstep=0.01, quantity='sq'):
    """Calculate the magnetic scattering via Fourier transform of the mPDF.

    Args:
        r (numpy array): r grid for the properly normalized mPDF.
        fr (numpy array): the mPDF, either normalized or unnormalized.
        qmin (float): minimum value of the output q-grid.
        qmax (float): maximum value of the output q-grid.
        qstep (float): spacing for the q-grid.
            unnormalized mPDF function D(r).
        quantity (str): type of magnetic scattering quantity to return; either
            'sq' or 'iq'. If 'sq', provide properly normalized mPDF; if 'iq',
            provide the unnormalized mPDF.
    Returns: q-grid and associated magnetic scattering.
    """
    if quantity=='sq':
        q, fq = sinTransform(r, fr, qmin, qmax, qstep)
        sq = 1.0*fq
        sq[1:] = fq[1:]/q[1:] + 1
        sq[0] = 0.0
        return q, sq
    elif quantity=='iq':
        q, iqq = sinTransform(r, fr, qmin, qmax, qstep)
        iq = 1.0*iqq
        iq[1:] = iq[1:]/q[1:]
        iq[0] = 0.0
        return q, iq
    else:
        print('Please specify a valid magnetic scattering type (sq or iq).')
        return 0*r, 0*fr

class MPDFcalculator:
    """Create an MPDFcalculator object to help calculate mPDF functions.

    This class is loosely modelled after the PDFcalculator class in diffpy.
    At minimum, it requires a magnetic structure with atoms and spins, and
    it calculates the mPDF from that. Various other options can be specified
    for the calculated mPDF.

    Args:
        magstruc (MagStructure object): provides information about the
            magnetic structure. Must have arrays of atoms and spins.
        calcList (python list): list giving the indices of the atoms array
            specifying the atoms to be used as the origin when calculating
            the mPDF. If given the string argument 'all', then every atom
            will be used (potentially causing very long calculation times).
        maxextension (float): extension of the r-grid on which the mPDF is
            calculated to properly account for contribution of pairs just
            outside the boundary.
        gaussPeakWidth(float): std deviation (in Angstroms) of Gaussian peak
            to be convoluted with the calculated mPDF to simulate thermal
            motion.
        dampRate (float): generalized ("stretched") exponential damping rate
                of the mPDF.
        dampPower (float): power of the generalized exponential function.
        qmin (float): minimum experimentally accessible q-value (to be used
            for simulating termination ripples). If <0, no termination effects
            are included.
        qmax (float): maximum experimentally accessible q-value (to be used
            for simulating termination ripples). If <0, no termination effects
            are included.
        rmin (float): minimum value of r for which mPDF should be calculated.
        rmax (float): maximum value of r for which mPDF should be calculated.
        rstep (float): step size for r-grid of calculated mPDF.
        ordScale (float): overall scale factor for the mPDF function f(r).
        paraScale (float): scale factor for the paramagnetic part of the
            unnormalized mPDF function D(r).
        rmintr (float): minimum value of r for the Fourier transform of the
            magnetic form factor required for unnormalized mPDF.
        rmaxtr (float): maximum value of r for the Fourier transform of the
            magnetic form factor required for unnormalized mPDF.
        drtr (float): step size for r-grid used for calculating Fourier
            transform of magnetic form mactor.
        label (string): Optional descriptive string for the MPDFcalculator.
        """
    def __init__(self, magstruc=None, calcList=[0], maxextension=10.0,
                 gaussPeakWidth=0.1, dampRate=0.0, dampPower=2.0, qmin=0.0,
                 qmax=-1.0, rmin=0.0, rmax=20.0, rstep=0.01,
                 ordScale=1.0, paraScale=1.0, rmintr=-5.0,
                 rmaxtr=5.0, label=''):
        if magstruc is None:
            self.magstruc = []
        else:
            self.magstruc = magstruc
            if magstruc.rmaxAtoms < rmax:
                print('Warning: Your structure may not be big enough for your')
                print('desired calculation range.')
        self.calcList = calcList
        self.maxextension = maxextension
        self.gaussPeakWidth = gaussPeakWidth
        self.dampRate = dampRate
        self.dampPower = dampPower
        self.qmin = qmin
        self.qmax = qmax
        self.rmin = rmin
        self.rmax = rmax
        self.rstep = rstep
        self.ordScale = ordScale
        self.paraScale = paraScale
        self.rmintr = rmintr
        self.rmaxtr = rmaxtr
        self.label = label

    def __repr__(self):
        if self.label == '':
            return 'MPDFcalculator() object'
        else:
            return self.label+': MPDFcalculator() object'

    def calc(self, normalized=True, both=False):
        """Calculate the magnetic PDF.

        Args:
            normalized (boolean): indicates whether or not the normalized mPDF
                should be returned.
            both (boolean): indicates whether or not both normalized and
                unnormalized mPDF quantities should be returned.

        Returns: numpy array giving the r grid of the calculation, as well as
            one or both the mPDF quantities.
        """
        if normalized and not both:
            rcalc, frcalc = calculatemPDF(self.magstruc.atoms, self.magstruc.spins,
                                          self.magstruc.gfactors, self.calcList,
                                          self.rstep, self.rmin, self.rmax,
                                          self.gaussPeakWidth, self.qmin, self.qmax,
                                          self.dampRate, self.dampPower,
                                          self.maxextension, self.ordScale,
                                          self.magstruc.K1)
            mask = (rcalc <= self.rmax + 0.5*self.rstep)            
            return rcalc[mask], frcalc[mask]
        elif not normalized and not both:
            rcalc, frcalc = calculatemPDF(self.magstruc.atoms, self.magstruc.spins,
                                          self.magstruc.gfactors, self.calcList,
                                          self.rstep, self.rmin, self.rmax+self.maxextension,
                                          self.gaussPeakWidth, self.qmin, self.qmax,
                                          self.dampRate, self.dampPower,
                                          self.maxextension, self.ordScale,
                                          self.magstruc.K1)
            Drcalc = calculateDr(rcalc, frcalc, self.magstruc.ffqgrid,
                                 self.magstruc.ff, self.paraScale, self.rmintr,
                                 self.rmaxtr, self.rstep, self.qmin, self.qmax,
                                 self.magstruc.K1, self.magstruc.K2)
            mask = (rcalc <= self.rmax + 0.5*self.rstep)
            return rcalc[mask], Drcalc[mask]
        else:
            rcalc, frcalc = calculatemPDF(self.magstruc.atoms, self.magstruc.spins,
                                          self.magstruc.gfactors, self.calcList,
                                          self.rstep, self.rmin, self.rmax+self.maxextension,
                                          self.gaussPeakWidth, self.qmin, self.qmax,
                                          self.dampRate, self.dampPower,
                                          self.maxextension, self.ordScale,
                                          self.magstruc.K1)
            Drcalc = calculateDr(rcalc, frcalc, self.magstruc.ffqgrid,
                                 self.magstruc.ff, self.paraScale, self.rmintr,
                                 self.rmaxtr, self.rstep, self.qmin, self.qmax,
                                 self.magstruc.K1, self.magstruc.K2)
            mask = (rcalc <= self.rmax + 0.5*self.rstep)
            return rcalc[mask], frcalc[mask], Drcalc[mask]

    def plot(self, normalized=True, both=False, scaled=True):
        """Plot the magnetic PDF.

        Args:
            normalized (boolean): indicates whether or not the normalized mPDF
                should be plotted.
            both (boolean): indicates whether or not both normalized and
                unnormalized mPDF quantities should be plotted.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel(r'r ($\AA$)')
        ax.set_xlim(xmin=self.rmin, xmax=self.rmax)
        if normalized and not both:
            rcalc, frcalc = calculatemPDF(self.magstruc.atoms, self.magstruc.spins,
                                          self.magstruc.gfactors, self.calcList,
                                          self.rstep, self.rmin, self.rmax,
                                          self.gaussPeakWidth, self.qmin, self.qmax,
                                          self.dampRate, self.dampPower,
                                          self.maxextension, self.ordScale,
                                          self.magstruc.K1)
            mask = (rcalc <= self.rmax + 0.5*self.rstep)            
            ax.plot(rcalc[mask], frcalc[mask]) 
            ax.set_ylabel(r'f ($\AA^{-2}$)')
        elif not normalized and not both:
            rcalc, frcalc = calculatemPDF(self.magstruc.atoms, self.magstruc.spins,
                                          self.magstruc.gfactors, self.calcList,
                                          self.rstep, self.rmin, self.rmax+self.maxextension,
                                          self.gaussPeakWidth, self.qmin, self.qmax,
                                          self.dampRate, self.dampPower,
                                          self.maxextension, self.ordScale,
                                          self.magstruc.K1)
            Drcalc = calculateDr(rcalc, frcalc, self.magstruc.ffqgrid,
                                 self.magstruc.ff, self.paraScale, self.rmintr,
                                 self.rmaxtr, self.rstep, self.qmin, self.qmax,
                                 self.magstruc.K1, self.magstruc.K2)
            mask = (rcalc <= self.rmax + 0.5*self.rstep)
            ax.plot(rcalc[mask], Drcalc[mask])
            ax.set_ylabel(r'd ($\AA^{-2}$)')
        else:
            rcalc, frcalc = calculatemPDF(self.magstruc.atoms, self.magstruc.spins,
                                          self.magstruc.gfactors, self.calcList,
                                          self.rstep, self.rmin, self.rmax+self.maxextension,
                                          self.gaussPeakWidth, self.qmin, self.qmax,
                                          self.dampRate, self.dampPower,
                                          self.maxextension, self.ordScale,
                                          self.magstruc.K1)
            Drcalc = calculateDr(rcalc, frcalc, self.magstruc.ffqgrid,
                                 self.magstruc.ff, self.paraScale, self.rmintr,
                                 self.rmaxtr, self.rstep, self.qmin, self.qmax,
                                 self.magstruc.K1, self.magstruc.K2)
            mask = (rcalc <= self.rmax + 0.5*self.rstep)
            if scaled:
                frscl = np.max(np.abs(frcalc))
                drscl = np.max(np.abs(Drcalc[rcalc>1.5]))
                scl = frscl / drscl
            else:
                scl = 1.0
            ax.plot(rcalc[mask], frcalc[mask], 'b-', label='f(r)')
            ax.plot(rcalc[mask], scl * Drcalc[mask], 'r-', label='d(r)')
            ax.set_ylabel(r'f, d ($\AA^{-2}$)')
            plt.legend(loc='best')
        plt.show()

    def runChecks(self):
        """Run some quick checks to help with troubleshooting.
        """
        print('Running checks on MPDFcalculator...\n')

        flagCount = 0
        flag = False

        ### check if number of spins and atoms do not match
        if self.magstruc.atoms.shape[0] != self.magstruc.spins.shape[0]:
            flag = True
        if flag:
            flagCount += 1
            print('Number of atoms and spins do not match; try calling')
            print('makeAtoms() and makeSpins() again on your MagStructure.\n')
        flag = False

        ### check for nan values in spin array
        if np.any(np.isnan(self.magstruc.spins)):
            flag = True
        if flag:
            flagCount += 1
            print('Spin array contains nan values ("not a number").\n')
        flag = False

        ### check if rmax is too big for rmaxAtoms in structure
        for key in self.magstruc.species:
            if self.magstruc.species[key].rmaxAtoms < self.rmax:
                flag = True
        if flag:
            flagCount += 1
            print('Warning: the atoms in your MagStructure may not fill a')
            print('volume large enough for the desired rmax for the mPDF')
            print('calculation. Adjust rmax and/or rmaxAtoms in the')
            print('MagSpecies or MagStructure objects.\n')
        flag = False

        ### check if calcList may not be representative of all MagSpecies.
        if len(self.calcList) < len(self.magstruc.species):
            flag = True
        if flag:
            flagCount += 1
            print('Warning: your calcList may not be representative of all')
            print('the magnetic species. calcList should have the index of')
            print('at least one spin from each species. Use')
            print('magStruc.getSpeciesIdxs() to see starting indices for')
            print('each species.\n')
        flag = False

        ### check if calcList has indices that exceed the spin array
        if (np.array(self.calcList).max()+1) > self.magstruc.atoms.shape[0]:
            flag = True
        if flag:
            flagCount += 1
            print('calcList contains indices that are too large for the')
            print('arrays of atoms and spins contained in the MagStructure.')
        flag = False

        ### check for unphysical parameters like negative scale factors
        if np.min((self.paraScale, self.ordScale)) < 0:
            flag = True
        if flag:
            flagCount += 1
            print('Warning: you have a negative scale factor.')
            print(('Paramagnetic scale = ', self.paraScale))
            print(('Ordered scale = ', self.ordScale))
        flag = False

        if flagCount == 0:
            print('All checks passed. No obvious problems found.\n')

    def rgrid(self):
        """Return the current r grid of the mPDF calculator."""
        return np.arange(self.rmin, self.rmax+self.rstep, self.rstep)

    def copy(self):
        """Return a deep copy of the MPDFcalculator object."""
        return copy.deepcopy(self)

