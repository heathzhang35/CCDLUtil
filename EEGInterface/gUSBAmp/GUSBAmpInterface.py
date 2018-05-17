# needs socket and struct library
import socket
import struct
import time
import queue
import threading
import CCDLUtil.EEGInterface.DataSaver
import numpy as np
import CCDLUtil.EEGInterface.EEG_INDEX
import CCDLUtil.EEGInterface.EEGInterface as CCDLEEGParent
import CCDLUtil.DataManagement.DataParser as CCDLDataParser
import pylsl


class GUSBAmpStreamer(CCDLEEGParent.EEGInterfaceParent):


    def __init__(self, channels_for_live, out_buffer_queue, put_data_on_out_queue_flag=False, data_save_queue=None, subject_name=None, subject_tracking_number=None, experiment_number=None,
                 misc_queue_list=None, misc_queue_list_channels=None, samples_to_save=1):
        """
        A data collection object for the EEG interface.  This provides option for live data streaming and saving data to file.

        For live data streaming, use with a threading or multiprocessing queue (ie. Queue.queue()
           Data will be put on the queue, which can be read by another thread.)

        Modifies the EEG_INDEX and EEG_INDEX_2 in CCDLUtil/EEGInterface/EEG_INDEX.py when each packet arrives.  These variables can be read from any thread.
            Use this to time mark events in your other programs.

        :param channels_for_live: List of channel names (or indexes) to put on the out_buffer_queue. If [] or None, no channels will be put on the out_buffer_queue.
                                  If 'All', all channels will be placed on the out_buffer_queue.
        :param data_save_queue: queue to put data to save.  If None, data will not be saved.
        :param out_buffer_queue: The channel listed in the channels_for_live parameter will be placed on this queue. This is intended for live data analysis.
                                 If None, no data will be put on the queue.
                                 Items put on the out buffer queue will be a numpy array (though this can be either a 2D or a 1D numpy array)
        :param subject_name: Optional -- Name of the subject. Defaults to 'None'
        :param subject_tracking_number: Optional -- Subject Tracking Number (AKA TMS group experiment number tracker). Defaults to 'None'
        :param experiment_number: Optional -- Experimental number. Defaults to 'None'
        """

        # Call our EEGInterfaceParent init method.  Channels_for_live is converted to lower case in super call if it is a string.
        super(GUSBAmpStreamer, self).__init__(channels_for_live, out_buffer_queue, data_save_queue=data_save_queue, put_data_on_out_queue_flag=put_data_on_out_queue_flag,
                                              subject_name=subject_name, subject_tracking_number=subject_tracking_number, experiment_number=experiment_number)

        ''' Make sure our misc_queue list and misc_queue_list_channels are proper.'''
        if misc_queue_list is not None and misc_queue_list_channels is None:
            misc_queue_list_channels = ['All'] * len(misc_queue_list)
        elif misc_queue_list is not None and len(misc_queue_list) != len(misc_queue_list_channels):
            raise ValueError('Misc_queue_list and misc_queue_list_channels must be the same length')
        self.misc_queue_list, self.misc_queue_list_channels = misc_queue_list, misc_queue_list_channels
        self.zipped_misc_queue_and_channel_list = list(zip(self.misc_queue_list, self.misc_queue_list_channels))
        self.samples_to_save = samples_to_save

        # first resolve an EEG stream on the lab network
        print("looking for an EEG stream...")
        self.streams = pylsl.resolve_stream('type', 'EEG')

        # create a new inlet to read from the stream
        print("Creating inlet...")
        self.inlet = pylsl.StreamInlet(self.streams[0])

        self.current_index = 0

    def start_recording(self):
        """
        Start our recording
        """
        print("Starting recording...")

        # samples to save counter
        counter = 0

        misc_queue_buffer = None

        # ##### Main Loop #### #
        while True:
            sample, timestamp = self.inlet.pull_sample()
            if self.current_index == 0:
                print("Receiving Data:", sample)


            # Get the time we collected the sample
            self.data_index += 1  # Increase our sample counter

            CCDLUtil.EEGInterface.EEG_INDEX.EEG_INDEX = self.data_index
            CCDLUtil.EEGInterface.EEG_INDEX.EEG_INDEX_2 = self.data_index
            self.current_index = self.data_index
            counter += 1
            # print self.data_index, CCDLUtil.EEGInterface.EEG_INDEX.EEG_INDEX
            ###################
            # Handle the Data #
            ###################
            # Save the Data - We put data on the queue to be saved - format for queue (index, time, data)
            if self.data_save_queue is not None:
                self.data_save_queue.put((self.data_index, timestamp, sample))

            # Put data on the out queue
            if self.put_data_on_out_queue_flag and self.out_buffer_queue is not None and self.channels_for_live is not None and self.channels_for_live != []:
                # Only put on the channels we need.  self.channels_for_live is guaranteed lower case... we'll program defensively
                if self.channels_for_live == 'all' or self.channels_for_live == 'All' or self.channels_for_live == 'ALL':
                    trimmed_data_for_out_queue = sample
                else:
                    trimmed_data_for_out_queue = [sample[index] for index in self.channels_for_live]
                self.out_buffer_queue.put(trimmed_data_for_out_queue)


            ''' Take care of putting data on our misc queues. '''
            for misc_queue, wanted_misc_channels in self.zipped_misc_queue_and_channel_list:
                if wanted_misc_channels.lower().strip() == 'all':
                    trimmed_data_for_out_queue = np.asarray(sample)
                else:
                    trimmed_data_for_out_queue = np.asarray([sample[index] for index in wanted_misc_channels])

                trimmed_data_for_out_queue = np.expand_dims(trimmed_data_for_out_queue, axis=0)
                assert len(trimmed_data_for_out_queue.shape) == 2
                misc_queue_buffer = CCDLDataParser.stack_epochs(existing=misc_queue_buffer, new_trial=trimmed_data_for_out_queue, axis=0)
                # when we save up enough samples, send them to out queue
                if counter >= self.samples_to_save:
                    print('misc shape', misc_queue_buffer.shape)
                    misc_queue.put(misc_queue_buffer)
                    counter = 0


if __name__ == '__main__':
    dc = GUSBAmpStreamer(channels_for_live='All', out_buffer_queue=queue.Queue, data_save_queue=None)
    dc.start_recording()
