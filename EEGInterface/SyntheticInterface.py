import time
import numpy as np
from CCDLUtil.EEGInterface.EEGInterface import EEGInterfaceParent
from CCDLUtil.Utility.Decorators import threaded


class SyntheticStreamer(EEGInterfaceParent):

	NUM_CHANNELS = 8

	def __init__(self, num_channels=8, fs=300, live=True, save_data=False):
		super(SyntheticStreamer, self).__init__(live=live, save_data=save_data)
		self.num_channels = num_channels
		self.NUM_CHANNELS = num_channels
		self.fs = fs
		self.recording = False

	def start_recording(self):
		# fire off data generating thread
		self.recording = True
		self.__generate_data()

	def stop_recording(self):
		self.recording = False

	@threaded(False)
	def __generate_data(self):
		wait_time = 1 / self.fs
		while self.recording:
			time.sleep(wait_time) # to simulate sampling rate
			data = np.random.rand(8)
			if self.live:
				self.out_buffer_queue.put(data)
			if self.save_data:
				self.data_save_queue.put(data)
