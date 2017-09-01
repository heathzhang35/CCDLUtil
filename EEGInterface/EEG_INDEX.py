"""
To avoid messing with thread safety, we'll just keep two different counters.  Because only 1 thread is writing
the worst that could come out of this is, in a very rare case, a bad read.  Likely, this value can be reconstructed from
other values, but we'll go ahead and keep a backup eeg_index anyway. Concurrency issues for a single float value have never
been an issue for me (in a lot of data collection).
"""
CURR_EEG_INDEX = 0
CURR_EEG_INDEX_2 = 0
EEG_ID_VAL = 0
