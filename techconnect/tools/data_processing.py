import numpy as np
import scipy.signal as signal

def unstitch_oscilloscope_data(x_data, y_data, time_tags):
    x_data = x_data[x_data<time_tags[1]]
    segment_length = x_data.shape[0]
    y_data = np.reshape(y_data, (segment_length, time_tags.shape[0]))
    return x_data, y_data

def stitch_oscilloscope_data(x_data, y_data, time_tags):
    x_data = np.concatenate([x_data + time_tag for time_tag in time_tags])
    y_data = np.reshape(y_data, x_data.shape)
    return x_data, y_data

def find_single_ramp_1D(data, threshold='auto', direction=None, turning_point_indexes=(0,1), lpfilter=True):
    data_normd = (data-np.mean(data))/np.max(data)
    decimation = 1
    if lpfilter:
        data_normd = lowpass_filter(data_normd, 0.75)
    if len(data)>500:
        data_normd = signal.decimate(data_normd, 10)
        decimation *= 10
    if len(data)>2000:
        data_normd = signal.decimate(data_normd, 5)
        decimation *= 5

    data_diff=np.diff(data_normd)
    if threshold == 'auto':
        threshold = 0.65*np.max(np.abs(np.diff(data_diff)))
    turning_points, peak_info = signal.find_peaks(np.abs(np.diff(data_diff)), height=threshold)
    turning_points = turning_points*decimation + int(decimation//2)

    counter = 0
    if direction == 'forward':
        single_ramp_slope = -1
        while single_ramp_slope<=0:
            sr_turning_points = turning_points[counter:counter+2] + 1
            single_ramp = data[sr_turning_points[0]:sr_turning_points[1]]
            single_ramp_slope = np.mean(np.diff(single_ramp))
            counter += 1
    if direction == 'reverse':
        single_ramp_slope = 1
        while single_ramp_slope>=0:
            sr_turning_points = turning_points[counter:counter+2] + 1
            single_ramp = data[sr_turning_points[0]:sr_turning_points[1]]
            single_ramp_slope = np.mean(np.diff(single_ramp))
            counter += 1
    else:
        sr_turning_points = turning_points[turning_point_indexes[0]:turning_point_indexes[1]+1] + 1
        single_ramp = data[sr_turning_points[0]:sr_turning_points[1]]

    return sr_turning_points, single_ramp

def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def lowpass_filter(arr, corner_frequency):
    """
        Low pass filter a 1D array
    """
    b, a = signal.butter(3, corner_frequency)
    return signal.filtfilt(b, a, arr)