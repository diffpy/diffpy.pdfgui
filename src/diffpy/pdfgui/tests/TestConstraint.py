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

"""Unit tests for constraint.py
"""


import unittest

from diffpy.pdfgui.control.controlerrors import ControlSyntaxError
from diffpy.pdfgui.control.constraint import Constraint

##############################################################################
class TestConstraint(unittest.TestCase):
    """test methods of TestConstraint"""

    def setUp(self):
        self.c = Constraint('@1')
        return

    def test___init__(self):
        """check Constraint.__init__()
        """
        self.assertTrue(1 in self.c.parguess)
        self.assertEqual(1, len(self.c.parguess))
        c1 = Constraint('2*@2 + 3.0', 13.0)
        self.assertEqual(1, len(c1.parguess))
        self.assertEqual(5.0, c1.parguess[2])
        return

    def test_guess(self):
        """check Constraint.guess()
        """
        self.c.guess(9)
        self.assertEqual(1, len(self.c.parguess))
        self.assertEqual(9, self.c.parguess[1])
        return

    def test___setattr__(self):
        """check Constraint.__setattr__()
        """
        self.c.guess(9)
        self.c.formula = '9*@7 +18'
        self.assertEqual(1, len(self.c.parguess))
        self.assertEqual(-1.0, self.c.parguess[7])
        self.assertRaises(ControlSyntaxError, setattr,
                self.c, 'formula', '')
        self.assertRaises(ControlSyntaxError, setattr,
                self.c, 'formula', '@@1')
        self.assertRaises(ControlSyntaxError, setattr, self.c,
                'formula', '@1*/55')
        self.assertRaises(ControlSyntaxError, setattr, self.c,
                'formula', '@1**3')
        return

    def test_evalFormula(self):
        """check Constraint.evalFormula()
        """
        value = self.c.evalFormula({1 : 5.0})
        self.assertEqual(5.0, value)
        self.c.formula = 'sin(@3)'
        from math import pi, sqrt
        value = self.c.evalFormula({3 : pi/3.0})
        self.assertAlmostEqual(sqrt(0.75), value, 8)
        return

# End of class TestConstraint

if __name__ == '__main__':
    unittest.main()

# End of file
