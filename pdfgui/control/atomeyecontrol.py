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
import subprocess
import re
import tempfile
from threading import Timer

def plot(structure, executable):
    '''Plots the structure in AtomEye.
    
    @param structure: (Structure class) structure to be plotted
    @param executable: (string) Name of atomeye executable. If the executable is
    not on the user's PATH, then the full path to the executable is needed.
    
    Creates a file in some temporary directory and plot it in Atomeye, then
    deletes both the file and the directory.
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

        # Remove the files after atomeye has a chance to read them. Since we
        # can't tell when this actually happens, we start at threaded timer
        # delete them later.
        def __removeFiles(dir, file):
            if os.path.exists(file): os.remove(file)
            if os.path.exists(dir): os.rmdir(dir)
            return
        T = Timer(20, __removeFiles, args=[dirname, fullpath])

        # This should be done with try...except...finally, but this only works
        # properly in python 2.5.
        import platform
        if platform.system() == 'Windows': 
            # replace string
            def toCygwin(winpath):
                drive,path=os.path.splitdrive(winpath)
                path = path.replace('\\', '/')
                if drive.endswith(':'): drive = drive[:-1]
                return "/cygdrive/%s/%s"%(drive,path)
            command = 'bash.exe -l -c "DISPLAY=127.0.0.1:0.0 %s %s"'%(toCygwin(executable), toCygwin(fullpath))
        else:
            command = "%s %s"%(executable, fullpath)

        try:
            structure.write(fullpath,"xcfg")
            proc = subprocess.Popen(command, shell=True)
            T.start()
        except OSError:
            # The executable does not exist
            T.start()
            from controlerrors import ControlConfigError
            raise ControlConfigError("Either AtomEye is not present on your system or you have not specified the path to AtomEye under Edit->Preferences.")
        except:
            T.start()
            raise


##### testing code ############################################################
if __name__ == "__main__":
    from diffpy.Structure import Structure

    structure = Structure()
    structure.read('../../tests/testdata/LaMnO3.pdb')
    
    plot(structure)
    
##### end of testing code #####################################################    
