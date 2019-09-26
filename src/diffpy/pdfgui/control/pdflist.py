#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Jiwu Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

from diffpy.pdfgui.control.controlerrors import ControlKeyError

class PDFList(list):
    """list class of PDFComponent, which can be accessed through index or a
    name string
    """
    def __init__(self, *args):
        """Initialize

        args -- argument list
        """
        list.__init__(self, args)
        return

    def __getitem__(self, idnm):
        """Get the item by idnm

        idnm -- The index or name of the item
        return: The requested object
        """
        try:
            return list.__getitem__(self, idnm)
        except TypeError:
            for item in self:
                if item.name == idnm:
                    return item
            else:
                raise ControlKeyError("'%s' does not exist" % idnm)

    def __setitem__(self, idnm, obj):
        """Set the item by idnm

        idnm -- The index or name of the item
        obj  -- The object to be inserted
        """
        if obj.name in self.keys():
            raise ControlKeyError("'%s' already exists" % obj.name)
        try:
            list.__setitem__(self, idnm, obj)
            return
        except TypeError:
            self.append(obj)
            return

    def __delitem__(self, idnm):
        """Delete the item by idnm.

        idnm -- The index or name of the item
        """
        try:
            list.__delitem__(self, idnm)
            return
        except TypeError:
            try:
                index = self.keys.index(idnm)
                list.__delitem__(self, index)
            except IndexError:
                raise ControlKeyError("'%s' does not exist" % idnm)

    def rename(self, idnmrf, newname):
        """Rename an item

        idnmrf -- index,name or reference to the object
        newname -- new name
        """
        if newname in self.keys():
            raise ControlKeyError("'%s' already exists" % newname)
        try:
            self.index(idnmrf)
            # if no exception, it is a object in the list.
            idnmrf.name = newname
        except ValueError:
            self[idnmrf].name = newname
        return

    def keys(self):
        """Get the names of the held objects.

        return: list of names
        """
        return [ x.name for x in self ]

    def values(self):
        """Get all held objects

        return: list of objects
        """
        return self[:]

    def items(self):
        """Get name-object pairs

        return: a list of tuple ( name, object)
        """
        return [ (x.name, x) for x in self ]

# End of file
