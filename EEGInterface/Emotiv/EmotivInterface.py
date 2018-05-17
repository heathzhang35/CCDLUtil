import CCDLUtil.EEGInterface.EEGInterface as EEGParent
from . import Constants
import ctypes as ct
import sys
import time
import numpy as np
from threading import Thread
from CCDLUtil.Utility.Decorators import threaded

class EmotivStreamer(EEGParent.EEGInterfaceParent):

    def __init__(self,eeg_file_path, lib_path, channels_for_live='All', live=True, save_data=True, 
                 subject_name=None, subject_tracking_number=None, experiment_number=None):
        # call parent constructor
        super(EmotivStreamer, self).__init__(channels_for_live=channels_for_live, subject_name=subject_name,
                                             subject_tracking_number=subject_tracking_number,
                                             experiment_number=experiment_number)
        sys.path.append(Constants.LIB_PATH)
        # set EDK library path
        self.lib_path = lib_path
        self.libEDK = ct.cdll.LoadLibrary(self.lib_path)
        # set EEG file save path
        self.eeg_file_path = eeg_file_path

    def setup_var(self):
        """
        Set up variables needed for the experiment
        :return: see usage in start_recording_and_saving_data
        """
        return self.libEDK.EE_EmoEngineEventCreate(), self.libEDK.EE_EmoStateCreate(), ct.c_uint(0), ct.c_uint(0), ct.c_uint(0), ct.c_uint(1726), ct.c_float(1), ct.c_int(0)

    @threaded(False)
    def start_recording(self):
        """
        Start recording brain signal from Emotiv headset
        """
        self.start_recording_and_saving_data(self.eeg_file_path)


    def start_recording_and_saving_data(self, eeg_file_path):
        """
        Build up connection with Emotiv headset and start recording data
        :param eeg_file_path: the path to save eeg file
        """
        # set up variables
        e_event, e_state, user_id, n_samples, n_sam, composer_port, secs, state = self.setup_var()
        # pointers
        n_samples_taken = ct.pointer(n_samples)
        data = ct.pointer(ct.c_double(0))
        user = ct.pointer(user_id)
        ready_to_collect = False
        # start connection
        print("Connecting...")
        if self.libEDK.EE_EngineConnect("Emotiv Systems-5") != 0: # connection failed
            print("Emotiv Engine start up failed.")
            self.stop_connection(e_event=e_event, e_state=e_state)
            sys.exit(1)
        print("Connected! Start receiving data...")
        # write data to file
        f = open(eeg_file_path, 'w')
        # write header
        print(Constants.HEADER, file=f)
        h_data = self.libEDK.EE_DataCreate()
        self.libEDK.EE_DataSetBufferSizeInSec(secs)
        # start recording
        while True:
            state = self.libEDK.EE_EngineGetNextEvent(e_event)
            if state == 0:
                event_type = self.libEDK.EE_EmoEngineEventGetType(e_event)
                self.libEDK.EE_EmoEngineEventGetUserId(e_event, user)
                # add user
                if event_type == 16:
                    print("User added")
                    self.libEDK.EE_DataAcquisitionEnable(user_id, True)
                    ready_to_collect = True
            if ready_to_collect:
                self.libEDK.EE_DataUpdateHandle(0, h_data)
                self.libEDK.EE_DataGetNumberOfSample(h_data,n_samples_taken)
                # print "Updated :", n_samples_taken[0]
                if n_samples_taken[0] != 0:
                    n_sam = n_samples_taken[0]
                    arr = (ct.c_double*n_samples_taken[0])()
                    ct.cast(arr, ct.POINTER(ct.c_double))
                    #self.libEDK.EE_DataGet(h_data, 3,byref(arr), nSam)
                    data = np.array('d') # zeros(n_samples_taken[0],double)
                    for sampleIdx in range(n_samples_taken[0]):
                        # channel 14 + loc data 6 + timestamp 1 = 23
                        data = np.zeros(23)
                        for i in range(22):
                            self.libEDK.EE_DataGet(h_data, Constants.TARGET_CHANNEL_LIST[i], ct.byref(arr), n_sam)
                            print(arr[sampleIdx],",", end=' ', file=f)
                            data[i] = arr[sampleIdx]
                        # write our own time stamp
                        t = time.time()
                        data[-1] = t
                        print(t, end=' ', file=f)
                        # put data onto out buffer queue
                        self.out_buffer_queue.put(data)
                        # switch line
                        print('\n', end=' ', file=f)
            time.sleep(0.2)
        # not sure the use of this in the original program...
        self.libEDK.EE_DataFree(h_data)
        self.stop_connection(e_event=e_event, e_state=e_state)

    def stop_connection(self, e_event, e_state):
        """
        Stop the connection with Emotiv headset
        :param e_event: e_event
        :param e_state: e_state
        """
        self.libEDK.EE_EngineDisconnect()
        self.libEDK.EE_EmoStateFree(e_state)
        self.libEDK.EE_EmoEngineEventFree(e_event)

### dummy code to get data
@threaded(False)
def get_data(emotiv):
    while True:
        print(emotiv.out_buffer_queue.get())


if __name__ == '__main__':
    emotiv = EmotivStreamer("test.csv", ".\edk.dll")
    emotiv.start_recording()
    get_data(emotiv)


