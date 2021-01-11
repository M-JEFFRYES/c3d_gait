from ezc3d import c3d
import numpy as np
import json

def proof_of_anon(filepath):
    """
    This function prints out the meta data fields stored within the C3D file to highlight information to anonymise.
    """
    
    c3d_obj = c3d(filepath)


    print(c3d_obj['header'].keys())
    headers = ['points', 'analogs', 'events']
    print("No patient identifable info\n\n")
    
    print(c3d_obj['data'].keys())
    data = ['points', 'meta_points', 'analogs']
    print("No patient identifable info\n\n")

    print(c3d_obj.c3d_swig)
    print("No patient identifable info\n\n")


    print(c3d_obj['parameters'].keys())
    params = ['TRIAL', 'SUBJECTS', 'POINT', 'ANALOG', 'FORCE_PLATFORM', 'EVENT_CONTEXT', 'EVENT', 'MANUFACTURER', 'ANALYSIS', 'PROCESSING']

    print("c3d_obj['parameters']['PROCESSING'] contains clinical exam measurment, but in isolation these are not patient identifiable\n")
    print(c3d_obj['parameters']['SUBJECTS'].keys())
    subjects = ['__METADATA__', 'USED', 'IS_STATIC', 'USES_PREFIXES', 'NAMES', 'MARKER_SETS']

    print("c3d_obj['parameters']['SUBJECTS']['NAMES'] needs to be replaced with a reference or null value")    
    return

def anonymize(filePATH, outputDIR=None, subjectname="ANON", trialno=1, verbose=False):
    """
    This function removes the patients name from the C3D file meaning the patient can not be identified.
    Then the anonymous C3D file is saved.
        Arguments:
            filePATH(String): Path to the original C3D file

            outputDIR(String)(optional): Path of the directory to save the anonymised C3D to, if its not specified the file will be saved in the current working directory
            subjectname(String)(optional): Subject reference used in the context of the study, if not specified the subject will be named "ANON"
            trialno(int)(optional): Trial number for the subject, if not specified 1 will be assigned
            verbose(Boolean)(optional): If true the function will print once the anonymised file hase been saved, default value is False
        Returns:
            None, but a new C3D file will have been saved
    """

    if outputDIR ==None:
        outputPATH = "{}_trial_{}.c3d".format(subjectname, trialno)
    else:
        outputPATH = "{}\\{}_Trial_{}.c3d".format(outputDIR, subjectname, trialno)

    c3d_obj = c3d(filePATH)

    c3d_obj['parameters']['SUBJECTS']['NAMES']['value'] = subjectname

    c3d_obj.write(outputPATH)

    if verbose==True:
        print("C3D File from: {}".format(filePATH))
        print("Has been anonymized to: {}".format(outputPATH))
    return
