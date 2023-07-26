"""
Cavity scan data acquisition
============================
This example script performs data acquisition for a cavity scan using a Keysight 3000T series oscilloscope.

Usage:
    - Import the necessary modules: numpy, matplotlib.pyplot, Keysight3000T, tc_utils
    - Create an instance of the Keysight3000T class and connect to the oscilloscope using the `connect` method.
    - Define the `channels` variable as a list of channel numbers.
    - Call the `unstitched_data_acquisition` method of the Keysight3000T class to perform data acquisition.
    - Iterate through the acquired data and plot it using `matplotlib.pyplot.plot`.
    - Display the plot using `matplotlib.pyplot.show`.

Note:
    - This module assumes that the necessary dependencies are installed and the oscilloscope is properly connected.
    - The `unstitched_data_acquisition` method is responsible for acquiring the data and returning the necessary arrays.
    - The acquired data is plotted using `matplotlib.pyplot.plot`.
    - Make sure to adjust the parameters of the `unstitched_data_acquisition` method and customize the plot as needed.
"""


import numpy as np
import matplotlib.pyplot as plt
from techconnect.oscilloscopes.keysight import Keysight3000T
import techconnect.tools.file_handling as tc_utils

def main():
    """
    This function performs data acquisition and plots the acquired data.
    """
    # Create an instance of the Keysight3000T class
    ossc = Keysight3000T()
    
    # Connect to the first device listed in the connections
    # if there is more than one device connected, you may need to find the address manually
    ossc.connect(ossc.list_connections(verbose=True)[0]) 
    
    # Define the channels to acquire data from
    channels = [1,2,3,4]
    
    # Acquire the data using the specified parameters
    x_data, y_data, time_tags, channel_info = ossc.unstitched_data_acquisition(
        time_window=0.05, 
        segment_number=200, 
        channels=channels, 
        save_directory=None
    )
    
    # Plot the acquired data for each channel and segment
    for x, y_segments in zip(x_data.values(), y_data.values()):
        for seg in range(y_segments.shape[0]):
            plt.plot(x, y_segments[seg])
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()
