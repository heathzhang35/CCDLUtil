import numpy as np
import CCDLUtil.ML.CrossValidation as CCDLCV
import CCDLUtil.DataManagement.Log as CCDLLog
import CCDLUtil.Utility.Constants as CCDLConstants
import CCDLUtil.Utility.SystemInformation as CCDLSI
import CCDLUtil.Graphics.PyCrosshair as CCDLPyCross
import CCDLUtil.SignalProcessing.Fourier as CCDLFourier
import CCDLUtil.DataManagement.DataParser as CCDLDataParser
import CCDLUtil.DataManagement.FileParser as CCDLFileParser
import CCDLUtil.EEGInterface.DataSaver as CCDLEEGDatasaver
import CCDLUtil.EEGInterface.gUSBAmp.GUSBAmpInterface as CCDLGusb
import CCDLUtil.Experiment.Static.Static_ML_Util as CCDL_Static_ML
import CCDLUtil.EEGInterface.OpenBCI.OpenBCIInterface as CCDLOpenBCI
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import CCDLUtil.ArduinoInterface.Arduino2LightInterface as CCDLArduino
import CCDLUtil.EEGInterface.BrainAmp.BrainAmpInterface as CCDLBrainAmp
import CCDLUtil.Experiment.Static.StaticConstants as CCDLStaticConstants

CLASSIFICATION_WINDOW_SIZE_SECONDS = 6  # TODO change this to 6


def get_channel_info(eeg_system):
    channel_list = None
    channel_dict = None
    if eeg_system == CCDLConstants.EEGSystemNames.GUSB_AMP:
        pass
    elif eeg_system == CCDLConstants.EEGSystemNames.BRAIN_AMP:
        channel_list = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 'Fz',
                        'Cz', 'Pz', 'Oz', 'FC1', 'FC2', 'CP1', 'CP2', 'FC5', 'FC6', 'CP5', 'CP6', 'TP9', 'TP10', 'POz']
        channel_dict = dict(list(zip(channel_list, list(range(len(channel_list)))))) if channel_list is not None else None
    elif eeg_system == CCDLConstants.EEGSystemNames.OpenBCI:
        pass
    else:
        raise ValueError('Invalid or unimplemented eeg system')
    # channel dict maps name to channel index.
    return channel_list, channel_dict


def extract_bci_data_by_type(eeg_data, eeg_type, eeg_col_index=0, clock_col_index=1):
    """

    :param eeg_data: Our eeg data with all extra parameters still present (like timestamps, indexes and aux values)
    :param eeg_type: str - our eeg system type
    :param eeg_col_index: Column of our eeg indexes (usually 0, defaults to 0)
    :param clock_col_index: Column of our eeg timestamps (usually 1, defaults to 1)
    :return:
    """
    eeg_indexes = eeg_data[:, eeg_col_index]
    clock_times = eeg_data[:, clock_col_index]
    aux_data = None
    if eeg_type == CCDLConstants.EEGSystemNames.BRAIN_AMP:
        trim_data = eeg_data[:, clock_col_index + 1:-1]  # remove the index stamps, timestamps and heart channel.
        assert trim_data.shape[1] == 31  # Assure we have 31 channels.
    else:
        raise NotImplemented('Only extracting BrainAmp data is supported currently.')
    return eeg_indexes, clock_times, trim_data, aux_data


def extract_csv(log_file_path, eeg_file_path, header_size=1):
    trial_list, header_list = CCDLFileParser.load_ast_dictionary_by_trial(file_path=log_file_path, header_size=header_size)
    start_eeg_index_keys = header_list[0]['start_eeg_index_keys']
    start_time_list_keys = header_list[0]['start_time_list_keys']
    end_eeg_index_keys = header_list[0]['end_eeg_index_keys']
    end_time_list_keys = header_list[0]['end_time_list_keys']
    tasks = header_list[0]['tasks']
    fs = header_list[0]['fs']
    subject_name = header_list[0]['subject_name']
    date_collected = header_list[0]['date_collected']
    eeg_type = header_list[0]['EEG_SYSTEM']
    task_description = header_list[0]['task_description']
    eeg_indexes, clock_times, eeg_data, aux_data = extract_bci_data_by_type(eeg_data=CCDLFileParser.iter_loadtxt(filename=eeg_file_path, skiprows=15),
                                                                            eeg_type=eeg_type)
    return start_eeg_index_keys, start_time_list_keys, end_eeg_index_keys, end_time_list_keys, tasks, eeg_type, task_description, eeg_indexes, clock_times, eeg_data, fs, date_collected, subject_name, aux_data, trial_list, header_list


def remove_unwanted_epochs(labels, epoched_data_list):
    """
    If an element in labels is none, it will remove that element in epoched_data list:
        example:
            if labels = [1, None, 0]
              and epoched_data_list = [epoch1, epoch2, epoch3]

            we would return:
                new_labels = [1, 0]
                epoched_data_list = [epoch1, epoch3]

    :param labels: Our labels that may contain None
    :param epoched_data_list: Our standard epoched data list
    :return: new_labels, new_epoch_data_list with None elements removed as descirbed.
    """
    new_epoch_data_list = []
    for ii, label in enumerate(labels):
        if label is not None:
            new_epoch_data_list.append(epoched_data_list[ii])
    new_labels = [xx for xx in labels if xx is not None]
    return new_labels, new_epoch_data_list


