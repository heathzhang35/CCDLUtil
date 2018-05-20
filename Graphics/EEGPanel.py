"""
EEG Visualizer embedded
"""
import threading
import time
import numpy as np
import wx
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


class EEGPanel(wx.Panel):

    def __init__(self, parent, num_channel=8, fs=256, num_seconds=3):
        """
        Initialize EEG Panel

        :param parent: wx.Frame
        :param num_channel: the number of channels of data from EEG headset
        :param fs: the sampling rate
        :param num_seconds: the number of seconds of data shown (fs * num_seconds)
        """
        # init panel
        super(EEGPanel, self).__init__(parent)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        # the number of channels
        self.num_channel = num_channel
        self.fs = fs
        self.num_seconds = num_seconds
        # EEG Data to draw on graph
        self.data_to_draw = np.zeros(num_channel * fs * num_seconds).reshape((num_channel, fs * num_seconds))
        # EEG data figure
        self.fig = Figure()
        # subplots (one for each channel)
        self.axarr = []
        # add subplots
        for i in range(num_channel):
            ax = self.fig.add_subplot(num_channel, 1, i + 1)
            self.axarr.append(ax)
        self.plots = []
        # set plot styple
        self._plot_style()
        # create canvas
        self.eeg_canvas = FigureCanvas(self, -1, self.fig)
        self.eeg_canvas.mpl_connect("button_press_event", self._on_click_subplot)
        # set sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.eeg_canvas, proportion=1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        # animation
        self.idx = 0
        # full is used to indicate if the plot region is full. If so, old data will be shifted
        # before new data comes in
        self.full = False
        self.ani = animation.FuncAnimation(self.fig, self._animate, blit=False, interval=4)

    def add_data(self, data):
        """
        Add data to graph.

        :param data: the data to be visualized
        """
        assert isinstance(data, np.ndarray) and data.shape[0] == self.num_channel
        # udpate data to be drawn
        for i, d in enumerate(data):
            if self.full:
                self._shift_data()
                self.data_to_draw[i, self.idx - 1] = d
            else:
                self.data_to_draw[i][self.idx] = d
                self.idx += 1
        if self.idx == self.data_to_draw.shape[1]:
            self.full = True

    def _plot_style(self):
        """Initialize one plot for each channel
        """
        for i, ax in enumerate(self.axarr):
            # style
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_ylabel(str(i + 1), rotation=0, fontsize=12)
            line, = ax.plot(np.arange(self.fs * self.num_seconds), self.data_to_draw[i])
            self.plots.append(line)

    def _animate(self, _):
        """Update for live plot

        :param _: unused data holder
        """
        # set data
        for i in range(len(self.plots)):
            self.plots[i].set_ydata(self.data_to_draw[i])
            
        for ax in self.axarr:
            ax.relim()
            ax.autoscale_view()
        return self.plots

    def _shift_data(self):
        # shift data to left by one
        for i in range(self.data_to_draw.shape[0]):
            for j in range(1, self.data_to_draw.shape[1]):
                self.data_to_draw[i, j - 1] = self.data_to_draw[i, j]

    def on_close(self, event):
        self.Destroy()

    ### place holder for now: when the user click on one channel, a separate window opens ###
    def _on_click_subplot(self, event):
        for i, ax in enumerate(self.axarr):
            if ax == event.inaxes:
                print(i)


### TESTING ###
def feed_data(eeg_panel):
    # feed a lot of data
    i = 0
    # add data
    while i < 10000:
        eeg_panel.add_data(np.random.rand(8))
        time.sleep(0.004)


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = wx.Frame(None, -1, 'simple.py')
    panel = EEGPanel(frame, num_channel=8, num_seconds=1)
    # streamer = OpenBCIStreamer(port="/dev/tty.usbserial-DB00J8G0", live=True, save_data=True)
    # streamer.start_recording()
    t = threading.Thread(target=feed_data, args=(panel, ), daemon=True).start()
    frame.Show()
    app.MainLoop()

