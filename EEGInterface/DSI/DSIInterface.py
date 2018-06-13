import sys, os
from os import listdir
import platform
import CCDLUtil.EEGInterface.EEGInterface
import CCDLUtil.EEGInterface.EEG_INDEX
import CCDLUtil.EEGInterface.DSI.API.DSI as DSI
import time


class DSIStreamer(CCDLUtil.EEGInterface.EEGInterface.EEGInterfaceParent):

	def __init__(self, channels_for_live='All', live=True, save_data=True, subject_name=None,
                subject_tracking_number=None, experiment_number=None, port=None, impedances=False):
		"""
		A data collection object for the DSI EEG interface.
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
		:param port: serial port address for communicating with DSI hardware
		"""
		super(DSIStreamer, self).__init__(channels_for_live, live, save_data, subject_name, subject_tracking_number, experiment_number)


		__all__ = [
			'Headset', 'Source', 'Channel',
			'SampleCallback', 'MessageCallback',
			'DSIException',
			'IfStringThenRawString', 'IfStringThenNormalString',
		]
		#dll, globalFuncs = DSI.LoadAPI()
		#locals().update(globalFuncs)
		#__all__ += list(globalFuncs.keys())

		# config port
		if not port:
			self.port = self._find_dsi_port()
		else:
			self.port = port
		
		self.h = DSI.Headset()
		self.h.SetMessageCallback(self.__message_callback)
		self.h.Connect(port)

		if impedances:
			self.h.SetSampleCallback(self.__sample_callback_impedances)
			self.h.StartImpedanceDriver()
		else:
			# ************************ NEED TO SET THIS VARIABLE!!!! ***************************
			source_ref = None
			self.h.SetSampleCallback(self.__sample_callback_signals)
			if source_ref is not None:
				self.h.SetDefaultReference(source_ref, True)

	def start_recording(self):
		"""
        Begins data acquisition
        """
		print('start recording')
		self.h.StartDataAcquisition()
		pass

	def stop_recording(self):
		"""
		Stops data acquisition
		"""
		print('stop recording')
		self.h.StopDataAcquisition()
		pass

	def _find_dsi_port(self):

		# automatically find ports
		#system = platform.system()

		if sys.platform.lower().startswith('win'):
			# TODO: test on windows 10/7
			return "COM6"

		#elif platform == "Darwin":
		else:
			# list dev
			devs = listdir("/dev/")
			for dev in devs:
				if "cu.DSI" in dev:
					return dev

		raise ValueError('Failed to find port automatically. Please find port manually and pass into constructor')


	def __message_callback(self, msg, lvl=0):
		# use DSI's default callback
		return DSI.ExampleMessageCallback(msg, lvl)


	def __sample_callback_signals(headset_ptr, packet_time, streamer):
		#DSI.ExampleSampleCallback_Signals(headset_ptr, packet_time, user_data)
		h = DSI.Headset(headset_ptr)

		# get data points
		try:
			# might want to use ch.ReadBuffered()
			data = [ch.GetSignal() for ch in h.Channels()]
			streamer.data_index += 1
		except Exception as e:
			print((e.message, e))
			# continue to run, ignore the incomplete packet
			return

		# send to out buffer for live data analysis
		if streamer.live:
			streamer.out_buffer_queue.put(data)

		# save data
		if streamer.save_data:
			data_str = str(streamer.data_index) + ',' + str(time.time()) + ',' + ','.join([str(val) for val in data])
			streamer.data_save_queue.put((None, None, data_str + '\n'))

		# Set EEG INDEX parameters (not sure of purpose)
		CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX = streamer.data_index
		CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX_2 = streamer.data_index


	def __sample_callback_impedances(headset_ptr, packet_time, streamer):
		# use DSI's default callback
		DSI.ExampleSampleCallback_Impedances(headset_ptr, packet_time, None)


if __name__ == '__main__':
	streamer = DSIStreamer()
	streamer.start_recording()
	streamer.start_saving_data(save_data_file_path='test.csv', header='Sample Header')
	cue = 'start'
	while cue != 'stop':
		cue = eval(input("Enter stop to finish recording: "))
	streamer.stop_recording()
