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
        # dict for how to anonymize tags, # indicated remove tag altogether
        self.tagsAnon = {'AccessionNumber': '00000000',
                         'PatientID': '100000',
                         'PatientAddress': 'Unknown',
                         'StudyID': '00000000',
                         'PerformedProcedureStepID': '#',
                         'ScheduledProcedureStepID': '#',
                         'RequestAttributesSequence': '#'}

        self.tagsAnon_nums = ['(0008, 0050)', '(0010, 0020)', '(0010, 1040)', '(0020, 0010)', '(0040, 0253)', '(0040, 0009)', '(0040, 0275)']

        # so far just the A's
        self.additionalTags = {'AccessionNumber': '00000000',
                          'AcquisitionComments': '#',
                          'AcquisitionContextSequence': '#',
                          'AcquisitionDate': '#',
                          'AcquisitionDateTime': '#',
                          'AcquisitionDeviceProcessingDescr': '#',
                          'AcquisitionProtocolDescription': '#',
                          'AcquisitionTime': '#',
                          'ActualHumanPerformersSequence': '#',
                          'AdditionalPatientHistory': '#',
                          'AddressTrial': '#',
                          'AdmissionID': '#',
                          'AdmittingDate': '#',
                          'AdmittingDiagnosesDescription': '#',
                          'AdmittingDiagnosesCodeSequence': '#',
                          'AdmittingTime': '#',
                          'Allergies': '#',
                          'Arbitrary': '#',
                          'AuthorObserverSequence': '#'
                          }

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



        # iterate through every patient in library
        idCount = 100000
        for name, patient in self.PatientObjects.iteritems():
            # increments the id
            self.tagsAnon['PatientID'] = str(idCount)
            idCount = idCount + 1

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

                for tag, value in self.tagsAnon.iteritems():
                    if value == '#':
                        try:
                            x = ds.data_element(tag).tag
                            del ds[x]
                        except:
                            # the tag didn't exist in the first place
                            pass
                    else:
                        try:
                            ds.data_element(tag).value = value
                        except:
                            # tag didn't exist
                            pass

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