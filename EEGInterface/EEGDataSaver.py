"""
This file is for saving EEG Data
"""

import CCDLUtil.DataManagement.StringParser as StringParser
import time
import sys
import Queue

def start_eeg_data_saving(save_data_file_path, queue, header=None, timeout=15):
    """

    This function is called from the BrainAmpInterface.

    A function to be called in a new thread whose sole purpose is to save eeg data to disk.
    :param save_data_file_path: A string - The full file name to save the data (for example './data/subjectX.csv').
    :param queue: The queue to read the data from.
            Data should be placed on the queue in the form:
                index, time, data

                - Index
                    Where index is the packet (or sample) index.  This can be a string or a number.
                - Time
                    Time is the time in which the transferred data was collected.  This is typically from time.time().
                        This can be a string or a number.
                - Data
                    A list of data points in the form [chan 1, chan 2...], where chan X is a number.
                    If data is a list, it will be comma separated.  If data is a string, we'll write it to file as it was provided to us.

            Data save format.
                Data will be saved in the comma separated format:
                    index,time,chan1,chan2,chan3...\n

    :param header: Header for the file.  If no header is wanted, pass None.  Defaults to None.
    :param timeout: If we don't collect any data after timeout seconds, we'll quit all processes.  If none, there won't be a timeout.

    :return: Runs infinitely.  Kill by terminating the thread.
    """
    f = file(save_data_file_path, 'w')
    # Write our header with only one newline character
    if header is not None:
        if header.endswith('\n'):
            f.write(header)
        else:
            f.write(header)
            f.write('\n')
        f.flush()
    while True:
        # get our components
        try:
            if timeout is None:
                index, t, data = queue.get()
            else:
                index, t, data = queue.get(timeout)
        except Queue.Empty:
            print "Data is not being collected."
            time.sleep(2)
            # quit system
            sys.exit(1)
        index = '' if index is None else str(index) + ','
        t = '' if t is None else str(t) + ','
        if type(data) is list:
            # convert our data items to strings
            data = map(str, data)
            # convert our data to a comma separated string
            data = ','.join(data)
        else:
            if type(data) is not str:
                raise TypeError("Invalid data type -- data must be either string or ")
        # add a newline if needed.  Commas are already accounted for
        data_str = str(index) + str(t) + StringParser.idempotent_append_newline(data)
        # Write our index and timestamp
        f.write(data_str)
        # Flush our buffer
        f.flush()
