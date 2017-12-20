import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Filters import butter_bandpass_filter  

# read data
data = np.asarray(pd.read_csv('~/Downloads/H81_RestingState.csv'))
# get sub figs
fig, axarr = plt.subplots(8, 2, sharex=True)
# x
x = np.arange(256)
for i in range(2, 10):
    ax = axarr[i - 2, 0]
    ax.plot(x, data[0:256, i]) 

data = butter_bandpass_filter(data, 5, 100, 256, 2)
for i in range(2, 10):
    ax = axarr[i - 2, 1]
    ax.plot(x, data[0:256, i]) 

plt.show()
