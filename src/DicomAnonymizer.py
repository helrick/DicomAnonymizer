'''
GUI for DICOM Anonymizer
'''

import wx
import os
import sys
from PatientSelector import PatientLibrary

import wx.lib.scrolledpanel as sp
import wx.lib.stattext as ST
import wx.grid

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
        self.InfoIcon = wx.StaticBitmap(panel, bitmap=(wx.ArtProvider.GetBitmap(wx.ART_HELP)))
        self.ContinueButton = wx.Button(panel, label="Continue")

        # Sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddStretchSpacer(prop=1)

        self.sizer.Add(self.InfoIcon, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        self.sizer.Add(self.PathSelection, flag=wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border=10)
        self.sizer.Add(self.SelectDirButton, flag=wx.ALIGN_CENTER)

        self.sizer.AddStretchSpacer(prop=1)

        self.sizer.Add(self.ContinueButton, flag=wx.ALIGN_RIGHT | wx.ALL, border=10 )
        panel.SetSizer(self.sizer)
        panel.Layout()

        # Event Handlers
        self.SelectDirButton.Bind(wx.EVT_BUTTON, self.onSelectDir)
        self.InfoIcon.Bind(wx.EVT_MOTION, self.displayInfo)

        self.SetInitialSize((550, 225))
        self.Center()
        self.Show()

    def displayInfo(self, event):
        self.InfoIcon.SetToolTip("Click 'Select a DICOM Directory', choose a folder containing DICOM images, and press "
                                 "'Continue' to view the selected files")

    def onSelectDir(self, event):
        dialog = wx.DirDialog(self, "Choose Source Folder", "", wx.DD_DEFAULT_STYLE| wx.DD_DIR_MUST_EXIST)
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

    def OnClose(self, event):
        try:
          os.remove('tempfile.png')
        except OSError:
          pass
        self.Destroy()
        sys.exit()


class SelectFiles(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(SelectFiles, self).__init__(*args, **kwargs)
        global patientLib

        patientLib = createLibrary()
        self.Maximize(True)

        self.panel = wx.Panel(self)
        self.WindowSize = self.GetSize()
        self.SetSizeHints(self.WindowSize[0],self.WindowSize[1])

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.leftPanel = sp.ScrolledPanel(self.panel, size=(self.WindowSize[0] / 4, self.WindowSize[1] - 20))
        self.leftPanel.SetupScrolling()
        self.leftPanel.SetBackgroundColour((200,200,200))

        self.rightPanel = sp.ScrolledPanel(self.panel, size=(self.WindowSize[0] / 4, self.WindowSize[1] - 100))
        self.rightPanel.SetupScrolling()
        self.rightPanel.SetBackgroundColour((200,200,200))

        self.imagePanel = wx.Panel(self.panel, pos=(400, 10))
        self.imagePanel.Show()
        self.xrayImage = wx.StaticBitmap()
        self.xrayDate = wx.StaticText(self.panel, pos=((self.WindowSize[0]/2) - 250, 520))

        # Initialize Buttons

        self.selectImage = wx.Button(self.panel, pos=(self.WindowSize[0]/2 - 75, 520), label="Select Image")
        self.deselectImageButton = wx.Button(self.panel, pos=(self.WindowSize[0]/2 + 25, 520), label="Deselect Image")

        self.chooseLabel = wx.ComboBox(self.panel, pos=(self.WindowSize[0]/2 -100, 580), choices=["Pre-Op",
                                       "6 weeks Post-Op", "3 months Post-Op", "6 months Post-Op", "1 year Post-Op", "5 years Post-Op"])
        self.setLabelButton = wx.Button(self.panel, pos=(self.WindowSize[0]/2 + 75, 582), label="Set Label")

        self.anonSelected = wx.Button(self.panel, pos=(self.WindowSize[0]*.83, self.WindowSize[1]*0.9), label="Anonymize Selected")
        self.InfoIcon = wx.StaticBitmap(self.imagePanel, bitmap=(wx.ArtProvider.GetBitmap(wx.ART_HELP)))

        # Hide/Show Buttons
        self.selectImage.Hide()
        self.deselectImageButton.Hide()
        self.chooseLabel.Hide()
        self.setLabelButton.Hide()
        self.anonSelected.Show()

        # EVENT HANDLERS
        self.selectImage.Bind(wx.EVT_BUTTON, self.chooseImage)
        self.deselectImageButton.Bind(wx.EVT_BUTTON, self.deselectImage)
        self.setLabelButton.Bind(wx.EVT_BUTTON, self.setLabel)
        self.anonSelected.Bind(wx.EVT_BUTTON, self.nextScreen)
        self.InfoIcon.Bind(wx.EVT_MOTION, self.displayInfo)

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

        self.imgSizer = wx.BoxSizer( wx.HORIZONTAL)
        self.imgSizer.Add(self.InfoIcon, 0, wx.ALIGN_LEFT | wx.ALL, border=5)
        self.imagePanel.SetSizer(self.imgSizer)
        self.imgSizer.Layout()

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
        try:
          os.remove('tempfile.png')
        except OSError:
          pass
        parent = self.GetParent()
        parent.Destroy()
        sys.exit()

    def displayInfo(self, event):
        # figure out if can make this tooltip stay a bit longer
        wx.ToolTip.SetAutoPop(300000)
        self.InfoIcon.SetToolTip("Click images on the left to preview them. Click 'Select Image' to mark an image for "
                                 "anonymization, and 'Label PreOp' or 'Label PostOp' to label the image. If you'd like "
                                 "to change your selection, choose an image on the right and click 'Deselect Image'. "
                                 "Once you are satisfied with your selections, Click 'Anonymize Selected' to go to the "
                                 "next step")

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
                set = False
                for lst in value.fileLabels:
                    if f in lst:
                        lb.Append(os.path.basename(os.path.normpath(f.filename)) + '$' + lst[1], value)
                        set = True
                if not set:
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
            for f in files:
                set = False
                for lst in value.fileLabels:
                    if f in lst:
                        rlb.Append(os.path.basename(os.path.normpath(f.filename))+'$'+lst[1], value)
                        set = True
                if not set:
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
        imgName = event.GetString().split("$")[0]

        # get the pydicom object
        for dcmObject in self.CurrentPatient.unusedFiles + self.CurrentPatient.usedFiles:
            if (os.path.basename(os.path.normpath(dcmObject.filename)) == imgName):
                self.CurrentDICOMObject = dcmObject

        # fill date string here
        self.xrayDate.SetLabel(self.CurrentDICOMObject.AcquisitionDate)

        from matplotlib import pyplot
        try:
            pyplot.imshow(self.CurrentDICOMObject.pixel_array, cmap=pyplot.cm.bone)
            pyplot.axis('off')
        except:
            if not self.selectImage.IsShown():
                self.selectImage.Show()
            self.chooseLabel.Show()
            self.setLabelButton.Show()
            self.deselectImageButton.Show()
            print 'unable to display images of this type'
            return

        from io import BytesIO
        from matplotlib import rc

        rc('savefig', format='png')
        buf = BytesIO()
        pyplot.savefig(buf, bbox_inches='tight', pad_inches=0.0)
        buf.seek(0)
        img = wx.Image(buf, wx.BITMAP_TYPE_PNG)
        img.Resize(size=(500, 500), pos=(0, 0), red=255, green=255, blue=255)
        png = wx.Bitmap(img)

        # checks that the image and button are properly destroyed before deleting
        if self.xrayImage:
            self.xrayImage.Destroy()
        if not self.selectImage.IsShown():
            self.selectImage.Show()
        self.chooseLabel.Show()
        self.setLabelButton.Show()
        self.deselectImageButton.Show()

        self.xrayImage = wx.StaticBitmap(self.panel, -1, png, (self.WindowSize[0]/2 -250, 10), (500, 500))

    def setLabel(self, event):
        isSet = False
        for lst in self.CurrentPatient.fileLabels:
            if self.CurrentDICOMObject in lst:
                lst[1] = self.chooseLabel.GetValue()
                isSet = True
        if not isSet:
            self.CurrentPatient.fileLabels.append([self.CurrentDICOMObject, self.chooseLabel.GetValue()])

        self.chooseImage(event)
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

    def nextScreen(self, event):
        #TODO: should first check that there are selected images
        global patientLib
        patientLib.basicAnonymizeLibrary()
        AnonymizeFiles(self, title='Anonymize Files')
        self.Show(False)


class AnonymizeFiles(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AnonymizeFiles, self).__init__(*args, **kwargs)
        global patientLib

        # FRAME ATTRIBUTES

        self.Maximize(True)
        self.WindowSize = self.GetSize()
        self.SetSizeHints(self.WindowSize[0], self.WindowSize[1])
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

        self.genInfoPanel = wx.Panel(self.infoPanel)

        self.patientInfo = wx.StaticText(self.genInfoPanel)
        self.newPatientNameLabel = wx.StaticText(self.genInfoPanel)
        self.newPatientNameLabel.Hide()
        self.newPatientName = wx.TextCtrl(self.genInfoPanel, style=wx.TE_PROCESS_ENTER, value="Enter New Patient Name")
        self.newPatientName.Hide()
        self.updateNameButton = wx.Button(self.genInfoPanel, label="Update Name")
        self.updateNameButton.Hide()

        self.exportButton = wx.Button(self.genInfoPanel, label="Export Selected")

        self.patientTags = wx.grid.Grid(self.infoPanel)
        self.patientTags.CreateGrid(0,2)
        self.patientTags.SetColLabelValue(0, 'Tag')
        self.patientTags.SetColLabelValue(1, 'Value')
        self.patientTags.Hide()

        # EVENT HANDLERS

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.exportButton.Bind(wx.EVT_BUTTON, self.exportSelected)
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

    def exportSelected(self, event):
        dest = ""
        dialog = wx.DirDialog(self, "Choose or Create Destination Folder", dest)
        if dialog.ShowModal() == wx.ID_OK:
            dest = dialog.GetPath()

        for lb in self.SelectedPatientFiles:
            # get the patient from the first checked image value
            try:
                curr_patient = (lb.GetClientData(lb.GetCheckedItems()[0]))
                for item in lb.GetCheckedItems():
                    fileString = str(lb.GetString(item))
                    for ds in curr_patient.usedFiles:
                        if os.path.basename(os.path.normpath(ds.filename)) == fileString.split("$")[0]:
                            ds.save_as(str(os.path.join(dest, fileString.split("$")[0])))
            except:
                # no files from this listbox selected
                pass

        # TODO: ensure file actually exported before displaying success message

        dlg = wx.MessageDialog(self, 'Files Exported, the program can be closed now', '', wx.OK | wx.ICON_INFORMATION)
        val = dlg.ShowModal()
        dlg.Show()

        dialog.Destroy()

    def OnClose(self, event):
        grandparent = self.GetParent().GetParent()
        grandparent.Destroy()
        self.Destroy()
        sys.exit()

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
                sDate = value.sessionDate
                selectableText = ST.GenStaticText(self.filePanel, label=(pName+'-'+sDate))
                self.SelectedPatients.append(selectableText)
                selectableText.Bind(wx.EVT_LEFT_DOWN, self.selectPatient)

            # gets usedFiles from each patient
            files = value.usedFiles
            fileNames = []

            # gets name of selected ('used') files associated with current patient
            if files:
                rlb = wx.CheckListBox(self.filePanel, size=(self.WindowSize[0] / 4 - 50, 100), choices=fileNames)
                for f in files:
                    isSet = False
                    for lst in value.fileLabels:
                        if f in lst:
                            rlb.Append(os.path.basename(os.path.normpath(f.filename)) + '$' + lst[1], value)
                            isSet = True
                    if not isSet:
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

        self.refreshGrid()


    def displayImageInfo(self, event):
        self.selectedPatient = event.GetClientData()
        for ds in self.selectedPatient.usedFiles:
            if os.path.basename(os.path.normpath(ds.filename)) == (event.GetString().split("$")[0]):
                self.selectedImage = ds

        for textObject in self.SelectedPatients:
            textObject.SetForegroundColour((0, 0, 0))
            textObject.SetBackgroundColour((200, 200, 200))
            textObject.Refresh()
        self.refreshGrid()


    def refreshGrid(self):
        global patientLib

        if self.patientTags.GetNumberRows() != 0:
            self.patientTags.DeleteRows(numRows=self.patientTags.GetNumberRows())

        dataset = self.selectedImage

        for elem in dataset:
            tagString = str(elem.tag) + ' ' + str(elem.name)
            valueString = str(elem.repval)
            tagName = str(elem.tag)

            self.patientTags.AppendRows(1)
            rows = self.patientTags.GetNumberRows()
            self.patientTags.SetCellValue(rows-1,0, tagString)
            self.patientTags.SetCellValue(rows-1,1, valueString)

            if tagName in patientLib.tagsAnon_nums:
                self.patientTags.SetCellBackgroundColour(rows - 1, 0, (113, 237, 142))
                self.patientTags.SetCellBackgroundColour(rows - 1, 1, (113, 237, 142))

            if tagName == '(0010, 0010)':
                self.patientTags.SetCellBackgroundColour(rows-1, 0, (255, 228, 94))
                self.patientTags.SetCellBackgroundColour(rows-1, 1, (255, 228, 94))

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
    SelectFolderDialog(None, title="Select DICOM Directory", style= wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    app.MainLoop()
