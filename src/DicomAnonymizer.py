'''
Program Flow for DICOM Anonymizer
'''

import wx
import os.path

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
        dialog.Destroy()
        SelectFiles(None, title="Select Files to Anonymize")


class SelectFiles(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SelectFiles, self).__init__(*args, **kwargs)
        self.Show()




if __name__ == "__main__":
    app = wx.App()
    SelectFolderDialog(None, title="Select DICOM Directory")
    app.MainLoop()