import CCDLUtil.DataManagement.DataParser as CCDLDataParser
import CCDLUtil.DataManagement.FileParser as CCDLFileParser
import CCDLUtil.SignalProcessing.Fourier as CCDLFourier
import numpy as np


def extract_ssvep_features(freqs, density_from_only_relevant_channels, freq_left, freq_right):
    """

    :param freqs = list of freqs
    :param density_from_only_relevant_channels = density shape (epoch, density, channel) OR (epoch, density)
    :param freq_left: int - frequency of the left light
    :param freq_right: int - frequency of the right light
    :param nperseg: fs if nperseg is None
    :param noverlap: default 200
    :return: feature_names, features
        features is a np array of shape [epoch, feature]
    """
    freqs_left, density_left = CCDLDataParser.trim_freqs(density=density_from_only_relevant_channels, freqs=freqs, low=freq_left, high=freq_left + 1)
    freqs_right, density_right = CCDLDataParser.trim_freqs(density=density_from_only_relevant_channels, freqs=freqs, low=freq_right, high=freq_right + 1)
    features = np.concatenate((density_left, density_right), axis=1)
    feature_names = [freq_left, freq_right]
    return feature_names, features


def extract_single_ssvep_features(freqs, density_from_only_relevant_channels, freq_left, freq_right):
    """
    :param freqs = list of freqs
    :param density_from_only_relevant_channels = density shape (epoch, density, channel) OR (epoch, density)
    :param freq_left: int - frequency of the left light
    :param freq_right: int - frequency of the right light
    :param nperseg: fs if nperseg is None
    :param noverlap: default 200
    :return: feature_names, features
        features is a np array of shape [epoch, feature]
    """
    freqs_left, density_left = CCDLDataParser.trim_freqs(density=density_from_only_relevant_channels, freqs=freqs, low=freq_left, high=freq_left + 1)
    features = np.concatenate((density_left, density_left), axis=1)
    feature_names = freq_left
    return feature_names, features


def extact_alpha_features_single_channel(freqs, density_from_only_relevant_channels, inclusive_exclusive_alpha_band):
    """
    :param freqs = list of freqs
    :param density_from_only_relevant_channels = density shape (epoch, density, channel) OR (epoch, density)
    :param freq_left: int - frequency of the left light
    :param freq_right: int - frequency of the right light
    :param nperseg: fs if nperseg is None
    :param noverlap: default 200
    :return: feature_names, features
        features is a np array of shape [epoch, feature]
    """
    density = density_from_only_relevant_channels
    feature_names, features = CCDLDataParser.trim_freqs(freqs, density, low=inclusive_exclusive_alpha_band[0], high=inclusive_exclusive_alpha_band[1])
    if features.shape[2] == 1:
        features = np.squeeze(features)
    return feature_names, features
