#defines a class to store all the .dcm files associated with a patient
#methods to apply the anonymization to all selected files of that patient
import dicom
from PatientSelector import PatientLibrary

class Patient(PatientLibrary):
    #creates new patient with first file in the unselected list being the
    #file that triggered the creation of a new patient object
    def __init__(self,dcmObject):

        #create dicom object from filePath (requires proper filepath)
        #TODO: actually may not need this, delete commented out code
        #ds = dicom.read_file(filePath)

        #initialize lists to store the dicom objects
        #unusedFiles will not be anonymized or exported, 
        #it contains the first dcm object initially
        #usedFiles will be anonymized and exported
        self.unusedFiles = [dcmObject]
        self.usedFiles = []

        self.fileLabels = []

        
        #initialize the Patient data attributes to be anonymized
        self.unAnon_PatientsName = dcmObject.PatientsName
        self.unAnon_PatientBday = dcmObject.PatientBirthDate

    #TODO: delete?
    #only pass if the file has been confirmed to have the same patient name
    def addFile(self, filePath):
        #create a dcmObject from the filepath using the pydicom library
        ds = dicom.read_file(filePath)
        
        #extra check to ensure incorrect filePath hasn't been passed
        if (ds.PatientsName == self.unAnon_PatientsName):
            self.unusedFiles.append(ds)
        else:
            raise SystemError('Attempted to add .dcm file not belonging to patient')

    #TODO: remove addFile function if this works
    def add_dicomObject(self, dicomObject):
        # extra check to ensure incorrect object hasn't been passed
        if (dicomObject.PatientsName == self.unAnon_PatientsName):
            self.unusedFiles.append(dicomObject)
        else:
            raise SystemError('Attempted to add .dcm file not belonging to patient')


    #takes in a dicom object (should be on the unusedFiles list)
    #removes it from unusedFiles and adds to usedFiles
    def useSelectedObject(self, dcmObject):
        if dcmObject not in self.unusedFiles:
            raise SystemError("Attempted to use file that isn't on unusedFiles list")
        else:
            #remove selected object from unused files list and move it to the used one
            self.unusedFiles.remove(dcmObject)
            self.usedFiles.append(dcmObject)

    #once the used and unused lists have been completed, allow user to change
    #the PatientsName tag of all the dcm files on the usedFiles list
    def changePatientsName(self, newPatientsName):
        if newPatientsName == self.unAnon_PatientsName:
            raise SystemError("Anonymized name cannot be same as Real Name")
        else:
            #TODO: triple ensure this actually changes the objects! 
            #must export for changes to take effect
            for dcmObject in self.usedFiles:
                dcmObject.PatientsName = newPatientsName
        
        #XXX: if anonymize in place is implemented later, this would be the spot, using:
        '''
        if anonymizeSource:
            for dcmObject in unusedFiles:
                dcmObject.PatientsName = newPatientsName
            #must also change other tags and export to source (overwriting originals)
        '''





    #TODO: write this, comment out for now since errors
    '''
    def anonymizeUsedFiles(self):
        #TODO: write code for anonymization of all tags
        #first implement with obvious ones,
        #then use DICOM PS3.15 2017e Attribute Confidentiality Profiles
        for dcmObject in self.usedFiles:
            #go through each tag that needs to be anonymized on every object
        
        
    '''

def main():
    print "here"
    #nothing here

if __name__ == "__main__":
    main()