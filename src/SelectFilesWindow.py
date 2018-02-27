'''
This window will display all Patients (determined by unique PatientsName tag) and 
the DICOM files associated with them. It will give a preview of the selected file and
allow the user to determine whether it should be used
'''

import wx
import os.path
from PatientSelector import PatientLibrary

#temporary solution, this should be passed from file dialog
path = "/Users/hillary/Documents/School/4th_Year/Winter2018/CISC499/test-data"

class SelectFilesWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(SelectFilesWindow, self).__init__(*args, **kwargs)
        self.patientLib = createLibrary()
        self.Maximize(True)
        self.panel = wx.Panel(self)

        self.imagePanel = wx.Panel(self.panel, pos=(400,10))
        self.imagePanel.Show()
        self.xrayImage = wx.StaticBitmap()
        self.selectImage = wx.Button()
        self.CurrentDICOMObject = None
        self.CurrentPatient = None

        self.LeftPatientText = []
        self.LeftPatientFileLists = []

        self.RightPatientText = []
        self.RightPatientFileLists = []

        self.showUnusedFiles()
        self.showUsedFiles()



    def showUnusedFiles(self):
        self.LeftPatientText = []
        self.LeftPatientFileLists = []
        count = 0
        '''
        patientName = wx.StaticText(panel, pos=(10,15), label="John Doe")
        chooseFile = wx.ListBox(panel, pos=(10,30), size=(300,100), 
            choices=['xray1','chart','ct','xray2','xray3','chart2','mri'])
        self.Show(True)
        '''
        for name, value in self.patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            self.LeftPatientText.append(wx.StaticText(self.panel, pos=(10, ((count * 125) + 15)), label=pName))

            #gets all the unusedFiles from each patient
            files = value.unusedFiles
            fileNames = []
            lb = wx.ListBox(self.panel, pos=(10, ((count * 125) + 30)), size=(300, 100), choices=fileNames)
            for f in files:
                lb.Append(os.path.basename(os.path.normpath(f.filename)), value)
            self.LeftPatientFileLists.append(lb)
            count = count+1
            lb.Bind(wx.EVT_LISTBOX, self.displayImage)


        self.Show(True)

    def showUsedFiles(self):
        self.RightPatientText = []
        self.RightPatientText = []
        count = 0
        for name, value in self.patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            self.RightPatientText.append(wx.StaticText(self.panel, pos=(950, ((count * 125) + 15)), label=pName))

            #gets usedFiles from each patient
            files = value.usedFiles
            fileNames = []
            rlb = wx.ListBox(self.panel, pos=(950, ((count * 125) + 30)), size=(300, 100), choices=fileNames)
            for f in files:
                rlb.Append(os.path.basename(os.path.normpath(f.filename)), value)
            self.RightPatientFileLists.append(rlb)
            count = count+1
            #lb.Bind(wx.EVT_LISTBOX, self.displayImage)


    def displayImage(self, event):
        self.CurrentPatient = event.GetClientData()
        imgName = event.GetString()

        #get the pydicom object
        for dcmObject in self.CurrentPatient.unusedFiles:
            if (os.path.basename(os.path.normpath(dcmObject.filename)) == imgName):
                self.CurrentDICOMObject = dcmObject

        from matplotlib import pyplot
        pyplot.imshow(self.CurrentDICOMObject.pixel_array, cmap=pyplot.cm.bone)
        pyplot.axis('off')

        pyplot.savefig('tempfile.png', bbox_inches = 'tight', pad_inches=0.0)
        i = wx.Image('tempfile.png', 'image/png', -1)
        i.Resize(size=(500,500),pos=(0,0),red=255, green=255, blue=255)
        png = i.ConvertToBitmap()

        # checks that the image and button are properly destroyed before deleting
        if self.xrayImage:
            self.xrayImage.Destroy()

        self.selectImage = wx.Button(self.panel, pos=(600,520), label="Select Image")

        self.xrayImage = wx.StaticBitmap(self.panel,-1,png,(380, 10), (500,500))
        self.selectImage.Bind(wx.EVT_BUTTON, self.chooseImage)




    def chooseImage(self, event):
        # adds selected file to usedFiles list
        self.CurrentPatient.usedFiles.append(self.CurrentDICOMObject)
        # removes the selected image from the unused files
        self.CurrentPatient.unusedFiles.remove(self.CurrentDICOMObject)

        # destroys the existing listboxes, buttons, and text printed to the screen
        for leftnameText in self.LeftPatientText:
            leftnameText.Destroy()
        for leftlistBox in self.LeftPatientFileLists:
            leftlistBox.Destroy()

        for rightnameText in self.RightPatientText:
            rightnameText.Destroy()
        for rightlistBox in self.RightPatientFileLists:
            if rightlistBox: # not exactly sure why this works...
                rightlistBox.Destroy()

        # reprints the new unused files and patients
        self.showUnusedFiles()
        self.showUsedFiles()



def createLibrary():
    patientLib = PatientLibrary(path)
    patientLib.populatePatientLibrary()
    return patientLib


def main():
    app = wx.App()
    
    SelectFilesWindow(None, title="Select Files to Anonymize" )
    app.MainLoop()

main()

