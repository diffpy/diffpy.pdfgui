########################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Dmitriy Bryndin
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################

#
# Structure plotter (using Atomeye)
# 
# Dmitriy Bryndin
#
# version
__id__ = "$Id$"
__revision__ = "$Revision$"

import os
import re
import tempfile

def plot(structure):
    '''Plots the structure in Atomeye
    
    @param structure: (Structure class) structure to be plotted
    
    Creates a file in some temporary directory and plot it in Atomeye,
    then deletes both the file and the directory.
    Filename is given according to the structure's title.
    '''
    # do not plot empty structure
    if (structure != None) and (len(structure) > 0):
        dirname = tempfile.mkdtemp()
        filename = structure.title
        if not filename:
            filename = "structure"
        else:
            filename = re.sub('\W', '_', filename)

        fullpath = os.path.join(dirname, filename)
        
        try:
            structure.write(fullpath,"xcfg")
            command = "(atomeye %s; rm %s; rmdir %s)&" % \
                            (fullpath, fullpath, dirname)
            os.system(command)
        except:
            # if something bad happends, remove previously created directory
            if os.path.exists(fullpath):
                os.remove(fullpath)
            if os.path.exists(dirname):
                os.rmdir(dirname)
            raise

##### testing code ############################################################
if __name__ == "__main__":
    from Structure import Structure

    structure = Structure()
    structure.read('../../tests/testdata/LaMnO3.pdb')
    
    plot(structure)
    
##### end of testing code #####################################################    
