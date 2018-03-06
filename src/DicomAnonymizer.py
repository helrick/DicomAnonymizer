'''
Program Flow for DICOM Anonymizer
'''

import wx
import os.path
from PatientSelector import PatientLibrary
import Functions

sourcePath = ''
patientLib = None


class SelectFolderDialog(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(SelectFolderDialog, self).__init__(*args, **kwargs)
        panel = wx.Panel(self)
        self.currentDirectory = os.getcwd()

        # Initialize Widgets
        self.PathSelection = wx.TextCtrl(panel, style=wx.TE_READONLY)
        self.SelectDirButton = wx.Button(panel, label="Select DICOM Directory")
        self.ContinueButton = wx.Button(panel, label="Continue")

        # Sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddStretchSpacer(prop=1)

        self.sizer.Add(self.PathSelection, flag=wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border=10)
        self.sizer.Add(self.SelectDirButton, flag=wx.ALIGN_CENTER)

        self.sizer.AddStretchSpacer(prop=1)

        self.sizer.Add(self.ContinueButton, flag=wx.ALIGN_RIGHT | wx.ALL, border=10 )
        panel.SetSizer(self.sizer)
        panel.Layout()

        # Event Handlers
        self.SelectDirButton.Bind(wx.EVT_BUTTON, self.onSelectDir)

        self.SetInitialSize((550, 225))
        self.Center()
        self.Show()

    def onSelectDir(self, event):
        dialog = wx.DirDialog(self, message="Choose Source Folder")
        if dialog.ShowModal() == wx.ID_OK:
            global sourcePath
            sourcePath = dialog.GetPath()
            self.PathSelection.ChangeValue(sourcePath)
            # Enable Event Handler for Continue Button
            self.ContinueButton.Bind(wx.EVT_BUTTON, self.onContinue)
        dialog.Destroy()



    def onContinue(self, event):
        SelectFiles(None, title="Select Files to Anonymize")
        self.Show(False)

import wx.lib.scrolledpanel as sp

class SelectFiles(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(SelectFiles, self).__init__(*args, **kwargs)
        global patientLib
        patientLib = createLibrary()
        self.Maximize(True)
        self.panel = wx.Panel(self)
        self.WindowSize = self.GetSize()

        self.leftPanel = sp.ScrolledPanel(self.panel, size=(self.WindowSize[0] / 4, self.WindowSize[1] - 20))
        self.leftPanel.SetupScrolling()
        self.leftPanel.SetBackgroundColour((200,200,200))


        self.rightPanel = sp.ScrolledPanel(self.panel, size=(self.WindowSize[0] / 4, self.WindowSize[1] - 100))
        self.rightPanel.SetupScrolling()
        self.rightPanel.SetBackgroundColour((200,200,200))

        self.imagePanel = wx.Panel(self.panel, pos=(400, 10))
        self.imagePanel.Show()
        self.xrayImage = wx.StaticBitmap()

        # Initialize Buttons
        '''
        self.selectImage = wx.Button(self.imagePanel, pos=(600, 520), label="Select Image")
        self.classifyPreop = wx.Button(self.imagePanel, pos=(600, 550), label="Label Pre-Op")
        self.classifyPostop = wx.Button(self.imagePanel, pos=(598, 570), label="Label Post-Op")
        '''
        self.selectImage = wx.Button(self.panel, pos=(self.WindowSize[0]/2, 520), label="Select Image")
        self.classifyPreop = wx.Button(self.panel, pos=(self.WindowSize[0]/2, 550), label="Label Pre-Op")
        self.classifyPostop = wx.Button(self.panel, pos =(self.WindowSize[0]/2 -2, 570), label="Label Post-Op")
        self.anonSelected = wx.Button(self.panel, pos=(self.WindowSize[0]*.83, self.WindowSize[1]*0.9), label="Anonymize Selected")


        # Hide/Show Buttons
        self.selectImage.Hide()
        self.classifyPreop.Hide()
        self.classifyPostop.Hide()
        self.anonSelected.Show()

        # EVENT HANDLERS
        self.selectImage.Bind(wx.EVT_BUTTON, self.chooseImage)
        self.classifyPreop.Bind(wx.EVT_BUTTON, self.markPreop)
        self.classifyPostop.Bind(wx.EVT_BUTTON, self.markPostop)
        self.anonSelected.Bind(wx.EVT_BUTTON, self.nextScreen)

        self.CurrentDICOMObject = None
        self.CurrentPatient = None

        self.LeftPatientText = []
        self.LeftPatientFileLists = []

        self.RightPatientText = []
        self.RightPatientFileLists = []

        # SIZERS
        self.leftSizer = wx.BoxSizer( wx.VERTICAL)
        self.leftPanel.SetSizer(self.leftSizer)

        self.rightSizer = wx.BoxSizer( wx.VERTICAL)
        self.rightPanel.SetSizer(self.rightSizer)

        self.horzSizer = wx.BoxSizer( wx.HORIZONTAL)
        self.horzSizer.Add(self.leftPanel, 1)
        self.horzSizer.Add(self.imagePanel, 2)
        self.horzSizer.Add(self.rightPanel, 1)
        self.panel.SetSizer(self.horzSizer)

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
        global patientLib
        for name, value in patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            # self.LeftPatientText.append(wx.StaticText(self.leftPanel, pos=(10, ((count * 125) + 15)), label=pName))
            self.LeftPatientText.append(wx.StaticText(self.leftPanel, label=pName))

            # gets all the unusedFiles from each patient
            files = value.unusedFiles
            fileNames = []
            lb = wx.ListBox(self.leftPanel, size=(self.WindowSize[0] / 4 - 50, 100), choices=fileNames)
            #lb = wx.ListBox(self.panel, pos=(10, ((count * 125) + 30)), size=(300, 100), choices=fileNames)
            for f in files:
                lb.Append(os.path.basename(os.path.normpath(f.filename)), value)
            self.LeftPatientFileLists.append(lb)
            count = count + 1
            lb.Bind(wx.EVT_LISTBOX, self.displayImage)

        for nameText, listBox in zip(self.LeftPatientText, self.LeftPatientFileLists):
            self.leftSizer.Add(nameText, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10 )
            self.leftSizer.Add(listBox, 0, wx.LEFT, 10)

        self.leftSizer.Layout()
        self.Show(True)

    def showUsedFiles(self):
        self.RightPatientText = []
        self.RightPatientFileLists = []
        count = 0
        global patientLib
        for name, value in patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            # self.RightPatientText.append(wx.StaticText(self.panel, pos=(950, ((count * 125) + 15)), label=pName))
            self.RightPatientText.append(wx.StaticText(self.rightPanel, label=pName))

            # gets usedFiles from each patient
            files = value.usedFiles
            fileNames = []
            rlb = wx.ListBox(self.rightPanel, size=(self.WindowSize[0] / 4 - 50, 100), choices=fileNames)
            # rlb = wx.ListBox(self.panel, pos=(950, ((count * 125) + 30)), size=(300, 100), choices=fileNames)
            for f in files:
                rlb.Append(os.path.basename(os.path.normpath(f.filename)), value)
            self.RightPatientFileLists.append(rlb)
            count = count + 1
        for nameText, listBox in zip(self.RightPatientText, self.RightPatientFileLists):
            self.rightSizer.Add(nameText, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10 )
            self.rightSizer.Add(listBox, 0, wx.LEFT, 10)

        self.rightSizer.Layout()
        self.Show(True)

    def displayImage(self, event):
        self.CurrentPatient = event.GetClientData()
        imgName = event.GetString()

        # get the pydicom object
        for dcmObject in self.CurrentPatient.unusedFiles:
            if (os.path.basename(os.path.normpath(dcmObject.filename)) == imgName):
                self.CurrentDICOMObject = dcmObject

        from matplotlib import pyplot
        pyplot.imshow(self.CurrentDICOMObject.pixel_array, cmap=pyplot.cm.bone)
        pyplot.axis('off')

        pyplot.savefig('tempfile.png', bbox_inches='tight', pad_inches=0.0)
        i = wx.Image('tempfile.png', 'image/png', -1)
        i.Resize(size=(500, 500), pos=(0, 0), red=255, green=255, blue=255)
        png = i.ConvertToBitmap()

        # checks that the image and button are properly destroyed before deleting
        if self.xrayImage:
            self.xrayImage.Destroy()
        if not self.selectImage.IsShown():
            self.selectImage.Show()
        self.classifyPreop.Show()
        self.classifyPostop.Show()

        self.xrayImage = wx.StaticBitmap(self.panel, -1, png, (380, 10), (500, 500))
        # EVENT HANDLERS
        '''
        self.selectImage.Bind(wx.EVT_BUTTON, self.chooseImage)
        self.classifyPreop.Bind(wx.EVT_BUTTON, self.markPreop)
        self.classifyPostop.Bind(wx.EVT_BUTTON, self.markPostop)
        '''

    def markPreop(self, event):
        # if the current file is already mark post op, remove it from that list
        if self.CurrentDICOMObject in self.CurrentPatient.postopFiles:
            self.CurrentPatient.postopFiles.remove(self.CurrentDICOMObject)

        # add the file to the preop list if it's not already there
        if self.CurrentDICOMObject not in self.CurrentPatient.preopFiles:
            self.CurrentPatient.preopFiles.append(self.CurrentDICOMObject)

    def markPostop(self, event):
        if self.CurrentDICOMObject in self.CurrentPatient.preopFiles:
            self.CurrentPatient.preopFiles.remove(self.CurrentDICOMObject)

        if self.CurrentDICOMObject not in self.CurrentPatient.postopFiles:
            self.CurrentPatient.postopFiles.append(self.CurrentDICOMObject)

    def chooseImage(self, event):
        # adds selected file to usedFiles list
        self.CurrentPatient.usedFiles.append(self.CurrentDICOMObject)
        # removes the selected image from the unused files
        self.CurrentPatient.unusedFiles.remove(self.CurrentDICOMObject)

        # destroys the existing listboxes, buttons, and text printed to the screen
        numChildren = len(self.leftSizer.GetChildren())
        for child in range(0, numChildren):
            self.leftSizer.Hide(0)
            self.leftSizer.Remove(0)

        for leftnameText in self.LeftPatientText:
            leftnameText.Destroy()
        for leftlistBox in self.LeftPatientFileLists:
            leftlistBox.Destroy()

        numChildren = len(self.rightSizer.GetChildren())
        for child in range(0, numChildren):
            self.rightSizer.Hide(0)
            self.rightSizer.Remove(0)

        for rightnameText in self.RightPatientText:
            rightnameText.Destroy()
        for rightlistBox in self.RightPatientFileLists:
            #if rightlistBox:  # not exactly sure why this works...
                rightlistBox.Destroy()

        # reprints the new unused files and patients
        self.showUnusedFiles()
        self.showUsedFiles()

    def nextScreen(self, event):
        #TODO: should first check that there are selected images
        AnonymizeFiles(self, title='Anonymize Files')
        self.Show(False)



class AnonymizeFiles(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AnonymizeFiles, self).__init__(*args, **kwargs)
        global patientLib
        self.Maximize(True)
        self.panel = wx.Panel(self)
        self.WindowSize = self.GetSize()

        self.filePanel = sp.ScrolledPanel(self.panel, size=(self.WindowSize[0] / 4, self.WindowSize[1] - 20))
        self.filePanel.SetupScrolling()
        self.filePanel.SetBackgroundColour((200,200,200))

        self.infoPanel = wx.Panel(self.panel)
        self.infoPanel.SetBackgroundColour((100,200,200))
        self.infoPanel.Show()

        for name, value in patientLib.PatientObjects.iteritems():
            print (value.unAnon_PatientsName)

        self.SelectedPatients = []
        self.SelectedPatientFiles = []

        self.fileSizer = wx.BoxSizer( wx.VERTICAL)
        self.filePanel.SetSizer(self.fileSizer)

        #self.infoSizer = wx.BoxSizer( wx.VERTICAL)
        #self.infoPanel.SetSizer(self.infoSizer)

        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.horzSizer.Add(self.filePanel, 1)
        self.horzSizer.Add(self.infoPanel, 3, wx.EXPAND)
        self.panel.SetSizer(self.horzSizer)

        self.showSelectedFiles()

        self.panel.Layout()


    def showSelectedFiles(self):
        self.SelectedPatients = []
        self.SelectedPatientFiles = []
        count = 0
        global patientLib
        for name, value in patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            # self.RightPatientText.append(wx.StaticText(self.panel, pos=(950, ((count * 125) + 15)), label=pName))
            if(value.usedFiles):
                self.SelectedPatients.append(wx.StaticText(self.filePanel, label=pName))

            # gets usedFiles from each patient
            files = value.usedFiles
            fileNames = []
            if(files):
                rlb = wx.ListBox(self.filePanel, size=(self.WindowSize[0] / 4 - 50, 100), choices=fileNames)
                for f in files:
                    rlb.Append(os.path.basename(os.path.normpath(f.filename)), value)
                self.SelectedPatientFiles.append(rlb)
        for nameText, listBox in zip(self.SelectedPatients, self.SelectedPatientFiles):
            self.fileSizer.Add(nameText, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
            self.fileSizer.Add(listBox, 0, wx.LEFT, 10)

        self.fileSizer.Layout()
        self.Show(True)


def createLibrary():
    global sourcePath
    patientLib = PatientLibrary(sourcePath)
    patientLib.populatePatientLibrary()
    return patientLib




if __name__ == "__main__":
    app = wx.App()
    SelectFolderDialog(None, title="Select DICOM Directory")
    app.MainLoop()