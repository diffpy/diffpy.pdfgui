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


import sys,os
#sys.path.append(os.getcwd()+'/../control')
from pdfgui.control.pdfguicontrol import pdfguicontrol
from pdfgui.control.controlerrors import *
from pdfgui.control.constraint import Constraint
from pdfgui.control.plotter import Plotter
import __main__

import wx
import copy

## simpel gui application ##
class PDFApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        #controlFrame = ControlFrame(None, -1, "", [50,50],[960,700])
        #self.SetTopWindow(controlFrame)
        #controlFrame.Show()
        return 1

class PDFFrame ( wx.Frame ):
    UPDATE = 1
    ERROR = 2
    def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        panel = wx.Panel(self, -1)
        staticText = wx.StaticText( panel, -1, "PDFFit is running",
                                     (160, 70), (-1, -1), wx.ALIGN_CENTER)
        staticText.SetBackgroundColour('Yellow')
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow, self)
        
    def onCloseWindow(self, event):
        #self.control.cleanup(False, True) # no save, force exit
        #self.control.exit()
        self.Destroy()
        
    def lock(self):
        if not wx.Thread_IsMain():
            wx.MutexGuiEnter()
    
    def unlock(self):
        if not wx.Thread_IsMain():
            wx.MutexGuiLeave()
            
    def onFittingStatusChanged(self, name, fitStatus,jobStatus):            
        pass

    def postEvent(self, type, info):
        print "MSG:type=%i,info=%s"%(type, info )

## end of class PDFApp

def _build(cfg, pathname):
    """fill up pdfguicontrol according to cfg"""
    control = pdfguicontrol()
    for fitInfo in cfg:
        # insert fitting and set up
        fitting = control.newFitting(fitInfo[0]) 

        # set parameters
        #for par,val in fitInfo[1].items():
        #  fitting.setpar(par,val)
        for dataInfo in fitInfo[2]:
            # load data and set up
            data = control.loadDataset(fitting, pathname + dataInfo[1], dataInfo[0] )
            constraints = dataInfo[3]
            cfg = dataInfo[2]
            for var, formula in constraints.items():
                data.constraints[var] = Constraint(formula)
            for k, v in cfg.items():
                setattr(data, k, v ) 
        
        for strucInfo in fitInfo[3]:
            # load strucutre
            struc = control.loadStructure(fitting, pathname + strucInfo[1], strucInfo[0] )
            constraints = strucInfo[2]
            for var, formula in constraints.items():
                struc.constraints[var] = Constraint(formula)
    return control


def _start():
    control = pdfguicontrol()
    control.start(control.fits)

def _plot():
    control = pdfguicontrol()
    ids = [ fit.datasets[0] for fit in control.fits ]
    ids2 = [ fit.phases[0] for fit in control.fits ]
   
    control.plot('r', ['Gobs', 'Gcalc'], ids, True, 3.0)
    control.plot('step', ['lat(1)'], ids2, False, step=None)
    control.plot('step', [1,100], control.fits, True, step=None)

def _rstart():
    hostCfg = { 'name'              : 'musolffc', 
                #'host'              : 'musolffc.pa.msu.edu',
                'host'              : 'pannonia.pa.msu.edu',
                'port'              : '22',
                'use_default_port'  : True,
                # 0=password, 1=RSA, 2=DSA
                'authentication'    : 1,
                'username'          : 'jiwuliu',
                #'username'          : 'PDFuser',
                #'password'          : 'danse&05',
                'use_default_path'  : True,
                'path'              : '',
                'passphrase'        : ''
              }
    control = pdfguicontrol()
    control.setHost(hostCfg)
    control.start(control.fits)
 
def main():
    app = PDFApp(0)     
    frame = PDFFrame(None, -1, "PDFFit")
    control = pdfguicontrol(gui=frame)  
    frame.control = control
    frame.Show()

    import lcmocfg,nicfg
    #cfg = lcmocfg.buildConfig()
    cfg = nicfg.buildConfig()

    import sys,os
    if len(sys.argv) > 1:
      pathname = sys.argv[1] + '/'
    else:
      pathname = 'testdata/' # default folder
    
    ######### Run #########
    try:
        try:
            control = _build(cfg, pathname)
            #control.startQueue()
            #control.load(pathname + 'test.ddp')
            #_plot()
            #_rstart()
            control.save(pathname + 'ni.ddp')
            app.MainLoop()
        finally:
            control.close(True)
            control.exit()
    except ControlError, error:
        print "Control Error: %s"%error.info  

if __name__ == '__main__':
    main()
