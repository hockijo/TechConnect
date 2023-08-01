"""
Keysight
--------
This module contains the instrument classes for keysight oscilloscopes. It uses the methods created in the base class for the data parsing and saving,
but the communication is handled by the methods defined here.

Pieces salvaged from InfiniiVision_SegmentedMemory_Waveform.py
"""
import os
import time

import numpy as np 
import pickle as pkl

from techconnect.base._instrument import VISAInstrument
import techconnect.tools.file_handling as file_handling
from techconnect.oscilloscopes._ossc_base import Oscilloscope 

__all__ = ['Keysight3000T']

class Keysight3000T(Oscilloscope):
    """
    Class representing the Keysight 3000T series oscilloscope.

    Attributes
    ----------
    query_delay : float
        The delay between query and read in seconds.

    Methods
    -------
    __init__()
        Initializes the Keysight3000T object.
    segmented_initialization(channel)
        Perform segmented initialization for a specific channel.
    calculate_segment_number(acquistion_time)
        Calculate the number of segments based on the acquisition time.
    setup_time_window(time_window)
        Set up the time window for each segment.
    setup_triggering()
        Set up the triggering mode for the oscilloscope.
    segmented_acquistion_setup(segment_count, acquistion_type='NORMAL', sample_rate='AUTO')
        Set up the segmented acquisition mode.
    manual_channel_setup(channel, vertical_scale, vertical_range, vertical_offset, bw_limit, coupling)
        Perform manual setup for a specific channel.
    auto_setup()
        Perform automatic setup for the oscilloscope.
    single_acquisition()
        Perform a single acquisition.
    digitize_acquisition(channels)
        Digitize the acquisition for the specified channels.
    retrieve_channel_info(channel)
        Retrieve information about a specific channel.
    data_export_setup(channel)
        Set up data export for a specific channel.
    get_number_of_points(channel)
        Get the number of points for a specific channel.
    generate_x_data(channel_info)
        Generate the x-axis data based on the channel information.
    stitch_multiseg_x_data(x_data, time_tags)
        Stitch together the x-axis data for multi-segment acquisition.
    scale_y_data(y_data, channel_info)
        Scale the y-axis data based on the channel information.
    collect_single_segment_data(segment_index, channel, channel_info)
        Collect data for a single segment and channel.
    collect_multi_segment_data(number_of_segments, channel, stitched)
        Collect data for multiple segments and a specific channel.
    parse_and_save(save_directory, save_dict, acquisition_info)
        Parse and save the acquired data.
    stitched_data_acquisition(acquisition_time, channels, segment_number=1000, save_directory=None, acquisition_type='HRESOLUTION')
        Perform stitched data acquisition.
    unstitched_data_acquisition(time_window, segment_number, channels, save_directory=None, acquisition_type='HRESOLUTION')
        Perform unstitched data acquisition.
    """

    def __init__(self):
        super().__init__()
        self.query_delay = 0.1

    def segmented_initialization(self, channel):
        """
        Initializes the given channel by turning on the display, enabling automatic sample rate selection, and enabling automatic points selection.

        Parameters
        ----------
        channel : int
            The channel number to be initialized.

        Returns
        -------
        None
        """
        lines = (
            f":CHAN{channel}:DISPLAY ON",
            f":ACQUIRE:CHAN {channel}:SRATE:AUTO ON",
            f":ACQUIRE:CHAN {channel}:POINTS:AUTO ON"
        )

        self.write_lines(lines)
    
    def retrieve_channel_info(self, channel):
        channel_info = self.query_SCPI(f":WAVEFORM:SOURCE CHAN{channel};:WAVEFORM:PREAMBLE?").split(',')
        return {
            'format': int(channel_info[0]),
            'type': int(channel_info[1]),
            'points': int(float(channel_info[2])),
            'count': int(channel_info[3]),
            'xincrement': float(channel_info[4]),
            'xorigin': float(channel_info[5]),
            'xreference': float(channel_info[6]),
            'yincrement': float(channel_info[7]),
            'yorigin': float(channel_info[8]),
            'yreference': float(channel_info[9])
        }

    def calculate_segment_number(self, acquisition_time):
        """
        Calculate the segment number based on the acquisition time.

        Parameters
        ----------
        acquisition_time : float
            The acquisition time in seconds.

        Returns
        -------
        segment_number : int
            The calculated segment number.
        """
        sample_rate = int(float(self.query_SCPI(f":ACQUIRE:SRATE?")))
        points_per_segment = int(float(self.query_SCPI(f":ACQUIRE:POINTS?")))
        
        segment_number = int(np.ceil((acquisition_time*sample_rate)/points_per_segment))
        return segment_number
    
    def setup_time_window(self, time_window):
        """
        Sets up the time window for the instrument.

        Parameters
        ----------
        time_window : float
            The time window value to be set.

        Returns
        -------
        None
            This function does not return anything.
        """
        self.write_SCPI(f":TIMEBASE:SCALE {time_window/10}")

    def setup_triggering(self):
        """
        Sets up triggering for the device. It will be edge triggered externally, and on a positive slope
        """
        lines = (":TRIGGER:MODE EDGE",
                 ":TRIGGER:EDGE:SOURCE EXT",
                 ":TRIGGER:EDGE:SLOPE POSITIVE")
        self.write_lines(lines)

    def segmented_acquistion_setup(self, segment_count:int,  
                                    acquistion_type='NORMAL',
                                    sample_rate='AUTO'
                                    ):
        """
        Set up the segmented acquisition mode for the oscilloscope.

        Parameters
        ----------
        segment_count : int
            The number of segments to acquire.
        acquistion_type : str, optional
            The type of acquisition. Defaults to 'NORMAL'.
        sample_rate : str, optional
            The sample rate. Defaults to 'AUTO'.

        Returns
        -------
        None
        """
        lines = (
            f":ACQUIRE:MODE SEGMENTED",
            f":ACQUIRE:SEGMENTED:COUNT {segment_count}",
            f":ACQUIRE:TYPE {acquistion_type}"
        )

        self.write_lines(lines)

    def manual_channel_setup(self, channel: int,
                      vertical_scale,
                      vertical_range,
                      vertical_offset,
                      bw_limit,
                      coupling,
                      ):
        """
        Sets up the manual configuration for a specific channel.

        Parameters
        ----------
        channel : int
            The channel number.
        vertical_scale : 
            The vertical scale.
        vertical_range : 
            The vertical range.
        vertical_offset : 
            The vertical offset.
        bw_limit : 
            The bandwidth limit.
        coupling : 
            The coupling type.

        Returns
        -------
        None
            This function does not return anything.
        """
        lines = (
            f":CHAN{channel}:DISPLAY ON",
            f":CHAN{channel}:BWLIMIT{bw_limit}",
            f":CHAN{channel}:COUPLING{coupling}",
            f":CHAN{channel}:OFFSET{vertical_offset}",
            f":CHAN{channel}:RANGE{vertical_range}",
            f":CHAN{channel}:SCALE{vertical_scale}",
        )

        self.write_lines(lines)

    def auto_setup(self):
        """
        Automatically sets up the instrument by sending the SCPI command ":AUTOSCALE".
        """
        self.write_SCPI(f":AUTOSCALE")

    def single_acquisition(self):
        """
        Sends a command to the SCPI instrument to perform a single acquisition.
        """
        self.write_SCPI(f":SINGLE")

    def digitize_acquisition(self, channels):
        """
        Digitize the acquisition for the given channels.

        Parameters
        ----------
        channels : list of int
            A list of channel numbers to digitize.

        Returns
        -------
        None
            This function does not return anything.
        """
        line = ":DIGITIZE"
        if len(channels)>1:
            for channel in channels:
                line += f" CHANNEL{channel}"

        self.write_SCPI(line)

    def data_export_setup(self, channel):
        """
        Set up the data export for a specific channel.

        Parameters
        ----------
        channel : int
            The channel number.

        Returns
        -------
        None
            This function does not return anything.
        """
        lines = (
            f":WAVEFORM:SOURCE CHAN{channel}",
            f":WAVEFORM:FORMAT WORD",
            f":WAVEFORM:BYTEORDER LSBFIRST",
            f":WAVEFORM:UNSIGNED 0",
            f":WAVEFORM:POINTS MAX",
            f":WAVEFORM:POINTS:MODE RAW"
        )

        self.write_lines(lines)

    def get_number_of_points(self, channel):
        """
        Get the number of points in a waveform for a given channel.

        Parameters
        ----------
        channel : str
            The channel number.

        Returns
        -------
        int
            The number of points in the waveform.
        """
        return int(self.write_SCPI(f"WAVEFORM:SOURCE CHAN{channel};:WAVEFORM:POINTS?"))
    
    def collect_single_segment_data(self, segment_index, channel, channel_info):
        """
        Collects data for a single segment in the waveform.

        Parameters
        ----------
        segment_index : int
            The index of the segment to collect data from.
        channel : str
            The channel to collect data from.
        channel_info : dict
            A dictionary containing information about the channel.

        Returns
        -------
        tuple
            A tuple containing the segment time tag (float) and the collected data (ndarray).
        """
        self.write_SCPI(f":ACQUIRE:SEGMENTED:INDEX {segment_index}")
        segment_time_tag = float(self.query_SCPI(f":WAVEFORM:SEGMENTED:TTAG?"))

        y_data = np.asarray(self.instrument.query_binary_values(f":WAVEFORM:SOURCE CHAN{channel};DATA?", delay=0, datatype='h', is_big_endian=False))
        y_data = self.scale_y_data(y_data, channel_info)

        return segment_time_tag, y_data

