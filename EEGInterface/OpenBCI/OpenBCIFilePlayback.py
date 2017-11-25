import time

import OpenBCIHardwareInterface as HardwareInterface
import OpenBCIInterface
import ParentInterface.EpochIndex as EpochIndex
import ParentInterface.OnlinePredScreen as OnlinePredScreen
from ParentInterface import OnlinePredBufferMessages


class OpenBCIFilePlayback(OpenBCIInterface.OpenBCIStreamer):
    """
    Inherits from OpenBCIStreamer. This is to simulate the same interface we would receive from OpenBCI
    """

    def __init__(self, data_dir_path, subject_num, qm_queue, current_eeg_index_lock, port, pick_dict,
                 online_pred_screen_queue, queue_dict, run_buffer_control, nback_epoch_control, live_data_queue=None):
        super(self.__class__, self).__init__(data_dir_path, subject_num, qm_queue, current_eeg_index_lock, port,
                                             live_data_queue)
        assert type(pick_dict) is dict
        self.queue_dict = queue_dict
        meta = pick_dict['meta']
        self.fs = int(meta['fs'])
        self.task_type = meta['task_type']
        channel_cols = meta['channel_cols']
        # Shape epoch, sample, channel.  We are removing the aux channels and time series channels.
        # We're not going to concern ourselves with non eeg items.
        self.data = pick_dict['data']

        self.labels = pick_dict['labels']
        self.online_pred_screen_queue = online_pred_screen_queue
        self.run_buffer_control = run_buffer_control
        self.nback_epoch_control = nback_epoch_control

    def start_open_bci_streamer(self):
        self.start_openbci_playback(self.write_file_callback)

    def start_openbci_playback(self, callback):
        # Initialize our epoch and sample counters. We'll use these values to know what data to put on the queue

        # We keep track of the current epoch index and the previous epoch index.
        epoch_index = EpochIndex.EPOCH_INDEX
        start_epoch_index = EpochIndex.EPOCH_INDEX
        previous_epoch_index = epoch_index

        # Keep track of the sample index.
        sample_index = 0
        samples_per_epoch = self.data.shape[1]

        num_epochs = self.data.shape[0]
        while True:
            if EpochIndex.START_PLAYBACK_DATA_FLAG:
                if self.nback_epoch_control:
                    # We are allowing a different module to control the current index
                    epoch_index = EpochIndex.EPOCH_INDEX
                    if epoch_index != previous_epoch_index:
                        # We started a new epoch.  Set our sample index back to zero.
                        sample_index = 0
                        previous_epoch_index = epoch_index

                if self.run_buffer_control:

                    # Check if we are starting a new epoch
                    if sample_index >= samples_per_epoch:
                        # Add 1 to our epoch index if we aren't at the start of a trial. Start from the beginning if we just read the last epoch
                        epoch_index = 0 if epoch_index > num_epochs else epoch_index + 1
                        self.queue_dict['online_preds_messages'].put(OnlinePredBufferMessages.STOP_AND_RESET)
                        sample_index = 0  # start our sample_index over again.
                    if self.run_buffer_control and sample_index == 0:
                        print "Starting Collection"
                        self.queue_dict['online_preds_messages'].put(OnlinePredBufferMessages.START_COLLECTION)
                        correct_label = self.labels[epoch_index]['readable']
                        self.online_pred_screen_queue.put((OnlinePredScreen.OnlinePredScreen.CORRECT_LABEL, correct_label))
                        # We are starting a new epoch, we need to put a new label onto the queue. We'll be using the readable

                # Send all channels for this epoch and sample
                try:
                    data_to_send = self.data[epoch_index, sample_index, :]
                    data_packet = HardwareInterface.OpenBCISample(packet_id=sample_index, aux_data=[1, 2, 3],
                                                                  channel_data=data_to_send)
                    callback(data_packet)
                except IndexError:
                    print "Index Error", epoch_index, sample_index
                # We wait for a bit before sending our next data packet.
                time.sleep(1.0 / self.fs)
                sample_index += 1
                # print "Sample Index", sample_index, "Epoch Index", epoch_index
            else:
                time.sleep(0.01)
