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

"""class Constraint for storage of a single constraint equation
constraints will be stored in { variable : constraint } dictionary
"""

import re
import math

from diffpy.pdfgui.control.controlerrors import ControlSyntaxError

class Constraint:
    """Constraint --> storage and check of a single constraint equation

    Data members:
        formula  -- right-side of constraint equation (string).  When
                    assigned it is checked for math correctness and updates
                    the parguess dictionary
        parguess -- read-only dictionary of parameter indices and their
                    estimated initial values.  Values are None if they
                    cannot be estimated.

    Private members:
        __lhs    -- last value of constrained variable passed to guess()
    """

    def __init__(self, formula, value=None):
        """initialize the Constraint.

        formula  -- (string) right-side of constraint equation
        value    -- (optional) current value of the variable

        __init__ raises ControlSyntaxError when formula is incorrect
        """
        # initialize private members firsts
        self.__lhs = None
        self.parguess = { }
        # initialize formula member avoid __setattr__
        self.__dict__['formula'] = 'None'
        # formula should be assigned as a last one
        self.formula = formula
        if value is not None:
            self.guess(value)
        return

    def evalFormula(self, parvalues):
        """evaluate constraint formula

        parvalues -- dictionary of int parameter indices and float values.

        returns formula result
        """
        fncp = self.lambdaFormula()
        result = fncp(parvalues)
        return result

    def lambdaFormula(self):
        """Build lambda function from constraint formula.
        Lambda function expects dictionary argument.

        returns lambda function
        """
        expr = re.sub(r'@(\d*)', r'p[\1]', self.formula)
        f = eval('lambda p:' + expr, vars(math))
        return f

    def guess(self, value):
        """guess the initial values of parameters contained in parguess

        value -- current value of the constrained variable

        The keys of self.parguess are indices of parameters used in formula,
        and the values are suggested parameter values (None if they cannot
        be estimated).

        returns a copy of self.parguess
        """
        self.__lhs = float(value)
        for k in self.parguess:
            self.parguess[k] = None
        # solve linear formulas of one variable
        if len(self.parguess) == 1:
            fncp = self.lambdaFormula()
            # check if fncp is linear with eps precision
            try:
                eps = 1.0e-8
                lo, hi = 1.0 - eps ,  1.0 + eps
                k, = self.parguess.keys()
                y = [ fncp({k : 0.25}), fncp({k : 0.5}), fncp({k : 0.75}) ]
                dy = [ y[1] - y[0],  y[2] - y[1] ]
                ady = [ abs(z) for z in dy ]
                if lo*ady[0] <= ady[1] <= hi*ady[0] and dy[0]!=0.0:
                    a = 4*dy[0]
                    b = y[1] - 0.5*a
                    self.parguess[k] = (value-b)/a
            except (ValueError, ZeroDivisionError):
                pass
        return dict(self.parguess)

    def __setattr__(self, name, value):
        """check math and update parguess when formula is assigned
        """
        if name != "formula":
            self.__dict__[name] = value
            return
        # here we are assigning to formula
        # first we need to check it it is valid
        newformula = value
        pars = re.findall(r'@\d+', newformula)
        # require at least one parameter in the formula
        if len(pars) == 0:
            message = "No parameter in formula '%s'" % newformula
            raise ControlSyntaxError(message)
        try:
            # this raises ControlSyntaxError if newformula is invalid
            # define fncx in math module namespace
            fncx = eval('lambda x:' +
                        re.sub(r'@\d+', 'x', newformula), vars(math))
            # check if fncx(0.25) is float
            fncx(0.25) + 0.0
        except (ValueError, SyntaxError, TypeError, NameError):
            message = "invalid constraint formula '%s'" % newformula
            raise ControlSyntaxError(message)
        # few more checks of the formula:
        if newformula.find('**') != -1:
            emsg = ("invalid constraint formula '{}', "
                    "operator '**' not supported.").format(newformula)
            raise ControlSyntaxError(emsg)
        # checks checked
        self.__dict__['formula'] = newformula
        self.parguess = dict.fromkeys([ int(p[1:]) for p in pars ])
        if self.__lhs is not None:
            self.guess(self.__lhs)
        return

# End of class Constraint

# End of file
