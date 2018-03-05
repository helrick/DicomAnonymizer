'''
Functions for use by DICOM Anonymizer program
'''
from PatientSelector import PatientLibrary

def createLibrary(path):
    patientLib = PatientLibrary(path)
    patientLib.populatePatientLibrary()
    return patientLib
