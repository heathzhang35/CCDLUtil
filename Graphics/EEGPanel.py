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
from CCDLUtil.EEGInterface.DSI.DSIInterface import DSIStreamer
from CCDLUtil.EEGInterface.SyntheticInterface import SyntheticStreamer
from CCDLUtil.Utility.Decorators import threaded
from CCDLUtil.Graphics.SubjectFrame import SubjectFrame


class EEGPanel(wx.Panel):

	def __init__(self, parent, num_channels=8, fs=256, num_seconds=3, roll=False):
		"""
		Initialize EEG Panel

		:param parent: wx.Frame
		:param num_channels: the number of channels of data from EEG headset
		:param fs: the sampling rate
		:param num_seconds: the number of seconds of data shown (fs * num_seconds)
		:param roll: True for constant, moving stream; False (default) for overlay
		"""
		super(EEGPanel, self).__init__(parent)
		self.Bind(wx.EVT_CLOSE, self.on_close)

		self.num_channels = num_channels
		self.fs = fs
		self.num_seconds = num_seconds

		self.data_to_draw = np.zeros(num_channels * fs * num_seconds).reshape((num_channels, fs * num_seconds))

		self.fig = Figure()
		# subplots (one for each channel)
		self.axarr = []
		for i in range(num_channels):
			ax = self.fig.add_subplot(num_channels, 1, i + 1)
			self.axarr.append(ax)
		self.plots = []
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
		if not roll:
			self.idx = 0
		self.ani = animation.FuncAnimation(self.fig, self._animate, blit=False, interval=17)
		self.roll = roll


	def add_data(self, data):
		"""
		Add data to graph.

		:param data: the data to be visualized
		"""
		assert isinstance(data, np.ndarray) and data.shape[0] == self.num_channels

		if self.roll:
			self._shift_data()
			self.data_to_draw[:, -1] = data[:]
		else:
			self.data_to_draw[:, self.idx] = data[:]
			self.idx += 1
			if self.idx == self.data_to_draw.shape[1]:
				self.idx = 0


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
		for i in range(len(self.plots)):
			self.plots[i].set_ydata(self.data_to_draw[i])
		self.__rescale()
		return self.plots

	def __rescale(self):
		for ax in self.axarr:
			ax.relim()
			ax.autoscale_view()

	def _shift_data(self):
		# shift data to left by one
		self.data_to_draw = np.roll(self.data_to_draw, shift=-1, axis=1)

	def on_close(self, event):
		self.Destroy()

	### place holder for now: when the user click on one channel, a separate window opens ###
	def _on_click_subplot(self, event):
		for i, ax in enumerate(self.axarr):
			if ax == event.inaxes:
				print(i)



##### TESTING #####
def feed_data(streamer, eeg_panel):
	while True:
		eeg_panel.add_data(np.asarray(streamer.out_buffer_queue.get()))


def main():
	app = wx.App(redirect=False)
	frame = wx.Frame(None, -1, 'EEG - LIVE')
	fs = 300
	panel = EEGPanel(frame, fs=fs, num_channels=8, num_seconds=5, roll=False)
	#streamer = SyntheticStreamer(live=True, fs=fs) # test with fake EEG data
	streamer = DSIStreamer(live=True, save_data=False)
	streamer.start_recording()
	t = threading.Thread(target=feed_data, args=(streamer, panel, ), daemon=True).start()
	frame.Show()
	app.MainLoop()
	streamer.stop_recording()


if __name__ == '__main__':
	main()
