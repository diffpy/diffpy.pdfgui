#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""class Parameter for handling one refined parameter
To be stored in Fitting.parameters { idx : parameter } dictionary
"""

import six

from diffpy.pdfgui.control.controlerrors import \
        ControlTypeError, ControlKeyError, ControlRuntimeError, ControlError

class Parameter:
    """Parameter is class for value and properties of refined parameter.
    Because the initial value of Parameter may come from another Fitting,
    it is accessed by setInitial(), initialStr() and initialValue() methods.

    Data members:
        idx       -- integer identifier of this parameter in PdfFit
        name      -- optional description
        refined   -- refined value of the parameter, float or None.
        fixed     -- flag for fixing the parameter in refinement [False]

    Private members:
        __initial -- stores the initial value, float, or "=fitname:idx" string
        __fitrepr -- None or string representation of Fitting instance
    """
    # fits should reference PDFGuiControl.fits

    def __init__(self, idx, initial=0.0):
        """Initialize new parameter

        idx     -- idx of this parameter in PdfFit
        initial -- optional initial value of the parameter.
                   It can be float, Fitting, "=fitname" or "=fitname:idx" string.
        """
        self.idx = idx
        self.name = ''
        self.refined = None
        self.fixed = False
        self.__initial = None
        self.__fitrepr = None
        self.setInitial(initial)
        return

    def setInitial(self, initial):
        """set initial value to float or refined value from another Fitting.

        initial -- initial value, it can be something convertible to float,
                   Fitting reference or string in "=fitname" or
                   "=fitname:idx" format.
        """
        self.__fitrepr = None
        from diffpy.pdfgui.control.fitting import Fitting
        try:
            self.__initial = float(initial)
            return
        except (ValueError, TypeError):
            pass
        if isinstance(initial, Fitting):
            self.__initial = "=" + initial.name
            self.__fitrepr = repr(initial)
        elif isinstance(initial, six.string_types) and initial[:1] == '=':
            self.__initial = initial
            self.__findLinkedFitting()
        else:
            raise ControlTypeError("invalid type of Parameter initial value")
        return

    def initialStr(self):
        """Convert initial value to string.

        returns string in "=fitname:idx" or "%f" format
        """
        if isinstance(self.__initial, float):
            s = str(self.__initial)
        else:
            self.__findLinkedFitting()
            s = self.__initial
        return s

    def initialValue(self):
        """Convert initial value to float.
        For linked parameters it may raise:
            ControlKeyError      if source Fitting does not exist
            KeyError             when parameter does not exist
            ControlRunTimeError  for self-dependent parameters

        returns the initial value
        """
        if isinstance(self.__initial, float):
            value = self.__initial
        else:
            try:
                value = self.__getLinkedValue()
            except RuntimeError as v:
                # we will catch only recursion RuntimeError
                if "maximum recursion" in str(v):
                    raise ControlRuntimeError("self-dependent parameter")
                # other RuntimeError should be left alone
                else:
                    raise
        return float(value)

    def __getLinkedValue(self):
        """Private retrieval of parameter value from linked Fitting.
        """
        # Check to see if the fit name has a ':' in it
        isplit = self.__initial.split(':')
        # Who needs regular expressions?
        try:
            if len(isplit) == 1:
                srcidx = self.idx
                fitname = self.__initial[1:]
            else:
                srcidx = int(isplit[-1])
                fitname = (':'.join(isplit[:-1]))[1:]
        except ValueError:
            # __initial should be in the form "=fitname[:srcidx]"
            raise ControlError("Malformed linked parameter %s" % self.__initial)
        srcfit = self.__findLinkedFitting()
        if srcfit is None:
            raise ControlKeyError("Fitting '%s' does not exist" % fitname)
        # Check to see if srcfit has paramter srcidx
        try:
            srcpar = srcfit.parameters[srcidx]
        except KeyError:
            raise ControlKeyError("Fitting '%s' has no parameter %s" % (fitname, srcidx))

        if srcpar.refined is not None:
            value = srcpar.refined
        elif isinstance(srcpar.__initial, float):
            value = srcpar.__initial
        else:
            value = srcpar.__getLinkedValue()
        return value

    def __findLinkedFitting(self):
        """Private search for linked Fitting by name and by representation.
        Should be called only when initial value is linked to another
        Fitting.  Updates self.__initial and self.__fitrepr.

        returns reference to Fitting when found or None
        """
        # Check to see if the fit name has a ':' in it
        isplit = self.__initial.split(':')
        try:
            srcidx = int(isplit[-1])
            fitname = (':'.join(isplit[:-1]))[1:]
        except ValueError:
            fitname = self.__initial[1:]
            srcidx = self.idx
            self.__initial += ":%i" % srcidx
        from diffpy.pdfgui.control.pdfguicontrol import pdfguicontrol
        fits = pdfguicontrol().fits
        fitnames = [ f.name for f in fits ]
        fitrepres = [ repr(f) for f in fits ]
        # first find linked fitting by name
        if fitname in fitnames:
            idx = fitnames.index(fitname)
            self.__fitrepr = fitrepres[idx]
            ref = fits[idx]
        # if not found by name, look up by representation
        elif self.__fitrepr in fitrepres:
            idx = fitrepres.index(self.__fitrepr)
            self.__initial = "=%s:%i" % (fitnames[idx], srcidx)
            ref = fits[idx]
        # here self.__initial was not found, but let it pass
        # maybe the linked fitting will be defined later
        else:
            self.__fitrepr = None
            ref = None
        return ref

# End of class Parameter
