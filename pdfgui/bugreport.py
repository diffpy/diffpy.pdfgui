#!/usr/bin/env python
########################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################

"""Routines for submitting bugreport through www.diffpy.org.
"""

# version
__id__ = "$Id$"

import urlparse
import HTMLParser
from diffpy.pdfgui.control.controlerrors import ControlError
from diffpy.pdfgui import __version__


# constants:

ROOT_URL = "http://www.diffpy.org/"
FORM_URL = urlparse.urljoin(ROOT_URL, "bugreport/pdfgui/")
FORM_REALM = "diffpy"
FORM_USER = "diffuser"
FORM_ENCPW = "LPR3rU9s"


# Routines

def submitBugReport(formfields):
    """Fill in and submit bugreport form at FORM_URL.
    The post url is obtained by parsing the first HTML form.

    formfields -- dictionary containing the keys.  When optional
                  fields are not specified, use defaults as listed:

                  "reporter"    optional, ["anonymous"]
                  "summary"     required
                  "description" required
                  "component"   optional, ["pdfgui"]
                  "version"     optional, [current version of PDFgui]
                  "traceback"   optional, [""]

                  All values get stripped from leading and trailing spaces.
                  Any other keys in formfields are ignored.

    No return value.
    Raise KeyError when formfields does not have required keys.
    Raise IOError on failed posting.
    """
    import urllib
    import urllib2
    import cookielib
    from diffpy.pdfgui import __version__
    # build dictionary with default values:
    formdata = {
        "reporter" : formfields.get("reporter", "").strip() or "anonymous",
        "summary" : formfields["summary"],
        "description" : formfields["description"],
        "component" : formfields.get("component", "pdfgui"),
        "version" : formfields.get("version", __version__),
        "traceback" : formfields.get("traceback", ""),
    }
    # format formdata items:
    for k in formdata:
        formdata[k] = formdata[k].strip()
    if formdata["description"]:
        formdata["description"] += "\n"
    if formdata["traceback"]:
        formdata["traceback"] = "\n" + formdata["traceback"] + "\n"
    # open FORM_URL
    handler = urllib2.HTTPBasicAuthHandler()
    handler.add_password(FORM_REALM, ROOT_URL,
            FORM_USER, FORM_ENCPW.encode('rot13'))
    cookier = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
    opener = urllib2.build_opener(handler, cookier)
    formcontent = opener.open(FORM_URL).read()
    # find where does the form post its data
    try:
        action = getFormAction(formcontent)
    # raise invalid web form as IOError so there is a meaningful error message
    except HTMLParser.HTMLParseError, err:
        emsg = "Invalid webform - %s" % err
        raise IOError, emsg
    post_url = urlparse.urljoin(FORM_URL, getFormAction(formcontent))
    post_headers = {'User-agent' : 'PDFgui (compatible; MSIE 5.5; WindowsNT)'}
    post_content = urllib.urlencode(formdata)
    post_request = urllib2.Request(post_url, post_content, post_headers)
    post_handle = opener.open(post_request)
    # result can be obtained by post_handle.read(), but it is not needed
    return


def getFormAction(content):
    """Extract action attribute from the first form in HTML document.

    content -- HTML code

    Return string.
    Raise ValueError if form action attribute is not defined.
    Raise HTMLParseError for invalid HTML code.
    """
    extract_action = _HTMLFormActionGetter()
    action = extract_action(content)
    return action


# Helper classes


class _HTMLFormActionGetter(HTMLParser.HTMLParser):
    """Helper HTMLParser for extracting action attriubte from the
    first form.
    
    Instance data:
    
    _form_actions   -- list of action values from all <form> tags found.

    See also getFormAction().
    """


    # declaration of instance data attributes
    _form_actions = None


    def handle_starttag(self, tag, attrs):
        """Store "action" attributes from all HTML forms in _form_actions.
        """
        if tag == "form":
            dattr = dict(attrs)
            self._form_actions.append(dattr.get("action"))
        return


    def __call__(self, content):
        """Obtain action from the first form in the document.

        content -- HTML code

        Return action string.
        Raise ValueError when there is no form or when action is not defined.
        """
        self.reset()
        self._form_actions = []
        self.feed(content)
        self.close()
        if len(self._form_actions) == 0 or self._form_actions[0] is None:
            emsg = "Cannot find <form> with action attribute."
            raise ValueError, emsg
        return self._form_actions[0]


# End of class _HTMLFormActionGetter


# test code

if __name__ == "__main__":
    import time
    submitBugReport({
        "summary" : "test, do not post",
        "description" : "posted from submitBugReport on " + time.ctime(),
    })
