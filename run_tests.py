#!/usr/bin/env python

import diffpy.pdfgui.tests


def run_tests():
    assert diffpy.pdfgui.tests.test().wasSuccessful()
    assert diffpy.pdfgui.tests.testdeps().wasSuccessful()


if __name__ == "__main__":
    run_tests()
