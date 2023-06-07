import numpy as np
import pandas as pd
import os
import time
import matplotlib.pyplot as plt

from oscilloscopes import Keysight3000T
from signal_generators import Agilent33250A

def test_oscillscope():
    ossc = Keysight3000T()
    ossc.connect(ossc.list_connections(verbose=True)[0])

    channels = [1]
    x_data, y_data, time_tags, channel_info = ossc.data_acquistion(10, channels, save_directory=r"data_test", segment_number=100)  # 

    for x, y in zip(x_data.values(), y_data.values()):
        plt.plot(x, y)
        
    plt.show()

def test_siggen():
    channel=1

    signal_gen = Agilent33250A()
    signal_gen.connect(signal_gen.list_connections(verbose=True)[0])

    signal_gen.turnOff(channel)
    signal_gen.setupSine(100, 1)
    signal_gen.turnOn(channel)


print()