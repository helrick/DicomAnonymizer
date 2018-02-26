'''
Testing the embedding of a dicom image inside a wxPython GUI window
'''
import dicom
import matplotlib
import wx
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas

#for displaying the image as part of a GUI window
def main():
    ds = dicom.read_file('xr_tspine.dcm')

class Window(wx.Frame):
    title = 'testing plot embedding'
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        self.create_main_panel()

        self.draw_figure()

    def create_main_panel(self):
        self.panel = wx.Panel(self)
        self.fig = Figure()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

    def draw_figure(self):
        ds = dicom.read_file('xr_tspine.dcm')
        self.data = map(ds.pixel_array)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.MainLoop()


'''
#for simply displaying the image
import pylab
def main():
    ds = dicom.read_file('xr_tspine.dcm')
    pylab.imshow(ds.pixel_array, cmap=pylab.cm.bone)
    pylab.axis('off')
    pylab.show()
main()
'''
