import numpy as np

def unstitch_oscilloscope_data(x_data, y_data, time_tags):
    x_data = x_data[x_data<time_tags[1]]
    segment_length = x_data.shape[0]
    y_data = np.reshape(y_data, (segment_length, time_tags.shape[0]))
    return x_data, y_data

def stitch_oscilloscope_data(x_data, y_data, time_tags):
    x_data = np.concatenate([x_data + time_tag for time_tag in time_tags])
    y_data = np.reshape(y_data, x_data.shape)
    return x_data, y_data