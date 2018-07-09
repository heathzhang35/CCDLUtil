import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import random
import time
import numpy as np

import SignalProcessing.Fourier as Fourier
import Utility.Constants as Constants
from EEGInterface.DSI.DSIInterface import DSIStreamer
from EEGInterface.SyntheticInterface import SyntheticStreamer
from ArduinoInterface.Arduino2LightInterface import Arduino2LightInterface as Arduino
from SignalProcessing.Filters import butter_bandpass_filter
from DataManagement.Log import Log
from Utility.Decorators import threaded

import wx
from Graphics.Cursor import CursorPanel
from Graphics.Crosshair import CHPanel
from Graphics.Prompt import PromptPanel
from Graphics.Subject import SubjectFrame



ROTATE = 'rotate'
DONT_ROTATE = 'dont_rotate'
EEG_COLLECT_TIME_SECONDS = 20
WINDOW_SIZE_SECONDS = 2
ARDUINO = False # usually True for use with Arduino lights; False for testing
log = Log('DSI_test.log')


class SSVEPGUI(wx.App):
	def __init__(self, separate_frames=True, display_index=0):
		self.frame = None
		self.__display_index = display_index
		self.__cursor_delta = None
		super().__init__()

	def OnInit(self):
		self.frame = SSVEPSubjectFrame(self.__display_index)
		self.frame.Show()
		size = self.frame.GetSize()
		width = size.GetWidth()
		self.__cursor_delta = width / 30
		return True

	def show_cursor(self):
		self.frame.show_cursor()

	def show_crosshair(self):
		self.frame.show_crosshair()

	def flash_crosshair(self):
		self.frame.flash_crosshair()

	def show_prompt(self, text):
		self.frame.show_prompt(text)

	def move_cursor_left(self):
		self.frame.move_cursor(-self.__cursor_delta)

	def move_cursor_right(self):
		self.frame.move_cursor(self.__cursor_delta)

	def reached_boundary(self):
		return self.frame.reached_boundary()

	def closest_to(self):
		return self.frame.closest_to()

	def reset_cursor(self):
		self.frame.reset_cursor()

	def set_choices(self, choices):
		self.frame.set_choices(choices)

	def collide(self):
		self.frame.collide()



class SSVEPSubjectFrame(SubjectFrame):
	def __init__(self, display_index=0):
		super().__init__(display_index)
		self.cursor = CursorPanel(self)
		self.ch = CHPanel(self)
		self.ch.Hide()
		self.prompt = PromptPanel(self)
		self.prompt.Hide()

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.cursor, 1, wx.EXPAND)
		self.sizer.Add(self.ch, 1, wx.EXPAND)
		self.sizer.Add(self.prompt, 1, wx.EXPAND)
		self.SetSizer(self.sizer)

	def show_cursor(self):
		self.cursor.Show()
		self.ch.Hide()
		self.prompt.Hide()
		self.Layout()

	def show_crosshair(self):
		self.ch.Show()
		self.cursor.Hide()
		self.prompt.Hide()
		self.Layout()

	def flash_crosshair(self):
		assert self.ch.IsShown(), "must show crosshair!"
		self.ch.flash_red()

	def show_prompt(self, text):
		self.prompt.set_text(text)
		self.prompt.Show()
		self.cursor.Hide()
		self.ch.Hide()
		self.Layout()

	def move_cursor(self, delta):
		assert self.cursor.IsShown(), "must show cursor!"
		self.cursor.move_x(delta)

	def reached_boundary(self):
		assert self.cursor.IsShown(), "must show cursor!"
		return self.cursor.reached_boundary()

	def closest_to(self):
		assert self.cursor.IsShown(), "must show cursor!"
		return self.cursor.closest_to()

	def collide(self):
		assert self.cursor.IsShown(), "must show cursor!"
		self.cursor.collide()
	
	def reset_cursor(self):
		self.cursor.reset()

	def set_choices(self, choices):
		self.cursor.set_choices(choices)



