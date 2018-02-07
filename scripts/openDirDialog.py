'''
Test of a dialog to open one or more folders
'''

import os
import wx
import wx.lib.agw.multidirdialog as MDD

class MyForm(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self,None, wx.ID_ANY, "Choose a DICOM Directory")
        panel = wx.Panel(self, wx.ID_ANY)
        self.currentDirectory = os.getcwd()
        
        selectDirsButton = wx.Button(panel, label="Select Patient Folder(s)")
        selectDirsButton.Bind(wx.EVT_BUTTON, self.onSelectDirs)

    def onSelectDirs(self, event):
        dlg = MDD.MultiDirDialog(self, title="Choose source folder", defaultPath=self.currentDirectory, agwStyle=0)
        
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            print "Source folder selected:"
            for path in paths:
                print path
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()
