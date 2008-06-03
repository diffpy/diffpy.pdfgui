#!/usr/bin/env python

"""Unit tests for bugreport.py
"""

# version
__id__ = '$Id$'

import re
import unittest

import diffpy.pdfgui.bugreport
from diffpy.pdfgui.bugreport import submitBugReport
from diffpy.pdfgui.bugreport import getFormAction


##############################################################################
class Test_submitBugReport(unittest.TestCase):

    SAVE_bugreport_FORM_URL = diffpy.pdfgui.bugreport.FORM_URL

    def setUp(self):
        return

    def tearDown(self):
        """Restore constants in the bugreport module.
        """
        diffpy.pdfgui.bugreport.FORM_URL = self.SAVE_bugreport_FORM_URL
        return

    def test_invalid_arguments(self):
        """check submitBugReport() handling of arguments
        """
        nosummary = {'description' : 'example description'}
        nodescription = {'summary' : 'example summary'}
        self.assertRaises(KeyError, submitBugReport, nosummary)
        self.assertRaises(KeyError, submitBugReport, nodescription)
        return

    def test_failed_posting(self):
        """check submitBugReport raises IOError, when posting fails.
        """
        import time
        import urlparse
        formfields = {
            "summary" : "TestBugReport, do not post.",
            "description" : "posted by test_failed_posting, " + time.ctime(),
        }
        # make FORM url invalid
        diffpy.pdfgui.bugreport.FORM_URL = urlparse.urljoin(
                diffpy.pdfgui.bugreport.ROOT_URL, "does/not/exist/")
        self.assertRaises(IOError, submitBugReport, formfields)
        return


# End of class Test_submitBugReport

##############################################################################

HTMLFORM = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>

<head>
  <title>Bug submission form</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body>
<form action="/check/action0" method="POST">
  Reporter:
  <input type="text" name="reporter" size=64 maxlength=256><br>

  Summary:
  <input type="text" name="summary" size=64 maxlength=1024><br>
</form>

<form action="/check/action1" method="POST">
  Reporter:
  <input type="text" name="reporter" size=64 maxlength=256><br>

  Summary:
  <input type="text" name="summary" size=64 maxlength=1024><br>
</form>
</body>

</html>
"""

class Test_getFormAction(unittest.TestCase):

    def test_getFormAction(self):
        """check getFormAction return value.
        """
        self.assertEqual('/check/action0', getFormAction(HTMLFORM))
        return

    def test_missing_action(self):
        """check if missing form action raises ValueError.
        """
        noaction = re.sub(r'(?s)<body>.*</body>', '<body>\n</body>',
                HTMLFORM)
        self.assertRaises(ValueError, getFormAction, noaction)
        return

    def test_invalid_html(self):
        """check if invalid HTML raises ValueError.
        """
        badhtml = re.sub(r'(?s)<body>.*', '<bo', HTMLFORM)
        self.assertRaises(ValueError, getFormAction, badhtml)
        return

# End of class Test_getFormAction

if __name__ == '__main__':
    unittest.main()

# End of file
