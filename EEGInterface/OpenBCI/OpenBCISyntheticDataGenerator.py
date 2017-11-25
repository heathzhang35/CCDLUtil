import random
import time

import OpenBCIHardwareInterface as HardwareInterface
import OpenBCIInterface


class OpenBCISyntheticData(OpenBCIInterface.OpenBCIStreamer):
    """
    Inherits from OpenBCIStreamer. This is to simulate the same interface we would receive from OpenBCI
    """

    def __init__(self, data_dir_path, subject_num, qm_queue, current_eeg_index_lock, port, live_data_queue=None):
        super(self.__class__, self).__init__(data_dir_path, subject_num, qm_queue, current_eeg_index_lock, port, live_data_queue)

    def start_open_bci_streamer(self):
        self.start_openbci_synth(self.write_file_callback)

    def start_openbci_synth(self, callback):
        packet_id = 0
        while True:
            packet_id += 1
            time.sleep(1.0 / 250.0)
            data = [random.randint(0, 10) for _ in xrange(8)]
            data_packet = HardwareInterface.OpenBCISample(packet_id=packet_id, aux_data=[1, 2, 3], channel_data=data)
            callback(data_packet)