def trial_logic(eeg, gui, low_freq, high_freq, prompt, sleep_time_if_not_ran=2):
	"""
	Run a full trial of SSVEP experiment.

	:param eeg: Used EEG system (or None)
	:param gui: a wxPython application
	:param low_freq: the low frequency density we need
	:param high_freq: the high frequency density we need
	:param prompt: the prompt sentences to show on SSVEP screen
	:param sleep_time_if_not_ran: time to sleep if eeg == None
	:return: the answer, stop early or late
	"""
	fs = eeg.get_sampling_rate()
	delta = 10 # how far we want to move the cursor each time

	out_buffer_queue = None if eeg is None else eeg.out_buffer_queue
	log.info("start: " + str(time.time()))

	gui.show_prompt(prompt)
	time.sleep(2)

	start_time = time.time()

	# shape of sample is : (sample, channel)
	packet = np.asarray(out_buffer_queue.get())
	samples_per_packet = packet.shape[0]

	# get constants for full trial
	single_trial_duration_samples = EEG_COLLECT_TIME_SECONDS * fs
	single_trial_duration_packets = int(single_trial_duration_samples / samples_per_packet)

	# get constants for single window
	window_size_samples = WINDOW_SIZE_SECONDS * fs
	window_size_packets = window_size_samples / samples_per_packet

	# b is the np array to hold all data in single trial
	b = np.zeros(shape=(single_trial_duration_samples,))
	packet_index = 0

	gui.reset_cursor()
	gui.show_cursor()

	eeg.clear_out_buffer()

	while packet_index < single_trial_duration_packets:
		# insert the visualizer here
		packet = None
		try:
			packet = out_buffer_queue.get(timeout=3)   # Gives us a (10, 1) matrix.
		except Exception as e:
			print(e)
			exit(1)
			
		samples = np.squeeze(packet)	  # Gives us a (10,) array
		sample_index = packet_index * samples_per_packet
		b[sample_index: sample_index + samples_per_packet] = samples
		packet_index += 1

		# if we have enough samples, perform FFT on a single window
		if packet_index != 0 and packet_index % window_size_packets == 0:
			# print "packet index: ", packet_index, ", do FFT"
			window = b[packet_index * samples_per_packet - window_size_samples:packet_index * samples_per_packet]
			# filter using 5 - 30 Hz
			window = butter_bandpass_filter(window, 5, 30, 250, order=2)
			# perform FFT
			freq, density = Fourier.get_fft_all_channels(data=np.expand_dims(np.expand_dims(window, axis=0), axis=2),
														 fs=fs, noverlap=fs // 2, nperseg=fs)

			# compare densities of 17Hz and 15Hz frequencies
			# and move cursor left or right accordingly
			if density[0][high_freq][0] <= density[0][low_freq][0]:
				gui.move_cursor_left()
			else:
				gui.move_cursor_right()

			rb = gui.reached_boundary()
			# if we reach left boundary
			if rb == -1:
				log.info("end: " + str(time.time()))
				log.info("ROTATE")
				gui.collide()
				return ROTATE, start_time, time.time()
			# right boundary
			if rb == 1:
				log.info("end: " + str(time.time()))
				log.info("NO ROTATE")
				gui.collide()
				return DONT_ROTATE, start_time, time.time()


	## if time runs out, find which side cursor is closest to
	ct = gui.closest_to()
	gui.collide()
	# closest to left
	gui.show_crosshair()
	log.info("end: " + str(time.time()))
	if ct == -1:
		log.info("ROTATE")
		return ROTATE, start_time, time.time()
	else:
		log.info("NO ROTATE")
		return DONT_ROTATE, start_time, time.time()



def build_prompt_list():
	"""Build a question list for SSVEP task
	"""
	return ['YES', 'NO', 'YES', 'NO', 'YES', 'NO']


@threaded(False)
def run_experiment(eeg, app, prompt_list):
	app.set_choices(['YES', 'NO'])

	# create arduino
	if ARDUINO: ard = Arduino(com_port=15)

	# start
	i = 1
	for prompt in prompt_list:
		if ARDUINO:
			ard.turn_both_on()
		trial_logic(eeg, app, high_freq=17, low_freq=15, prompt=prompt)
		if ARDUINO:
			ard.turn_both_off()
		time.sleep(5)
		i += 1


def main():
	# questions for our subject
	prompt_list = build_prompt_list()

	# SyntheticStreamer is a fake streamer for testing purposes
	eeg = SyntheticStreamer(live=True, save_data=False)

	# DSIStreamer will interact with the DSI-7
	#eeg = DSIStreamer(live=True, save_data=True)

	eeg.start_recording()

	# Uncomment this line to start saving data for post analysis
	#eeg.start_saving_data('ssvep_dsi_test.csv')

	# change display_index for multi-display systems
	gui = SSVEPGUI(display_index=0)

	run_experiment(eeg, gui, prompt_list)
	gui.MainLoop()


if __name__ == '__main__':
	main()
