#defines a class to store all the .dcm files associated with a patient
#methods to apply the anonymization to all selected files of that patient
import dicom

class Patient:
    #creates new patient with first file in the unselected list being the
    #file that triggered the creation of a new patient object
    def __init__( self, filePath):

        #create dicom object from filePath (requires proper filepath)
        ds = dicom.read_file(filePath)

        #initialize lists to store the dicom objects
        #unusedFiles will not be anonymized or exported, 
        #it contains the first dcm object initially
        #usedFiles will be anonymized and exported
        self.unusedFiles = [ds]
        self.usedFiles = []
        
        #initialize the Patient data attributes to be anonymized
        self.unAnon-PatientsName = ds.PatientsName

    #only pass if the file has been confirmed to have the same patient name
    def addFile(filePath):
        #create a dcmObject from the filepath using the pydicom library
        ds = dicom.read_file(filePath)
        
        #extra check to ensure incorrect filePath hasn't been passed
        if (ds.PatientsName == self.unAnon-PatientsName):
            self.unusedFiles.append(ds)
        else:
            raise SystemError('Attempted to add .dcm file not belonging to patient')
    
    #takes in a dicom object (should be on the unusedFiles list)
    #removes it from unusedFiles and adds to usedFiles
    def useSelectedObject(dcmObject):
        if dcmObject not in unusedFiles:
            raise SystemError("Attempted to use file that isn't on unusedFiles list")
        else:
            #remove selected object from unused files list and move it to the used one
            self.unusedFiles.remove(dcmObject)
            self.usedFiles.append(dcmObject)

    #once the used and unused lists have been completed, allow user to change
    #the PatientsName tag of all the dcm files on the usedFiles list
    def changePatientsName(newPatientsName):
        if newPatientsName == unAnon-PatientsName:
            raise SystemError("Anonymized name cannot be same as Real Name")
        else:
            #TODO: triple ensure this actually changes the objects! 
            #must export for changes to take effect
            for dcmObject in usedFiles:
                dcmObject.PatientsName = newPatientsName
        
        #XXX: if anonymize in place is implemented later, this would be the spot, using:
        '''
        if anonymizeSource:
            for dcmObject in unusedFiles:
                dcmObject.PatientsName = newPatientsName
            #must also change other tags and export to source (overwriting originals)
        '''
        
    def anonymizeUsedFiles():
        #TODO: write code for anonymization of all tags
        #first implement with obvious ones,
        #then use DICOM PS3.15 2017e Attribute Confidentiality Profiles
        for dcmObject in usedFiles:
            #go through each tag that needs to be anonymized on every object
        
        