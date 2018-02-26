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

        self.Maximize(True)
        self.makeGUI()

    def makeGUI(self):
        panel = wx.Panel(self)
        #idea: for each patient, print their name, then make a listbox for each patient
        #inside the listbox have all the files associated with that patient
        pLib = createLibrary()

        patientText = []
        patientFileLists = []
        count = 0
        for name, value in pLib.PatientObjects.iteritems():
            patientText.append(wx.StaticText(panel, pos=(10,((count*125)+15)), label=value.unAnon_PatientsName))
            files = value.unusedFiles
            fileNames = []
            for f in files:
                fileNames.append(os.path.basename(os.path.normpath(f.filename)))
            patientFileLists.append(wx.ListBox(panel, pos=(10,((count*125)+30)),
                                               size=(300,100), choices=fileNames))
            count = count+1

        

        self.Show(True)


        '''
        patientName = wx.StaticText(panel, pos=(10,15), label="John Doe")
        chooseFile = wx.ListBox(panel, pos=(10,30), size=(300,100), 
                choices=['xray1','chart','ct','xray2','xray3','chart2','mri'])
        self.Show(True)
        '''


def createLibrary():
    patientLib = PatientLibrary(path)
    patientLib.populatePatientLibrary()
    return patientLib


def main():
    app = wx.App()
    
    SelectFilesWindow(None, title="Select Files to Anonymize", )
    app.MainLoop()

main()

