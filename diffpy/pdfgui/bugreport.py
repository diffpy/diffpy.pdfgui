#!/usr/bin/env python
##############################################################################
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
##############################################################################

"""Routines for submitting bugreport through www.diffpy.org.
"""


import urlparse
import HTMLParser


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
    formdata_user = {
        "reporter" : formfields.get("reporter", "").strip() or "anonymous",
        "summary" : formfields["summary"],
        "description" : formfields["description"],
        "component" : formfields.get("component", "pdfgui"),
        "version" : formfields.get("version", __version__),
        "traceback" : formfields.get("traceback", ""),
    }
    # format formdata_user items:
    for k in formdata_user:
        formdata_user[k] = formdata_user[k].strip()
    if formdata_user["description"]:
        formdata_user["description"] += "\n"
    if formdata_user["traceback"]:
        formdata_user["traceback"] = "\n" + formdata_user["traceback"] + "\n"
    # open FORM_URL
    handler = urllib2.HTTPBasicAuthHandler()
    handler.add_password(FORM_REALM, ROOT_URL,
            FORM_USER, FORM_ENCPW.encode('rot13'))
    cookier = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
    opener = urllib2.build_opener(handler, cookier)
    formcontent = opener.open(FORM_URL).read()
    # find where does the form post its data
    try:
        formattr, formdata = getFormData(formcontent)
    # invalid web form would throw ValueError, raise this as
    # IOError so we get a meaningful error message from the gui.
    except ValueError, err:
        emsg = "Invalid webform - %s" % err
        raise IOError(emsg)
    # build the formadata dictionary
    formdata.update(formdata_user)
    post_url = urlparse.urljoin(FORM_URL, formattr['action'])
    post_headers = {'User-agent' : 'PDFgui (compatible; MSIE 5.5; WindowsNT)'}
    post_content = urllib.urlencode(formdata)
    post_request = urllib2.Request(post_url, post_content, post_headers)
    post_handle = opener.open(post_request)
    # result can be obtained by post_handle.read(), but it is not needed
    # silence the pyflakes syntax checker
    assert post_handle or True
    return


def getFormData(content, index=0):
    """Extract the attributes and input data from the specified <form> block.

    content  -- HTML code
    index    -- zero-based index of the form in the HTML document

    Return a tuple of (formattr, formdata) dictionaries, where
    formattr -- has all the attributes of the <form> element
    formdata -- has all the contain input field names and their values
    Raise ValueError when index-th <form> block does not exist.
    """
    datagetter = _HTMLFormDataGetter()
    fmattr, fmdata = datagetter(content)
    if index >= len(fmdata):
        emsg = "<form> block number %i does not exist" % index
        raise ValueError(emsg)
    rv = (fmattr[index], fmdata[index])
    return rv


# Helper classes


class _HTMLFormDataGetter(HTMLParser.HTMLParser):
    """Helper HTMLParser for extracting form data attributes from
    the first form.

    Instance data:

    _formattrs   -- list of attribute dictionaries for all <form> tags
    _formdata    -- list of input data dictionaries from all <form> tags

    See also getFormData().
    """


    # declaration of instance data attributes
    _formattrs = None
    _formdata = None


    def handle_starttag(self, tag, attrs):
        """Store data dictionary for all HTML forms in the document.
        """
        dattr = dict(attrs)
        if tag == "form":
            self._formattrs.append(dattr)
            self._formdata.append({})
        if tag == "input" and 'name' in dattr:
            name = dattr['name']
            value = dattr.get('value', '')
            self._formdata[-1][name] = value
        return


    def __call__(self, content):
        """Return a list of data dictionaries for all HTML forms in the document.

        content -- HTML code

        Return two lists of dictionaries for form attributes and form data.
        Raise ValueError for invalid HTML code or when no form is present.
        """
        self.reset()
        self._formattrs = []
        self._formdata = []
        try:
            self.feed(content)
            self.close()
        except HTMLParser.HTMLParseError, err:
            raise ValueError, str(err)
        return (self._formattrs, self._formdata)


# End of class _HTMLFormDataGetter


# test code

if __name__ == "__main__":
    import time
    submitBugReport({
        "summary" : "test, do not post",
        "description" : "posted from submitBugReport on " + time.ctime(),
    })
