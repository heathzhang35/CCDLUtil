import OpenBCIHardwareInterface as BciHwInter
import CCDLUtil.Utility.SystemInformation as SystemInfo
import CCDLUtil.EEGInterface.EEG_INDEX
import CCDLUtil.EEGInterface.EEGInterfaceParent
import Queue
import threading
import CCDLUtil.EEGInterface.EEGDataSaver as EEGDataSaver
import time


class OpenBCIStreamer(CCDLUtil.EEGInterface.EEGInterfaceParent.EEGInterfaceParent):

    def __init__(self, out_buffer_queue, channels_for_live='All', channels_for_save='All', include_aux_in_save_file=True, data_save_queue=None, subject_name=None,
                 subject_tracking_number=None, experiment_number=None, channel_names=None, port=None, baud=115200):
        """
        A data collection object for the EEG interface.  This provides option for live data streaming and saving data to file.

        For live data streaming, use with a threading or multiprocessing queue (ie. Queue.queue()
           Data will be put on the queue, which can be read by another thread.)

        Modifies the EEG_INDEX and EEG_INDEX_2 in CCDLUtil/EEGInterface/EEG_INDEX.py when each packet arrives.  These variables can be read from any thread.
            Use this to time mark events in your other programs.

        :param channels_for_live: List of channel Indexes (Only!! -- channel names has not been implemented for OpenBCI) to put on the out_buffer_queue.
                                    If [], no channels will be put on the out_buffer_queue.
                                  If 'All', all channels will be placed on the out_buffer_queue.
        :param channels_for_save: List of channel Indexes (Only!! -- channel names has not been implemented for OpenBCI) to put on the data_save_queue.
                                    If [], no channels will be put on the out_buffer_queue.
                                    If 'All', all channels will be placed on the out_buffer_queue.
        :param include_aux_in_save_file: If True, we'll pass our AUX channels (along with the channels specified in channels_for_save) to our data_save_queue
        :param data_save_queue: queue to put data to save.  If None, data will not be saved.
        :param out_buffer_queue: The channel listed in the channels_for_live parameter will be placed on this queue. This is intended for live data analysis.
                                 If None, no data will be put on the queue.
                                 Items put on the out buffer queue will be a numpy array (though this can be either a 2D or a 1D numpy array)
        :param subject_name: Optional -- Name of the subject. Defaults to 'None'
        :param subject_tracking_number: Optional -- Subject Tracking Number (AKA TMS group experiment number tracker). Defaults to 'None'
        :param experiment_number: Optional -- Experimental number. Defaults to 'None'
        """

        super(OpenBCIStreamer, self).__init__(channels_for_live, out_buffer_queue, data_save_queue=data_save_queue, subject_name=subject_name,
                                              subject_tracking_number=subject_tracking_number, experiment_number=experiment_number)
        # in super, self.data_index is set to 0
        self.channel_names = str(channel_names)
        self.channels_for_save = channels_for_save
        self.include_aux_in_save_file = include_aux_in_save_file
        self.channels_for_live = channels_for_live

        # Set our port to default if a port isn't passed
        self.port = OpenBCIStreamer.get_default_port() if port is None else port

        self.out_buffer_queue = out_buffer_queue
        self.baud = baud

    @staticmethod
    def get_default_port():
        """
        Returns the default port for the current operating system.
        :return:
        """
        if SystemInfo.is_linux():
            return '/dev/ttyUSB0'
        elif SystemInfo.is_windows():
            return 'COM0'
        else:
            raise ValueError('Default Port for OS not recognized')

    def write_file_callback(self, data_packet):
        """
        This is a callback from our OpenBCI board.  A data packet is passed (a list of the data points)
        :param data_packet:  Data as taken from the OpenBCI board.  This is generally an OpenBCI sample object.
        """

        try:
            data = data_packet.channel_data  #  List of data points
            self.data_index += 1     # data_index starts at -1, thus our data is always indexed >= 0 by incrementing here instead of at the end of the method.
            aux_data = data_packet.aux_data  # List of AUX data (note that this is sampled at a fraction of the rate of the data.  Each packet will have this field
                                             # but packets that don't have aux data will have a list of zeros.
            id_val = data_packet.id


        except Exception as e:
            # If we throw an error in this portion of the code, exit everything
            print e.message, e
            raise  e # Won't run

        # Put on Out Buffer for live data analysis.
        if self.out_buffer_queue is not None:
            # Get our channels from channels for live:
            if type(self.channels_for_live) is str and self.channels_for_live.lower() == 'all':
                self.out_buffer_queue.put(data)
            elif type(self.channels_for_live) is list:
                # Get only the indexes contained in the channels for live list.
                trimmed_data = self.trim_channels_with_channel_index_list(data, self.channels_for_live)
                self.out_buffer_queue.put(trimmed_data)
            else:
                if self.channels_for_live is not None:

                    raise ValueError('Invalid channels_for_live value.')

        if self.data_save_queue is not None:
            data_to_put_on_queue = None
            if type(self.channels_for_save) is str and self.channels_for_save.lower() == 'all':
                data_to_put_on_queue = data
            elif type(self.channels_for_live) is list:
                data_to_put_on_queue = self.trim_channels_with_channel_index_list(data, self.channels_for_save)
            else:
                if self.channels_for_save is not None:
                    raise ValueError('Invalid channels_for_live value.')

            if data_to_put_on_queue is not None:

                data_str = str(id_val) + ',' + str(time.time()) + ',' + ','.join([str(xx) for xx in data_to_put_on_queue])

                if self.include_aux_in_save_file:
                    data_str += ',' + ','.join([str(yy) for yy in aux_data])

                # Data put on the data save queue is a len three tuple.
                self.data_save_queue.put((None, None, data_str + '\n'))

        # Set our two EEG INDEX parameters.
        CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX = self.data_index
        CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX_2 = self.data_index
        CCDLUtil.EEGInterface.EEG_INDEX.EEG_ID_VAL = id_val

    def start_open_bci_streamer(self):
        """
        Starts the open BciHwInter streamer. This method streams data infinitely and does not return.

        To keep naming consistant across EEG systems, calling .start_recording provides the same utility.
        """
        board = BciHwInter.OpenBCIBoard(port=self.port, baud=self.baud, scaled_output=False, log=True)
        board.start_streaming(self.write_file_callback)

    def start_recording(self):
        """
        Starts the open BciHwInter streamer. This method streams data infinitely and does not return.
        Data is put onto the out_buffer_queue and data_save_queue as according to the initialization of this object.
        """
        self.start_open_bci_streamer()

if __name__ == '__main__':
    data_save_queue = Queue.Queue()
    obs = OpenBCIStreamer(out_buffer_queue=None, data_save_queue=data_save_queue, port="COM5")
    threading.Thread(target=lambda: EEGDataSaver.start_eeg_data_saving(save_data_file_path='RestingStateMay24.csv', queue=data_save_queue, header="Sample Header")).start()
    obs.start_open_bci_streamer()
