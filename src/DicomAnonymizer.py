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
        SelectFiles(self, title="Select Files to Anonymize")
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
        self.deselectImageButton = wx.Button(self.panel, pos=(self.WindowSize[0]/2, 600), label="Deselect Image")
        self.anonSelected = wx.Button(self.panel, pos=(self.WindowSize[0]*.83, self.WindowSize[1]*0.9), label="Anonymize Selected")


        # Hide/Show Buttons
        self.selectImage.Hide()
        self.classifyPreop.Hide()
        self.classifyPostop.Hide()
        self.deselectImageButton.Hide()
        self.anonSelected.Show()

        # EVENT HANDLERS
        self.selectImage.Bind(wx.EVT_BUTTON, self.chooseImage)
        self.classifyPreop.Bind(wx.EVT_BUTTON, self.markPreop)
        self.classifyPostop.Bind(wx.EVT_BUTTON, self.markPostop)
        self.deselectImageButton.Bind(wx.EVT_BUTTON, self.deselectImage)
        self.anonSelected.Bind(wx.EVT_BUTTON, self.nextScreen)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

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

    def OnClose(self, event):
        parent = self.GetParent()
        self.Destroy()
        parent.Destroy()
        event.Skip()

    def showUnusedFiles(self):
        self.LeftPatientText = []
        self.LeftPatientFileLists = []
        global patientLib
        for name, value in patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            self.LeftPatientText.append(wx.StaticText(self.leftPanel, label=pName))

            # gets all the unusedFiles from each patient
            files = value.unusedFiles
            fileNames = []
            lb = wx.ListBox(self.leftPanel, size=(self.WindowSize[0] / 4 - 50, 100), choices=fileNames)
            for f in files:
                if f in value.preopFiles:
                    lb.Append(os.path.basename(os.path.normpath(f.filename))+'*preop', value)
                elif f in value.postopFiles:
                    lb.Append(os.path.basename(os.path.normpath(f.filename))+'*postop', value)
                else:
                    lb.Append(os.path.basename(os.path.normpath(f.filename)), value)
            self.LeftPatientFileLists.append(lb)

            lb.Bind(wx.EVT_LISTBOX, self.displayImage)

        for nameText, listBox in zip(self.LeftPatientText, self.LeftPatientFileLists):
            self.leftSizer.Add(nameText, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10 )
            self.leftSizer.Add(listBox, 0, wx.LEFT, 10)

        self.leftSizer.Layout()
        self.Show(True)

    def showUsedFiles(self):
        self.RightPatientText = []
        self.RightPatientFileLists = []

        global patientLib
        for name, value in patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            self.RightPatientText.append(wx.StaticText(self.rightPanel, label=pName))

            # gets usedFiles from each patient
            files = value.usedFiles
            fileNames = []
            rlb = wx.ListBox(self.rightPanel, size=(self.WindowSize[0] / 4 - 50, 100), choices=fileNames)
            # rlb = wx.ListBox(self.panel, pos=(950, ((count * 125) + 30)), size=(300, 100), choices=fileNames)
            for f in files:
                if f in value.preopFiles:
                    rlb.Append(os.path.basename(os.path.normpath(f.filename))+'*preop', value)
                elif f in value.postopFiles:
                    rlb.Append(os.path.basename(os.path.normpath(f.filename))+'*postop', value)
                else:
                    rlb.Append(os.path.basename(os.path.normpath(f.filename)), value)
            self.RightPatientFileLists.append(rlb)
            rlb.Bind(wx.EVT_LISTBOX, self.displayImage)

        for nameText, listBox in zip(self.RightPatientText, self.RightPatientFileLists):
            self.rightSizer.Add(nameText, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10 )
            self.rightSizer.Add(listBox, 0, wx.LEFT, 10)

        self.rightSizer.Layout()
        self.Show(True)

    def displayImage(self, event):
        self.CurrentPatient = event.GetClientData()
        imgName = event.GetString().split("*")[0]

        # get the pydicom object
        for dcmObject in self.CurrentPatient.unusedFiles + self.CurrentPatient.usedFiles:
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
        self.deselectImageButton.Show()

        #for rlb in self.RightPatientFileLists:
        #    rlb.Bind(wx.EVT_LISTBOX, self.displayImage)

        self.xrayImage = wx.StaticBitmap(self.panel, -1, png, (380, 10), (500, 500))


    def markPreop(self, event):
        # if the current file is already mark post op, remove it from that list
        if self.CurrentDICOMObject in self.CurrentPatient.postopFiles:
            self.CurrentPatient.postopFiles.remove(self.CurrentDICOMObject)

        # add the file to the preop list if it's not already there
        if self.CurrentDICOMObject not in self.CurrentPatient.preopFiles:
            self.CurrentPatient.preopFiles.append(self.CurrentDICOMObject)

        self.reprintFiles()



    def markPostop(self, event):
        if self.CurrentDICOMObject in self.CurrentPatient.preopFiles:
            self.CurrentPatient.preopFiles.remove(self.CurrentDICOMObject)

        if self.CurrentDICOMObject not in self.CurrentPatient.postopFiles:
            self.CurrentPatient.postopFiles.append(self.CurrentDICOMObject)

        self.reprintFiles()

    def reprintFiles(self):

        for leftnameText in self.LeftPatientText:
            leftnameText.Destroy()
        for leftlistBox in self.LeftPatientFileLists:
            leftlistBox.Destroy()


        for rightnameText in self.RightPatientText:
            rightnameText.Destroy()
        for rightlistBox in self.RightPatientFileLists:
            rightlistBox.Destroy()

        self.leftPanel.Layout()
        self.rightPanel.Layout()
        # reprints the new unused files and patients
        self.showUnusedFiles()
        self.showUsedFiles()

    def deselectImage(self, event):

        if self.CurrentDICOMObject not in self.CurrentPatient.unusedFiles:
            self.CurrentPatient.unusedFiles.append(self.CurrentDICOMObject)
        if self.CurrentDICOMObject in self.CurrentPatient.usedFiles:
            self.CurrentPatient.usedFiles.remove(self.CurrentDICOMObject)

        '''
        self.CurrentPatient.unusedFiles.append(self.CurrentDICOMObject)
        self.CurrentPatient.usedFiles.remove(self.CurrentDICOMObject)
        '''


        for leftnameText in self.LeftPatientText:
            leftnameText.Destroy()
        for leftlistBox in self.LeftPatientFileLists:
            leftlistBox.Destroy()


        for rightnameText in self.RightPatientText:
            rightnameText.Destroy()
        for rightlistBox in self.RightPatientFileLists:
            rightlistBox.Destroy()

        self.leftPanel.Layout()
        self.rightPanel.Layout()
        # reprints the new unused files and patients
        self.showUnusedFiles()
        self.showUsedFiles()


    def chooseImage(self, event):

        if self.CurrentDICOMObject not in self.CurrentPatient.usedFiles:
            self.CurrentPatient.usedFiles.append(self.CurrentDICOMObject)
        if self.CurrentDICOMObject in self.CurrentPatient.unusedFiles:
            self.CurrentPatient.unusedFiles.remove(self.CurrentDICOMObject)

        '''
        # adds selected file to usedFiles list
        self.CurrentPatient.usedFiles.append(self.CurrentDICOMObject)
        # removes the selected image from the unused files
        self.CurrentPatient.unusedFiles.remove(self.CurrentDICOMObject)
        '''

        # destroys the existing listboxes, buttons, and text printed to the screen
        '''
        numChildren = len(self.leftSizer.GetChildren())
        for child in range(0, numChildren):
            self.leftSizer.Hide(0)
            self.leftSizer.Remove(0)
        '''

        for leftnameText in self.LeftPatientText:
            leftnameText.Destroy()
        for leftlistBox in self.LeftPatientFileLists:
            leftlistBox.Destroy()

        '''
        numChildren = len(self.rightSizer.GetChildren())
        for child in range(0, numChildren):
            self.rightSizer.Hide(0)
            self.rightSizer.Remove(0)
        '''

        for rightnameText in self.RightPatientText:
            rightnameText.Destroy()
        for rightlistBox in self.RightPatientFileLists:
            rightlistBox.Destroy()

        self.leftPanel.Layout()
        self.rightPanel.Layout()
        # reprints the new unused files and patients
        self.showUnusedFiles()
        self.showUsedFiles()

    def nextScreen(self, event):
        #TODO: should first check that there are selected images
        AnonymizeFiles(self, title='Anonymize Files')
        self.Show(False)


