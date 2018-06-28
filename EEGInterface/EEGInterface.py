"""
To save data, it is suggested that this module is used with the EEGDataSaver.
threading.Thread(target=lambda: EEGDataSaver.start_eeg_data_saving(subject_data_path, self.data_save_queue, header=None)).start()

"""

import sys
import time
import queue
from CCDLUtil.Utility.Decorators import threaded


class EEGInterfaceParent(object):

	"""
	A Parent interface that should be inherited other systems that interface with EEG.
	"""

	def __init__(self, channels_for_live='All', live=True, save_data=True, subject_name=None, subject_tracking_number=None, experiment_number=None):
		"""
		A data collection object for the EEG interface.
		This provides option for live data streaming and saving data to file.

		Modifies the EEG_INDEX and EEG_INDEX_2 in CCDLUtil/EEGInterface/EEG_INDEX.py when each packet arrives.
		These variables can be read from any thread. Use this to time mark events in your other programs.

		:param channels_for_live: List of channel names (or indexes) to put on the out_buffer_queue. If [], no channels
					will be put on the out_buffer_queue. If 'All' (case is ignored), all channels will be placed on the
					out_buffer_queue.  Defaults to All.
		:param live: True to create out_buffer_queue. Default to True
		:param save_data: True to create data_save_queue. Default to True
		:param subject_name: Optional -- Name of the subject. Defaults to 'None'
		:param subject_tracking_number: Optional -- Subject Tracking Number (AKA TMS group experiment number tracker). Defaults to 'None'
		:param experiment_number: Optional -- Experimental number. Defaults to 'None'
		"""

		self.subject_name = str(subject_name) if subject_name is not None else "None"
		self.subject_number = str(subject_tracking_number) if subject_tracking_number is not None else 'None'
		self.experiment_number = str(experiment_number) if experiment_number is not None else 'None'
		# Count each block we receive, start at -1 to avoid a fence/post problem.
		self.data_index = -1
		# data saving and live analysis flags
		self.live = live
		self.save_data = save_data
		# A separate queue (other than the one for storing data) that puts the channels_for_live data points on
		self.out_buffer_queue = queue.Queue() if live else None
		# block counter to check overflows of tcpip buffer
		self.last_block = -1
		self.channels_for_live = channels_for_live
		if type(self.channels_for_live) is str:
			self.channels_for_live = self.channels_for_live.lower()
			if self.channels_for_live != 'all':
				raise ValueError('Invalid channels_for_live parameter')
		# create data save queue
		self.data_save_queue = queue.Queue() if save_data else None
		self.stopped = False

	@staticmethod
	def trim_channels_with_channel_index_list(data, channel_index_list):
		"""
		Saves data[i] where i is an element in channel_index_list.
		For example:
			data = [500, 400, 350, 450]
			channel_index_list = [0, 2]
			trim_channels_with_channel_index_list(data, channel_index_list) -> [500, 350]

		:param data: A string of data points
		:param channel_index_list: A list of channel indexes that we want to save.
		:return: trimmed data list
		"""
		return [data[xx] for xx in channel_index_list]

	def start_recording(self):
		"""
		To be overridden by child
		"""
		pass

	def stop_recording(self):
		"""
		To be overridden by child
		"""
		self.stopped = True

	def clear_out_buffer(self):
		"""
		Clears out buffer for live analysis
		"""
		q = self.out_buffer_queue
		with q.mutex:
			q.queue.clear()

	@threaded(False)
	def start_saving_data(self, save_data_file_path, header=None, timeout=15):
		"""
		Spawns new thread and saves egg data
		:param save_data_file_path: A string - The full file name to save the data (for example './data/subjectX.csv').
		:param queue: The queue to read the data from.
				Data should be placed on the queue in the form:
					index, time, data

					- Index
						Where index is the packet (or sample) index.  This can be a string or a number.
					- Time
						Time is the time in which the transferred data was collected.  This is typically from time.time().
							This can be a string or a number.
					- Data
						A list of data points in the form [chan 1, chan 2...], where chan X is a number.
						If data is a list, it will be comma separated.  If data is a string, we'll write it to file as it was provided to us.

				Data save format.
					Data will be saved in the comma separated format:
						index,time,chan1,chan2,chan3...\n

		:param header: Header for the file.  If no header is wanted, pass None.  Defaults to None.
		:param timeout: If we don't collect any data after timeout seconds, we'll quit all processes.  If none, there won't be a timeout.
		"""
		f = open(save_data_file_path, 'w')
		# Write our header with only one newline character
		if header is not None:
			if header.endswith('\n'):
				f.write(header)
			else:
				f.write(header)
				f.write('\n')
			f.flush()
		while not self.stopped:
			# get our components
			try:
				if timeout is None:
					index, t, data = self.data_save_queue.get()
				else:
					index, t, data = self.data_save_queue.get(timeout)
			except queue.Empty:
				print("Data is not being collected.")
				time.sleep(2)
				# quit system
				sys.exit(1)
			index = '' if index is None else str(index) + ','
			t = '' if t is None else str(t) + ','
			if type(data) is list:
				# convert our data items to strings
				data = list(map(str, data))
				# convert our data to a comma separated string
				data = ','.join(data)
			else:
				if type(data) is not str:
					raise TypeError("Invalid data type -- data must be either string or ")
			# add a newline if needed.  Commas are already accounted for
			data_str = str(index) + str(t) + append_and_switch_line(data)
			# Write our index and timestamp
			f.write(data_str)
			# Flush our buffer
			f.flush()


def append_and_switch_line(string):
	"""
	Checks if there is a newline on the string.  If there is not, it appends one.
	Raises a type error if string is not a str object.
	:param string: String to append newline to.  Throws a type error if not a string.
	:return: String with a newline character at the end.
	"""
	if type(string) is not str:
		raise TypeError
	if string.endswith('\n'):
		return string
	else:
		return string + '\n'
