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
    constraints['lat(2)']='@2'
    constraints['lat(3)']='@3'
    constraints['delta1']='@102'
    for i in range (1,5):
       constraints["u11(%i)"%i]='@7'
       constraints["u22(%i)"%i]='@7'
       constraints["u33(%i)"%i]='@7'
    for i in range (5,9):
       constraints["u11(%i)"%i]='@8'
       constraints["u22(%i)"%i]='@8'
       constraints["u33(%i)"%i]='@8'
    for i in range (9,13):
       constraints["u11(%i)"%i]='@9'
       constraints["u22(%i)"%i]='@9'
       constraints["u33(%i)"%i]='@9'
    for i in range (13,21):
       constraints["u11(%i)"%i]='@10'
       constraints["u22(%i)"%i]='@10'
       constraints["u33(%i)"%i]='@10'
    constraints['x(1)']="1.0+@21"
    constraints['y(1)']="0.0+@22"
    constraints['x(2)']="0.5+@21"
    constraints['y(2)']="0.5-@22"
    constraints['x(3)']="0.0-@21"
    constraints['y(3)']="1.0-@22"
    constraints['x(4)']="0.5-@21"
    constraints['y(4)']="0.5+@22"
    constraints['x(9)']="0.0+@23"
    constraints['y(9)']="0.0+@24"
    constraints['x(10)']="0.5+@23"
    constraints['y(10)']="0.5-@24"
    constraints['x(11)']="1.0-@23"
    constraints['y(11)']="1.0-@24"
    constraints['x(12)']="0.5-@23"
    constraints['y(12)']="0.5+@24"
    constraints['x(13)']="0.0+@25"
    constraints['y(13)']="0.0+@26"
    constraints['z(13)']="0.0+@27"
    constraints['x(14)']="-0.5+@25"
    constraints['y(14)']="0.5-@26"
    constraints['z(14)']="1.0-@27"
    constraints['x(15)']="1.0-@25"
    constraints['y(15)']="1.0-@26"
    constraints['z(15)']="0.5+@27"
    constraints['x(16)']="0.5-@25"
    constraints['y(16)']="0.5+@26"
    constraints['z(16)']="0.5-@27"
    constraints['x(17)']="1.0-@25"
    constraints['y(17)']="1.0-@26"
    constraints['z(17)']="1.0-@27"
    constraints['x(18)']="0.5-@25"
    constraints['y(18)']="0.5+@26"
    constraints['z(18)']="0.0+@27"
    constraints['x(19)']="0.0+@25"
    constraints['y(19)']="0.0+@26"
    constraints['z(19)']="0.5-@27"
    constraints['x(20)']="-0.5+@25"
    constraints['y(20)']="0.5-@26"
    constraints['z(20)']="0.5+@27"
    return constraints
    
def _parameters():
    """set parameters
    return value: parameters dict
    """
    parameters = {}
    parameters[1]='lat(1)'
    parameters[2]='lat(2)'
    parameters[3]='lat(3)'
    parameters[100]=1.0 #0.992
    parameters[102]=1.0 #1.23
    parameters[7]='u11(1)'
    parameters[8]='u11(5)'
    parameters[9]='u11(9)'
    parameters[10]='u11(13)'
    parameters[21]=-0.00390
    parameters[22]='y(1)'
    parameters[23]='x(9)'
    parameters[24]='y(9)'
    parameters[25]='x(13)'
    parameters[26]='y(13)'
    parameters[27]='z(13)'
    return parameters

def _dataCfg():
    cfg = {}
    cfg['qmax'] = 32.0
    cfg['sigmaq'] = 0.0
    cfg['stype'] = 'N'
    cfg['fitrmin'] = 1.7
    cfg['fitrmax'] = 14.0
    return cfg
    
dataInfos = [['d980','r980K.gr'], 
            ['d650','r650K.gr'], 
            ['d550','r550K.gr'],  
            ['d800','r800K.gr'], 
            ['d730','r730K.gr'],  
            ['d300','r300K.gr'], 
            ['d700','r700K.gr'], 
            ['d750','r750K.gr'], 
            ['d740','r740K.gr'], 
            ['d720','r720K.gr']]
strucInfos = [['LaMnO3','LaMnO3.stru'],]

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