def save_classifier(log_file_path, classifier, verbose=True):
    """
    Saves our classifier.  Our classifier will be saved in the location and with the same name as our log file.
        The log.txt will be replaced with classifier.pickle when saving.
    :param log_file_path: str - Path to the log file
    :param classifier: object - Classifier to be saved
    :param Verbose: if verbose, we'll print where we are saving.
    """
    log_file_path = str(log_file_path)
    if not log_file_path.endswith('log.txt'):
        raise ValueError('Invalid log format. Must end with log.txt %s' % str(log_file_path))
    new_path = log_file_path.replace('log.txt', 'classifier.pickle')
    CCDLFileParser.save_pickle_file(pickle_file_path=new_path, data=classifier)
    if verbose:
        print("Classifier saved to:", new_path)


def main(log_file_path, eeg_file_path, eeg_type, channel_list, channel_dict, labels, relevant_indexes, feature_type, left_ssvep=11, right_ssvep=13, extract_by='indexes'):
    start_eeg_index_keys, start_time_list_keys, end_eeg_index_keys, end_time_list_keys, tasks, eeg_type, task_description, eeg_indexes, clock_times, \
        eeg_data, fs, date_collected, subject_name, aux_data, trial_list, header_list = extract_csv(log_file_path, eeg_file_path)

    mat_save_path = log_file_path.replace('_log.txt', '.mat')

    CCDLFileParser.save_standard_mat_format(save_path=mat_save_path, channel_names=channel_list, date_collected=date_collected, eeg_system=eeg_type,
                                            event_markers={'start_eeg_index_keys': start_eeg_index_keys,
                                                           'start_time_list_keys': start_time_list_keys,
                                                           'end_eeg_index_keys': end_eeg_index_keys,
                                                           'end_time_list_keys': end_time_list_keys},
                                            experiment_description=task_description, fs=fs, packet_indexes=eeg_indexes, time_stamps=clock_times, unepoched_eeg_data=eeg_data,
                                            aux_data=aux_data, subject_name=subject_name)
    nperseg = fs
    noverlap = int(fs // 2)
    """ Epoch the data """
    if extract_by == 'indexes':
        epoched_data_list = CCDLDataParser.epoch_data_from_key(eeg_data_indexes=eeg_indexes, eeg_data=eeg_data, trial_list=trial_list,
                                                               start_key_list=start_eeg_index_keys, end_key_list=end_eeg_index_keys)
    else:
        # Extract by time.
        epoched_data_list = CCDLDataParser.epoch_data_from_key(eeg_data_indexes=clock_times, eeg_data=eeg_data, trial_list=trial_list,
                                                               start_key_list=start_time_list_keys, end_key_list=end_time_list_keys)
    assert len(epoched_data_list) == len(labels)

    """ Tidy up our Epochs. """
    labels, epoched_data_list = remove_unwanted_epochs(labels=labels, epoched_data_list=epoched_data_list)  # remove epochs with label None.

    epoched_data_list = CCDLDataParser.cut_epoches_to_same_number_of_samples(epoched_data_list=epoched_data_list)

    assert len(epoched_data_list) == 2  # Classification is binary. We should gurentee this list is len 2.
    epoched_data = np.concatenate((epoched_data_list[0], epoched_data_list[1]), axis=0)
    labels = [labels[0]] * len(epoched_data_list[0]) + [labels[1]] * len(epoched_data_list[1])  # Create our labels

    rewindowed_epoched_data, labels, windows_per_epoch = CCDLDataParser.reepoch_data_with_fixed_window_size(epoched_data=epoched_data, labels=labels, window_size=CLASSIFICATION_WINDOW_SIZE_SECONDS * fs)
    # rewindowed_epoched_data -> shape (epoch, sample, channel)
    rewindowed_epoched_data = CCDLDataParser.idempotent_add_channel_dimension(rewindowed_epoched_data[:, :, relevant_indexes])

    """ Extract our Features """
    freqs, density = CCDLFourier.get_fft_all_channels(data=rewindowed_epoched_data, fs=fs, nperseg=nperseg, noverlap=noverlap)

    # Todo fix this so it can do more than just alpha.
    if feature_type == CCDLStaticConstants.ALPHA:
        feature_names, features = CCDL_Static_ML.extact_alpha_features_single_channel(freqs=freqs, density_from_only_relevant_channels=density, inclusive_exclusive_alpha_band=(8, 13))
    elif feature_type == CCDLStaticConstants.SSVEP_ALPHA:
        feature_names, features = CCDL_Static_ML.extact_alpha_features_single_channel(freqs=freqs, density_from_only_relevant_channels=density, inclusive_exclusive_alpha_band=(8, 14))
    elif feature_type == CCDLStaticConstants.SSVEP_LR:
        feature_names, features = CCDL_Static_ML.extract_ssvep_features(freqs=freqs, density_from_only_relevant_channels=density, freq_left=left_ssvep, freq_right=right_ssvep)
    else:
        raise
    features = features.squeeze()

    """ Fit Our Classifier """
    print("Cross Validation Score:", np.average(CCDLCV.run_leave_one_out_cv(features=features, labels=labels)))
    lda = LinearDiscriminantAnalysis()
    lda.fit(X=features, y=labels)
    save_classifier(log_file_path=log_file_path, classifier=lda)