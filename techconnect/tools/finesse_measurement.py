import numpy as np
import matplotlib.pyplot as plt
import techconnect.tools.data_processing as datatools
import scipy.signal as signal

def begin_ramp(signal_generator, v1, v2, frequency=10, channel=1):
    amplitude_pp = np.abs(v1-v2) * 1.4
    offset = 0.8*np.min([v1, v2]) + amplitude_pp/2
    signal_generator.initialise_device()
    print(signal_generator.setupRamp(frequency, amplitude_pp, offset=offset, channel=channel))
    signal_generator.turnOn(channel=channel)

def collect_data(oscilloscope, frequency=10, channels=[1,2,3,4], repitition=10, save_directory=None):
    return oscilloscope.unstitched_data_acquisition(time_window=1/frequency, segment_number=repitition, channels=channels, save_directory=save_directory)

def calculate_finesse(x_data, y_data, height='auto'):
    turning_points, _ = datatools.find_single_ramp_1D(x_data, direction=None)
    x_data = x_data[turning_points[0]:turning_points[1]]
    y_data = y_data[turning_points[0]:turning_points[1]]

    #finding the peaks and calculating the finesse
    if height == 'auto': height = 0.75*np.max(y_data)
    peaks, peak_info = signal.find_peaks(y_data, height=height, width=1, distance=int(0.25*len(y_data)))

    fsr = np.abs(peaks[0]-peaks[1])
    fwhm = np.mean(peak_info['widths'])
    finesse = fsr/fwhm
    return x_data, y_data, finesse

def measure_finesse(signal_generator, oscilloscope, v1, v2, scan_channel, pd_channel,
                    frequency=10, signal_channel=1, ossc_channels=[1,2,3,4], 
                    repitition=10, save_directory=None, peak_height='auto'):
    """
    Measures the finesse of a cavity using a signal generator and an oscilloscope.

    Parameters
    ----------
    signal_generator : SignalGenerator
        The signal generator used to generate the scanning signal.
    oscilloscope : Oscilloscope
        The oscilloscope used to measure the optical signal.
    v1 : float
        The voltage of the first resonant peak.
    v2 : float
        The voltage of the second resonant peak.
    scan_channel : int
        The channel number measuring the scanning voltage.
    pd_channel : int
        The channel number of the photodetector.
    frequency : int, optional
        The frequency of the scanning signal. Defaults to 10.
    signal_channel : int, optional
        The channel number of the signal on the signal generator. Defaults to 1.
    ossc_channels : list of int, optional
        The channels to be used on the oscilloscope. Defaults to [1,2,3,4].
    repitition : int, optional
        The number of times to repeat the measurement. Defaults to 10.
    save_directory : str, optional
        The directory to save the collected data. Defaults to None.
    peak_height : str, optional
        The height of the peak. Defaults to 'auto', which corresponds to 0.75*max(pd_channel).

    Returns
    -------
    tuple
        A tuple containing the average finesse and a list of finesse values for each segment.
    """
    
    begin_ramp(signal_generator, v1, v2, frequency=frequency, channel=signal_channel)
    time, y_data, time_tags, channel_info = collect_data(oscilloscope, frequency=frequency, 
                                                           channels=ossc_channels, repitition=repitition, 
                                                           save_directory=save_directory)
    
    x_data = y_data[scan_channel]
    y_data = y_data[pd_channel]

    finesse_list = []
    for segment in range(y_data.shape[0]):
        segment_x_data, segment_y_data, finesse = calculate_finesse(x_data[segment], y_data[segment], height=peak_height)
    
        print(f"The finesse of segment {segment} is {finesse}\n")
        finesse_list.append(finesse)

        plt.figure()
        plt.plot(segment_x_data, segment_y_data)
        plt.xlabel('x_data')
        plt.ylabel('y_data')

    avg_finesse = np.mean(np.asarray(finesse_list))
    print(f"Average Finesse is {avg_finesse}\n")

    return avg_finesse, finesse_list

if __name__ == '__main__':
    from techconnect.signal_generators.rigol import DG4000
    from techconnect.oscilloscopes.keysight import Keysight3000T

    signal_generator = DG4000()
    oscilloscope = Keysight3000T()

    signal_generator.connect('USB0::0x1AB1::0x0641::DG4E205003358::INSTR')
    oscilloscope.connect('USB0::0x2A8D::0x1766::MY57452226::INSTR')
    v1 = 0.5
    v2 = 6
    scan_channel = 1
    pd_channel = 4

    avg_finesse, finesse_list = measure_finesse(signal_generator, oscilloscope, v1, v2, scan_channel, pd_channel,
                                                save_directory='data/finesse_measurement', signal_channel=2)
    plt.show()    
    signal_generator.close_device()
    oscilloscope.close_device()