import CCDLUtil.EEGInterface.EEGInterface as EEGParent
import Constants
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
        # flag for recording
        self._recording = False
        # file to write to
        self.f = None
        # events for recording
        self.e_event = None
        self.e_state = None

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

    def stop_recording(self, stop_streamer=False):
        if stop_streamer:
            self._recording = False
        # give a little time for thread to change flag
        time.sleep(2)
        self.f.flush()
        self.f.close()

    def start_recording_and_saving_data(self, eeg_file_path):
        """
        Build up connection with Emotiv headset and start recording data
        :param eeg_file_path: the path to save eeg file
        """
        # set up variables
        self.e_event, self.e_state, user_id, n_samples, n_sam, composer_port, secs, state = self.setup_var()
        # pointers
        n_samples_taken = ct.pointer(n_samples)
        data = ct.pointer(ct.c_double(0))
        user = ct.pointer(user_id)
        ready_to_collect = False
        # start connection
        print "Connecting..."
        if self.libEDK.EE_EngineConnect("Emotiv Systems-5") != 0: # connection failed
            print "Emotiv Engine start up failed."
            self.stop_connection()
            sys.exit(1)
        print "Connected! Start receiving data..."
        self._recording = True
        # write data to file
        self.f = open(eeg_file_path, 'w')
        # write header
        for header in Constants.HEADER:
            # last one in header
            if header != "TIMESTAMP" and not self.f.closed:
                self.f.write(header + ",")
            elif not self.f.closed:
                self.f.write(header + "\n")
        h_data = self.libEDK.EE_DataCreate()
        self.libEDK.EE_DataSetBufferSizeInSec(secs)
        # start recording
        while self._recording:
            state = self.libEDK.EE_EngineGetNextEvent(self.e_event)
            if state == 0:
                event_type = self.libEDK.EE_EmoEngineEventGetType(self.e_event)
                self.libEDK.EE_EmoEngineEventGetUserId(self.e_event, user)
                # add user
                if event_type == 16:
                    print "User added"
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
                            if not self.f.closed:
                                print >>self.f,arr[sampleIdx],",",
                            data[i] = arr[sampleIdx]
                        # write our own time stamp
                        t = time.time()
                        data[-1] = t
                        if not self.f.closed:
                            print >>self.f,t,
                        # put data onto out buffer queue
                        self.out_buffer_queue.put(data)
                        # switch line
                        if not self.f.closed:
                            print >>self.f,'\n',
            time.sleep(0.2)
        # not sure the use of this in the original program...
        self.libEDK.EE_DataFree(h_data)
        # self.stop_connection(self.e_event=self.e_event, e_state=e_state)

    def stop_connection(self):
        """
        Stop the connection with Emotiv headset
        :param e_event: e_event
        :param e_state: e_state
        """
        self.libEDK.EE_EngineDisconnect()
        self.libEDK.EE_EmoStateFree(self.e_state)
        self.libEDK.EE_EmoEngineEventFree(self.e_event)

    def set_file(self, new_file_path):
        # stop recording
        if not self.f.closed:
            self.stop_recording(stop_streamer=True)
        self.eeg_file_path = new_file_path
        self.start_recording()


@threaded(False)
def get_data(emotiv):
    while True:
        print emotiv.out_buffer_queue.get()


if __name__ == '__main__':
    emotiv = EmotivStreamer("test.csv", ".\edk.dll")
    emotiv.start_recording()
    # get_data(emotiv)
    time.sleep(5)
    emotiv.stop_recording(stop_streamer=True)
    time.sleep(5)
    emotiv.start_recording()



