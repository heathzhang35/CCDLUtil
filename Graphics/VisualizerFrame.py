import wx
from EEGPanel import EEGPanel
from MSPanel import MSPanel

class VisualizerFrame(wx.Frame):

    def __init__(self, parent, id, out_buffer_queue):
        # init parent
        wx.Frame.__init__(self, parent, id)
        # set title
        self.SetTitle("EEG Visualizer")
        # set init size
        self.SetSize(1280, 800)
        # get normal panel
        topPanel = wx.Panel(self)
        # set data to use
        self.data_queue = out_buffer_queue
        # init our panels
        # self.eeg_panel = EEGPanel(topPanel, )
        # self.ms_panel = MSPanel(topPanel)
        # self.ms_panel.draw()
        # # create box sizer
        # sizer = wx.BoxSizer(wx.HORIZONTAL)
        # sizer.Add(self.eeg_panel, 2, wx.ALL | wx.GROW, border=10)
        # sizer.Add(self.ms_panel, 1, wx.ALL | wx.GROW, border=10)
        # topPanel.SetSizer(sizer)
        self.Show()

if __name__ == '__main__':

    app = wx.App()
    VisualizerFrame(None, -1)
    app.MainLoop()


