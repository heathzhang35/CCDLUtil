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

# Todo  This script has 32 channels hard-coded.  This needs to be fixed to work with other numbers.

# needs socket and struct library
import socket
import struct
import time
import Queue
import numpy as np
import CCDLUtil.EEGInterface.EEG_INDEX
import CCDLUtil.EEGInterface.EEGInterface
from CCDLUtil.Utility.Decorators import threaded
import csv


class Marker:
    """Marker class for storing marker information"""
    def __init__(self):
        self.position = 0
        self.points = 0
        self.channel = -1
        self.type = ""
        self.description = ""


class BrainAmpStreamer(CCDLUtil.EEGInterface.EEGInterface.EEGInterfaceParent):

    """
    A Parent interface that should be inherited other systems that interface with EEG.
    """

    def __init__(self, channels_for_live, live=True, save_data=True, subject_name=None, subject_tracking_number=None,
                 experiment_number=None):
        """
        A data collection object for the EEG interface.  This provides option for live data streaming and saving data to file.

        For live data streaming, use with a threading or multiprocessing queue (ie. Queue.queue()
           Data will be put on the queue, which can be read by another thread.)

        Modifies the EEG_INDEX and EEG_INDEX_2 in CCDLUtil/EEGInterface/EEG_INDEX.py when each packet arrives.  These variables can be read from any thread.
            Use this to time mark events in your other programs.

        :param channels_for_live: List - a list of channel names (or indexes) to put on the out_buffer_queue. If [], no channels will be put on the out_buffer_queue.
                                  If 'All', all channels will be placed on the out_buffer_queue.  Channels for live **cannot** be just an int. It must be a list or 'All'.
        :param data_save_queue: queue to put data to save.  If None, data will not be saved.
        :param out_buffer_queue: The channel listed in the channels_for_live parameter will be placed on this queue. This is intended for live data analysis.
                                 If None, no data will be put on the queue.
                                 Items put on the out buffer queue will be a numpy array (though this can be either a 2D or a 1D numpy array).
                                 Data put on this queue is downsampled to 500 Hz.  **Data put on this queue is of the shape (sample, channel)**.

                                 10 Samples are put on this queue at a time.  Thus the actual shape will be (10, channel)

        :param subject_name: Optional -- Name of the subject. Defaults to 'None'
        :param subject_tracking_number: Optional -- Subject Tracking Number (AKA TMS group experiment number tracker). Defaults to 'None'
        :param experiment_number: Optional -- Experimental number. Defaults to 'None'
        """
        # Call our EEGInterfaceParent init method.
        super(BrainAmpStreamer, self).__init__(
            channels_for_live=channels_for_live, live=live, save_data=save_data, subject_name=subject_name,
            subject_tracking_number=subject_tracking_number, experiment_number=experiment_number)
        # Create a tcpip socket
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to recorder host via 32Bit RDA-port
        # adapt to your host, if recorder is not running on local machine
        # change port to 51234 to connect to 16Bit RDA-port

        try:
            self.con.connect(("localhost", 51244))
        except:
            print "--Ensure that the BrainVision software is on and the dongle is plugged in and functioning."
            print "See CCDLUtil Documentation for instructions on how to run the BrainVision EEG system --"
            time.sleep(1)
            raise

    @staticmethod
    def recv_data(socket, requestedSize):
        # Helper function for receiving whole message
        returnStream = ''
        while len(returnStream) < requestedSize:
            databytes = socket.recv(requestedSize - len(returnStream))
            if databytes == '':
                raise RuntimeError("connection broken")
            returnStream += databytes

        return returnStream

    @staticmethod
    def split_string(raw):
        """
          Helper function for splitting a raw array of
          zero terminated strings (C) into an array of python strings
        """
        stringlist = []
        s = ""
        for i in range(len(raw)):
            if raw[i] != '\x00':
                s = s + raw[i]
            else:
                stringlist.append(s)
                s = ""

        return stringlist

    @staticmethod
    def get_properties(rawdata):
        """
        Helper function for extracting eeg properties from a raw data array
        """
        # Extract numerical data
        (channelCount, samplingInterval) = struct.unpack('<Ld', rawdata[:12])
        # Extract resolutions
        resolutions = []
        for c in range(channelCount):
            index = 12 + c * 8
            restuple = struct.unpack('<d', rawdata[index:index+8])
            resolutions.append(restuple[0])

        # Extract channel names
        channelNames = BrainAmpStreamer.split_string(rawdata[12 + 8 * channelCount:])

        return channelCount, samplingInterval, resolutions, channelNames

    def get_data(self, rawdata, num_channels):
        """
        Helper function for extracting eeg and marker data from a raw data array
        """
        # read from tcpip socket

        # Extract numerical data
        (block, points, markerCount) = struct.unpack('<LLL', rawdata[:12])

        # Extract eeg data as array of floats
        data = []
        for i in range(points * num_channels):
            index = 12 + 4 * i
            value = struct.unpack('<f', rawdata[index:index+4])
            data.append(value[0])

        # Extract markers
        markers = []
        index = 12 + 4 * points * num_channels
        for m in range(markerCount):
            markersize = struct.unpack('<L', rawdata[index:index+4])

            ma = Marker()
            (ma.position, ma.points, ma.channel) = struct.unpack('<LLl', rawdata[index+4:index+16])
            typedesc = BrainAmpStreamer.split_string(rawdata[index + 16:index + markersize[0]])
            ma.type = typedesc[0]
            ma.description = typedesc[1]

            markers.append(ma)
            index = index + markersize[0]
        return block, points, markerCount, data, markers

    @threaded(False)
    def start_recording(self):
        """
        Start our recording
        """
        # ##### Main Loop #### #
        print "start recording"
        while True:
            raw_data, msgsize, msgtype = self.get_raw_data()
            # Perform action dependent on the message type
            if msgtype == 1:
                channel_count, sampling_interval, resolutions, channel_names, channel_dict, meta_info_str = self.first_message_actions(raw_data)
            elif msgtype == 4:
                # Data message, extract data and markers
                (block, points, marker_count, data, markers) = self.get_data(raw_data, channel_count)
                # data is a list of length 3200
                assert len(data) == 3200
                # Get the time we collected the sample
                data_recieve_time = time.time()
                self.data_index += 1  # Increase our sample counter

                CCDLUtil.EEGInterface.EEG_INDEX.EEG_INDEX = self.data_index
                CCDLUtil.EEGInterface.EEG_INDEX.EEG_INDEX_2 = self.data_index

                ######################
                # Check for overflow #
                ######################
                if self.last_block != -1 and block > self.last_block + 1:
                    print "*** Index: " + str(self.data_index) + "OVERFLOW with " + str(block - self.last_block) + " datablocks ***"
                    if self.subject_data_path is not None:
                        with open(self.subject_data_path + self.subject_name + '_Overflow.txt', 'a') as handle_f:
                            handle_f.write(str(self.data_index) + '\t' + str(block - self.last_block) + '\n')
                self.last_block = block
                self.print_marker_count(markers=marker_count, marker_count=marker_count)

                ###################
                # Handle the Data #
                ###################
                # Save the Data - We put data on the queue to be saved - format for queue (index, time, data)
                if self.data_save_queue is not None:
                    downsampled_matrix = self.downsample_all_channels(data=data, resolutions=resolutions)
                    save_string = self.convert_downsample_matrix_to_save_string(data_index=self.data_index,
                                                                                data_recieve_time=data_recieve_time, downsampled_matrix=downsampled_matrix)
                    self.data_save_queue.put((None, None, save_string))

                # The data put on the out buffer queue is downsamled to 500 Hz.
                if self.live:
                    self.handle_out_buffer_queue(data, resolutions, channel_count, channel_dict)

            elif msgtype == 3:
                self.con.close()  # Stop message, terminate program; Close tcpip connection
                break

    def convert_downsample_matrix_to_save_string(self, data_index, data_recieve_time, downsampled_matrix):
        """
        converts a downsample matrix of shape(samples, channels) to a string that can be used to save to a file
        """
        ret_str = ''
        data_index_str = str(data_index)
        data_recieve_time_str = str(data_recieve_time)
        for ii in xrange(downsampled_matrix.shape[0]):
            ret_str += ','.join([data_index_str, data_recieve_time_str] + map(str, list(downsampled_matrix[ii, :]))) + '\n'
        return ret_str

    def downsample_all_channels(self, data, resolutions):
        """
        Downsamples our data from 5000 Hz to 500 Hz for all channels
        :param data: One data packet for 32 channels.
        :param resolutions: Our resolutions
        :return: A matrix of shape 10 by 32.  That is 10 samples for 32 channels.
        """
        # We sample at 5000 Hz.  We want to down sample to 500 hz.  We collect data in packets of 100 samples
        # at 50 Hz. 100 * 50 = 5000
        # If we took a single sample from each packet, we would be sampling at 50 Hz.
        # Because we want to sample at 500 Hz, we need to take 10x as many samples, so for every packet,
        # we need to collect 10 data points out of the 100 (aka, we need to collect every 10th data point)

        indexes_needed = range(0, 100, 10)
        # Shape is (Samples, Channels)
        channels = np.zeros((len(indexes_needed), len(resolutions)))
        for ii, resolution in enumerate(resolutions):
            # TODO: document this change
            channel_data = [data[index * 32 + ii] * resolution for index in indexes_needed]
            channels[:, ii] = np.asarray(channel_data)
        return channels

    def handle_out_buffer_queue(self, data, resolutions, channel_count, channel_dict):
        """
        Puts every 10th sample on the out_buffer_queue (downsampling to 500 Hz)
        Number of channels: 32
        Sampling Rate [Hz]: 5000
        Sampling Interval [micro seconds]: 200  (0.0002 seconds; 5000 Hz)

        Packet size = 100 samples
        Packet arrival = 50 Hz
        """
        # We sample at 5000 Hz.  We want to down sample to 500 hz.  We collect data in packets of 100 samples
        # at 50 Hz. 100 * 50 = 5000
        # If we took a single sample from each packet, we would be sampling at 50 Hz.
        # Because we want to sample at 500 Hz, we need to take 10x as many samples, so for every packet,
        # we need to collect 10 data points out of the 100 (aka, we need to collect every 10th data point)

        # 100 is the number of samples we get once
        indexes_needed = range(0, 100, 10)
        # Shape is (Samples, Channels)
        # size is correct: 10 x 1
        channels = np.zeros((len(indexes_needed), len(self.channels_for_live)))
        for ii, ch in enumerate(self.channels_for_live):
            # Get the channel index
            if type(ch) is str:
                channel_index = channel_dict[ch]
            else:
                channel_index = ch
            # Get our resolution for this channel (0.5)
            resolution = resolutions[channel_index]
            # TODO: doucment this change -- fixed the indexing of channel data
            channel_data = [data[index * 32 + channel_index] * resolution for index in indexes_needed]
            channels[:, ii] = np.asarray(channel_data)
        # Put our numpy array of channels on the queue.  Channels shape -> [samples (10), channel]
        self.out_buffer_queue.put(channels)

    @staticmethod
    def print_marker_count(markers, marker_count):
        # Print markers, if there are some in actual block
        if marker_count > 0:
            for m in range(marker_count):
                print "Marker " + markers[m].description + " of type " + markers[m].type

    @staticmethod
    def calc_avg_power(data1s, channel_count, sampling_interval, resolutions):
        if len(data1s) > channel_count * 1000000 / sampling_interval:
            index = int(len(data1s) - channel_count * 1000000 / sampling_interval)
            data1s = data1s[index:]
            avg = 0
            # Do not forget to respect the resolution !!!
            for i in range(len(data1s)):
                avg = avg + data1s[i] * data1s[i] * resolutions[i % channel_count] * resolutions[i % channel_count]
            avg /= len(data1s)
            print "Average power: " + str(avg)
            return []
        else:
            return data1s

    def first_message_actions(self, raw_data, verbose=False):
        """
        Executes all actions associated with the first message (such as collecting meta information)
        :param raw_data:
        :param verbose: If true, prints message to console.
        :return:
        """
        # Start message, extract eeg properties and display them
        (channel_count, sampling_interval, resolutions, channel_names) = BrainAmpStreamer.get_properties(raw_data)
        # reset block counter
        self.last_block = -1

        sampling_interval_seconds = sampling_interval * 10.0 ** -6
        meta_info_str = "Subject Name,\t" + str(self.subject_name) + \
                        "\nSubject Tracking Number,\t" + str(self.subject_number) + \
                        "\nExperiment Number,\t" + str(self.experiment_number) + \
                        "\nNumber of channels,\t" + str(channel_count) + \
                        "\nSampling interval,\t" + str(sampling_interval) + ' microseconds (' + str(sampling_interval_seconds) + ' seconds)' + \
                        '\nOriginal Sampling Frequency,\t' + str(1.0 / sampling_interval_seconds) + ' Hz' + \
                        '\nDownsampled Sampling Frequency,\t' + str(500) + ' Hz' + \
                        "\nResolutions,\t,\t" + str(resolutions) + \
                        "\nChannel Names,\t,\t" + str(channel_names)
        if self.data_save_queue is not None:
            self.data_save_queue.put((None, None, meta_info_str))
        if verbose:
            print meta_info_str

        channel_dict = dict(zip(channel_names, range(channel_count)))
        return channel_count, sampling_interval, resolutions, channel_names, channel_dict, meta_info_str

    def get_raw_data(self):
        # Get message header as raw array of chars
        raw_hdr = BrainAmpStreamer.recv_data(self.con, 24)

        # Split array into usefull information id1 to id4 are constants
        (id1, id2, id3, id4, msgsize, msgtype) = struct.unpack('<llllLL', raw_hdr)

        # Get data part of message, which is of variable size
        raw_data = BrainAmpStreamer.recv_data(self.con, msgsize - 24)
        return raw_data, msgsize, msgtype


if __name__ == '__main__':
    # streamer
    dc = BrainAmpStreamer(['Oz'], live=True, save_data=True)
    # start
    dc.start_recording()
    # save
    dc.start_saving_data('test.csv')

