'''
This window will display all Patients (determined by unique PatientsName tag) and 
the DICOM files associated with them. It will give a preview of the selected file and
allow the user to determine whether it should be used
'''

import wx

class SelectFilesWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(SelectFilesWindow, self).__init__(*args, **kwargs)

        self.Maximize(True)
        self.makeGUI()

    def makeGUI(self):
        panel = wx.Panel(self)
        #idea: for each patient, print their name, then make a listbox for each patient
        #inside the listbox have all the files associated with that patient
        patientName = wx.StaticText(panel, pos=(10,15), label="John Doe")
        chooseFile = wx.ListBox(panel, pos=(10,30), size=(300,100), 
                choices=['xray1','chart','ct','xray2','xray3','chart2','mri'])
        self.Show(True)



def main():
    app = wx.App()
    
    SelectFilesWindow(None, title="Select Files to Anonymize", )
    app.MainLoop()

main()

