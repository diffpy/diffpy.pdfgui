#!/usr/bin/env python

import diffpy.pdfgui.tests

assert diffpy.pdfgui.tests.test().wasSuccessful()
assert diffpy.pdfgui.tests.testdeps().wasSuccessful()
