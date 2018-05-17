import CCDLUtil.EEGInterface.OpenBCI.OpenBCIHardwareInterface as BciHwInter
import CCDLUtil.EEGInterface.EEG_INDEX
import CCDLUtil.EEGInterface.EEGInterface
from CCDLUtil.Utility.Decorators import threaded
import time
import serial


class OpenBCIStreamer(CCDLUtil.EEGInterface.EEGInterface.EEGInterfaceParent):

    def __init__(self, channels_for_live='All', channels_for_save='All', live=True, save_data=True,
                 include_aux_in_save_file=True, subject_name=None, subject_tracking_number=None, experiment_number=None,
                 channel_names=None, port=None, baud=115200):
        """
        Inherits from CCDLUtil.EEGInterface.EEGInterfaceParent.EEGInterfaceParent

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

        super(OpenBCIStreamer, self).__init__(
            channels_for_live=channels_for_live, live=live, save_data=save_data, subject_name=subject_name,
            subject_tracking_number=subject_tracking_number, experiment_number=experiment_number)
        # in super, self.data_index is set to 0
        self.channel_names = str(channel_names)
        self.channels_for_save = channels_for_save
        self.include_aux_in_save_file = include_aux_in_save_file
        self.channels_for_live = channels_for_live
        # Set our port to default if a port isn't passed
        if port is None:
            raise ValueError("port cannot be None!")
        self.port = port
        self.baud = baud
        # create board object from hardware interface
        self.board = BciHwInter.OpenBCIBoard(port=self.port, baud=self.baud, scaled_output=False, log=True)

    def callback_fn(self, data_packet):
        """
        This is a callback from our OpenBCI board.  A data packet is passed (a list of the data points)

        :param data_packet:  Data as taken from the OpenBCI board.  This is generally an OpenBCI sample object.
        """
        try:
            # List of data points
            data = data_packet.channel_data
            # starts at -1, our data is always indexed >= 0 by incrementing here instead of at the end of the method.
            self.data_index += 1
            # List of AUX data. note that this is sampled at a fraction of the rate of the data.
            # Each packet will have this field
            aux_data = data_packet.aux_data
            # but packets that don't have aux data will have a list of zeros.
            id_val = data_packet.id

        except Exception as e:
            # If we throw an error in this portion of the code, exit everything
            print(e.message, e)
            # continue to run, ignore the incomplete packet
            return

        # Put on Out Buffer for live data analysis.
        if self.live:
            # Get our channels from channels for live:
            if type(self.channels_for_live) is str and self.channels_for_live.lower() == 'all':
                self.out_buffer_queue.put(data)
            elif type(self.channels_for_live) is list:
                # Get only the indexes contained in the channels for live list.
                trimmed_data = OpenBCIStreamer.trim_channels_with_channel_index_list(data, self.channels_for_live)
                self.out_buffer_queue.put(trimmed_data)
            else:
                if self.channels_for_live is not None:
                    raise ValueError('Invalid channels_for_live value.')
        # Save data
        if self.save_data:
            data_to_put_on_queue = None
            if type(self.channels_for_save) is str and self.channels_for_save.lower() == 'all':
                data_to_put_on_queue = data
            elif type(self.channels_for_live) is list:
                data_to_put_on_queue = OpenBCIStreamer.trim_channels_with_channel_index_list(data, self.channels_for_save)
            else:
                if self.channels_for_save is not None:
                    raise ValueError('Invalid channels_for_live value.')

            if data_to_put_on_queue is not None:

                data_str = str(id_val)+','+str(time.time())+','+','.join([str(xx) for xx in data_to_put_on_queue])

                if self.include_aux_in_save_file:
                    data_str += ',' + ','.join([str(yy) for yy in aux_data])

                # Data put on the data save queue is a len three tuple.
                self.data_save_queue.put((None, None, data_str + '\n'))

        # Set our two EEG INDEX parameters.
        CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX = self.data_index
        CCDLUtil.EEGInterface.EEG_INDEX.CURR_EEG_INDEX_2 = self.data_index
        CCDLUtil.EEGInterface.EEG_INDEX.EEG_ID_VAL = id_val

    @threaded(False)
    def start_recording(self):
        """
        Starts the open BciHwInter streamer. Called in a new thread
        """

        print('start recording')
        try:
            self.board.start_streaming(self.callback_fn)
        except serial.SerialException:
            pass

    def stop_recording(self):
        print('stop recording')
        self.stopped = True
        self.board.stop()
        self.board.disconnect()


if __name__ == '__main__':

    obs = OpenBCIStreamer(live=True, save_data=True, port='COM6')
    obs.start_recording()
    obs.start_saving_data(save_data_file_path='TestDataLoss/testing_3.csv', header="Sample Header")
    cue = 'start'
    while cue != 'stop':
        cue = input("Enter stop to finish recording: ")

    obs.stop_recording()


