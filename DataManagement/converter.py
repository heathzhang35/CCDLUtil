import pyedflib
import numpy as np
from os import listdir


def all_edf_files():
	return [i for i in listdir('.') if i.endswith('.edf')]

def convert_edf_to_txt(path):
	print "start converting " + path
	# get edf reader
	f = pyedflib.EdfReader(path)		
	# get signals in the file
	n = f.signals_in_file
	# get labels: channels from BrainAmp
	labels = f.getSignalLabels()
	# create data dict 
	data_dict = dict()
	sigbufs = np.zeros((n, f.getNSamples()[0]))	
	for i in np.arange(n):
		sigbufs[i, :] = f.readSignal(i)
		data_dict[str(labels[i])] = sigbufs[i]	
	
	# create new txt file
	ff = open(path[:-4] + '.csv', 'w')
	# write header
	ff.write(','.join(data_dict.keys()) + '\n')
	# write data
	data_lst = zip(*[data_dict[i] for i in data_dict.keys()])
	for i in data_lst:
		data = [str(d) for d in i]
		ff.write(','.join(data) + '\n')			
	ff.close()
	print "done"

def convert_all():
	for i in all_edf_files():
		convert_edf_to_txt(i)

convert_all()
