"""
This contains methods for collecting data in order to train a classifier for the BrainNet and BIAV experiments.
"""

import os
import time
import Queue
import winsound
import datetime
import threading
import multiprocessing
import CCDLUtil.DataManagement.Log as CCDLLog
import CCDLUtil.Utility.Constants as CCDLConstants
import CCDLUtil.Graphics.PyCrosshair as CCDLPyCross
import CCDLUtil.DataManagement.FileParser as CCDLFP
import CCDLUtil.Utility.SystemInformation as CCDLSI
import CCDLUtil.EEGInterface.EEGDataSaver as CCDLEEGDatasaver
import CCDLUtil.EEGInterface.gUSBAmp.GUSBAmpInterface as CCDLGusb
import CCDLUtil.EEGInterface.OpenBCI.OpenBCIStreamer as CCDLOpenBCI
import CCDLUtil.ArduinoInterface.Arduino2LightInterface as CCDLArduino
import CCDLUtil.EEGInterface.BrainAmp.BrainAmpInterface as CCDLBrainAmp

EYES_CLOSED_TEXT_DICT = {'text': 'Eyes Closed', 'pos': (None, 100), 'color': (0, 0, 255)}  # If pos is None, it will be centered.
EYES_OPEN_TEXT_DICT = {'text': 'Eyes Open', 'pos': (None, 100), 'color': (0, 255, 0)}

REST_TEXT_DICT = {'text': 'Rest', 'pos': (None, 100), 'color': (255, 0, 255)}  # If pos is None, it will be centered.
LOOK_AT_LIGHT_TEXT_DICT = {'text': 'Look At Light', 'pos': (None, 100), 'color': (0, 255, 0)}

LOOK_AT_LEFT_LIGHT_TEXT_DICT = {'text': 'Look At Left Light', 'pos': (None, 100), 'color': (255, 0, 0)}
LOOK_AT_RIGHT_LIGHT_TEXT_DICT = {'text': 'Look At Right Light', 'pos': (None, 100), 'color': (0, 0, 255)}

END_TEXT_DICT = {'text': 'Task Complete', 'pos': (None, 100), 'color': (255, 0, 0)}


def get_user_info(data_storage_path, take_init):
    # subject_data_folder_path ends with /
    subject_num, subject_data_folder_path = CCDLFP.manage_storage(data_storage_location=data_storage_path, take_init=take_init)
    task = raw_input('Enter Task: ') if take_init else "No specified task_description"
    return subject_num, subject_data_folder_path, task


def print_info(message, trial_index, start_time):
    """
    prints our passed message, our trial index and our start time converted over to minutes and seconds.
    """
    m, s = divmod(time.time() - start_time, 60)
    print message, trial_index, '\t', "%d:%02d" % (m, s)


def start_eeg(eeg_system, subject_data_folder_path, subject_num, comport=None, vebose=True, out_buffer_queue=None, channels_for_live='All'):
    """
    Starts streaming our EEG in a new thread
    :param eeg_system: str - eeg system type
    :param subject_data_folder_path: path to subject folder.  Doesn't matter if it ends with \ or not.
    :param subject_num: any_type - subject identifier
    :param comport: Port of the EEG system.  This is only needed for using an eeg system that requires it (specifically OpenBCI)
    :return: eeg, data_save_queue
            eeg - a reference to our eeg object
            data_save_queue - q that eeg data is put in order to be saved.
    """

    # # Start our threads for running the EEG.
    data_save_queue = Queue.Queue()
    eeg = None
    if eeg_system == CCDLConstants.EEGSystemNames.GUSB_AMP:
        eeg = CCDLGusb.GUSBAmpStreamer(channels_for_live=channels_for_live, out_buffer_queue=out_buffer_queue, data_save_queue=data_save_queue, subject_name=str(subject_num))
        threading.Thread(target=lambda: eeg_system.start_recording()).start()
    elif eeg_system == CCDLConstants.EEGSystemNames.BRAIN_AMP:
        eeg = CCDLBrainAmp.BrainAmpStreamer(channels_for_live=channels_for_live, out_buffer_queue=out_buffer_queue, data_save_queue=data_save_queue, subject_name=str(subject_num))
    elif eeg_system == CCDLConstants.EEGSystemNames.OpenBCI:
        eeg = CCDLOpenBCI.OpenBCIStreamer(channels_for_live=channels_for_live, out_buffer_queue=out_buffer_queue, data_save_queue=data_save_queue, subject_name=str(subject_num), port=comport)

    if eeg_system is not None:
        if subject_data_folder_path[-1] != '\\':
            subject_data_folder_path += '\\'
        save_data_file_path = subject_data_folder_path + 'Subject%s_eeg.csv' % str(subject_num)
        threading.Thread(target=lambda: CCDLEEGDatasaver.start_eeg_data_saving(save_data_file_path=save_data_file_path, queue=data_save_queue)).start()
        threading.Thread(target=lambda: eeg.start_recording()).start()
        if vebose:
            print "Saving EEG data to:\t", os.path.abspath(save_data_file_path)
    return eeg, data_save_queue


