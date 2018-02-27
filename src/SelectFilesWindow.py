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

        self.image = wx.StaticText(self.panel,pos=(10,0),label='')

        self.showUnusedFiles()



    def showUnusedFiles(self):
        #panel = wx.Panel(self)
        #idea: for each patient, print their name, then make a listbox for each patient
        #inside the listbox have all the files associated with that patient
        #pLib = createLibrary()

        patientText = []
        patientFileLists = []
        count = 0
        '''
        patientName = wx.StaticText(panel, pos=(10,15), label="John Doe")
        chooseFile = wx.ListBox(panel, pos=(10,30), size=(300,100), 
            choices=['xray1','chart','ct','xray2','xray3','chart2','mri'])
        self.Show(True)
        '''
        for name, value in self.patientLib.PatientObjects.iteritems():
            pName = value.unAnon_PatientsName
            patientText.append(wx.StaticText(self.panel, pos=(10,((count*125)+15)), label=pName))
            #gets all the unusedFiles from each patient
            files = value.unusedFiles
            fileNames = []
            lb = wx.ListBox(self.panel, pos=(10, ((count * 125) + 30)), size=(300, 100), choices=fileNames)
            for f in files:
                lb.Append(os.path.basename(os.path.normpath(f.filename)), value)
                #fileNames.append(os.path.basename(os.path.normpath(f.filename)) + '-' + name)
            patientFileLists.append(lb)
            #patientFileLists.append(wx.ListBox(self.panel, pos=(10,((count*125)+30)),
            #                                   size=(300,100), choices=fileNames))
            count = count+1
            lb.Bind(wx.EVT_LISTBOX, self.displayImage)

        #self.Bind(wx.EVT_LISTBOX,self.displayImage)

        self.Show(True)

    def displayImage(self, event):
        obj = event.GetClientData()
        imgName = event.GetString()
        self.image.SetLabel(obj.unAnon_PatientsName + imgName)
        ds = ''
        #get the pydicom object
        for dcmObject in obj.unusedFiles:
            if (os.path.basename(os.path.normpath(dcmObject.filename)) == imgName):
                ds = dcmObject

        self.image.SetLabel(ds.PatientAddress)

        from matplotlib import pyplot
        import matplotlib
        pyplot.imshow(ds.pixel_array, cmap=pyplot.cm.bone)
        pyplot.axis('off')



        pyplot.savefig('tempfile.png', bbox_inches = 'tight', pad_inches=0.0)
        i = wx.Image('testfile.png', 'image/png', -1)
        png = i.ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (400, 10), (png.GetWidth(), png.GetHeight()))
        '''
        import tempfile
        with tempfile.TemporaryFile(suffix=".png") as tmpfile:
            pyplot.savefig(tmpfile, format="png")
            tmpfile.seek(0)
            import base64
            print base64.b64encode(tmpfile.read())
            im = wx.Image(tempfile)
            im.Show()
             
        print ds.Rows
        print ds.Columns
        image = wx.Image(ds.Columns,ds.Rows)
        image.SetData( (ds.pixel_array).tostring())
        image.Show()
        #bitmap = wx.Image(ds.Rows, ds.Columns, ds.pixel_array)
        #bitmap.Show()
        
        

        #image = wx.StaticText(self.panel,pos=(10,0),label=obj.unAnon_PatientsName)
        #image = wx.StaticText(self.panel, pos=(10, 0), label=event.GetString())
        #image.Show(True)
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

