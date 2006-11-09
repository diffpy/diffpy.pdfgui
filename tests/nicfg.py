#!/usr/bin/env python
########################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Jiwu Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################


"""Generate a configuration for LCMO refinement, using LCMO data in the same directory"""
def _dataConstraints():
    """set constraints for data
    return value: a constraint dict
    """
    constraints = {}
    constraints['dscale']='@100'
    return constraints

def _strucConstraints():
    """set constraints for structure
    return value: a constraint dict
    """
    constraints = {}
    constraints['lat(1)']='@1'
    constraints['lat(2)']='@1'
    constraints['lat(3)']='@1'
    return constraints
    
def _parameters():
    """set parameters
    return value: parameters dict
    """
    parameters = {}
    parameters[1]=3.56
    parameters[100]=1.0 
    return parameters

def _dataCfg():
    cfg = {}
    cfg['qmax'] = 30.0
    cfg['sigmaq'] = 0.0
    cfg['stype'] = 'N'
    cfg['fitrmin'] = 1.5
    cfg['fitrmax'] = 10.0
    return cfg
    
dataInfos = [['Ni','Ni.dat'], ]
strucInfos = [['Ni', 'Ni.stru'],]

def buildConfig():
    """build config for Ni project"""
    # Prepare 
    dataConstraints = _dataConstraints()
    strucConstraints = _strucConstraints()
    dataCfg = _dataCfg()
    parameters = _parameters()

    allFits = []
    # dataList: name filename dataCfg dataConstraints
    struc = [ strucInfos[0][0], strucInfos[0][1], strucConstraints]
    for dataInfo in dataInfos:
        data = [dataInfo[0], dataInfo[1], dataCfg, dataConstraints]

        allFits.append( ('fit-' + dataInfo[0], parameters, (data,), (struc,) ))
    return allFits

if __name__ == '__main__':
    print buildConfig()