def run_pygame(queue, window_x_pos=-1920):
    """
    Run in a new process to start the pygame crosshair.
    """
    ccdl_cursor = CCDLPyCross.PyCrosshair(window_x_pos=window_x_pos)
    # threading.Thread(target=lambda: ccdl_cursor.run_with_queue(queue))
    ccdl_cursor.run_with_queue(q=queue)


def static_eeg_data_collection_experiment_setup(data_storage_path, eeg_system_type, take_init, run_arduino, arduino_comport, sleep_dur=3, verbose=True):
    """
    Starts our Data collection experiment.
    :param data_storage_path: Path to data storage dir
    :param eeg_system_type: ie 'OpenBCI', brain amp, etc.
    :param take_init: True if we want to take information from the user. If false, we'll use made up info.
    :param eeg_system_type: String - our type of eeg system
    :param task_description: String - a description of our task_description
    :param durations: A list of task_description durations
    :param tasks: list - a list of strings representing our tasks.  For example ['task_description', 'rest']
    :param start_time_list_keys: a list keys that represent starting each task_description. For example ['start_task_time', 'start_rest_time']
    :param start_eeg_index_keys: a list keys that represent starting each task_description. For example ['start_task_eeg_index', 'start_eeg_index']
    :param end_time_list_keys:
    :param end_eeg_index_keys: a list keys that represent starting each task_description. For example ['end_task_eeg_index', 'end_eeg_index']
    :param num_trials: Number of trials to run, where each trial consists of len(tasks) number of rounds.
    :param beep_duration: int - duration of beep
    :param text_dicts: list of text_dictionaries to show onscreen
    :param beep_freqs: list - duration of beeps.
    :param arduino_commands: list - list of arduino commands to supply before the trial.  If none, this parameter is ignored.
    :param arduino_queue: queue to put arduino commands in.
    :param verbose: bool - If true, will print our data path to the console.
    """
    ######################
    # Get Config Queues  #
    ######################
    # Start our Crosshair
    crosshair_mp_queue = multiprocessing.Queue()
    multiprocessing.Process(target=run_pygame, args=(crosshair_mp_queue,)).start()

    logger_queue = Queue.Queue()  # multithreading queue
    arduino_queue = Queue.Queue()

    if run_arduino:
        threading.Thread(target=lambda xx=arduino_queue, yy=arduino_comport: CCDLArduino.Arduino2LightInterface(com_port=yy).read_from_queue(queue=xx)).start()

    subject_num, subject_data_folder_path, task = get_user_info(data_storage_path, take_init)

    subject_log_file_path = subject_data_folder_path + 'Subject%s_log.txt' % subject_num
    # If we are wanting to save our data, we'll start our logging thread.
    threading.Thread(target=lambda: CCDLLog.Log(log_queue=logger_queue, subject_log_file_path=subject_log_file_path).start_log(verbose=False)).start()
    if verbose:
        print "Saving log to:\t", os.path.abspath(subject_log_file_path)

    # Starts our eeg and saves data.
    eeg, data_save_queue = start_eeg(eeg_system_type, subject_data_folder_path, subject_num)

    time.sleep(sleep_dur)  # All our threads can take a bit to start, especially if of our cache is cold.

    return crosshair_mp_queue, logger_queue, subject_num, subject_data_folder_path, task, eeg, arduino_queue, data_save_queue


