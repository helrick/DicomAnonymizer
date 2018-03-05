'''
Program Flow for DICOM Anonymizer
'''

import wx
import os.path
from PatientSelector import PatientLibrary
import Functions

sourcePath = ''

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



class SelectFiles(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SelectFiles, self).__init__(*args, **kwargs)
        self.PatientLib = Functions.createLibrary(sourcePath)
        self.CurrentDICOMObject = None
        self.CurrentPatient = None

        self.panel = wx.Panel(self)

        self.leftPanel = wx.Panel(self.panel)

        # Initialize Widgets (left, center, right)
        self.LeftPatientText = []
        self.LeftPatientFileLists = []

        '''
        self.xrayImage = wx.StaticBitmap()
        self.selectImage = wx.Button(self.panel, label="Select Image")
        self.selectImage.Show(False)
        '''

        self.RightPatientText = []
        self.RightPatientFileLists = []

        # Create Left Sizer
        self.LeftVertSizer = wx.BoxSizer(wx.VERTICAL)

        # fill the PatientText and FileLists with Patient info
        self.getUnusedFiles()


        # put left widgets into left sizer

        for nameText, listBox in zip(self.LeftPatientText, self.LeftPatientFileLists):
            self.LeftVertSizer.Add(nameText, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
            self.LeftVertSizer.Add(listBox, flag=wx.ALIGN_CENTER | wx.ALL, border=10)


        # make left sizer the sizer for left panel
        self.leftPanel.SetSizer(self.LeftVertSizer)

        # make the parent sizer for main panel
        self.HorzSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HorzSizer.Add(self.LeftVertSizer, flag=wx.ALIGN_LEFT)

        self.SetSizer(self.HorzSizer)
        self.panel.Layout()


        '''
        comment after here
       

        # Create the Sizers
        self.HorzSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.LeftVertSizer = wx.BoxSizer(wx.VERTICAL)
        self.CenterVertSizer = wx.BoxSizer(wx.VERTICAL)
        self.RightVertSizer = wx.BoxSizer(wx.VERTICAL)

        # fill the PatientText and FileLists with Patient info
        self.getUnusedFiles()

        # Put Widgets into Left Sizer

        for nameText, listBox in zip(self.LeftPatientText, self.LeftPatientFileLists):
            self.LeftVertSizer.Add(nameText, flag=wx.ALIGN_CENTER | wx.ALL, border = 10)
            self.LeftVertSizer.Add(listBox, flag=wx.ALIGN_CENTER | wx.ALL, border = 10)
        
        # Put Widgets into Center Sizer
        #self.CenterVertSizer.Add(self.selectImage, flag=wx.ALIGN_CENTER | wx.ALL, border = 10)


        # Put Sub-Sizers into Horizontal Sizers
        
        self.HorzSizer.Add(self.LeftVertSizer, flag=wx.ALIGN_LEFT | wx.EXPAND)
        self.HorzSizer.Add(self.CenterVertSizer, flag=wx.ALIGN_CENTER | wx.EXPAND)
        
        # self.HorzSizer.Add(self.LeftVertSizer, flag=wx.ALIGN_LEFT | wx.EXPAND)

        self.leftPanel.SetSizer(self.LeftVertSizer)
        self.leftPanel.Layout()
        self.HorzSizer.Add(self.leftPanel)


        self.panel.SetSizer(self.HorzSizer)
        self.panel.Layout()
        '''
        self.Maximize(True)
        self.Show()

    def getUnusedFiles(self):
        self.LeftPatientText = []
        self.LeftPatientFileLists = []
        count = 0
        for name, value in self.PatientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            self.LeftPatientText.append(wx.StaticText(self.leftPanel, label=pName))

            files = value.unusedFiles
            fileNames = []
            lb = wx.ListBox(self.leftPanel, choices=fileNames)
            for f in files:
                lb.Append(os.path.basename(os.path.normpath(f.filename)), value)
            self.LeftPatientFileLists.append(lb)
            count = count + 1
            #lb.Bind(wx.EVT_LISTBOX, self.displayImage)


    def displayImage(self, event):
        self.CurrentPatient = event.GetClientData()
        imgName = event.GetString()

        #get the pydicom object given the current patient and image name
        for dcmObject in self.CurrentPatient.unusedFiles:
            if(os.path.basename(os.path.normpath(dcmObject.filename)) == imgName):
                self.CurrentDICOMObject = dcmObject

        from matplotlib import pyplot
        pyplot.imshow(self.CurrentDICOMObject.pixel_array, cmap=pyplot.cm.bone)
        pyplot.axis('off')

        pyplot.savefig('tempfile.png', bbox_inches='tight', pad_inches=0.0)
        i = wx.Image('tempfile.png', 'image/png', -1)
        i.Resize(size=(500, 500), pos=(0, 0), red=255, green=255, blue=255)
        png = i.ConvertToBitmap()

        if self.xrayImage:
            self.xrayImage.Destroy()
        if not self.selectImage.IsShown():
            self.selectImage.Show()

        self.xrayImage = wx.StaticBitmap(self.centerPanel, -1, png, (500,500))






if __name__ == "__main__":
    app = wx.App()
    SelectFolderDialog(None, title="Select DICOM Directory")
    app.MainLoop()