"""
For filters related to EEG data processing.
"""

import numpy as np
import scipy.signal as scisig

def butter_bandpass(low, high, fs, order=5):
    """
    Wrapper function for the scipy butter
    :param low: Frequency to filter above
    :param high: Frequency to filter below
    :param fs: Sampling rate (hz)
    :param order: Order of filter to use (default = 5)
    :return: Numerator (b) and denominator (a) polynomials of the IIR filter
    """
    nyq = 0.5 * fs
    b, a = scisig.butter(order, [low / nyq, high / nyq], btype='band')
    return b, a

def butter_bandpass_filter(data, low, high, fs, order=5):
    """
    Filters passed data with a bandpass butter function
    :param data: data to be bandpass filtered
    :param low: Frequency to filter above
    :param high: Frequency to filter below
    :param fs: Sampling rate (hz)
    :param order: Order of filter to use (default = 5)
    :return: filtered data (and modifies original data).
    """
    b, a = butter_bandpass(low, high, fs, order=order)
    data = data - np.mean(data)
    return scisig.lfilter(b, a, data)

def butter_notch_filter(data, notch, fs, Q=30.0):
    """
    Filters passed data with a notch butter function
    :param data: data to be bandpass filtered
    :param notch: Frequency to remove
    :param fs: Sampling rate (hz)
    :param Q: Quality factor (default 30.0)
    :return: filtered data (and modifies original data).
    """
    Q = Q
    w0 = notch/(fs/2)  # Normalized Frequency
    b, a = scisig.iirnotch(w0, Q)
    return scisig.lfilter(b, a, data)