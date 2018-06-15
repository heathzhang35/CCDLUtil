import sys, os, ctypes
import threading
from os import listdir
import platform
import CCDLUtil.EEGInterface.EEGInterface
import CCDLUtil.EEGInterface.EEG_INDEX
import CCDLUtil.EEGInterface.DSI.API.DSI as DSI
from CCDLUtil.Utility.Decorators import threaded
import time, datetime
import random



SampleCallback  = ctypes.CFUNCTYPE(None,			ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p)
MessageCallback = ctypes.CFUNCTYPE(ctypes.c_int,	ctypes.c_char_p, ctypes.c_int)



class DSIStreamer(CCDLUtil.EEGInterface.EEGInterface.EEGInterfaceParent):

	# --- Trigger States --- #
	TRIGGER_OFF = 0
	TRIGGER_ONCE = 1
	TRIGGER_HOLD = 2

	the_streamer = None
	the_lock = threading.RLock()

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
		
		# configure port if needed
		if not port:
			self.port = self.__find_dsi_port()
		else:
			self.port = port
		
		self.h = DSI.Headset()
		self.h.SetMessageCallback(self.__message_callback)

		try:
			self.h.Connect(self.port)
		except Exception:
			print('Unable to connect to DSI headset. Please check that the light is flashing blue')
			exit()

		if impedances:
			self.h.SetSampleCallback(self.__sample_callback_impedances, 0)
			self.h.StartImpedanceDriver()
		else:
			# TODO: set source reference
			source_ref = None
			self.h.SetSampleCallback(self.__sample_callback_signals, 0)
			if source_ref is not None:
				self.h.SetDefaultReference(source_ref, True)

		self.__trigger = DSIStreamer.TRIGGER_OFF
		#self.__lock = threading.Lock() # to protect trigger

		self.start_time = None # to be set at recording time

		now = datetime.datetime.now()

		self.header = "Date, " + now.strftime("%Y-%m-%d") + "\n"\
					+ "Start Time, " + now.strftime("%H:%M:%S.%f")[:-3] + "\n"\
					+ "Reference, " + self.h.GetReferenceString() + "\n\n"\
					+ "Index, Time, LE, F4, C4, PO8, PO7, C3, F3, Trigger\n"

		self.__init()


	def __init(self):
		# Necessary for working with Wearable Sensing's weird API
		DSIStreamer.the_streamer = self


	@threaded(False)
	def start_recording(self):
		"""
        Begins data acquisition
        """
		print('start recording')
		self.start_time = time.time()
		self.h.StartDataAcquisition()
		self.h.Idle(2.0)


	def stop_recording(self):
		"""
		Stops data acquisition
		"""
		print('stop recording')
		self.h.StopDataAcquisition()
		self.stopped = True
		self.h.Idle(2.0)


	def start_saving_data(self, save_data_file_path, header=None, timeout=15):
		super(DSIStreamer, self).start_saving_data(save_data_file_path, self.header, timeout)


	def trigger(self):
		"""
		An instantaneous trigger pull
		"""
		with DSIStreamer.the_lock:
			if self.__trigger != DSIStreamer.TRIGGER_HOLD:
				self.__trigger = DSIStreamer.TRIGGER_ONCE 

	def trigger_hold(self):
		"""
		Press and hold trigger
		"""
		with DSIStreamer.the_lock:
			self.__trigger = DSIStreamer.TRIGGER_HOLD

	def trigger_release(self):
		"""
		Release held trigger
		"""
		with DSIStreamer.the_lock:
			self.__trigger = DSIStreamer.TRIGGER_OFF

	def trigger_value(self):
		with DSIStreamer.the_lock:
			return int(self.__trigger)


	def __find_dsi_port(self):
		"""
		Locate port through which DSI headset communicates; this is system dependent
		"""
		if sys.platform.lower().startswith('win'):
			# TODO: test on windows 10/7
			return "COM6"
		else:
			# list dev
			devs = listdir("/dev/")
			for dev in devs:
				if "cu.DSI" in dev:
					return "/dev/" + dev
		raise ValueError('Failed to find port automatically. Please find port manually and pass into constructor')


	@MessageCallback
	def __message_callback(msg, lvl=0):
		# use DSI's default callback
		return DSI.ExampleMessageCallback(msg, lvl)

	
	@SampleCallback
	def __sample_callback_impedances(headset_ptr, packet_time, user_data):
		# use DSI's default callback
		DSI.ExampleSampleCallback_Impedances(headset_ptr, packet_time, user_data)


	@SampleCallback
	def __sample_callback_signals(headset_ptr, packet_time, user_data):
		#streamer = DSIStreamer.the_streamer
		h = DSI.Headset(headset_ptr)

		# read in data
		data = None
		try:
			# might want to use ch.ReadBuffered()
			data = [ch.GetSignal() for ch in h.Channels()]
			#data = [random.randint(0, 10) for _ in range(7)]
			DSIStreamer.the_streamer.data_index += 1
		except Exception as e:
			#print((e.message, e))
			print(e)
			exit()
			# continue to run, ignore the incomplete packet
			#return

		# account for client requested trigger press
		with DSIStreamer.the_lock:
			val = DSIStreamer.the_streamer.trigger_value()
			if DSIStreamer.the_streamer.trigger_value() != DSIStreamer.TRIGGER_OFF:
				data[-1] = 1
				if DSIStreamer.the_streamer.trigger_value() == DSIStreamer.TRIGGER_ONCE:
					DSIStreamer.the_streamer.trigger_release()
			else:
				data[-1] = 0

		# send to out buffer for live data analysis
		if DSIStreamer.the_streamer.live:
			DSIStreamer.the_streamer.out_buffer_queue.put(data)

		# save data
		if DSIStreamer.the_streamer.save_data:
			data_str = str(DSIStreamer.the_streamer.data_index) + ',' + str(time.time() - DSIStreamer.the_streamer.start_time) + ',' + ','.join([str(val) for val in data])
			DSIStreamer.the_streamer.data_save_queue.put((None, None, data_str + '\n'))

		# Set EEG INDEX parameters (not sure of purpose)
		CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX = DSIStreamer.the_streamer.data_index
		CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX_2 = DSIStreamer.the_streamer.data_index




if __name__ == '__main__':

	streamer = DSIStreamer(live=False)
	streamer.start_recording()
	streamer.start_saving_data('test.csv')

	time.sleep(0.1)
	streamer.trigger()
	time.sleep(0.1)
	streamer.trigger_hold()
	time.sleep(2)
	streamer.trigger_release()
	time.sleep(1)

	#cue = 'start'
	#while cue != 'stop':
	#	cue = input("Enter stop to finish recording: ")

	streamer.stop_recording()
	print("ctrl-C to end")
	# TODO: make saving thread close on it's own?
