'''
Defines functions to sort through a given folder
and create Patient objects when dicom file with new
patient name encountered. Sends dicom files with
pre-exisiting patients to their respective Patient object
Stores a library of Patients for display to windows
'''

import dicom
import os
import magic


class PatientLibrary():

    '''
    Initializes a patient library with a
    path to the folder to be anonymized
    '''
    def __init__(self, folderPath):

        self.sourceDir = folderPath
        #store Patient objects in dict
        self.PatientObjects = {}

    '''
    Iterates through the files in the source directory,
    creates Patient objects and stores the dicom objects
    with the correct Patient object
    '''
    def populatePatientLibrary(self):
        #go through every file in directory
        #use magic to determine if dicom file
        #if dicom file, check if name not seen
        #if seen -> add file to correct patient in dict
        #if new -> create Patient object, add initial
        #dicom object to Patient, add Patient to dict

        from Patient import Patient

        for root, directories, filenames in os.walk(self.sourceDir):
            for filename in filenames:
                filePath = os.path.join(root, filename)


                #determines MIME file type with magic library
                type = magic.from_file(filePath)

                #creates pydicom object for all files
                #with MIME type of DICOM
                if 'DICOM' in type:
                    ds = dicom.read_file(filePath)
                    pName = ds.PatientsName
                    pBday = ds.PatientBirthDate

                    pIdent = pName+pBday
                    #if patient already seen, add ds to Patient
                    if pIdent in self.PatientObjects:
                        self.PatientObjects[pIdent].add_dicomObject(ds)
                    #if unseen patient name, create new Patient with ds
                    else:
                        patient = Patient(ds)
                        self.PatientObjects[pIdent] = patient

    def basicAnonymizeLibrary(self):
        id = '123'
        tagsAnon = {'AccessionNumber': '00000000', 'PatientID' : id, 'PatientAddress' : 'Unknown'}
        # iterate through every patient in library
        for name, patient in self.PatientObjects.iteritems():
            # iterate through every dicom file selected for anonymization
            for ds in patient.usedFiles:
                '''
                tagname = "PatientID"
                print ds.data_element(tagname).value
                del ds[0x10,0x1040]
                try:
                    ds[0x10,0x1040].value = 'Unknown'
                except KeyError:
                    print 'Tag Do not exist'
                '''

                for tag, value in tagsAnon.iteritems():
                    ds.data_element(tag).value = value

                ''''
                print ds[0x10,0x1040]
                print ds.data_element("PatientAddress").value
                ds.data_element("PatientAddress").value = 'Unknown'
                print ds.data_element("AccessionNumber").value
                ds.data_element("AccessionNumber").value = '00000000'
                '''


    def testLibrary(self):
        import os.path
        for name, value in self.PatientObjects.iteritems():
            print name
            files = value.unusedFiles
            for f in files:
                print os.path.basename(os.path.normpath(f.filename))



def main():

    #to test
    path = input("Enter dir path: ")
    pLib = PatientLibrary(path)
    pLib.populatePatientLibrary()
    pLib.testLibrary()

if __name__ == "__main__":
    main()