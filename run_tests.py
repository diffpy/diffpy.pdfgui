#!/usr/bin/env python

import unittest

import diffpy.pdfgui.tests


class TestPDFGui(unittest.TestCase):

    def test_main_suite(self):
        self.assertTrue(diffpy.pdfgui.tests.test().wasSuccessful())

    def test_deps_suite(self):
        self.assertTrue(diffpy.pdfgui.tests.testdeps().wasSuccessful())


if __name__ == "__main__":
    unittest.main()
