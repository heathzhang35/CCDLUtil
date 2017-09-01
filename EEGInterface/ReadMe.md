## EEG Interface Module


This module is for directly interfacing with EEG systems (such as the
BrainVision Amplifier (aka Brain amp) and Open BCI.  This module
is also for synthetic data generators.


### OpenBCI

### Debugging
See the main readme file for more information on debugging.

#### OpenBCIHardwareInterface.py
Running OpenBCIHardwareInterface.py (ie python OpenBCIHardwareInterface.py) will print all the samples to console.
This has been tested, so if there is a problem running this script, then the problem is likely with OpenBCI
itself.

#### OpenBCIStreamer.py
An example of how to run and save data into a file called sample.csv

    data_save_queue = Queue.Queue()
    obs = OpenBCIStreamer(out_buffer_queue=None, data_save_queue=data_save_queue)
    threading.Thread(target=lambda: EEGDataSaver.start_eeg_data_saving(save_data_file_path='./sample.csv', queue=data_save_queue, header="Sample Header")).start()
    obs.start_open_bci_streamer()

