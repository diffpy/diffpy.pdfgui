#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2007 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Tooltips for pdfgui panels.
"""

def _expand_tooltip_aliases(ttps):
    "Replace aliased equivalent values {other} in tooltip strings."
    isalias = lambda s: (s[1:-1] and s[::len(s) - 1] == '{}' and
                         s[1:-1].replace('_', '').isalnum())
    for n, t in list(ttps.items()):
        if not isalias(t):
            continue
        t1 = t.format(**ttps)
        assert not isalias(t1), "chained tooltip alias is not allowed"
        ttps[n] = t1
    return ttps


datasetconfigurepanel = {
#    'panelNameLabel'      : '', # StaticText "Data Set Configuration"
    'radioBoxStype'       : 'Radiation type', # RadioBox "Scatterer Type", choices=["Neutron", "X-ray"]
    'radioBoxSampling'       : 'Fit sampling type', # RadioBox "Scatterer Type", choices=["Default", "Nyquist", "Custom"]
#    'labelDataRange'      : '', # StaticText "Data Range"
    'textCtrlDataFrom'    : 'Data r_min', # TextCtrl
#    'labelDataTo'         : '', # StaticText "to"
    'textCtrlDataTo'      : 'Data r_max', # TextCtrl
#    'labelFitRange'       : '', # StaticText "Fit Range"
    'textCtrlDataStep'      : 'Step size in the data', # TextCtrl
    'textCtrlFitFrom'     : 'Fit r_min', # TextCtrl
#    'labelFitTo'          : '', # StaticText "to"
    'textCtrlFitTo'       : 'Fit r_max', # TextCtrl
    'textCtrlFitStep'      : 'Step size in the fit', # TextCtrl
#    'labelScaleFactor'    : '', # StaticText "Scale Factor"
    'textCtrlScaleFactor' : 'Data scale factor', # TextCtrl
#    'labelQmax'           : '', # StaticText "Qmax"
    'textCtrlQmax'        : 'Upper limit used for Fourier transform to obtain data PDF', # TextCtrl
#    'labelQdamp'          : '', # StaticText "Qdamp"
    'textCtrlQdamp'       : 'Resolution dampening factor', # TextCtrl
#    'labelQbroad'         : '', # StaticText "Qbroad"
    'textCtrlQbroad'      : 'Resolution peak broadening factor', # TextCtrl
#    'labelTemperature'    : '', # StaticText "Temperature"
    'textCtrlTemperature' : 'Temperature at which the data were collected', # TextCtrl
#    'labelDoping'         : '', # StaticText "Doping"
    'textCtrlDoping'      : 'Sample characteristic doping level (if applicable)', # TextCtrl
    }

datasetconstraintpanel = {
    'panelNameLabel' : '', # StaticText "Data Set Constraints"
    'labelScaleFactor' : '', # StaticText "Scale Factor"
    'textCtrlScaleFactor' : 'Data scale factor', # TextCtrl
    'labelQdamp' : '', # StaticText "Qdamp"
    'textCtrlQdamp' : 'Resolution dampening factor', # TextCtrl
    'labelQbroad' : '', # StaticText "Qbroad"
    'textCtrlQbroad' : 'Resolution peak broadening factor', # TextCtrl
    }

datasetresultspanel = {
    'panelNameLabel' : '', # StaticText "Data Set Results"
    'labelScaleFactor' : '', # StaticText "Scale Factor"
    'textCtrlScaleFactor' : 'Data scale factor', # TextCtrl
    'labelQdamp' : '', # StaticText "Qdamp"
    'textCtrlQdamp' : 'Resolution dampening factor', # TextCtrl
    'labelQbroad' : '', # StaticText "Qbroad"
    'textCtrlQbroad' : 'Resolution peak broadening factor', # TextCtrl
    }



dopingseriespanel = {
#    'instructionsLabel' : '', # StaticText "Select a fit from the tree on the left then add datasets and assign\ndoping elements and values below. If you have not set up a fit to be\nthe template for the series, hit cancel and rerun this macro once a\nfit has been created."
#    'labelBaseElement' : '', # StaticText "Base element"
#    'textCtrlBaseElement' : '', # TextCtrl
#    'labelDopant' : '', # StaticText "Dopant"
#    'textCtrlDopant' : '', # TextCtrl
    'listCtrlFiles' : 'Click header to sort by doping', # AutoWidthListCtrl
#    'buttonUp' : '', # BitmapButton
#    'buttonDown' : '', # BitmapButton
#    'buttonAdd' : '', # Button "Add"
#    'buttonDelete' : '', # Button "Delete"
#    'goButton' : '', # Button "OK"
#    'cancelButton' : '', # Button "Cancel"
    }

phasepanel = _expand_tooltip_aliases({
#    'sizerLatticeParameters_staticbox' : '', # StaticBox
#    'sizerAdditionalParameters_staticbox' : '', # StaticBox
#    'sizerAtoms_staticbox' : '', # StaticBox
#    'sizerPanelName_staticbox' : '', # StaticBox
#    'labelPanelName' : '', # StaticText "Phase Configuration"
    'labelA' : '{textCtrlA}', # StaticText "a"
    'textCtrlA' : 'Lattice parameter a', # TextCtrl
    'labelB' : '{textCtrlB}', # StaticText "b"
    'textCtrlB' : 'Lattice parameter b', # TextCtrl
    'labelC' : '{textCtrlC}', # StaticText "c"
    'textCtrlC' : 'Lattice parameter c', # TextCtrl
    'labelAlpha' : '{textCtrlAlpha}', # StaticText "alpha"
    'textCtrlAlpha' : 'Lattice angle alpha', # TextCtrl
    'labelBeta' : '{textCtrlBeta}', # StaticText "beta"
    'textCtrlBeta' : 'Lattice angle beta', # TextCtrl
    'labelGamma' : '{textCtrlGamma}', # StaticText "gamma"
    'textCtrlGamma' : 'Lattice angle gamma', # TextCtrl
    'labelScaleFactor' : '{textCtrlScaleFactor}', # StaticText "Scale Factor"
    'textCtrlScaleFactor' : 'Phase scale factor', # TextCtrl
    'labelDelta1' : '{textCtrlDelta1}', # StaticText "delta1"
    'textCtrlDelta1' : 'Linear atomic correlation factor', # TextCtrl
    'labelDelta2' : '{textCtrlDelta2}', # StaticText "delta2"
    'textCtrlDelta2' : 'Quadratic atomic correlation factor', # TextCtrl
    'labelSratio' : '{textCtrlSratio}', # StaticText "sratio"
    'textCtrlSratio' : 'Low r peak sharpening', # TextCtrl
    'labelRcut' : '{textCtrlRcut}', # StaticText "rcut"
    'textCtrlRcut' : 'Peak sharpening cutoff', # TextCtrl
    'labelStepcut' : '{textCtrlStepcut}', # StaticText "stepcut"
    'textCtrlStepcut' : 'Cutoff for profile step-function', #TextCtrl
    'labelSpdiameter'     : '{textCtrlSpdiameter}', # StaticText "Spdiameter"
    'textCtrlSpdiameter' : 'Spherical nanoparticle amplitude correction',
#    'labelIncludedPairs' : '', # StaticText "Included Pairs"
    'textCtrlIncludedPairs' :
"""[!]{element|indexOrRange|all}-[!]{element|indexOrRange|all}
Examples:
all-all              all possible pairs
Na-Na                only Na-Na pairs
all-all, !Na-        all pairs except Na-Na
all-all, -!Na        same as previous
Na-1:4               pairs of Na and first 4 atoms
all-all, !Cl-!Cl     exclude any pairs containing Cl
all-all, !Cl-, -!Cl  same as previous
1-all                only pairs including the first atom""", # TextCtrl "all-all"
#    'gridAtoms' : '', # AutoWidthLabelsGrid
})


plotpanel = {
#    'xDataCombo' : '', # ComboBox
#    'yDataList' : '', # KeyEventsListCtrl
    'offsetLabel' : 'The vertical gap between stacked plots', # StaticText "offset"
#    'offsetTextCtrl' : '', # TextCtrl
    'plotButton' : 'Plot the selected data', # Button "Plot"
    'resetButton' : 'Reset the plot configuration', # Button "Reset"
    }


preferencespanel = {
    'structureDirCheckBox' : (
        "Remember the structures directory across sessions.  "
        "If unchecked, the initial structures directory will "
        "default to the current path."
    ),

    'dataDirCheckBox' : (
        "Remember the data set directory across sessions.  "
        "If unchecked, the initial data set directory will "
        "default to the current path."
    ),

    'textCtrlViewer' : (
        "The name of the structure viewer executable, "
        "e.g., 'atomeye' or 'pymol'."
    ),

    'textCtrlArgument' : \
        """\
The command-line arguments to the structure viewer.
'%s' represents the file name that will be passed to the viewer.
Command-line switches placed here will be passed as well.
E. g. '%s' or '-c %s' (for pymol).\
        """,

    'choiceFormat' : 'Choose a file format the structure viewer accepts.'
}


temperatureseriespanel = {
#    'instructionsLabel' : '', # StaticText "Select a fit from the tree on the left then add datasets and assign\ntemperatues below. If you have not set up a fit to be the template\nfor the series, hit cancel and rerun this macro once a fit has been\ncreated."
    'listCtrlFiles' : 'Click header to sort by temperature', # AutoWidthListCtrl
#    'buttonUp' : '', # BitmapButton
#    'buttonDown' : '', # BitmapButton
#    'buttonAdd' : '', # Button "Add"
#    'buttonDelete' : '', # Button "Delete"
#    'goButton' : '', # Button "OK"
#    'cancelButton' : '', # Button "Cancel"
    }
