"""
A file to create mock data in a manner similar format to the BrainAmp Interface
"""

"""
============================
A m p l i f i e r  S e t u p
============================

Default Sampling Rate - 5000 Fs
Number of channels: 32 (including ECG channel)
Sampling Interval [micro seconds]: 200  (0.0002 seconds; 5000 Hz)

Packet size = 100 samples
Packet arrival = 50 Hz

See CCDLUtil/Documentation/BrainAmp for more information on how to use the Brain Amp interface.

This script is a modified Python RDA client for the RDA tcpip interface of the BrainVision Recorder. The unmodified file is
within this same folder.

"""

# TODO: This script has 32 channels hard-coded.  This needs to be fixed to work with other numbers.

# needs socket and struct library
from socket import *
from struct import *
import time
import queue
import threading
import EEGInterface.DataSaver
import numpy as np
import EEGInterface.EEG_INDEX



class BrainAmpSyntheticDataGenerator(object):

    def __init__(self, subject_data_path, channels_for_live, out_buffer_queue, subject_name=None, subject_tracking_number=None, experiment_number=None):
        """
        A data collection object for the Brain Amp interface.  This provides option for live data streaming and saving data to file.

        For live data streaming, use with a threading or multiprocessing queue (ie. Queue.queue().
           Data will be put on the queue, which can be read by another thread.)

        Modifies the EEG_INDEX and EEG_INDEX_2 in CCDLUtil/EEGInterface/EEG_INDEX.py when each packet arrives.  These variables can be read from any thread.
            Use this to time mark events in your other programs.

        :param subject_data_path: Path to save the save the data.  If None, no data will be saved.
        :param channels_for_live: List of channel names (or indexes) to put on the process_queue.
        :param out_buffer_queue: The channels_for_live channel data will be placed on this queue if it is not None.
        :param subject_name: Optional -- Name of the subject. Defaults to 'None'
        :param subject_tracking_number: Optional -- Subject Tracking Number (AKA TMS group experiment number tracker). Defaults to 'None'
        :param experiment_number: Optional -- Experimental number. Defaults to 'None'
        """
        # Typical 32 channels for live (take from signal tester)
        # ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 'Fz', 'Cz',
        #  'Pz', 'Oz', 'FC1', 'FC2', 'CP1', 'CP2', 'FC5', 'FC6', 'CP5', 'CP6', 'TP9', 'TP10', 'POz', 'ECG']


        # Get our data_save_queue.  We'll set it to non if subject_data_path is none, meaning we aren't going to be saving data.
        if subject_data_path is None:
            self.data_save_queue = None
        else:
            self.data_save_queue = queue.Queue()
            threading.Thread(target=lambda: EEGInterface.DataSaver.start_eeg_data_saving(subject_data_path, self.data_save_queue, header=None)).start()


        self.subject_data_path = subject_data_path
        self.subject_name= str(subject_name) if subject_name is not None else "None"
        self.subject_number = str(subject_tracking_number) if subject_tracking_number is not None else 'None'
        self.experiment_number = str(experiment_number) if experiment_number is not None else 'None'

        # Count each block we recieve
        self.data_index = -1

        # A separate queue (other than the one for storing data) that puts the channels_for_live data points on
        self.out_queue = out_buffer_queue

        # block counter to check overflows of tcpip buffer
        self.last_block = -1

        self.put_data_on_out_queue_flag = False
        self.channels_for_live = channels_for_live


    def start_recording(self):
        """
        Start our recording
        """

        # ##### Main Loop #### #
        while True:
            # TODO: fix this to be more dynamic and multidimensional.
            data = [self.data_index for _ in range(len(self.channels_for_live))]

            # Get the time we collected the sample
            data_recieve_time = time.time()
            self.data_index += 1  # Increase our sample counter

            EEGInterface.EEG_INDEX.EEG_INDEX = self.data_index
            EEGInterface.EEG_INDEX.EEG_INDEX_2 = self.data_index

            ###################
            # Handle the Data #
            ###################
            # Save the Data - We put data on the queue to be saved - format for queue (index, time, data)
            if self.data_save_queue is not None:
                self.data_save_queue.put((self.data_index, data_recieve_time, data))

            # if we are
            if self.put_data_on_out_queue_flag is not None:
                self.out_queue.put(data)


if __name__ == '__main__':
    dc = BrainAmpSyntheticDataGenerator('Placeholder', ['C3', 'C4'], queue.Queue())
    dc.start_recording()