import wx.lib.stattext as ST
import wx.grid


class AnonymizeFiles(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AnonymizeFiles, self).__init__(*args, **kwargs)
        global patientLib

        # FRAME ATTRIBUTES

        self.Maximize(True)
        self.WindowSize = self.GetSize()
        self.parent = self.GetParent()

        # LOGIC ATTRIBUTES

        self.SelectedPatients = []
        self.SelectedPatientFiles = []
        self.selectedPatient = None
        self.selectedImage = None

        # PANEL INITIALIZATIONS

        self.panel = wx.Panel(self)

        self.filePanel = sp.ScrolledPanel(self.panel, size=(self.WindowSize[0] / 4, self.WindowSize[1] - 20))
        self.filePanel.SetupScrolling()
        self.filePanel.SetBackgroundColour((200,200,200))

        self.infoPanel = sp.ScrolledPanel(self.panel)
        self.infoPanel.SetupScrolling()
        self.infoPanel.SetBackgroundColour((100,200,200))

        self.genInfoPanel = wx.Panel(self.infoPanel)
        self.genInfoPanel.SetBackgroundColour((200,50,50))

        self.patientInfo = wx.StaticText(self.genInfoPanel)
        self.newPatientNameLabel = wx.StaticText(self.genInfoPanel)
        self.newPatientNameLabel.Hide()
        self.newPatientName = wx.TextCtrl(self.genInfoPanel, style=wx.TE_PROCESS_ENTER, value="Enter New Patient Name")
        self.newPatientName.Hide()
        self.updateNameButton = wx.Button(self.genInfoPanel, label="Update Name")
        self.updateNameButton.Hide()

        self.exportButton = wx.Button(self.genInfoPanel, label="Export Selected",)

        self.patientTags = wx.grid.Grid(self.infoPanel)
        self.patientTags.CreateGrid(0,2)
        self.patientTags.SetColLabelValue(0, 'Tag')
        self.patientTags.SetColLabelValue(1, 'Value')
        self.patientTags.Hide()


        #for name, value in patientLib.PatientObjects.iteritems():
        #    print (value.unAnon_PatientsName)

        # EVENT HANDLERS

        self.Bind(wx.EVT_CLOSE, self.parent.OnClose)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.newPatientName.Bind(wx.EVT_SET_FOCUS, self.highlightText)
        self.updateNameButton.Bind(wx.EVT_BUTTON, self.updateName)
        self.newPatientName.Bind(wx.EVT_TEXT_ENTER, self.updateName)

        # SIZERS

        self.fileSizer = wx.BoxSizer(wx.VERTICAL)
        self.filePanel.SetSizer(self.fileSizer)

        self.genInfoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.genInfoSizer.Add(self.patientInfo, 4, wx.LEFT | wx.ALL, border=10)
        self.genInfoSizer.Add(self.newPatientNameLabel, 1, wx.ALIGN_RIGHT | wx.TOP, border=10)
        self.genInfoSizer.Add(self.newPatientName,3, wx.ALIGN_LEFT | wx.TOP, border=10)
        self.genInfoSizer.Add(self.updateNameButton, 1, wx.LEFT | wx.ALL, border=10)
        self.genInfoSizer.AddStretchSpacer(1)
        self.genInfoSizer.Add(self.exportButton, 1, wx.RIGHT | wx.ALL, border=10)
        self.genInfoPanel.SetSizer(self.genInfoSizer)

        self.infoSizer = wx.BoxSizer(wx.VERTICAL)
        self.infoSizer.Add(self.genInfoPanel, 1, wx.LEFT | wx.EXPAND| wx.ALL, border=10)
        self.infoSizer.Add(self.patientTags, 5, wx.CENTER | wx.ALL, border=10)
        self.infoPanel.SetSizer(self.infoSizer)

        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.horzSizer.Add(self.filePanel, 1)
        self.horzSizer.Add(self.infoPanel, 3, wx.EXPAND)
        self.panel.SetSizer(self.horzSizer)

        # FUNCTIONS

        self.showSelectedFiles()

        # UPDATE LAYOUT
        self.infoPanel.Layout()
        self.panel.Layout()

    def updateName(self, event):
        for ds in self.selectedPatient.usedFiles:
            ds.PatientName = str(self.newPatientName.GetValue())

        self.refreshGrid()

    def highlightText(self, event):
        # set selection works on windows, not on mac
        event.GetEventObject().SetSelection(-1,-1)


    def OnClose(self, event):
        self.Destroy()
        event.Skip()

    def showSelectedFiles(self):
        # Initialize function variables
        self.SelectedPatients = []  # holds the patient name StaticText widgets
        self.SelectedPatientFiles = []  # holds the patient files ListBox widgets
        global patientLib

        # goes through every patient in
        for name, value in patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName

            # if there are selected files for the patient
            if value.usedFiles:
                pBday = value.unAnon_PatientBday
                selectableText = ST.GenStaticText(self.filePanel, label=(pName+pBday))
                self.SelectedPatients.append(selectableText)
                #self.SelectedPatients.append(ST.GenStaticText(self.filePanel, label=pName))
                selectableText.Bind(wx.EVT_LEFT_DOWN, self.selectPatient)

            # gets usedFiles from each patient
            files = value.usedFiles
            fileNames = []

            # gets name of selected ('used') files associated with current patient
            if(files):
                rlb = wx.CheckListBox(self.filePanel, size=(self.WindowSize[0] / 4 - 50, 100), choices=fileNames)
                for f in files:
                    if f in value.preopFiles:
                        rlb.Append(os.path.basename(os.path.normpath(f.filename)) + '*preop', value)
                    elif f in value.postopFiles:
                        rlb.Append(os.path.basename(os.path.normpath(f.filename)) + '*postop', value)
                    else:
                        rlb.Append(os.path.basename(os.path.normpath(f.filename)), value)
                self.SelectedPatientFiles.append(rlb)
                rlb.Bind(wx.EVT_LISTBOX, self.displayImageInfo)


        # adds the StaticText and Listbox widgets to the boxSizer for the filePanel (fileSizer)
        for nameText, listBox in zip(self.SelectedPatients, self.SelectedPatientFiles):
            self.fileSizer.Add(nameText, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
            self.fileSizer.Add(listBox, 0, wx.LEFT, 10)

        self.fileSizer.Layout()
        self.Show(True)

    def selectPatient(self, event):
        global patientLib

        # remove highlight from other patient names
        self.unSelectPatients(event.GetEventObject())
        self.newPatientName.SetValue("Enter New Patient Name")

        self.selectedPatient = patientLib.PatientObjects[event.GetEventObject().Label]
        self.selectedImage = self.selectedPatient.usedFiles[0] # by default selects first image when patient selected
        #print patient.unAnon_PatientsName
        #print (patient.usedFiles[0]).PatientSex

        #self.patientInfo.SetLabel(patient.unAnon_PatientsName)



        self.refreshGrid()

        # check if patient in post or pre-op & display on infoPanel
        #for name, value in patientLib.PatientObjects:

    def displayImageInfo(self, event):
        self.selectedPatient = event.GetClientData()
        for ds in self.selectedPatient.usedFiles:
            if os.path.basename(os.path.normpath(ds.filename)) == (event.GetString().split("*")[0]):
                self.selectedImage = ds

        for textObject in self.SelectedPatients:
            textObject.SetForegroundColour((0, 0, 0))
            textObject.SetBackgroundColour((200, 200, 200))
            textObject.Refresh()
        self.refreshGrid()


    def refreshGrid(self):

        if self.patientTags.GetNumberRows() != 0:
            self.patientTags.DeleteRows(numRows=self.patientTags.GetNumberRows())

        dataset = self.selectedImage

        for elem in dataset:
            tagString = str(elem.tag) + ' ' + str(elem.name)
            valueString = str(elem.repval)


            self.patientTags.AppendRows(1)
            rows = self.patientTags.GetNumberRows()
            self.patientTags.SetCellValue(rows-1,0, tagString)
            self.patientTags.SetCellValue(rows-1,1, valueString)

            if 'Patient' in tagString:
                self.patientTags.SetCellBackgroundColour(rows-1, 0, (200,0,0))
                self.patientTags.SetCellBackgroundColour(rows-1, 1, (200,0,0))

        self.patientTags.AutoSize()
        self.patientTags.Show()
        self.patientInfo.SetLabel("Old Patient Name: " + self.selectedPatient.unAnon_PatientsName)
        self.patientInfo.Show()
        self.newPatientNameLabel.SetLabel("New Patient Name: ")
        self.newPatientNameLabel.Show()
        self.newPatientName.Show()
        self.updateNameButton.Show()

        self.infoPanel.Layout()
        self.genInfoPanel.Layout()




    def unSelectPatients(self, selectedText):
        for textObject in self.SelectedPatients:
            if selectedText.Label != textObject.GetLabel():
                textObject.SetForegroundColour((0,0,0))
                textObject.SetBackgroundColour((200,200,200))
                textObject.Refresh()
        selectedText.SetForegroundColour((0,0,0))
        selectedText.SetBackgroundColour((88, 164, 221))
        selectedText.Refresh()







def createLibrary():
    global sourcePath
    patientLib = PatientLibrary(sourcePath)
    patientLib.populatePatientLibrary()
    return patientLib


if __name__ == "__main__":
    app = wx.App()
    SelectFolderDialog(None, title="Select DICOM Directory")
    app.MainLoop()