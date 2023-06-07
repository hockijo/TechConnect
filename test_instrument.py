import numpy as np
import pandas as pd
import os
import time
import matplotlib.pyplot as plt

from oscilloscopes import Keysight3000T

ossc = Keysight3000T()
ossc.connect(ossc.list_connections()[0])

channels = [1]
x_data, y_data, time_tags, channel_info = ossc.data_acquistion(0.01, channels, save_directory=None, segment_number=50)  # r"data_test"

for x, y in zip(x_data.values(), y_data.values()):
    plt.plot(x, y)
    
plt.show()

print()