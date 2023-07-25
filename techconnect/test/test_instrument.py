import numpy as np
import pandas as pd
import os
import time
import matplotlib.pyplot as plt

from techconnect.oscilloscopes.keysight import Keysight3000T
from techconnect.signal_generators.agilent import Agilent33250A
import techconnect.tools.file_handling as file_handling

def test_oscillscope():
    ossc = Keysight3000T()
    ossc.connect(ossc.list_connections(verbose=True)[0])

    channels = [1]
    x_data, y_data, time_tags, channel_info = ossc.data_acquistion(10, channels, save_directory=r"data_test", segment_number=100)  # 

    save_dict = {
                    'x_data': x_data,
                    'y_data': y_data,
                    'time_tags': time_tags,
                    'channel_info': channel_info
                }

    # utils.save_to_json(save_dict, directory=r"data_test")

    for x, y in zip(x_data.values(), y_data.values()):
        plt.plot(x, y)

    plt.show()

def test_siggen():
    channel=1

    signal_gen = Agilent33250A(gpib_address=10)
    signal_gen.connect(signal_gen.list_connections(verbose=True)[0])

    signal_gen.turnOff(channel)
    signal_gen.setupSine(100, 1)
    signal_gen.turnOn(channel)

data = file_handling.open_pkl(r"data_test\08-06-2023-20-14-36_data_collection.pkl")
print()