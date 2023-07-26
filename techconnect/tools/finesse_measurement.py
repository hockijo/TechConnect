import numpy as np
import matplotlib.pyplot as plt

def begin_ramp(signal_generator, v1, v2, frequency=10, channel=1):
    amplitude_pp = np.abs(v1-v2)/2 * 1.4
    signal_generator.initialise_device()
    print(signal_generator.setup_ramp(frequency, amplitude_pp, offset=0.8*np.min([v1, v2]), channel=channel))
    signal_generator.turnOn(channel=channel)

def collect_data(oscilloscope, frequency=10, channels=[1,2,3,4], repitition=10, save_directory=None):
    