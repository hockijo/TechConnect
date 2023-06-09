import numpy as np 
import pickle as pkl
import os
import time
import json


def init_directory(directory):
    if directory is not None:
        if not os.path.exists(directory):
            os.makedirs(directory)
    else:
        directory = os.getcwd()
    
    return directory

def init_save_dict(data, metadata):
    save_dict = {'data': data}
    if metadata is not None:
        save_dict.update({'metadata': metadata})
    return save_dict

def save_to_pkl(data, metadata=None, directory=None, filename=time.strftime(r"%d-%m-%Y-%H-%M-%S", time.localtime())):
    save_dict = init_save_dict(data, metadata)
    directory = init_directory(directory)

    with open(os.path.join(directory, f'{filename}.pkl'), 'wb') as f:
        pkl.dump(save_dict, f)

def save_to_txt(array, directory=None, filename=time.strftime(r"%d-%m-%Y-%H-%M-%S", time.localtime())):
    directory = init_directory(directory)
    np.savetxt(os.path.join(directory, f'{filename}.txt'), array)

def save_to_json(data, metadata=None, directory=None, filename=time.strftime(r"%d-%m-%Y-%H-%M-%S", time.localtime())):
    save_dict = init_save_dict(data, metadata)
    directory = init_directory(directory)

    with open(os.path.join(directory, f'{filename}.json'), 'w') as f:
        json.dump(save_dict, f)

def open_pkl(filename):
    with open(filename, 'rb') as f:
        file = pkl.load(f)
    return file

def unstitch_oscilloscope_data(x_data, y_data, time_tags):
    x_data = x_data[x_data<time_tags[1]]
    segment_length = x_data.shape[0]
    y_data = np.reshape(y_data, (segment_length, time_tags.shape[0]))
    return x_data, y_data

def stitch_oscilloscope_data(x_data, y_data, time_tags):
    x_data = np.concatenate([x_data + time_tag for time_tag in time_tags])
    y_data = np.reshape(y_data, x_data.shape)
    return x_data, y_data