def main_logic(logger_queue, eeg, eeg_system_type, task_description, crosshair_mp_queue, durations, tasks, start_time_list_keys, start_eeg_index_keys, end_time_list_keys, end_eeg_index_keys,
               num_trials, beep_duration, text_dicts, beep_freqs=(2500, 1000), arduino_commands=None, arduino_queue=None, subject_name=None):

    """
    Runs our data collection, adding our data the logger queue, supplying text onscreen and supplying commands to the arduino.
    :param logger_queue: queue - Queue to save our log.
    :param eeg: object - A reference to our eeg system.
    :param eeg_system_type: String - our type of eeg system
    :param task_description: String - a description of our task_description
    :param crosshair_mp_queue: multiprocess queue - Our queue for our crosshair.
    :param durations: A list of task_description durations
    :param tasks: list - a list of strings representing our tasks.  For example ['task_description', 'rest']
    :param start_time_list_keys: a list keys that represent starting each task_description. For example ['start_task_time', 'start_rest_time']
    :param start_eeg_index_keys: a list keys that represent starting each task_description. For example ['start_task_eeg_index', 'start_eeg_index']
    :param end_time_list_keys:
    :param end_eeg_index_keys: a list keys that represent starting each task_description. For example ['end_task_eeg_index', 'end_eeg_index']
    :param num_trials: Number of trials to run, where each trial consists of len(tasks) number of rounds.
    :param beep_duration: int - duration of beep
    :param text_dicts: list of text_dictionaries to show onscreen
    :param beep_freqs: list - duration of beeps.
    :param arduino_commands: list - list of arduino commands to supply before the trial.  If none, this parameter is ignored.
    :param arduino_queue: queue to put arduino commands in.
    """
    subject_name = str(subject_name)
    assert len(tasks) == len(start_eeg_index_keys) == len(start_time_list_keys) == len(end_time_list_keys) == len(end_eeg_index_keys) == len(durations) == len(beep_freqs) == len(text_dicts), "All lists must be of the same length."
    if arduino_commands is not None:
        assert len(arduino_commands) == len(tasks), "All lists must be of the same length."
        assert arduino_queue is not None, 'If arduino_commands commands is None, an arduino queue must be passed.'

    logger_queue.put(str({'durations_dict': str(durations),
                          'tasks': tasks,
                          'start_time_list_keys':start_time_list_keys, 'start_eeg_index_keys':start_eeg_index_keys,
                          'end_time_list_keys':end_time_list_keys, 'end_eeg_index_keys':end_eeg_index_keys,
                          'StartTime': time.time(), 'start_eeg_index': eeg.data_index,
                          'EEG_SYSTEM': eeg_system_type, 'fs': CCDLSI.get_eeg_sampling_rate(eeg_system_type),
                          'task_description': task_description,
                          'subject_name': subject_name,
                          'date_collected': "{:%B %d, %Y}".format(datetime.datetime.now())}) + '\n')
    start_time = time.time()
    trial_index = 0
    save_dict = None
    while trial_index < num_trials:
        save_dict = {'trial_index': trial_index}
        round_index = 0
        for task, start_time_key, end_time_key, start_eeg_index_key, end_eeg_index_key, duration, beep_freq, text_dict in \
                zip(tasks, start_time_list_keys, end_time_list_keys, start_eeg_index_keys, end_eeg_index_keys, durations, beep_freqs, text_dicts):
            arduino_command = arduino_commands[round_index] if arduino_commands is not None else None

            if arduino_command is not None:
                arduino_queue.put(arduino_command)
            print_info('Start %s' % task, trial_index, start_time)
            # Signal task_description start
            crosshair_mp_queue.put((CCDLPyCross.PyCrosshair.SET_TEXT_DICTIONARY_LIST, [text_dict]))
            winsound.Beep(beep_freq, beep_duration)

            # Get start time
            save_dict[start_time_key] = time.time()
            save_dict[start_eeg_index_key] = eeg.data_index
            # Do task_description
            time.sleep(duration)
            # Get end task_description time
            save_dict[end_time_key] = time.time()
            save_dict[end_eeg_index_key] = eeg.data_index
            round_index += 1
        # Save all the stuff.
        logger_queue.put(str(save_dict) + '\n')
        trial_index += 1
    crosshair_mp_queue.put((CCDLPyCross.PyCrosshair.SET_TEXT_DICTIONARY_LIST, [END_TEXT_DICT]))
