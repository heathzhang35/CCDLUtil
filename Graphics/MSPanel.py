import sys, os
import csv
from threading import Thread
import numpy as np
from numpy.linalg import norm
from scipy.interpolate import griddata
import wx
import matplotlib
matplotlib.use('WXAgg') # to be used in wx
import matplotlib.animation as animation
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from Utility.AssertVal import assert_equal
from Util.Constants import BRAINAMP_CHANNEL_LIST


class MSPanel(wx.Panel):

    def __init__(self, parent, num_channels=31, N=150):
        """
        :param parent: Wx.Frame object
        :param num_channels: the number of channels data has. Default to 31 (brainamp)
        :param N: the level of interpolation for contour map. Default to 150
        """
        # init panel
        wx.Panel.__init__(self, parent)
        # the number of points to interpolate between 0 and 10
        self.N = N
        self._RADIUS = 3.8
        self._CENTER = [5, 5]
        # the number of channels source data has
        self.num_channels = num_channels
        # set channel positions
        if not num_channels == 31:
            raise ValueError("Visualization of non-BrainAmp channels not supported yet")
        self._coords = self._draw_coords()
        # EEG data panel
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, aspect=1)
        # data to calculate
        self.data = np.empty((self.num_channels,), dtype=float)
        # points to plot
        self.xi = np.linspace(0, 10, self.N)
        self.yi = np.linspace(0, 10, self.N)
        self.zi = None
        # points not to plot (outside of circle)
        self._deletes = self._crop_coords()
        # graphics
        self.eeg_canvas = FigureCanvas(self, -1, self.fig)
        self.SetBackgroundColour("black")
        self._plot_style()
        # set sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.eeg_canvas, proportion=1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(sizer)
        self.Fit()
        # set animation
        self.ani = animation.FuncAnimation(self.fig, self._animate, blit=False)

    def add_data(self, data):
        """
        Update the data to be visualized

        :param data: the new data to be visualized
        :return: None
        """
        assert_equal(len(data), self.num_channels)
        assert_equal(isinstance(data, np.ndarray), True)
        self.data = data

    def gfp(data):
        """
        Calculate GFP
        Reference: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4305485/pdf/nihms-652267.pdf
        """
        mean = np.mean(data)
        total = 0.
        for i in data:
            total += (i - mean) ** 2
        return math.sqrt(total / len(electrodes))

    def _update_data(self):
        """
        Calculate data interpolation and trim data outside of the circle

        :return: None
        """
        self.zi = griddata(self.coords, self.data, (self.xi[None, :], self.yi[:, None]), method='cubic')
        # crop zi to set points outside circle NaN
        for c in self._deletes:
            self.zi[c[0], c[1]] = "nan"

    def _animate(self, _):
        """Update for live plot

        :param _: unused data holder
        :return: sequence of object to be redrawn
        """
        # update
        self._update_data()
        # get contour
        self.ax.cla()
        self._plot_style()
        self.ax.contourf(self.xi, self.yi, self.zi, 60, cmap="bwr", zorder=1)
        return self.ax,

    def _plot_style(self):
        """
        Draw the head, two ears and nose

        :return: None
        """
        # add circle (head)
        head = matplotlib.patches.Circle([5, 5], radius=3.8, edgecolor="k", facecolor="none")
        self.ax.add_patch(head)
        # add two ears
        left_ear = matplotlib.patches.Ellipse(xy=[2, 5], width=3, height=3.0, angle=0, edgecolor="k", facecolor="w", zorder=0)
        self.ax.add_patch(left_ear)
        right_ear = matplotlib.patches.Ellipse(xy=[8, 5], width=3, height=3.0, angle=0, edgecolor="k", facecolor="w", zorder=0)
        self.ax.add_patch(right_ear)
        # add a nose
        xy = [[4.4, 8.6], [5, 9.5], [5.6, 8.6]]
        polygon = matplotlib.patches.Polygon(xy=xy, edgecolor="k", facecolor="w", zorder=0)
        self.ax.add_patch(polygon)

    @property
    def RADIUS(self):
        return self._RADIUS # read-only

    @property
    def CENTER(self):
        return self._CENTER # read-only

    @property
    def coords(self):
        return self._coords # read-only

    def _draw_coords(self):
        """
        Data points to be drawn (channel coordinates from BrainAmp)

        :return: array size (num_channel, 2)
        """
        t = np.empty([self.num_channels, 2], dtype=float)
        for i, c in enumerate(BRAINAMP_CHANNEL_LIST):
            t[i, 0] = c[0]
            t[i, 1] = c[1]
        return t

    def _crop_coords(self):
        """
        Calculate the set of points not to be drawn

        :return: the set of points outside of circle
        """
        s = set()
        for i in range(self.N):
            for j in range(self.N):
                if not self._within_circle(self.xi[i], self.yi[j]):
                    s.add((j, i))
        return s

    def _within_circle(self, x, y):
        """
        Return true if point (x, y) is within circle at (5, 5) with radius 3.8

        :param x: the x coordinate of the point
        :param y: the y coordinate of the point
        :return: true if point (x, y) is within circle at (5, 5) with radius 3.8
        """
        # 0.03 makes the edge look a little better
        return norm([self._CENTER[0] - x, self._CENTER[1] - y]) - 0.03 <= self._RADIUS


### TESTING ###

def get_data(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        # skip header
        next(reader)
        for row in reader:
            yield row


def feed_data(panel, filename):
    for row in get_data(filename):
        panel.add_data(np.asarray(row))


if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None, -1, 'simple.py')
    frame.SetSize(600, 600)
    panel = MSPanel(frame)
    # play animation file
    Thread(target=feed_data, args=(panel, "../data/downsampled_Marked_4-29.csv", ), daemon=True).start()
    # panel.draw()
    frame.Show()
    app.MainLoop()
