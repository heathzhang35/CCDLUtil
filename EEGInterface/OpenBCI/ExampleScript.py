"""
Example for out to use OpenBCI interface.
"""

import CCDLUtil.EEGInterface.OpenBCI.OpenBCIStreamer as CCDLStreamer
import CCDLUtil.EEGInterface.EEG_INDEX as CCDLEEGIndex
import Queue
import threading
import CCDLUtil.EEGInterface.EEGDataSaver as CCDLDataSaver
import time


def main():
    # Create our two multithread queues.
    out_buffer_queue = Queue.Queue()
    data_save_queue = Queue.Queue()

    # Create our Data streamer object
    obs = CCDLStreamer.OpenBCIStreamer(out_buffer_queue=out_buffer_queue, data_save_queue=data_save_queue, port="COM5", channels_for_live='all', channels_for_save='all')

    # Start our data saver in a new thread
    threading.Thread(target=lambda: CCDLDataSaver.start_eeg_data_saving(save_data_file_path='./sample.csv', queue=data_save_queue, header="Sample Header")).start()

    # Start our live data analysis in another thread
    threading.Thread(target=lambda out=out_buffer_queue: print_items_from_queue(out)).start()

    # Start streaming data!  Data will be sent to both the out_buffer_queue and data_save_queue
    obs.start_open_bci_streamer()


def print_items_from_queue(out_queue):
    i = 0
    while True:  # Record forever!
        # Get our next data packet.  This is a blocking call.
        data = out_queue.get()

        # Print our current size of our queue
        print "Approximate queue size", out_queue.qsize()
        if i % 100 == 0:
            # Print every 100th sample, along with the current EEG index
            print CCDLEEGIndex.CURR_EEG_INDEX, data
        i += 1


if __name__ == '__main__':
    main()
