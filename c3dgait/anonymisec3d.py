"""
The anonymis module provides a class to remove patient identifable data from a c3d file.
"""

from ezc3d import c3d
import json
import os

class Anonymise:
    """This class removes the patient identifiable data from the c3d file."""
    def __init__(self, c3dPath, subjectname="ANON"):
        """
        Loads the c3d file data and removes patient identifable data.

        :param c3dPath(string): Absolute or relative path to the c3d file
        :param subjectname(string)(optional): Reference to replace the patient name
        :return: None
        """

        # Load c3d file
        try:
            trial = c3d(c3dPath)
        except:
            raise Exception("Unable to open {}. Check the filepath is valid and not corrupted".format(c3dPath))
    
        # Remove name from c3d object
        trial['parameters']['SUBJECTS']['NAMES']['value'] = subjectname
        self.trialC3D = trial
        return
    
    def createFilePath(self, outputdir, condition, trialno):
        """
        Returns a file path for the anonymised c3d file to be save to.
        Format "{outputdir}/{subjectname}_{condition}_{trialno}.c3d

        :param outputdir(String): Absolute or relative path to chosen directory
        :param condition(String): Trial condition e.g barefoot
        :param trialno(int): Trial number
        
        :return: fielpath(String): Output file path
        """
        # Create file name
        filename= self.trialC3D['parameters']['SUBJECTS']['NAMES']['value']
        if condition!=None:
            filename = "{}_{}".format(filename, condition)
        else:
            pass

        if trialno!=None:
            filename  = "{}_{}.c3d".format(filename, trialno)
        else:
            filename  = "{}.c3d".format(filename)
        
        if outputdir!=None:
            filepath = os.path.join(outputdir, filename)
        else:
            filepath = filename
        return filepath

    def saveC3D(self, outputdir=None, condition=None, trialno=None):
        """
        Save the anonymised c3d file.

        :param outputdir(String): Absolute or relative path to chosen directory
        :param condition(String): Trial condition e.g barefoot
        :param trialno(int): Trial number
        :return: None
        """
        fpath = self.createFilePath(outputdir, condition, trialno)
        self.trialC3D.write(fpath)
        return




